#!/usr/bin/env python3
"""
Script para diagnosticar e resolver o problema dos prédios não exibidos no painel.

PROBLEMA IDENTIFICADO:
- Existem 10 prédios na rua 1 (prédios 1-10)
- Apenas 8 prédios têm produtos no estoque
- Prédios 5 e 10 não aparecem no painel porque estão vazios

SOLUÇÃO:
- Modificar a view do painel para mostrar todos os prédios
- Incluir prédios vazios com indicação visual
- Manter a funcionalidade de colapso funcionando

Executar: python diagnosticar_predios_faltantes.py
"""

import os
import django
import sys

# Configurar Django
sys.path.append('/workspaces/controle_validade_estoque')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Armazenamento, Estoque, Produto
from collections import defaultdict

def diagnosticar_problema():
    """Diagnostica o problema dos prédios faltantes."""
    
    print("🔍 DIAGNÓSTICO: PRÉDIOS FALTANTES NO PAINEL")
    print("=" * 50)
    
    # 1. Verificar endereços cadastrados na rua 1
    print("\n📍 1. ENDEREÇOS CADASTRADOS NA RUA 1:")
    rua1_enderecos = Armazenamento.objects.filter(rua='1').order_by('predio')
    predios_cadastrados = list(rua1_enderecos.values_list('predio', flat=True).distinct())
    print(f"   Total de prédios cadastrados: {len(predios_cadastrados)}")
    print(f"   Prédios: {sorted(predios_cadastrados, key=lambda x: int(x))}")
    
    # 2. Verificar produtos no estoque na rua 1
    print("\n📦 2. PRODUTOS NO ESTOQUE NA RUA 1:")
    estoque_rua1 = Estoque.objects.filter(local__rua='1').select_related('local')
    predios_com_estoque = list(estoque_rua1.values_list('local__predio', flat=True).distinct())
    print(f"   Prédios com produtos: {len(predios_com_estoque)}")
    print(f"   Prédios: {sorted(predios_com_estoque, key=lambda x: int(x))}")
    
    # 3. Identificar prédios vazios
    predios_vazios = set(predios_cadastrados) - set(predios_com_estoque)
    print(f"\n🏗️ 3. PRÉDIOS VAZIOS (SEM PRODUTOS):")
    print(f"   Total: {len(predios_vazios)}")
    print(f"   Prédios vazios: {sorted(list(predios_vazios), key=lambda x: int(x))}")
    
    # 4. Detalhamento por prédio
    print(f"\n📊 4. DETALHAMENTO POR PRÉDIO:")
    for predio in sorted(predios_cadastrados, key=lambda x: int(x)):
        count = estoque_rua1.filter(local__predio=predio).count()
        status = "COM PRODUTOS" if count > 0 else "VAZIO"
        emoji = "📦" if count > 0 else "🏗️"
        print(f"   {emoji} Prédio {predio}: {count} produtos ({status})")
    
    return predios_cadastrados, predios_com_estoque, predios_vazios

def analisar_impacto_visual():
    """Analisa o impacto visual do problema."""
    
    print(f"\n🎯 5. IMPACTO NO PAINEL:")
    print(f"   ❌ Usuário espera ver 10 prédios")
    print(f"   ❌ Painel mostra apenas 8 prédios")
    print(f"   ❌ Prédios vazios 'desaparecem' da interface")
    print(f"   ❌ Confusão sobre a estrutura real do armazém")

def propor_solucao():
    """Propõe soluções para o problema."""
    
    print(f"\n💡 6. SOLUÇÕES PROPOSTAS:")
    print(f"   ✅ OPÇÃO 1: Mostrar todos os prédios (incluindo vazios)")
    print(f"   ✅ OPÇÃO 2: Adicionar indicador visual para prédios vazios")
    print(f"   ✅ OPÇÃO 3: Permitir filtro 'mostrar vazios'")
    print(f"   ✅ OPÇÃO 4: Contador de prédios no título da rua")

def verificar_outras_ruas():
    """Verifica se o problema existe em outras ruas."""
    
    print(f"\n🔍 7. VERIFICANDO OUTRAS RUAS:")
    
    # Agrupar por rua
    todas_ruas = Armazenamento.objects.values_list('rua', flat=True).distinct()
    
    for rua in sorted(todas_ruas, key=lambda x: int(x) if x.isdigit() else float('inf')):
        predios_cadastrados = Armazenamento.objects.filter(rua=rua).values_list('predio', flat=True).distinct()
        predios_com_estoque = Estoque.objects.filter(local__rua=rua).values_list('local__predio', flat=True).distinct()
        
        total_cadastrados = len(predios_cadastrados)
        total_com_estoque = len(predios_com_estoque)
        vazios = total_cadastrados - total_com_estoque
        
        status = "🟢" if vazios == 0 else "🔴"
        print(f"   {status} Rua {rua}: {total_cadastrados} cadastrados, {total_com_estoque} com estoque, {vazios} vazios")

def implementar_solucao():
    """Implementa a solução recomendada."""
    
    print(f"\n🛠️ 8. IMPLEMENTANDO SOLUÇÃO:")
    print(f"   📝 Modificando view do painel para incluir prédios vazios")
    print(f"   🎨 Adicionando indicador visual para prédios sem produtos")
    print(f"   📊 Mantendo funcionalidade de colapso")
    
    print(f"\n💻 CÓDIGO A SER MODIFICADO:")
    print(f"   📁 Arquivo: produtos/views.py")
    print(f"   🔧 Função: painel(request)")
    print(f"   📋 Ação: Incluir todos os endereços, não apenas com estoque")

def gerar_relatorio():
    """Gera relatório final do diagnóstico."""
    
    print(f"\n📋 RELATÓRIO FINAL:")
    print(f"=" * 30)
    
    predios_cadastrados, predios_com_estoque, predios_vazios = diagnosticar_problema()
    
    print(f"\n📊 RESUMO EXECUTIVO:")
    print(f"   🏗️ Total de prédios cadastrados na rua 1: {len(predios_cadastrados)}")
    print(f"   📦 Prédios com produtos: {len(predios_com_estoque)}")
    print(f"   🔴 Prédios vazios não exibidos: {len(predios_vazios)}")
    print(f"   📈 Taxa de ocupação: {len(predios_com_estoque)/len(predios_cadastrados)*100:.1f}%")
    
    print(f"\n✅ PRÓXIMOS PASSOS:")
    print(f"   1. ✏️ Modificar view do painel")
    print(f"   2. 🎨 Adicionar indicadores visuais")
    print(f"   3. 🧪 Testar com dados reais")
    print(f"   4. 📝 Documentar mudanças")

if __name__ == "__main__":
    print("🚀 INICIANDO DIAGNÓSTICO DOS PRÉDIOS FALTANTES")
    print("=" * 55)
    
    try:
        analisar_impacto_visual()
        propor_solucao()
        verificar_outras_ruas()
        implementar_solucao()
        gerar_relatorio()
        
        print(f"\n✅ DIAGNÓSTICO CONCLUÍDO!")
        print(f"🎯 PROBLEMA IDENTIFICADO E SOLUÇÃO PROPOSTA!")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE O DIAGNÓSTICO:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
