#!/usr/bin/env python3
"""
Análise completa do sistema de controle de validade de estoque
Identifica erros, problemas e inconsistências
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Produto, Lote, Estoque, Armazenamento
from django.core.exceptions import ValidationError
from django.db import models
from datetime import date, timedelta
import re

class DiagnosticoSistema:
    def __init__(self):
        self.problemas = []
        self.avisos = []
        self.informacoes = []
    
    def log_problema(self, categoria, descricao, objeto=None):
        self.problemas.append({
            'categoria': categoria,
            'descricao': descricao,
            'objeto': str(objeto) if objeto else None
        })
    
    def log_aviso(self, categoria, descricao, objeto=None):
        self.avisos.append({
            'categoria': categoria,
            'descricao': descricao,
            'objeto': str(objeto) if objeto else None
        })
    
    def log_info(self, categoria, descricao, valor=None):
        self.informacoes.append({
            'categoria': categoria,
            'descricao': descricao,
            'valor': valor
        })
    
    def analisar_produtos(self):
        """Analisa produtos e identifica problemas"""
        print("🔍 Analisando produtos...")
        
        total_produtos = Produto.objects.count()
        self.log_info('PRODUTOS', 'Total de produtos', total_produtos)
        
        if total_produtos == 0:
            self.log_aviso('PRODUTOS', 'Nenhum produto cadastrado no sistema')
            return
        
        # Produtos com nomes numéricos
        produtos_numericos = []
        for produto in Produto.objects.all():
            if produto.nome.strip().isdigit():
                produtos_numericos.append(produto)
        
        if produtos_numericos:
            self.log_problema('PRODUTOS', f'{len(produtos_numericos)} produtos com nomes apenas numéricos')
            for produto in produtos_numericos[:5]:  # Mostra apenas os primeiros 5
                self.log_problema('PRODUTO_NUMERICO', f'ID {produto.id}: "{produto.nome}" (Código: {produto.codigo})')
        
        # Produtos com nomes muito curtos
        produtos_curtos = Produto.objects.filter(nome__regex=r'^.{1}$')
        if produtos_curtos.exists():
            self.log_problema('PRODUTOS', f'{produtos_curtos.count()} produtos com nomes muito curtos')
        
        # Produtos com códigos duplicados
        codigos_duplicados = Produto.objects.values('codigo').annotate(
            count=models.Count('codigo')
        ).filter(count__gt=1)
        
        if codigos_duplicados:
            self.log_problema('PRODUTOS', f'{len(codigos_duplicados)} códigos duplicados encontrados')
        
        # Produtos sem peso
        produtos_sem_peso = Produto.objects.filter(models.Q(peso__isnull=True) | models.Q(peso=''))
        if produtos_sem_peso.exists():
            self.log_aviso('PRODUTOS', f'{produtos_sem_peso.count()} produtos sem peso definido')
        
        # Produtos sem categoria
        produtos_sem_categoria = Produto.objects.filter(models.Q(categoria__isnull=True) | models.Q(categoria=''))
        if produtos_sem_categoria.exists():
            self.log_aviso('PRODUTOS', f'{produtos_sem_categoria.count()} produtos sem categoria')
    
    def analisar_lotes(self):
        """Analisa lotes e identifica problemas"""
        print("🔍 Analisando lotes...")
        
        total_lotes = Lote.objects.count()
        self.log_info('LOTES', 'Total de lotes', total_lotes)
        
        if total_lotes == 0:
            self.log_aviso('LOTES', 'Nenhum lote cadastrado no sistema')
            return
        
        # Lotes vencidos
        hoje = date.today()
        lotes_vencidos = Lote.objects.filter(validade__lt=hoje)
        if lotes_vencidos.exists():
            self.log_aviso('LOTES', f'{lotes_vencidos.count()} lotes vencidos')
        
        # Lotes próximos ao vencimento (30 dias)
        data_limite = hoje + timedelta(days=30)
        lotes_proximo_vencimento = Lote.objects.filter(
            validade__gte=hoje,
            validade__lte=data_limite
        )
        if lotes_proximo_vencimento.exists():
            self.log_aviso('LOTES', f'{lotes_proximo_vencimento.count()} lotes próximos ao vencimento (30 dias)')
        
        # Lotes sem produto associado (órfãos)
        lotes_orfaos = Lote.objects.filter(produto__isnull=True)
        if lotes_orfaos.exists():
            self.log_problema('LOTES', f'{lotes_orfaos.count()} lotes órfãos (sem produto)')
        
        # Lotes com datas inválidas
        lotes_data_invalida = Lote.objects.filter(validade__lt=date(2020, 1, 1))
        if lotes_data_invalida.exists():
            self.log_problema('LOTES', f'{lotes_data_invalida.count()} lotes com datas inválidas')
    
    def analisar_estoque(self):
        """Analisa estoque e identifica problemas"""
        print("🔍 Analisando estoque...")
        
        total_estoque = Estoque.objects.count()
        self.log_info('ESTOQUE', 'Total de itens em estoque', total_estoque)
        
        if total_estoque == 0:
            self.log_aviso('ESTOQUE', 'Nenhum item em estoque')
            return
        
        # Estoque sem produto
        estoque_sem_produto = Estoque.objects.filter(produto__isnull=True)
        if estoque_sem_produto.exists():
            self.log_problema('ESTOQUE', f'{estoque_sem_produto.count()} itens de estoque órfãos')
        
        # Estoque sem local definido
        estoque_sem_local = Estoque.objects.filter(local__isnull=True)
        if estoque_sem_local.exists():
            self.log_problema('ESTOQUE', f'{estoque_sem_local.count()} itens sem local definido')
        
        # Estoque com datas futuras (suspeito)
        from datetime import date
        estoque_data_futura = Estoque.objects.filter(data_armazenado__gt=date.today())
        if estoque_data_futura.exists():
            self.log_aviso('ESTOQUE', f'{estoque_data_futura.count()} itens com data de armazenamento futura')
    
    def analisar_armazenamento(self):
        """Analisa armazenamento e identifica problemas"""
        print("🔍 Analisando armazenamento...")
        
        total_armazenamento = Armazenamento.objects.count()
        self.log_info('ARMAZENAMENTO', 'Total de locais cadastrados', total_armazenamento)
        
        if total_armazenamento == 0:
            self.log_aviso('ARMAZENAMENTO', 'Nenhum local de armazenamento cadastrado')
            return
        
        # Locais sem capacidade definida
        locais_sem_capacidade = Armazenamento.objects.filter(capacidade_maxima__lte=0)
        if locais_sem_capacidade.exists():
            self.log_aviso('ARMAZENAMENTO', f'{locais_sem_capacidade.count()} locais sem capacidade definida')
        
        # Verificar locais com mesmo endereço
        from django.db.models import Count
        locais_duplicados = Armazenamento.objects.values('rua', 'predio', 'nivel', 'ap').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if locais_duplicados:
            self.log_problema('ARMAZENAMENTO', f'{len(locais_duplicados)} locais com endereços duplicados')
        
        # Verificar ocupação dos locais
        locais_ocupados = 0
        locais_vazios = 0
        
        for local in Armazenamento.objects.all():
            if hasattr(local, 'estoque_set') and local.estoque_set.exists():
                locais_ocupados += 1
            else:
                locais_vazios += 1
        
        self.log_info('ARMAZENAMENTO', 'Locais ocupados', locais_ocupados)
        self.log_info('ARMAZENAMENTO', 'Locais vazios', locais_vazios)
    
    def analisar_integridade_dados(self):
        """Analisa integridade dos dados"""
        print("🔍 Analisando integridade dos dados...")
        
        # Produtos com lotes mas sem estoque
        produtos_com_lotes_sem_estoque = Produto.objects.filter(
            lotes__isnull=False
        ).exclude(
            id__in=Estoque.objects.values_list('produto_id', flat=True)
        ).distinct()
        
        if produtos_com_lotes_sem_estoque.exists():
            self.log_aviso('INTEGRIDADE', f'{produtos_com_lotes_sem_estoque.count()} produtos com lotes mas sem estoque')
        
        # Produtos em estoque mas sem lotes
        produtos_estoque_sem_lotes = Produto.objects.filter(
            id__in=Estoque.objects.values_list('produto_id', flat=True)
        ).filter(lotes__isnull=True).distinct()
        
        if produtos_estoque_sem_lotes.exists():
            self.log_aviso('INTEGRIDADE', f'{produtos_estoque_sem_lotes.count()} produtos em estoque mas sem lotes')
    
    def gerar_relatorio(self):
        """Gera relatório final"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO DE DIAGNÓSTICO DO SISTEMA")
        print("="*80)
        
        print(f"\n📈 INFORMAÇÕES GERAIS:")
        for info in self.informacoes:
            print(f"   • {info['categoria']}: {info['descricao']} = {info['valor']}")
        
        if self.problemas:
            print(f"\n❌ PROBLEMAS ENCONTRADOS ({len(self.problemas)}):")
            for problema in self.problemas:
                if problema['objeto']:
                    print(f"   • [{problema['categoria']}] {problema['descricao']} - {problema['objeto']}")
                else:
                    print(f"   • [{problema['categoria']}] {problema['descricao']}")
        
        if self.avisos:
            print(f"\n⚠️  AVISOS ({len(self.avisos)}):")
            for aviso in self.avisos:
                if aviso['objeto']:
                    print(f"   • [{aviso['categoria']}] {aviso['descricao']} - {aviso['objeto']}")
                else:
                    print(f"   • [{aviso['categoria']}] {aviso['descricao']}")
        
        if not self.problemas and not self.avisos:
            print("\n✅ PARABÉNS! Nenhum problema crítico encontrado!")
        
        print("\n" + "="*80)
    
    def executar_diagnostico(self):
        """Executa diagnóstico completo"""
        print("🚀 Iniciando diagnóstico completo do sistema...")
        print("="*80)
        
        try:
            self.analisar_produtos()
            self.analisar_lotes()
            self.analisar_estoque()
            self.analisar_armazenamento()
            self.analisar_integridade_dados()
            
            self.gerar_relatorio()
            
        except Exception as e:
            print(f"❌ Erro durante diagnóstico: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    diagnostico = DiagnosticoSistema()
    diagnostico.executar_diagnostico()
