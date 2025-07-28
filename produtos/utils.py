"""
Utils otimizados para o sistema de controle de estoque
Consolidação de lógicas duplicadas e managers otimizados
"""

from datetime import date
from django.db.models import Q, Count, Prefetch
from django.db import transaction

class EstoqueManager:
    """Manager otimizado para operações de estoque"""
    
    @staticmethod
    def buscar_enderecos_vazios():
        """Buscar endereços vazios de forma otimizada"""
        from .models import Armazenamento, Estoque
        
        enderecos_com_estoque_ids = Estoque.objects.values_list('local_id', flat=True)
        return Armazenamento.objects.exclude(
            id__in=enderecos_com_estoque_ids
        ).order_by('rua', 'predio', 'nivel')
    
    @staticmethod
    def buscar_enderecos_ocupados():
        """Buscar endereços ocupados de forma otimizada"""
        from .models import Armazenamento, Estoque
        
        enderecos_com_estoque_ids = Estoque.objects.values_list('local_id', flat=True)
        return Armazenamento.objects.filter(
            id__in=enderecos_com_estoque_ids
        ).order_by('rua', 'predio', 'nivel')
    
    @staticmethod
    def buscar_enderecos_mixto():
        """Buscar endereços mistos (vazios primeiro) de forma otimizada"""
        from .models import Armazenamento, Estoque
        from itertools import chain
        
        enderecos_com_estoque_ids = Estoque.objects.values_list('local_id', flat=True)
        enderecos_vazios = Armazenamento.objects.exclude(
            id__in=enderecos_com_estoque_ids
        ).order_by('rua', 'predio', 'nivel')[:20]
        
        enderecos_ocupados = Armazenamento.objects.filter(
            id__in=enderecos_com_estoque_ids
        ).order_by('rua', 'predio', 'nivel')
        
        return list(chain(enderecos_vazios, enderecos_ocupados))
    
    @staticmethod
    def calcular_estatisticas():
        """Calcular estatísticas de estoque de forma otimizada"""
        from .models import Armazenamento, Estoque
        
        total_enderecos = Armazenamento.objects.count()
        enderecos_com_estoque = Estoque.objects.values('local').distinct().count()
        enderecos_vazios = total_enderecos - enderecos_com_estoque
        total_produtos = Estoque.objects.count()
        taxa_ocupacao = round((enderecos_com_estoque/total_enderecos)*100, 1) if total_enderecos > 0 else 0
        
        return {
            'total_enderecos': total_enderecos,
            'enderecos_com_estoque': enderecos_com_estoque,
            'enderecos_vazios': enderecos_vazios,
            'total_produtos': total_produtos,
            'taxa_ocupacao': taxa_ocupacao
        }

class ValidadeManager:
    """Manager otimizado para operações de validade"""
    
    @staticmethod
    def calcular_status_validade(lotes):
        """Calcular status de validade de forma otimizada"""
        if not lotes:
            return {
                'proxima_validade': None,
                'status_validade': "Sem lote",
                'dias_para_vencer': None
            }
        
        # Ordenar lotes por validade (FIFO)
        lotes_ordenados = sorted([l for l in lotes if l.validade], key=lambda x: x.validade)
        
        if not lotes_ordenados:
            return {
                'proxima_validade': None,
                'status_validade': "Sem validade",
                'dias_para_vencer': None
            }
        
        primeiro_lote = lotes_ordenados[0]
        proxima_validade = primeiro_lote.validade
        hoje = date.today()
        dias_para_vencer = (proxima_validade - hoje).days
        
        if dias_para_vencer < 0:
            status_validade = "Vencido"
        elif dias_para_vencer <= 7:
            status_validade = "Vence em breve"
        elif dias_para_vencer <= 30:
            status_validade = "Próximo ao vencimento"
        else:
            status_validade = "Válido"
        
        return {
            'proxima_validade': proxima_validade,
            'status_validade': status_validade,
            'dias_para_vencer': dias_para_vencer
        }
    
    @staticmethod
    def distribuir_validades_por_cards(estoques, todas_validades):
        """Distribuir validades pelos cards de forma otimizada"""
        enderecos_info = []
        
        for index, estoque in enumerate(estoques):
            # Cada card recebe uma validade específica da lista
            validade_do_card = None
            tipo_validade = "sem_validade"
            
            if todas_validades and index < len(todas_validades):
                validade_do_card = todas_validades[index]
                
                # Definir tipo da validade
                if index == 0:
                    tipo_validade = "saida"  # Primeira = mais antiga (saída)
                elif index == 1:
                    tipo_validade = "proxima"  # Segunda = próxima
                else:
                    tipo_validade = "futura"  # Demais = futuras
            
            endereco_info = {
                'id': estoque.id,
                'endereco_codigo': estoque.local.codigo or f"R{estoque.local.rua}P{estoque.local.predio}N{estoque.local.nivel}AP{estoque.local.ap}",
                'rua': estoque.local.rua,
                'predio': estoque.local.predio,
                'nivel': estoque.local.nivel,
                'ap': estoque.local.ap,
                'categoria': estoque.local.categoria_armazenamento,
                'data_armazenado': estoque.data_armazenado,
                'validade_do_card': validade_do_card,
                'tipo_validade': tipo_validade,
                'posicao_card': index + 1,
                'data_alteracao': estoque.data_alteracao,
            }
            
            enderecos_info.append(endereco_info)
        
        return enderecos_info

class ImportacaoManager:
    """Manager otimizado para operações de importação"""
    
    @staticmethod
    def validar_dados_csv(dados):
        """Validar dados do CSV de forma otimizada"""
        erros = []
        linhas_validas = []
        
        for i, linha in enumerate(dados, 1):
            erro_linha = []
            
            # Validações básicas
            if not linha.get('codigo', '').strip():
                erro_linha.append(f"Linha {i}: Código obrigatório")
            
            if not linha.get('nome', '').strip():
                erro_linha.append(f"Linha {i}: Nome obrigatório")
            
            # Validar validade se presente
            if linha.get('validade'):
                try:
                    from datetime import datetime
                    datetime.strptime(linha['validade'], '%d/%m/%Y')
                except ValueError:
                    erro_linha.append(f"Linha {i}: Data de validade inválida")
            
            if erro_linha:
                erros.extend(erro_linha)
            else:
                linhas_validas.append(linha)
        
        return linhas_validas, erros
    
    @staticmethod
    @transaction.atomic
    def importar_dados_otimizado(dados_validados):
        """Importar dados de forma otimizada com transação"""
        from .models import Produto, Lote, Estoque, Armazenamento
        from datetime import datetime
        
        produtos_criados = 0
        lotes_criados = 0
        estoques_criados = 0
        
        for linha in dados_validados:
            # Criar ou buscar produto
            produto, criado = Produto.objects.get_or_create(
                codigo=linha['codigo'],
                defaults={'nome': linha['nome']}
            )
            
            if criado:
                produtos_criados += 1
            
            # Criar lote se tiver validade
            if linha.get('validade'):
                validade_obj = datetime.strptime(linha['validade'], '%d/%m/%Y').date()
                lote, criado = Lote.objects.get_or_create(
                    produto=produto,
                    validade=validade_obj,
                    defaults={'quantidade': linha.get('quantidade', 1)}
                )
                
                if criado:
                    lotes_criados += 1
            
            # Criar estoque se tiver endereço
            if linha.get('endereco'):
                endereco = Armazenamento.objects.filter(
                    codigo=linha['endereco']
                ).first()
                
                if endereco:
                    estoque, criado = Estoque.objects.get_or_create(
                        produto=produto,
                        local=endereco,
                        defaults={
                            'data_armazenado': date.today(),
                            'data_validade': validade_obj if linha.get('validade') else None
                        }
                    )
                    
                    if criado:
                        estoques_criados += 1
        
        return {
            'produtos_criados': produtos_criados,
            'lotes_criados': lotes_criados,
            'estoques_criados': estoques_criados
        }

# Utilitários gerais
def formatar_codigo_endereco(local):
    """Formatar código de endereço de forma padronizada"""
    if local.codigo:
        return local.codigo
    return f"R{local.rua}P{local.predio}N{local.nivel}AP{local.ap}"

def calcular_dias_vencimento(validade):
    """Calcular dias para vencimento"""
    if not validade:
        return None
    
    hoje = date.today()
    return (validade - hoje).days

def obter_proxima_validade(produto):
    """Obter próxima validade de um produto (FIFO)"""
    lote = produto.lotes.filter(validade__isnull=False).order_by('validade').first()
    return lote.validade if lote else None

def otimizar_queryset_produto(queryset):
    """Otimizar queryset de produtos com prefetch"""
    return queryset.prefetch_related(
        Prefetch('lotes', queryset=queryset.model.objects.order_by('validade')),
        Prefetch('estoque_set', queryset=queryset.model.objects.select_related('local'))
    )
