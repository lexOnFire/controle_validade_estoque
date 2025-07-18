from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Armazenamento, Estoque, ValidadeEstoque
from django.contrib import messages
from .forms import ProdutoForm, ArmazenamentoForm


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
 
def armazenar_produto(request,produto_id):
    from .models import ValidadeEstoque
    produto = get_object_or_404(Produto,id=produto_id)
    enderecos_disponiveis = Armazenamento.objects.filter(livre=True) | Armazenamento.objects.filter(estoque__produto=produto)
    if request.method == 'POST':
        endereco_id = request.POST.get('endereco_id')
        validade = request.POST.get('validade')
        data_armazenado = request.POST.get('data_armazenado')
        adicionar_val = request.POST.get('adicionar_validade')
        local = get_object_or_404(Armazenamento, id=endereco_id)
        estoque_existente = Estoque.objects.filter(produto=produto, local=local).first()
        if estoque_existente:
            if not adicionar_val:
                # Pergunta ao usuário se deseja adicionar nova validade
                return render(request, 'produtos/armazenar_produto.html', {
                    'produto': produto,
                    'enderecos': enderecos_disponiveis,
                    'pergunta_validade': True,
                    'endereco_id': endereco_id,
                    'validade': validade,
                    'data_armazenado': data_armazenado
                })
            # Adiciona nova validade ao estoque existente
            ValidadeEstoque.objects.create(estoque=estoque_existente, validade=validade)
            messages.success(request, 'Nova validade adicionada ao mesmo endereço!')
            return redirect('painel')
        # Cria novo estoque e validade
        if data_armazenado:
            estoque = Estoque.objects.create(produto=produto, local=local, data_armazenado=data_armazenado)
        else:
            estoque = Estoque.objects.create(produto=produto, local=local)
        ValidadeEstoque.objects.create(estoque=estoque, validade=validade)
        local.livre = False
        local.save()
        messages.success(request,'Produto armazenado com sucesso!')
        return redirect('painel')
    return render(request,'produtos/armazenar_produto.html',{'produto':produto,'enderecos':enderecos_disponiveis})

from django.contrib.auth.decorators import login_required

@login_required
def relatorio_estoque(request):
    dados = Estoque.objects.select_related('produto','local')
    return render(request,'produtos/relatorios.html',{'dados':dados})

@login_required
def painel(request):
    dados = Estoque.objects.select_related('produto','local')
    resultado_busca = None
    perguntar_armazenar = False
    produto_encontrado = None
    if request.method == 'POST' and 'codigo_busca' in request.POST:
        codigo = request.POST.get('codigo_busca')
        try:
            produto = Produto.objects.get(codigo=codigo)
            resultado_busca = produto
            perguntar_armazenar = True
            produto_encontrado = produto
        except Produto.DoesNotExist:
            resultado_busca = 'not_found'
    if request.method == 'POST' and 'armazenar_produto_id' in request.POST:
        produto_id = request.POST.get('armazenar_produto_id')
        return redirect('armazenar_produto', produto_id=produto_id)
    return render(request,'produtos/painel.html',{
        'dados': dados,
        'resultado_busca': resultado_busca,
        'perguntar_armazenar': perguntar_armazenar,
        'produto_encontrado': produto_encontrado
    })

def remover_produto(request,estoque_id):
    try:
        estoque = get_object_or_404(Estoque,id=estoque_id)
        estoque.local.livre = True
        estoque.local.save()
        estoque.delete()
        messages.success(request, 'Produto removido e endereço liberado com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao remover produto: {str(e)}')
    return redirect('painel')

    return redirect('painel')    
def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('painel')
    else:
        form = ProdutoForm()

    return render(request, 'produtos/cadastrar_produto.html',{'form':form})

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