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
from .models import Produto, Armazenamento, Estoque, Lote, HistoricoMovimentacao, Alerta
from django.utils import timezone
import csv
import io
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ProdutoForm, ArmazenamentoForm
from datetime import date, timedelta
import json

@login_required
def dashboard(request):
    """Dashboard principal com métricas e alertas"""
    # Estatísticas gerais
    stats = Produto.estatisticas()
    
    # Alertas ativos
    alertas_ativos = Alerta.objects.filter(status='ativo').order_by('-data_criacao')[:5]
    
    # Produtos próximos ao vencimento (próximos 7 dias)
    proximos_vencimento = []
    for produto in Produto.objects.all():
        proxima_validade = produto.proxima_validade()
        if proxima_validade and proxima_validade <= date.today() + timedelta(days=7):
            proximos_vencimento.append({
                'produto': produto,
                'validade': proxima_validade,
                'dias': (proxima_validade - date.today()).days
            })
    
    # Ocupação por prédio
    ocupacao_predios = {}
    for armazenamento in Armazenamento.objects.all():
        predio = armazenamento.predio
        if predio not in ocupacao_predios:
            ocupacao_predios[predio] = {'total': 0, 'ocupados': 0}
        ocupacao_predios[predio]['total'] += 1
        if not armazenamento.livre:
            ocupacao_predios[predio]['ocupados'] += 1
    
    # Calcular percentuais
    for predio in ocupacao_predios:
        if ocupacao_predios[predio]['total'] > 0:
            ocupacao_predios[predio]['percentual'] = round(
                (ocupacao_predios[predio]['ocupados'] / ocupacao_predios[predio]['total']) * 100, 1
            )
        else:
            ocupacao_predios[predio]['percentual'] = 0
    
    # Últimas movimentações
    ultimas_movimentacoes = HistoricoMovimentacao.objects.select_related('produto').order_by('-data_operacao')[:10]
    
    context = {
        'stats': stats,
        'alertas_ativos': alertas_ativos,
        'proximos_vencimento': proximos_vencimento,
        'ocupacao_predios': ocupacao_predios,
        'ultimas_movimentacoes': ultimas_movimentacoes,
    }
    
    return render(request, 'produtos/dashboard.html', context)

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
        # Criar histórico de movimentação
        HistoricoMovimentacao.objects.create(
            produto=produto,
            local_destino=local,
            tipo_operacao='entrada',
            quantidade=quantidade,
            usuario=request.user.username if request.user.is_authenticated else 'Sistema',
            observacoes=f'Produto armazenado - Lote: {numero_lote}'
        )
        
        # Verificar e criar alertas se necessário
        if validade:
            validade_date = timezone.datetime.strptime(validade, '%Y-%m-%d').date()
            dias_para_vencer = (validade_date - date.today()).days
            
            if dias_para_vencer <= 0:
                Alerta.objects.create(
                    tipo='vencido',
                    titulo=f'Produto Vencido: {produto.nome}',
                    mensagem=f'O produto {produto.nome} (código {produto.codigo}) está vencido desde {validade_date.strftime("%d/%m/%Y")}',
                    produto=produto
                )
            elif dias_para_vencer <= 30:
                Alerta.objects.create(
                    tipo='vencimento',
                    titulo=f'Produto Próximo ao Vencimento: {produto.nome}',
                    mensagem=f'O produto {produto.nome} (código {produto.codigo}) vence em {dias_para_vencer} dias ({validade_date.strftime("%d/%m/%Y")})',
                    produto=produto
                )

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
    filtro_predio = request.GET.get('predio', '')
    filtro_status = request.GET.get('status', '')
    filtro_categoria = request.GET.get('categoria', '')
    resultado_busca = None
    
    dados = Estoque.objects.select_related('produto', 'local').order_by('local__predio', 'local__rua', 'local__nivel', 'local__ap')

    # Filtros de busca
    if busca:
        dados = dados.filter(
            Q(produto__nome__icontains=busca) |
            Q(produto__codigo__icontains=busca) |
            Q(produto__fornecedor__icontains=busca)
        )
    
    if filtro_predio:
        dados = dados.filter(local__predio__icontains=filtro_predio)
    
    if filtro_categoria:
        dados = dados.filter(produto__categoria__icontains=filtro_categoria)

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

    # Filtro por status de validade
    if filtro_status:
        lista_filtrada = []
        for item in agrupados_lista:
            produto = item.produto
            proxima_validade = produto.proxima_validade()
            if proxima_validade:
                if filtro_status == 'vencido' and proxima_validade <= today:
                    lista_filtrada.append(item)
                elif filtro_status == 'proximo_vencimento' and today < proxima_validade <= hoje_mais_30:
                    lista_filtrada.append(item)
                elif filtro_status == 'valido' and proxima_validade > hoje_mais_30:
                    lista_filtrada.append(item)
        agrupados_lista = lista_filtrada

    # Agrupa os dados por prédio e depois por rua
    predios = {}
    for item in agrupados_lista:
        predio_nome = item.local.predio
        rua_nome = item.local.rua
        
        if predio_nome not in predios:
            predios[predio_nome] = {}
        
        if rua_nome not in predios[predio_nome]:
            predios[predio_nome][rua_nome] = []
        
        predios[predio_nome][rua_nome].append(item)
    
    # Função para ordenação numérica quando possível
    def ordenacao_inteligente(valor):
        """Ordena numericamente se possível, senão alfabeticamente"""
        try:
            return (0, int(valor))  # Se for número, usa ordenação numérica
        except ValueError:
            return (1, valor.lower())  # Se não for número, usa ordenação alfabética

    # Ordena os prédios, ruas e itens de forma inteligente
    predios_ordenados = {}
    
    # Ordena prédios
    predios_ordenados_keys = sorted(predios.keys(), key=ordenacao_inteligente)
    
    for predio_nome in predios_ordenados_keys:
        predios_ordenados[predio_nome] = {}
        
        # Ordena ruas dentro do prédio
        ruas_ordenadas_keys = sorted(predios[predio_nome].keys(), key=ordenacao_inteligente)
        
        for rua_nome in ruas_ordenadas_keys:
            # Ordena itens dentro da rua por nível e depois AP (ambos numericamente quando possível)
            predios_ordenados[predio_nome][rua_nome] = sorted(
                predios[predio_nome][rua_nome], 
                key=lambda x: (ordenacao_inteligente(str(x.local.nivel)), ordenacao_inteligente(str(x.local.ap)))
            )

    # Dados para filtros
    predios_disponiveis = list(Armazenamento.objects.values_list('predio', flat=True).distinct().order_by('predio'))
    categorias_disponiveis = list(Produto.objects.exclude(categoria__isnull=True).exclude(categoria='').values_list('categoria', flat=True).distinct().order_by('categoria'))

    return render(request, 'produtos/painel.html', {
        'predios': predios_ordenados,
        'busca': busca,
        'busca_codigo': busca_codigo,
        'filtro_predio': filtro_predio,
        'filtro_status': filtro_status,
        'filtro_categoria': filtro_categoria,
        'resultado_busca': resultado_busca,
        'predios_disponiveis': predios_disponiveis,
        'categorias_disponiveis': categorias_disponiveis,
        'today': today,
        'hoje_mais_30': hoje_mais_30
    })

def remover_produto(request,estoque_id):
    estoque = get_object_or_404(Estoque, id=estoque_id)
    produto = estoque.produto

    # Criar histórico de movimentação
    HistoricoMovimentacao.objects.create(
        produto=produto,
        local_origem=estoque.local,
        tipo_operacao='saida',
        quantidade=1,  # Assumindo quantidade 1, pode ser ajustado
        usuario=request.user.username if request.user.is_authenticated else 'Sistema',
        observacoes='Produto removido do estoque'
    )

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
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Produto "{produto.nome}" editado com sucesso!')
            return redirect('listar_produtos')
    else:
        form = ProdutoForm(instance=produto)
    
    return render(request, 'produtos/editar_produto.html', {
        'form': form, 
        'produto': produto
    })

@login_required
def listar_produtos(request):
    """Lista todos os produtos com opções de busca e edição"""
    query = request.GET.get('q', '')
    categoria_filter = request.GET.get('categoria', '')
    fornecedor_filter = request.GET.get('fornecedor', '')
    
    produtos = Produto.objects.all().order_by('nome')
    
    # Filtros de busca
    if query:
        produtos = produtos.filter(
            Q(nome__icontains=query) | 
            Q(codigo__icontains=query) |
            Q(categoria__icontains=query) |
            Q(fornecedor__icontains=query)
        )
    
    if categoria_filter:
        produtos = produtos.filter(categoria__icontains=categoria_filter)
    
    if fornecedor_filter:
        produtos = produtos.filter(fornecedor__icontains=fornecedor_filter)
    
    # Paginação
    paginator = Paginator(produtos, 20)  # 20 produtos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opções para filtros
    categorias = Produto.objects.values_list('categoria', flat=True).distinct().exclude(categoria__isnull=True).exclude(categoria='')
    fornecedores = Produto.objects.values_list('fornecedor', flat=True).distinct().exclude(fornecedor__isnull=True).exclude(fornecedor='')
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'categoria_filter': categoria_filter,
        'fornecedor_filter': fornecedor_filter,
        'categorias': categorias,
        'fornecedores': fornecedores,
        'total_produtos': produtos.count()
    }
    
    return render(request, 'produtos/listar_produtos.html', context)

@login_required
def excluir_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    
    # Verifica se o produto tem estoque
    tem_estoque = Estoque.objects.filter(produto=produto).exists()
    tem_lotes = Lote.objects.filter(produto=produto).exists()
    
    if request.method == 'POST':
        if tem_estoque or tem_lotes:
            messages.error(request, f'Não é possível excluir o produto "{produto.nome}" pois ele possui estoque ou lotes registrados.')
        else:
            nome_produto = produto.nome
            produto.delete()
            messages.success(request, f'Produto "{nome_produto}" excluído com sucesso!')
        return redirect('listar_produtos')
    
    return render(request, 'produtos/excluir_produto.html', {
        'produto': produto,
        'tem_estoque': tem_estoque,
        'tem_lotes': tem_lotes
    })

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
    
    # Buscar todos os endereços e agrupar por rua e prédio
    todos_enderecos = Armazenamento.objects.all()
    
    # Função para ordenação numérica quando possível
    def ordenacao_inteligente(valor):
        """Ordena numericamente se possível, senão alfabeticamente"""
        try:
            return (0, int(valor))  # Se for número, usa ordenação numérica
        except ValueError:
            return (1, valor.lower())  # Se não for número, usa ordenação alfabética
    
    # Agrupar endereços por rua e prédio
    enderecos_agrupados = {}
    for endereco in todos_enderecos:
        rua = endereco.rua
        predio = endereco.predio
        
        if rua not in enderecos_agrupados:
            enderecos_agrupados[rua] = {}
        
        if predio not in enderecos_agrupados[rua]:
            enderecos_agrupados[rua][predio] = []
        
        enderecos_agrupados[rua][predio].append(endereco)
    
    # Ordenar os grupos e endereços
    enderecos_ordenados = {}
    
    # Ordena ruas
    ruas_ordenadas_keys = sorted(enderecos_agrupados.keys(), key=ordenacao_inteligente)
    
    for rua in ruas_ordenadas_keys:
        enderecos_ordenados[rua] = {}
        
        # Ordena prédios dentro da rua
        predios_ordenados_keys = sorted(enderecos_agrupados[rua].keys(), key=ordenacao_inteligente)
        
        for predio in predios_ordenados_keys:
            # Ordena endereços dentro do prédio por nível e AP
            enderecos_ordenados[rua][predio] = sorted(
                enderecos_agrupados[rua][predio],
                key=lambda x: (ordenacao_inteligente(str(x.nivel)), ordenacao_inteligente(str(x.ap)))
            )
    
    return render(request, 'produtos/cadastrar_enderecos.html', {
        'form': form, 
        'ultimo_endereco': ultimo_endereco, 
        'enderecos_agrupados': enderecos_ordenados
    })

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

@login_required
def importar_produtos_csv(request):
    """View para importar produtos via CSV"""
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Nenhum arquivo foi enviado.')
            return redirect('importar_produtos_csv')
        
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Por favor, envie um arquivo CSV válido.')
            return redirect('importar_produtos_csv')
        
        try:
            # Lê o arquivo CSV
            decoded_file = csv_file.read().decode('utf-8-sig')  # utf-8-sig para remover BOM se presente
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            produtos_criados = 0
            produtos_existentes = 0
            erros = []
            
            # Mapear possíveis nomes de colunas
            mapeamento_colunas = {
                # Possíveis nomes para código
                'codigo': ['codigo', 'código', 'code', 'id', 'item', 'cod', 'cod_produto', 'produto_codigo'],
                # Possíveis nomes para nome
                'nome': ['nome', 'name', 'produto', 'descricao', 'descrição', 'description', 'item_name', 'produto_nome']
            }
            
            # Detectar as colunas corretas no CSV
            colunas_detectadas = list(reader.fieldnames)
            coluna_codigo = None
            coluna_nome = None
            
            for coluna in colunas_detectadas:
                coluna_lower = coluna.lower().strip()
                
                # Detectar coluna de código
                if not coluna_codigo:
                    for possivel_nome in mapeamento_colunas['codigo']:
                        if possivel_nome in coluna_lower:
                            coluna_codigo = coluna
                            break
                
                # Detectar coluna de nome
                if not coluna_nome:
                    for possivel_nome in mapeamento_colunas['nome']:
                        if possivel_nome in coluna_lower:
                            coluna_nome = coluna
                            break
            
            if not coluna_codigo or not coluna_nome:
                messages.error(request, f'Não foi possível detectar as colunas de código e nome. Colunas encontradas: {", ".join(colunas_detectadas)}')
                return redirect('importar_produtos_csv')
            
            # Processar cada linha
            for linha_num, row in enumerate(reader, start=2):  # Começar em 2 porque linha 1 é o cabeçalho
                try:
                    codigo = str(row[coluna_codigo]).strip()
                    nome = str(row[coluna_nome]).strip()
                    
                    if not codigo or not nome or codigo.lower() in ['nan', 'null', ''] or nome.lower() in ['nan', 'null', '']:
                        continue
                    
                    # Verificar se o produto já existe
                    if Produto.objects.filter(codigo=codigo).exists():
                        produtos_existentes += 1
                        continue
                    
                    # Criar o produto
                    Produto.objects.create(
                        codigo=codigo,
                        nome=nome,
                        peso='',  # Campo obrigatório, mas pode ficar vazio
                        categoria='Importado CSV',
                        fornecedor='',
                    )
                    
                    produtos_criados += 1
                    
                except Exception as e:
                    erros.append(f'Linha {linha_num}: {str(e)}')
            
            # Mensagens de resultado
            if produtos_criados > 0:
                messages.success(request, f'✅ {produtos_criados} produtos foram importados com sucesso!')
            
            if produtos_existentes > 0:
                messages.info(request, f'ℹ️ {produtos_existentes} produtos já existiam no sistema.')
            
            if erros:
                messages.warning(request, f'⚠️ {len(erros)} erros encontrados durante a importação.')
                for erro in erros[:5]:  # Mostrar apenas os primeiros 5 erros
                    messages.error(request, erro)
                if len(erros) > 5:
                    messages.error(request, f'... e mais {len(erros) - 5} erros.')
            
            return redirect('importar_produtos_csv')
            
        except Exception as e:
            messages.error(request, f'Erro ao processar o arquivo: {str(e)}')
            return redirect('importar_produtos_csv')
    
    # GET request - mostrar formulário
    total_produtos = Produto.objects.count()
    return render(request, 'produtos/importar_csv.html', {
        'total_produtos': total_produtos
    })

@login_required
def importar_abastecimento_csv(request):
    """View para importar dados de abastecimento (estoque) via CSV"""
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Nenhum arquivo foi enviado.')
            return redirect('importar_abastecimento_csv')
        
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Por favor, envie um arquivo CSV válido.')
            return redirect('importar_abastecimento_csv')
        
        try:
            # Lê o arquivo CSV
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            
            # Detectar separador (vírgula ou ponto-e-vírgula)
            separador = ','
            if ';' in decoded_file and decoded_file.count(';') > decoded_file.count(','):
                separador = ';'
                
            # Reset do io_string com separador correto
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string, delimiter=separador)
            
            produtos_abastecidos = 0
            produtos_nao_encontrados = 0
            produtos_autocadastrados = 0
            produtos_sem_validade = 0
            enderecos_criados = 0
            erros = []
            
            # Mapear possíveis nomes de colunas - Melhorado para FIFO
            mapeamento_colunas = {
                'codigo': ['codigo', 'código', 'code', 'id', 'item', 'cod', 'cod_produto', 'produto_codigo', 'cód', 'cód.', 'item_code', 'sku'],
                'nome': ['nome', 'name', 'produto', 'descricao', 'descrição', 'description', 'item_name', 'produto_nome', 'item_descricao'],
                'rua': ['rua', 'street', 'endereco_rua', 'rua_armazenamento', 'corredor', 'setor', 'area', 'zona'],
                'predio': ['predio', 'prédio', 'building', 'pred', 'endereco_predio', 'edificio', 'bloco', 'galpao', 'galpão'],
                'nivel': ['nivel', 'nível', 'floor', 'andar', 'endereco_nivel', 'pavimento', 'piso', 'niv', 'niv.'],
                'ap': ['ap', 'apartamento', 'apt', 'endereco_ap', 'posicao', 'posição', 'endereco', 'endereço', 'local', 'sala', 'box'],
                'validade': ['validade', 'vencimento', 'expiration', 'data_validade', 'expire_date', 'data_vencimento', 'vence_em', 'exp_date', 'val', 'val.', 'val. 1', 'val. 2', 'val. 3', 'val. 4'],
                'data_armazenado': ['data_armazenado', 'data_armazenamento', 'data_entrada', 'storage_date', 'entrada', 'data_estoque', 'recebimento', 'data abastec', 'data abastec.'],
                'lote': ['lote', 'numero_lote', 'batch', 'lot_number', 'numero_batch', 'batch_number', 'lote_numero', 'num_lote'],
                'quantidade': ['quantidade', 'qty', 'qtd', 'quantity', 'amount', 'estoque', 'saldo', 'unidades', 'qte'],
                'tipo': ['tipo', 'type', 'categoria', 'class', 'classificacao'],
                'palete': ['palete', 'pallet', 'estrado', 'base']
            }
            
            # Detectar as colunas corretas no CSV - Melhorado para FIFO
            colunas_detectadas = list(reader.fieldnames)
            colunas_mapeadas = {}
            
            # Primeiro, limpar e normalizar os nomes das colunas
            colunas_normalizadas = {}
            for coluna in colunas_detectadas:
                # Remove caracteres especiais e normaliza (mantém espaços para casos como "val. 1")
                coluna_normalizada = coluna.lower().strip()
                # Remove pontos no final, mas mantém pontos internos para casos como "val. 1"
                if coluna_normalizada.endswith('.'):
                    coluna_normalizada = coluna_normalizada[:-1].strip()
                colunas_normalizadas[coluna_normalizada] = coluna
            
            # Mapear colunas com busca mais flexível
            for tipo_campo, possivel_nomes in mapeamento_colunas.items():
                for coluna_normalizada, coluna_original in colunas_normalizadas.items():
                    for possivel_nome in possivel_nomes:
                        possivel_nome_normalizado = possivel_nome.lower().strip()
                        # Busca exata primeiro, depois contida
                        if possivel_nome_normalizado == coluna_normalizada or possivel_nome_normalizado in coluna_normalizada or coluna_normalizada in possivel_nome_normalizado:
                            colunas_mapeadas[tipo_campo] = coluna_original
                            break
                    if tipo_campo in colunas_mapeadas:
                        break
            
            # Tratamento especial para múltiplas colunas de validade (VAL. 1, VAL. 2, etc.)
            if 'validade' not in colunas_mapeadas:
                for coluna in colunas_detectadas:
                    coluna_lower = coluna.lower().strip()
                    if 'val' in coluna_lower and any(c.isdigit() for c in coluna_lower):
                        colunas_mapeadas['validade'] = coluna
                        break
            
            # Se não encontrou todas as colunas obrigatórias, tentar estratégia alternativa
            colunas_obrigatorias = ['codigo', 'rua', 'predio', 'nivel', 'ap']
            faltando = [col for col in colunas_obrigatorias if col not in colunas_mapeadas]
            
            # Estratégia alternativa: Se temos apenas 2 colunas e uma parece ser código, assumir formato simples
            if len(colunas_detectadas) >= 2 and 'codigo' not in colunas_mapeadas:
                # Tentar detectar coluna de código pela posição ou padrão
                for i, coluna in enumerate(colunas_detectadas):
                    coluna_lower = coluna.lower().strip()
                    if any(palavra in coluna_lower for palavra in ['cod', 'cód', 'id', 'sku', 'item']):
                        colunas_mapeadas['codigo'] = coluna
                        break
                # Se ainda não encontrou, usar primeira coluna como código
                if 'codigo' not in colunas_mapeadas and colunas_detectadas:
                    colunas_mapeadas['codigo'] = colunas_detectadas[0]
            
            # Para CSV simples (só código/produto), definir endereços padrão
            usar_endereco_padrao = False
            if len(faltando) >= 3:  # Faltam pelo menos 3 campos de endereço
                usar_endereco_padrao = True
                # Valores padrão para endereçamento
                endereco_padrao = {
                    'rua': 'RUA FIFO',
                    'predio': 'PREDIO FIFO',  
                    'nivel': 'N1',
                    'ap': '01'
                }
                messages.info(request, f'ℹ️ Usando endereçamento automático FIFO: {endereco_padrao}')
            
            # Verificar se ainda faltam colunas essenciais
            if not usar_endereco_padrao:
                faltando = [col for col in colunas_obrigatorias if col not in colunas_mapeadas]
                if faltando:
                    messages.error(request, f'Colunas obrigatórias não encontradas: {", ".join(faltando)}. Colunas disponíveis: {", ".join(colunas_detectadas)}. Mapeamento detectado: {colunas_mapeadas}')
                    return redirect('importar_abastecimento_csv')
            
            # Processar cada linha - Melhorado para FIFO
            for linha_num, row in enumerate(reader, start=2):
                try:
                    codigo = str(row[colunas_mapeadas['codigo']]).strip()
                    
                    # Limpar código (remover caracteres especiais, espaços extras)
                    codigo = ''.join(c for c in codigo if c.isalnum() or c in '-_').strip()
                    
                    if not codigo or codigo.lower() in ['nan', 'null', '', 'none']:
                        continue
                    
                    # Buscar o produto ou criar se não existir
                    try:
                        produto = Produto.objects.get(codigo=codigo)
                    except Produto.DoesNotExist:
                        # Tentar extrair nome do produto se disponível
                        nome_produto = codigo  # Padrão: usar código como nome
                        if 'nome' in colunas_mapeadas and colunas_mapeadas['nome'] in row:
                            nome_str = str(row[colunas_mapeadas['nome']]).strip()
                            if nome_str and nome_str.lower() not in ['nan', 'null', '', 'none', '-']:
                                nome_produto = nome_str[:100]  # Limitar tamanho do nome
                        
                        # Criar produto automaticamente
                        try:
                            produto = Produto.objects.create(
                                codigo=codigo,
                                nome=nome_produto,
                                categoria='Importado FIFO',
                                peso='',
                                fornecedor='Auto-cadastrado'
                            )
                            produtos_autocadastrados += 1
                            messages.info(request, f'✨ Produto "{codigo} - {nome_produto}" foi cadastrado automaticamente')
                        except Exception as e:
                            produtos_nao_encontrados += 1
                            erros.append(f'Linha {linha_num}: Erro ao criar produto "{codigo}": {str(e)}')
                            continue
                    
                    # Extrair dados do endereço (usar padrão se necessário)
                    if usar_endereco_padrao:
                        rua = endereco_padrao['rua']
                        predio = endereco_padrao['predio']
                        nivel = endereco_padrao['nivel']
                        # Gerar AP único baseado no código do produto
                        ap = f"{endereco_padrao['ap']}-{codigo[:8]}"  # Aumentar limite do AP
                    else:
                        rua = str(row[colunas_mapeadas['rua']]).strip()
                        predio = str(row[colunas_mapeadas['predio']]).strip()
                        nivel = str(row[colunas_mapeadas['nivel']]).strip()
                        ap = str(row[colunas_mapeadas['ap']]).strip()
                    
                    # Validar dados do endereço
                    if not all([rua, predio, nivel, ap]):
                        if usar_endereco_padrao:
                            erros.append(f'Linha {linha_num}: Erro ao gerar endereço padrão para código "{codigo}"')
                        else:
                            erros.append(f'Linha {linha_num}: Dados de endereço incompletos para código "{codigo}"')
                        continue
                    
                    # Buscar ou criar endereço de armazenamento
                    armazenamento, created = Armazenamento.objects.get_or_create(
                        rua=rua,
                        predio=predio,
                        nivel=nivel,
                        ap=ap,
                        defaults={'livre': False, 'capacidade_maxima': 1}
                    )
                    
                    if created:
                        enderecos_criados += 1
                    else:
                        armazenamento.livre = False
                        armazenamento.save()
                    
                    # Extrair dados opcionais - Melhorado para diferentes formatos e múltiplas validades
                    validade = None
                    
                    # Tentar múltiplas colunas de validade (VAL. 1, VAL. 2, VAL. 3, VAL. 4)
                    colunas_validade_possiveis = []
                    if 'validade' in colunas_mapeadas:
                        colunas_validade_possiveis.append(colunas_mapeadas['validade'])
                    
                    # Adicionar outras colunas que contenham "val"
                    for coluna in colunas_detectadas:
                        coluna_lower = coluna.lower().strip()
                        if 'val' in coluna_lower and coluna not in colunas_validade_possiveis:
                            colunas_validade_possiveis.append(coluna)
                    
                    # Tentar extrair validade de qualquer uma das colunas
                    valores_validade_tentativas = {}
                    for coluna_val in colunas_validade_possiveis:
                        if coluna_val in row and row[coluna_val]:
                            try:
                                validade_str = str(row[coluna_val]).strip()
                                valores_validade_tentativas[coluna_val] = validade_str
                                
                                if validade_str and validade_str.lower() not in ['nan', 'null', '', 'none', '-']:
                                    # Tentar diferentes formatos de data
                                    formatos_data = [
                                        '%Y-%m-%d',     # 2025-12-31
                                        '%d/%m/%Y',     # 31/12/2025
                                        '%d-%m-%Y',     # 31-12-2025
                                        '%Y/%m/%d',     # 2025/12/31
                                        '%d.%m.%Y',     # 31.12.2025
                                        '%Y.%m.%d',     # 2025.12.31
                                        '%d/%m/%y',     # 31/12/25
                                        '%d-%m-%y',     # 31-12-25
                                        '%y/%m/%d',     # 25/12/31
                                        '%Y%m%d',       # 20251231
                                        '%d%m%Y',       # 31122025
                                        '%d%m%y',       # 311225
                                    ]
                                    
                                    for formato in formatos_data:
                                        try:
                                            validade = timezone.datetime.strptime(validade_str, formato).date()
                                            break
                                        except ValueError:
                                            continue
                                            
                                    if validade:
                                        break  # Encontrou validade válida, parar de procurar
                                        
                            except Exception as e:
                                continue  # Tentar próxima coluna
                    
                    # Só gerar erro se encontrou valores nas colunas mas nenhum era válido
                    if not validade and valores_validade_tentativas:
                        # Verificar se pelo menos uma coluna tinha um valor não vazio
                        tem_valor_nao_vazio = any(
                            valor and str(valor).strip() and str(valor).strip().lower() not in ['nan', 'null', '', 'none', '-']
                            for valor in valores_validade_tentativas.values()
                        )
                        
                        if tem_valor_nao_vazio:
                            # Limitar a 3 valores para não poluir o log
                            valores_limitados = dict(list(valores_validade_tentativas.items())[:3])
                            erros.append(f'Linha {linha_num}: Formato de data inválido nas colunas de validade. Valores: {valores_limitados}')
                    
                    data_armazenado = date.today()
                    if 'data_armazenado' in colunas_mapeadas and colunas_mapeadas['data_armazenado'] in row and row[colunas_mapeadas['data_armazenado']]:
                        try:
                            data_str = str(row[colunas_mapeadas['data_armazenado']]).strip()
                            if data_str and data_str.lower() not in ['nan', 'null', '', 'none', '-']:
                                for formato in formatos_data:
                                    try:
                                        data_armazenado = timezone.datetime.strptime(data_str, formato).date()
                                        break
                                    except ValueError:
                                        continue
                        except Exception as e:
                            erros.append(f'Linha {linha_num}: Erro ao processar data de armazenamento: {str(e)}')
                    
                    numero_lote = ''
                    if 'lote' in colunas_mapeadas and colunas_mapeadas['lote'] in row:
                        numero_lote = str(row[colunas_mapeadas['lote']]).strip()
                        if numero_lote.lower() in ['nan', 'null', '', 'none', '-']:
                            numero_lote = ''
                    
                    # Se não tem lote definido, gerar um baseado na data e código
                    if not numero_lote and validade:
                        numero_lote = f"FIFO-{codigo}-{validade.strftime('%Y%m%d')}"
                    elif not numero_lote:
                        numero_lote = f"FIFO-{codigo}-{data_armazenado.strftime('%Y%m%d')}"
                    
                    quantidade = 1
                    if 'quantidade' in colunas_mapeadas and colunas_mapeadas['quantidade'] in row:
                        try:
                            qty_str = str(row[colunas_mapeadas['quantidade']]).strip()
                            if qty_str and qty_str.lower() not in ['nan', 'null', '', 'none', '-']:
                                # Limpar e converter quantidade
                                qty_str = qty_str.replace(',', '.')  # Converter vírgula para ponto
                                quantidade = max(1, int(float(qty_str)))  # Garantir pelo menos 1
                        except (ValueError, TypeError):
                            quantidade = 1
                    
                    # Criar registro de estoque
                    estoque, estoque_created = Estoque.objects.get_or_create(
                        produto=produto,
                        local=armazenamento,
                        defaults={
                            'data_armazenado': data_armazenado,
                            'usuario_responsavel': request.user.username if request.user.is_authenticated else 'Sistema CSV',
                            'observacoes': f'Importado via CSV - Linha {linha_num}'
                        }
                    )
                    
                    # Se não foi criado, atualizar data
                    if not estoque_created:
                        estoque.data_armazenado = data_armazenado
                        estoque.save()
                    
                    # Criar lote se tiver validade
                    if validade:
                        lote, lote_created = Lote.objects.get_or_create(
                            produto=produto,
                            validade=validade,
                            numero_lote=numero_lote,
                            defaults={'quantidade': quantidade}
                        )
                        
                        # Se lote já existe, somar quantidade
                        if not lote_created:
                            lote.quantidade += quantidade
                            lote.save()
                        
                        # Criar alertas se necessário
                        dias_para_vencer = (validade - date.today()).days
                        if dias_para_vencer <= 0:
                            Alerta.objects.get_or_create(
                                tipo='vencido',
                                produto=produto,
                                defaults={
                                    'titulo': f'Produto Vencido: {produto.nome}',
                                    'mensagem': f'O produto {produto.nome} (código {produto.codigo}) está vencido desde {validade.strftime("%d/%m/%Y")}'
                                }
                            )
                        elif dias_para_vencer <= 30:
                            Alerta.objects.get_or_create(
                                tipo='vencimento',
                                produto=produto,
                                defaults={
                                    'titulo': f'Produto Próximo ao Vencimento: {produto.nome}',
                                    'mensagem': f'O produto {produto.nome} (código {produto.codigo}) vence em {dias_para_vencer} dias ({validade.strftime("%d/%m/%Y")})'
                                }
                            )
                    else:
                        # Contar produtos sem validade (não é erro, é normal)
                        produtos_sem_validade += 1
                    
                    # Criar histórico de movimentação
                    HistoricoMovimentacao.objects.create(
                        produto=produto,
                        local_destino=armazenamento,
                        tipo_operacao='entrada',
                        quantidade=quantidade,
                        usuario=request.user.username if request.user.is_authenticated else 'Sistema CSV',
                        observacoes=f'Abastecimento via CSV - Lote: {numero_lote or "N/A"}'
                    )
                    
                    produtos_abastecidos += 1
                    
                except Exception as e:
                    erros.append(f'Linha {linha_num}: {str(e)}')
            
            # Mensagens de resultado
            if produtos_abastecidos > 0:
                messages.success(request, f'✅ {produtos_abastecidos} produtos foram abastecidos com sucesso!')
            
            if produtos_autocadastrados > 0:
                messages.success(request, f'✨ {produtos_autocadastrados} produtos foram cadastrados automaticamente!')
            
            if produtos_sem_validade > 0:
                messages.info(request, f'ℹ️ {produtos_sem_validade} produtos foram importados sem validade (normal para alguns produtos).')
            
            if enderecos_criados > 0:
                messages.info(request, f'🏢 {enderecos_criados} novos endereços de armazenamento foram criados.')
            
            if produtos_nao_encontrados > 0:
                messages.warning(request, f'⚠️ {produtos_nao_encontrados} produtos não puderam ser processados.')
            
            if erros and len(erros) <= 10:  # Mostrar todos os erros se forem poucos
                messages.warning(request, f'⚠️ {len(erros)} erros encontrados durante a importação.')
                for erro in erros:
                    messages.error(request, erro)
            elif erros:  # Muitos erros - mostrar apenas alguns
                messages.warning(request, f'⚠️ {len(erros)} erros encontrados durante a importação.')
                for erro in erros[:3]:  # Reduzir para 3 erros para não poluir
                    messages.error(request, erro)
                if len(erros) > 3:
                    messages.error(request, f'... e mais {len(erros) - 3} erros. Verifique os dados do CSV.')
            
            return redirect('importar_abastecimento_csv')
            
        except Exception as e:
            messages.error(request, f'Erro ao processar o arquivo: {str(e)}')
            return redirect('importar_abastecimento_csv')
    
    # GET request - mostrar formulário
    total_produtos = Produto.objects.count()
    total_estoque = Estoque.objects.count()
    total_enderecos = Armazenamento.objects.count()
    
    return render(request, 'produtos/importar_abastecimento.html', {
        'total_produtos': total_produtos,
        'total_estoque': total_estoque,
        'total_enderecos': total_enderecos
    })

@login_required
def alertas(request):
    """View para gerenciar alertas"""
    status_filtro = request.GET.get('status', 'ativo')
    
    alertas_list = Alerta.objects.all()
    if status_filtro:
        alertas_list = alertas_list.filter(status=status_filtro)
    
    alertas_list = alertas_list.order_by('-data_criacao')
    
    paginator = Paginator(alertas_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'produtos/alertas.html', {
        'page_obj': page_obj,
        'status_filtro': status_filtro
    })

@login_required
def marcar_alerta_lido(request, alerta_id):
    """Marca um alerta como lido"""
    alerta = get_object_or_404(Alerta, id=alerta_id)
    alerta.status = 'lido'
    alerta.data_leitura = timezone.now()
    alerta.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('alertas')

@login_required
def historico_movimentacoes(request):
    """View para histórico de movimentações"""
    tipo_filtro = request.GET.get('tipo', '')
    produto_filtro = request.GET.get('produto', '')
    
    movimentacoes = HistoricoMovimentacao.objects.select_related('produto', 'local_origem', 'local_destino')
    
    if tipo_filtro:
        movimentacoes = movimentacoes.filter(tipo_operacao=tipo_filtro)
    
    if produto_filtro:
        movimentacoes = movimentacoes.filter(
            Q(produto__nome__icontains=produto_filtro) |
            Q(produto__codigo__icontains=produto_filtro)
        )
    
    movimentacoes = movimentacoes.order_by('-data_operacao')
    
    paginator = Paginator(movimentacoes, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'produtos/historico.html', {
        'page_obj': page_obj,
        'tipo_filtro': tipo_filtro,
        'produto_filtro': produto_filtro,
        'tipos_operacao': HistoricoMovimentacao.TIPOS_OPERACAO
    })

@login_required
def extrair_produtos_abastecimento(request):
    """View para extrair e cadastrar produtos de um CSV de abastecimento"""
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Nenhum arquivo foi enviado.')
            return redirect('extrair_produtos_abastecimento')
        
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Por favor, envie um arquivo CSV válido.')
            return redirect('extrair_produtos_abastecimento')
        
        try:
            # Lê o arquivo CSV
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            
            # Detectar separador (vírgula ou ponto-e-vírgula)
            separador = ','
            if ';' in decoded_file and decoded_file.count(';') > decoded_file.count(','):
                separador = ';'
                
            # Reset do io_string com separador correto
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string, delimiter=separador)
            
            produtos_criados = 0
            produtos_existentes = 0
            erros = []
            
            # Mapear possíveis nomes de colunas
            mapeamento_colunas = {
                'codigo': ['codigo', 'código', 'code', 'id', 'item', 'cod', 'cod_produto', 'produto_codigo', 'cód', 'cód.', 'item_code', 'sku'],
                'nome': ['nome', 'name', 'produto', 'descricao', 'descrição', 'description', 'item_name', 'produto_nome', 'item_descricao'],
                'tipo': ['tipo', 'type', 'categoria', 'class', 'classificacao'],
            }
            
            # Detectar as colunas corretas no CSV
            colunas_detectadas = list(reader.fieldnames)
            colunas_mapeadas = {}
            
            # Normalizar e mapear colunas
            for coluna in colunas_detectadas:
                coluna_normalizada = coluna.lower().strip()
                if coluna_normalizada.endswith('.'):
                    coluna_normalizada = coluna_normalizada[:-1].strip()
                
                for tipo_campo, possivel_nomes in mapeamento_colunas.items():
                    for possivel_nome in possivel_nomes:
                        possivel_nome_normalizado = possivel_nome.lower().strip()
                        if possivel_nome_normalizado == coluna_normalizada or possivel_nome_normalizado in coluna_normalizada:
                            colunas_mapeadas[tipo_campo] = coluna
                            break
                    if tipo_campo in colunas_mapeadas:
                        break
            
            # Verificar se encontrou pelo menos código
            if 'codigo' not in colunas_mapeadas:
                # Tentar usar primeira coluna como código
                if colunas_detectadas:
                    colunas_mapeadas['codigo'] = colunas_detectadas[0]
                    messages.info(request, f'ℹ️ Usando "{colunas_detectadas[0]}" como coluna de código')
                else:
                    messages.error(request, 'Não foi possível detectar coluna de código no arquivo')
                    return redirect('extrair_produtos_abastecimento')
            
            # Processar cada linha
            for linha_num, row in enumerate(reader, start=2):
                try:
                    codigo = str(row[colunas_mapeadas['codigo']]).strip()
                    
                    # Limpar código
                    codigo = ''.join(c for c in codigo if c.isalnum() or c in '-_').strip()
                    
                    if not codigo or codigo.lower() in ['nan', 'null', '', 'none']:
                        continue
                    
                    # Verificar se o produto já existe
                    if Produto.objects.filter(codigo=codigo).exists():
                        produtos_existentes += 1
                        continue
                    
                    # Extrair nome do produto
                    nome_produto = codigo  # Padrão: usar código como nome
                    if 'nome' in colunas_mapeadas and colunas_mapeadas['nome'] in row:
                        nome_str = str(row[colunas_mapeadas['nome']]).strip()
                        if nome_str and nome_str.lower() not in ['nan', 'null', '', 'none', '-']:
                            nome_produto = nome_str[:100]  # Limitar tamanho do nome
                    
                    # Extrair categoria/tipo
                    categoria = 'Extraído de Abastecimento'
                    if 'tipo' in colunas_mapeadas and colunas_mapeadas['tipo'] in row:
                        tipo_str = str(row[colunas_mapeadas['tipo']]).strip()
                        if tipo_str and tipo_str.lower() not in ['nan', 'null', '', 'none', '-']:
                            categoria = tipo_str[:50]
                    
                    # Criar o produto
                    Produto.objects.create(
                        codigo=codigo,
                        nome=nome_produto,
                        categoria=categoria,
                        peso='',
                        fornecedor='Extraído CSV Abastecimento',
                    )
                    
                    produtos_criados += 1
                    
                except Exception as e:
                    erros.append(f'Linha {linha_num}: {str(e)}')
            
            # Mensagens de resultado
            if produtos_criados > 0:
                messages.success(request, f'✅ {produtos_criados} produtos foram extraídos e cadastrados com sucesso!')
            
            if produtos_existentes > 0:
                messages.info(request, f'ℹ️ {produtos_existentes} produtos já existiam no sistema.')
            
            if erros:
                messages.warning(request, f'⚠️ {len(erros)} erros encontrados durante a extração.')
                for erro in erros[:5]:
                    messages.error(request, erro)
                if len(erros) > 5:
                    messages.error(request, f'... e mais {len(erros) - 5} erros.')
            
            return redirect('extrair_produtos_abastecimento')
            
        except Exception as e:
            messages.error(request, f'Erro ao processar o arquivo: {str(e)}')
            return redirect('extrair_produtos_abastecimento')
    
    # GET request - mostrar formulário
    total_produtos = Produto.objects.count()
    return render(request, 'produtos/extrair_produtos_abastecimento.html', {
        'total_produtos': total_produtos
    })

def marcar_saida(request, estoque_id):
    """Marca um produto como saída, transferindo de 'inteiro' para 'meio'"""
    try:
        estoque = get_object_or_404(Estoque, id=estoque_id)
        
        # Verifica se o produto está atualmente como 'inteiro'
        if estoque.local.categoria_armazenamento != 'inteiro':
            messages.warning(request, 'Este produto já está marcado como saída.')
            return redirect('painel')
        
        # Procura por um local de saída (categoria 'meio') disponível
        # Preferencialmente na mesma rua e prédio
        local_saida = Armazenamento.objects.filter(
            categoria_armazenamento='meio',
            rua=estoque.local.rua,
            predio=estoque.local.predio,
            livre=True
        ).first()
        
        # Se não encontrou na mesma rua/prédio, procura qualquer local de saída disponível
        if not local_saida:
            local_saida = Armazenamento.objects.filter(
                categoria_armazenamento='meio',
                livre=True
            ).first()
        
        # Se ainda não encontrou, cria um novo local de saída no nível 0
        if not local_saida:
            local_saida = Armazenamento.objects.create(
                categoria_armazenamento='meio',
                rua=estoque.local.rua,
                predio=estoque.local.predio,
                nivel='0',
                ap=f'SAIDA-{estoque.local.rua}-{estoque.local.predio}',
                livre=True,
                capacidade_maxima=100,  # Capacidade maior para área de saída
                observacoes='Local de saída criado automaticamente'
            )
        
        # Registra a movimentação no histórico
        HistoricoMovimentacao.objects.create(
            produto=estoque.produto,
            tipo_operacao='saida',
            local_origem=estoque.local,
            local_destino=local_saida,
            data_operacao=date.today(),
            usuario_responsavel=request.user.username if request.user.is_authenticated else 'Sistema',
            observacoes=f'Produto marcado como saída - transferido de {estoque.local} para {local_saida}'
        )
        
        # Atualiza o local do estoque
        estoque_antigo = estoque.local
        estoque.local = local_saida
        estoque.data_armazenado = date.today()
        estoque.observacoes = f'Transferido para saída em {date.today().strftime("%d/%m/%Y")}'
        estoque.save()
        
        # Marca local antigo como livre se não houver mais produtos
        if not Estoque.objects.filter(local=estoque_antigo).exists():
            estoque_antigo.livre = True
            estoque_antigo.save()
        
        # Marca novo local como ocupado
        local_saida.livre = False
        local_saida.save()
        
        messages.success(request, f'Produto "{estoque.produto.nome}" marcado como saída com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao marcar produto como saída: {str(e)}')
    
    return redirect('painel')

def alterar_tipo_endereco(request, endereco_id):
    """Altera o tipo de armazenamento de um endereço"""
    try:
        endereco = get_object_or_404(Armazenamento, id=endereco_id)
        
        # Verifica se há produtos neste endereço
        produtos_no_endereco = Estoque.objects.filter(local=endereco).count()
        
        if produtos_no_endereco > 0:
            messages.warning(request, f'Não é possível alterar o tipo. Este endereço possui {produtos_no_endereco} produto(s) armazenado(s).')
            return redirect('painel')
        
        # Alterna o tipo
        if endereco.categoria_armazenamento == 'inteiro':
            endereco.categoria_armazenamento = 'meio'
            tipo_novo = 'Saída (Nível 0)'
        else:
            endereco.categoria_armazenamento = 'inteiro'
            tipo_novo = 'Palete Fechado (Nível 2)'
        
        endereco.save()
        
        messages.success(request, f'Tipo do endereço alterado para "{tipo_novo}" com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao alterar tipo do endereço: {str(e)}')
    
    return redirect('painel')