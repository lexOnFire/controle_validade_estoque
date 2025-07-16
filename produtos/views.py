from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Armazenamento, Estoque
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
    produto = get_object_or_404(Produto,id=produto_id)
    enderecos_disponiveis = Armazenamento.objects.filter(livre=True)
    if request.method == 'POST':
        endereco_id = request.POST.get('endereco_id')
        local = get_object_or_404(Armazenamento, id=endereco_id)
        Estoque.objects.create(produto=produto, local=local)
        local.livre = False
        local.save()
        messages.success(request,'Produto armazenado com sucesso!')
        return redirect('buscar_produto')
    return render(request,'produtos/armazenar_produto.html',{'produto':produto,'enderecos':enderecos_disponiveis})

def relatorio_estoque(request):
    dados = Estoque.objects.select_related('produto','local')
    return render(request,'produtos/relatorios.html',{'dados':dados})

def painel(request):
    dados = Estoque.objects.select_related('produto','local')

    return render(request,'produtos/painel.html',{'dados': dados})

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