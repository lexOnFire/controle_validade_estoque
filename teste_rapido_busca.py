#!/usr/bin/env python3
"""
Script para testar rapidamente a funcionalidade de busca por código em endereços vazios
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/workspaces/controle_validade_estoque')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Produto, Armazenamento, Estoque

def teste_rapido():
    print("🧪 Teste Rápido - Busca por Código em Endereços Vazios")
    print("=" * 60)
    
    # Verificar dados existentes
    total_produtos = Produto.objects.count()
    total_enderecos = Armazenamento.objects.count()
    total_estoque = Estoque.objects.count()
    
    print(f"📊 Dados do sistema:")
    print(f"   - Produtos: {total_produtos}")
    print(f"   - Endereços: {total_enderecos}")
    print(f"   - Itens em estoque: {total_estoque}")
    
    # Listar produtos disponíveis
    if total_produtos > 0:
        print(f"\n📦 Primeiros 5 produtos disponíveis:")
        for produto in Produto.objects.all()[:5]:
            print(f"   - {produto.nome} (Código: {produto.codigo})")
    
    # Verificar endereços vazios
    enderecos_vazios = []
    for endereco in Armazenamento.objects.all():
        if not Estoque.objects.filter(local=endereco).exists():
            enderecos_vazios.append(endereco)
    
    print(f"\n🏗️ Endereços vazios: {len(enderecos_vazios)}")
    
    if len(enderecos_vazios) > 0:
        print("   Primeiros 3 endereços vazios:")
        for endereco in enderecos_vazios[:3]:
            print(f"   - {endereco}")
            print(f"     URL: /produtos/buscar-produto-endereco/{endereco.id}/")
    
    # URLs para teste manual
    print(f"\n🔗 URLs para teste manual:")
    print(f"   - Painel: http://localhost:8000/produtos/painel/")
    if len(enderecos_vazios) > 0:
        endereco_teste = enderecos_vazios[0]
        print(f"   - Buscar em endereço vazio: http://localhost:8000/produtos/buscar-produto-endereco/{endereco_teste.id}/")
    
    print("=" * 60)
    print("✅ Teste concluído! Agora você pode testar manualmente no navegador.")

if __name__ == "__main__":
    teste_rapido()
