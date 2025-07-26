#!/usr/bin/env python3
"""
Script para demonstrar o painel com informações completas
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/workspaces/controle_validade_estoque')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Produto, Armazenamento, Estoque, Lote
from datetime import date, timedelta

def demonstrar_painel_completo():
    print("🖥️ Painel Completo - Informações Detalhadas")
    print("=" * 70)
    
    # Buscar alguns produtos no estoque para mostrar exemplo
    estoques = Estoque.objects.select_related('produto', 'local')[:5]
    
    if estoques:
        print("📋 Exemplo das informações mostradas no painel:")
        print()
        
        for i, estoque in enumerate(estoques, 1):
            produto = estoque.produto
            endereco = estoque.local
            lotes = produto.lotes.all().order_by('validade')
            
            print(f"🔹 PRODUTO {i}:")
            print(f"   📦 Nome: {produto.nome}")
            print(f"   🔢 Código: {produto.codigo}")
            print(f"   📍 Endereço: {endereco.rua}-{endereco.predio}-{endereco.nivel}-{endereco.ap}")
            
            if lotes.exists():
                primeiro_lote = lotes.first()
                proxima_validade = primeiro_lote.validade
                hoje = date.today()
                dias_para_vencer = (proxima_validade - hoje).days
                
                print(f"   📅 Próxima Validade: {proxima_validade.strftime('%d/%m/%Y')} ({dias_para_vencer} dias)")
                
                # Status de validade
                if dias_para_vencer < 0:
                    status = "❌ Vencido"
                elif dias_para_vencer <= 7:
                    status = "⚠️ Vence em breve"
                elif dias_para_vencer <= 30:
                    status = "🟡 Próximo ao vencimento"
                else:
                    status = "✅ Válido"
                
                print(f"   🚦 Status: {status}")
                
                if lotes.count() > 1:
                    print(f"   📦 Total de Lotes: {lotes.count()}")
                    print(f"   📋 Datas dos Lotes: {', '.join([l.validade.strftime('%d/%m') for l in lotes])}")
            else:
                print(f"   📦 Status: ⚪ Sem lote cadastrado")
            
            print(f"   📆 Data Armazenamento: {estoque.data_armazenado.strftime('%d/%m/%Y')}")
            
            if produto.updated_at:
                print(f"   🔄 Última Alteração: {produto.updated_at.strftime('%d/%m/%Y %H:%M')}")
            
            if estoque.observacoes:
                print(f"   📝 Observações: {estoque.observacoes}")
            
            print("-" * 50)
    
    else:
        print("❌ Nenhum produto encontrado no estoque")
    
    # Mostrar o que foi implementado
    print("\n✅ INFORMAÇÕES AGORA EXIBIDAS NO PAINEL:")
    print("   📍 Endereço completo (Rua-Prédio-Nível-AP)")
    print("   🔢 Código do produto")
    print("   📦 Nome do produto")
    print("   📅 Próxima data de validade")
    print("   🚦 Status de validade (Válido/Vencido/Vence em breve)")
    print("   📋 Total de lotes (se mais de 1)")
    print("   📆 Data de armazenamento")
    print("   🔄 Data da última alteração")
    print("   📝 Observações (se houver)")
    
    print("\n🎨 VISUAL MELHORADO:")
    print("   • Layout mais espaçado e organizado")
    print("   • Badges coloridos para status de validade")
    print("   • Informações agrupadas logicamente")
    print("   • Responsivo para dispositivos móveis")
    
    print(f"\n🔗 ACESSE O PAINEL:")
    print(f"   http://localhost:8000/produtos/painel/")
    
    print("\n" + "=" * 70)
    print("🎉 PAINEL RESTAURADO COM INFORMAÇÕES COMPLETAS!")
    print("=" * 70)

if __name__ == "__main__":
    demonstrar_painel_completo()
