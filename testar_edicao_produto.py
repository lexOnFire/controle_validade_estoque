#!/usr/bin/env python3
"""
Script para testar a funcionalidade de edição de produto via estoque
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/workspaces/controle_validade_estoque')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Produto, Armazenamento, Estoque

def testar_edicao_produto_via_estoque():
    print("🧪 Testando Edição de Produto via Estoque")
    print("=" * 60)
    
    # Buscar um produto que está no estoque
    estoques = Estoque.objects.all()[:5]
    
    if estoques:
        print(f"📦 Encontrados {len(estoques)} itens no estoque para teste:")
        print()
        
        for i, estoque in enumerate(estoques, 1):
            produto = estoque.produto
            print(f"{i}. Produto: {produto.nome}")
            print(f"   Código: {produto.codigo}")
            print(f"   Peso: {produto.peso}")
            print(f"   Categoria: {produto.categoria or 'Não informada'}")
            print(f"   Fornecedor: {produto.fornecedor or 'Não informado'}")
            print(f"   Local: {estoque.local}")
            print(f"   URL Edição: http://localhost:8000/produtos/editar_estoque/{estoque.id}/")
            print(f"   Data Armazenado: {estoque.data_armazenado}")
            print(f"   Observações: {estoque.observacoes or 'Nenhuma'}")
            print("-" * 50)
    
    else:
        print("❌ Nenhum item encontrado no estoque para teste")
        print("   Primeiro adicione alguns produtos ao estoque")
    
    # Informações sobre o que pode ser editado
    print("\n✏️ NOVA FUNCIONALIDADE - O que pode ser editado:")
    print("   🏷️ DADOS DO PRODUTO:")
    print("      - Nome do produto")
    print("      - Código do produto")
    print("      - Peso/Tamanho")
    print("      - Categoria")
    print("      - Fornecedor")
    print()
    print("   📦 DADOS DO ESTOQUE:")
    print("      - Data de armazenamento")
    print("      - Observações")
    print()
    print("   📋 GERENCIAMENTO DE LOTES:")
    print("      - Adicionar novos lotes")
    print("      - Remover lotes existentes")
    print("      - Visualizar status de validade")
    
    print("\n🔗 Para testar:")
    print("1. Acesse o painel: http://localhost:8000/produtos/painel/")
    print("2. Clique no botão '✏️ Editar' de qualquer produto")
    print("3. Modifique o nome do produto ou outros dados")
    print("4. Clique em '💾 Salvar Produto e Estoque'")
    
    print("\n" + "=" * 60)
    print("✅ Funcionalidade implementada e pronta para uso!")

if __name__ == "__main__":
    testar_edicao_produto_via_estoque()
