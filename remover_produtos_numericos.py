#!/usr/bin/env python3
"""
Script para remover produtos com nomes numéricos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Produto, Lote, Estoque
from django.db import transaction
import re

def remover_produtos_numericos(force=False):
    """Remove produtos com nomes apenas numéricos"""
    
    print("🔍 Identificando produtos com nomes numéricos...")
    
    # Buscar produtos problemáticos
    produtos_numericos = []
    for produto in Produto.objects.all():
        if produto.nome.strip().isdigit():
            produtos_numericos.append(produto)
    
    if not produtos_numericos:
        print("✅ Nenhum produto com nome numérico encontrado!")
        return
    
    print(f"📊 Encontrados {len(produtos_numericos)} produtos com nomes numéricos")
    
    # Separar produtos com e sem dependências
    produtos_sem_dependencias = []
    produtos_com_dependencias = []
    
    for produto in produtos_numericos:
        has_estoque = Estoque.objects.filter(produto=produto).exists()
        has_lotes = Lote.objects.filter(produto=produto).exists()
        
        if has_estoque or has_lotes:
            produtos_com_dependencias.append({
                'produto': produto,
                'tem_estoque': has_estoque,
                'tem_lotes': has_lotes
            })
        else:
            produtos_sem_dependencias.append(produto)
    
    print(f"   • Sem dependências: {len(produtos_sem_dependencias)}")
    print(f"   • Com dependências: {len(produtos_com_dependencias)}")
    
    if produtos_sem_dependencias:
        print(f"\n🗑️  Removendo {len(produtos_sem_dependencias)} produtos sem dependências:")
        
        with transaction.atomic():
            for produto in produtos_sem_dependencias:
                print(f"   • Removendo: \"{produto.nome}\" (ID: {produto.id}, Código: {produto.codigo})")
                produto.delete()
        
        print(f"✅ {len(produtos_sem_dependencias)} produtos removidos com sucesso!")
    
    if produtos_com_dependencias:
        print(f"\n⚠️  Produtos com dependências encontrados:")
        for item in produtos_com_dependencias[:10]:  # Mostra apenas os primeiros 10
            deps = []
            if item['tem_estoque']:
                deps.append('ESTOQUE')
            if item['tem_lotes']:
                deps.append('LOTES')
            
            produto = item['produto']
            print(f"   • \"{produto.nome}\" (ID: {produto.id}, Código: {produto.codigo}) - {', '.join(deps)}")
        
        if len(produtos_com_dependencias) > 10:
            print(f"   ... e mais {len(produtos_com_dependencias) - 10} produtos")
        
        if force:
            print(f"\n🔥 FORÇANDO remoção de {len(produtos_com_dependencias)} produtos com dependências...")
            
            with transaction.atomic():
                for item in produtos_com_dependencias:
                    produto = item['produto']
                    
                    # Remover estoque relacionado
                    if item['tem_estoque']:
                        Estoque.objects.filter(produto=produto).delete()
                        print(f"   • Removido estoque de: \"{produto.nome}\"")
                    
                    # Remover lotes relacionados
                    if item['tem_lotes']:
                        Lote.objects.filter(produto=produto).delete()
                        print(f"   • Removidos lotes de: \"{produto.nome}\"")
                    
                    # Remover produto
                    produto.delete()
                    print(f"   • Removido produto: \"{produto.nome}\" (ID: {produto.id})")
            
            print(f"✅ {len(produtos_com_dependencias)} produtos e suas dependências removidos!")
        else:
            print("\n💡 Para remover produtos com dependências, execute:")
            print("   python3 remover_produtos_numericos.py --force")

def main():
    import sys
    force = '--force' in sys.argv
    
    print("🚀 Iniciando remoção de produtos com nomes numéricos...")
    print("="*60)
    
    if force:
        print("⚠️  MODO FORÇA ATIVADO - Produtos com dependências também serão removidos!")
        resposta = input("\nTem certeza que deseja continuar? Digite 'CONFIRMAR': ")
        if resposta != 'CONFIRMAR':
            print("❌ Operação cancelada!")
            return
    
    try:
        remover_produtos_numericos(force=force)
        print("\n🎉 Operação concluída!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a operação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
