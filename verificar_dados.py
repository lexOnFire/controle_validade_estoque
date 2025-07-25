#!/usr/bin/env python3
"""
Script para verificar os dados do sistema
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Armazenamento, Estoque, Produto

def verificar_dados():
    """Verifica os dados atuais do sistema"""
    
    print("🔍 VERIFICANDO DADOS DO SISTEMA...")
    
    print("\n=== LOCAIS DE ARMAZENAMENTO ===")
    locais = Armazenamento.objects.all()[:10]
    for local in locais:
        print(f"{local.id}: {local} - Categoria: {local.categoria_armazenamento}")
    print(f"Total: {Armazenamento.objects.count()} locais")
    
    print("\n=== PRODUTOS NO ESTOQUE ===")
    estoques = Estoque.objects.select_related('produto', 'local')[:10]
    for estoque in estoques:
        print(f"{estoque.id}: {estoque.produto.nome} em {estoque.local} - Categoria: {estoque.local.categoria_armazenamento}")
    print(f"Total: {Estoque.objects.count()} itens no estoque")
    
    print("\n=== CATEGORIAS DE ARMAZENAMENTO ===")
    from django.db.models import Count
    categorias = Armazenamento.objects.values('categoria_armazenamento').annotate(count=Count('id'))
    for cat in categorias:
        print(f"{cat['categoria_armazenamento']}: {cat['count']} locais")

if __name__ == "__main__":
    verificar_dados()
