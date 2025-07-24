def editar_endereco(request, endereco_id):
    endereco = get_object_or_404(Armazenamento, id=endereco_id)
    if request.method == 'POST':
        form = ArmazenamentoForm(request.POST, instance=endereco)
        if form.is_valid():
            form.save()
            messages.success(request, 'Endereço editado com sucesso!')
            return redirect('cadastrar_enderecos')
    else:
        form = ArmazenamentoForm(instance=endereco)
    return render(request, 'produtos/editar_endereco.html', {'form': form, 'endereco': endereco})
from django.shortcuts import redirect
# View para editar/remover validade e data de armazenamento do lote
def editar_lote(request, lote_id):
    lote = get_object_or_404(Lote, id=lote_id)
    produto = lote.produto
    lotes = produto.lotes.all().order_by('validade')
    estoque = Estoque.objects.filter(produto=produto).order_by('data_armazenado').first()

    if request.method == 'POST':
        if 'remover_lote_id' in request.POST:
            remover_id = request.POST.get('remover_lote_id')
            Lote.objects.filter(id=remover_id).delete()
            return redirect('editar_lote', lote_id=lotes.exclude(id=remover_id).first().id if lotes.exclude(id=remover_id).exists() else lote_id)
        elif 'nova_validade' in request.POST:
            nova_validade = request.POST.get('nova_validade')
            novo_numero_lote = request.POST.get('novo_numero_lote', '')
            nova_quantidade = request.POST.get('nova_quantidade', 1)
            Lote.objects.create(produto=produto, validade=nova_validade, numero_lote=novo_numero_lote, quantidade=nova_quantidade)
            return redirect('editar_lote', lote_id=lote_id)
        else:
            validade = request.POST.get('validade')
            data_armazenado = request.POST.get('data_armazenado')
            lote.validade = validade
            lote.save()
            if estoque and data_armazenado:
                estoque.data_armazenado = data_armazenado
                estoque.save()
            return redirect('painel')

    return render(request, 'produtos/editar_lote.html', {
        'lote': lote,
        'lotes': lotes,
        'produto': produto,
        'data_armazenado': estoque.data_armazenado if estoque else None
    })
from django.contrib.auth.decorators import login_required
# Nova view para relatório completo do estoque
@login_required
def relatorio_completo(request):
    from datetime import date, timedelta
    estoque = Estoque.objects.select_related('produto', 'local').order_by('-data_armazenado')
    today = date.today()
    hoje_mais_30 = today + timedelta(days=30)
    return render(request, 'produtos/relatorio_completo.html', {
        'estoque': estoque,
        'today': today,
        'hoje_mais_30': hoje_mais_30
    })
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
    enderecos_disponiveis = list(Armazenamento.objects.filter(livre=True))
    # Se produto já está armazenado, inclui o endereço atual na lista
    if produto:
        estoque_atual = Estoque.objects.filter(produto=produto).first()
        if estoque_atual and estoque_atual.local not in enderecos_disponiveis:
            enderecos_disponiveis.append(estoque_atual.local)
    if request.method == 'POST':
        validade = request.POST.get('validade')
        data_armazenado = request.POST.get('data_armazenado')
        endereco_id = request.POST.get('endereco_id')
        numero_lote = request.POST.get('numero_lote', '')
        quantidade = request.POST.get('quantidade', 1)

        if not produto:
            # Criar novo produto
            codigo = request.POST.get('codigo')
            nome = request.POST.get('nome')
            peso = request.POST.get('peso')
            produto = Produto.objects.create(
                codigo=codigo,
                nome=nome,
                peso=peso
            )

        local = get_object_or_404(Armazenamento, id=endereco_id)

        # Adiciona novo lote
        lote = Lote.objects.create(
            produto=produto,
            validade=validade,
            numero_lote=numero_lote,
            quantidade=quantidade
        )

        # Atualiza ou cria registro de estoque
        estoque_existente = Estoque.objects.filter(produto=produto, local=local).first()
        if estoque_existente:
            # Atualiza data_armazenado para o mais recente, se informado
            if data_armazenado:
                estoque_existente.data_armazenado = data_armazenado
                estoque_existente.save()
            else:
                # Se não vier data, mantém a atual
                pass
        else:
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
    
    dados = Estoque.objects.select_related('produto', 'local').order_by('local__ap')

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

    # Agrupa por produto/local
    agrupados = {}
    for item in dados:
        chave = (item.produto.id, item.local.id)
        # Mantém apenas o registro mais recente (maior data_armazenado)
        if chave not in agrupados or item.data_armazenado > agrupados[chave].data_armazenado:
            agrupados[chave] = item
    agrupados_lista = list(agrupados.values())

    paginator = Paginator(agrupados_lista, 10)
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
    estoque = get_object_or_404(Estoque, id=estoque_id)
    produto = estoque.produto

    # Liberar endereço
    estoque.local.livre = True
    estoque.local.save()

    # Remover todos os lotes do produto
    produto.lotes.all().delete()

    # Remover todos os registros de estoque do produto
    Estoque.objects.filter(produto=produto).delete()

    # Mantém o Produto (nome/código) no banco
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
    ultimo_endereco = None
    if request.method == 'POST':
        if 'excluir_endereco_id' in request.POST:
            excluir_id = request.POST.get('excluir_endereco_id')
            Armazenamento.objects.filter(id=excluir_id).delete()
            messages.success(request, 'Endereço excluído com sucesso!')
            form = ArmazenamentoForm()  # Garante que o form seja instanciado
        elif request.POST.getlist('excluir_endereco_ids'):
            ids = request.POST.getlist('excluir_endereco_ids')
            Armazenamento.objects.filter(id__in=ids).delete()
            messages.success(request, f'{len(ids)} endereços excluídos com sucesso!')
            form = ArmazenamentoForm()
        else:
            form = ArmazenamentoForm(request.POST)
            if form.is_valid():
                ultimo_endereco = form.save()
                messages.success(request, 'Endereço cadastrado com sucesso!')
                form = ArmazenamentoForm(initial={
                    'rua': ultimo_endereco.rua,
                    'predio': ultimo_endereco.predio,
                    'nivel': ultimo_endereco.nivel,
                    'ap': ultimo_endereco.ap,
                })
    else:
        form = ArmazenamentoForm()
    enderecos = Armazenamento.objects.all().order_by('-id')
    return render(request, 'produtos/cadastrar_enderecos.html', {'form': form, 'ultimo_endereco': ultimo_endereco, 'enderecos': enderecos})

@login_required
def exportar_estoque_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="estoque.csv"'
    writer = csv.writer(response)
    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter
    from django.utils.encoding import smart_str
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="estoque.xlsx"'
    wb = Workbook()
    ws = wb.active
    ws.title = "Estoque"
    # Cabeçalho
    headers = ['Rua', 'Prédio', 'Nível', 'Ap', 'Código', 'Produto', 'Validade', 'Data de Armazenamento']
    ws.append(headers)
    # Dados
    all_rows = [headers]
    for item in Estoque.objects.select_related('produto', 'local'):
        lotes = list(item.produto.lotes.all().order_by('validade'))
        if lotes:
            for lote in lotes:
                row = [
                    str(item.local.rua),
                    str(item.local.predio),
                    str(item.local.nivel),
                    str(item.local.ap),
                    str(item.produto.codigo),
                    str(item.produto.nome),
                    lote.validade.strftime('%d/%m/%Y'),
                    item.data_armazenado.strftime('%d/%m/%Y')
                ]
                ws.append(row)
                all_rows.append(row)
        else:
            row = [
                str(item.local.rua),
                str(item.local.predio),
                str(item.local.nivel),
                str(item.local.ap),
                str(item.produto.codigo),
                str(item.produto.nome),
                '-',
                item.data_armazenado.strftime('%d/%m/%Y')
            ]
            ws.append(row)
            all_rows.append(row)
    # Ajusta largura das colunas conforme maior conteúdo
    for col_idx, col in enumerate(zip(*all_rows), 1):
        max_length = max(len(str(cell)) for cell in col)
        ws.column_dimensions[get_column_letter(col_idx)].width = max_length + 2
    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    response.write(output.getvalue())
    return response