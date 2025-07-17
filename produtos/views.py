from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Armazenamento, Estoque, Lote
from django.utils import timezone
import csv
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ProdutoForm, ArmazenamentoForm
from datetime import date, timedelta

def buscar_produto(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        try:
            produto = Produto.objects.get(codigo=codigo)
            return redirect('perguntar_armazenar',produto_id=produto.id)
        except Produto.DoesNotExist:
            messages.warning(request,'Produto não encontrado. Redirecionando para cadastro.')
            return redirect('cadastrar_produto')
    return render(request,'produtos/buscar_produto.html')

def perguntar_armazenar(request,produto_id):
    produto = get_object_or_404(Produto,id=produto_id)
    if request.method == 'POST':
        escolha = request.POST.get('armazenar')
        if escolha == 'sim':
            return redirect('armazenar_produto',produto_id=produto.id)
        else:
            messages.info(request,'operaçao cancelada')
            return redirect('buscar_produto')
    return render(request,'produtos/perguntar_armazenar.html',{'produto':produto})
 
def armazenar_produto(request, produto_id=None):
    produto = None
    if produto_id:
        produto = get_object_or_404(Produto, id=produto_id)
    enderecos_disponiveis = Armazenamento.objects.filter(livre=True)
    if request.method == 'POST':
        validade = request.POST.get('validade')
        quantidade = int(request.POST.get('quantidade', 1))
        data_armazenado = request.POST.get('data_armazenado')
        endereco_id = request.POST.get('endereco_id')

        if not produto:
            # Criar novo produto
            codigo = request.POST.get('codigo')
            nome = request.POST.get('nome')
            peso = request.POST.get('peso')
            
            produto = Produto.objects.create(
                codigo=codigo,
                nome=nome,
                peso=peso,
                validade=validade,
                quantidade=quantidade
            )
        else:
            # Atualizar produto existente com nova validade
            if not produto.validade:
                produto.validade = validade
            elif not produto.validade2:
                produto.validade2 = validade
            elif not produto.validade3:
                produto.validade3 = validade
            else:
                # Se todas as validades estiverem preenchidas, mover em sequência
                produto.validade = produto.validade2
                produto.validade2 = produto.validade3
                produto.validade3 = validade
            
            produto.quantidade += quantidade
            produto.save()

        local = get_object_or_404(Armazenamento, id=endereco_id)
        
        # Verificar se já existe estoque para este produto e local
        estoque_existente = Estoque.objects.filter(produto=produto, local=local).first()
        if estoque_existente:
            estoque_existente.data_armazenado = data_armazenado
            estoque_existente.save()
            messages.success(request, 'Produto atualizado com sucesso!')
        else:
            # Criar novo registro de estoque
            Estoque.objects.create(produto=produto, local=local, data_armazenado=data_armazenado)
            local.livre = False
            local.save()
            messages.success(request, 'Produto armazenado com sucesso!')
            
        return redirect('painel')

    return render(request, 'produtos/armazenar_produto.html', {
        'produto': produto,
        'codigo': produto.codigo if produto else request.GET.get('codigo', ''),
        'enderecos': enderecos_disponiveis,
        'hoje': timezone.now().date()
    })

@login_required
def relatorio_estoque(request):
    dados = Estoque.objects.select_related('produto', 'local').order_by('-data_armazenado')
    today = date.today()
    hoje_mais_30 = today + timedelta(days=30)
    
    paginator = Paginator(dados, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'produtos/relatorios.html', {
        'page_obj': page_obj,
        'today': today,
        'hoje_mais_30': hoje_mais_30
    })

@login_required
def painel(request):
    busca_codigo = request.GET.get('busca-codigo', '')
    busca = request.GET.get('busca', '')
    resultado_busca = None
    
    dados = Estoque.objects.select_related('produto', 'local').order_by('-data_armazenado')
    
    if busca:
        dados = dados.filter(
            Q(produto__nome__icontains=busca) |
            Q(produto__codigo__icontains=busca)
        )
    
    if busca_codigo:
        try:
            produto = Produto.objects.get(codigo=busca_codigo)
            resultado_busca = produto
        except Produto.DoesNotExist:
            resultado_busca = 'not_found'
    
    today = date.today()
    hoje_mais_30 = today + timedelta(days=30)
    
    paginator = Paginator(dados, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'produtos/painel.html', {
        'page_obj': page_obj,
        'busca': busca,
        'busca_codigo': busca_codigo,
        'resultado_busca': resultado_busca,
        'today': today,
        'hoje_mais_30': hoje_mais_30
    })

def remover_produto(request,estoque_id):
    estoque = get_object_or_404(Estoque,id=estoque_id)

    #liberar endereço
    estoque.local.livre = True
    estoque.local.save()

    #remover registro estoque
    estoque.delete()

    return redirect('painel')
    
def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('painel')
    else:
        form = ProdutoForm()
    return render(request, 'produtos/cadastrar_produto.html', {'form': form})

@login_required
def cadastrar_enderecos(request):
    if request.method == 'POST':
        form = ArmazenamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Endereço cadastrado com sucesso!')
            return redirect('painel')
    else:
        form = ArmazenamentoForm()
    return render(request, 'produtos/cadastrar_enderecos.html', {'form': form})

@login_required
def exportar_estoque_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="estoque.csv"'
    writer = csv.writer(response)
    writer.writerow(['Produto', 'Código', 'Quantidade', 'Validade', 'Endereço', 'Data de Abastecimento'])
    for item in Estoque.objects.select_related('produto', 'local'):
        writer.writerow([
            item.produto.nome,
            item.produto.codigo,
            item.produto.quantidade,
            item.produto.validade,
            item.local,
            item.data_armazenado
        ])
    return response