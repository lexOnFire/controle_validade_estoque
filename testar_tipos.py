#!/usr/bin/env python3
"""
Script para testar as funcionalidades de alteração de tipo
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Armazenamento, Estoque

def testar_alteracao_tipo():
    """Testa a funcionalidade de alteração de tipo"""
    
    print("🔧 TESTANDO ALTERAÇÃO DE TIPO...")
    
    # Mostrar alguns endereços com seus tipos atuais
    print("\n=== ENDEREÇOS POR TIPO ===")
    
    inteiros = Armazenamento.objects.filter(categoria_armazenamento='inteiro')[:5]
    meios = Armazenamento.objects.filter(categoria_armazenamento='meio')[:5]
    
    print("\n🏢 TIPOS 'INTEIRO' (Palete Fechado):")
    for endereco in inteiros:
        ocupacao = Estoque.objects.filter(local=endereco).count()
        print(f"  ID {endereco.id}: {endereco} - Produtos: {ocupacao}")
    
    print("\n📦 TIPOS 'MEIO' (Saída):")
    for endereco in meios:
        ocupacao = Estoque.objects.filter(local=endereco).count()
        print(f"  ID {endereco.id}: {endereco} - Produtos: {ocupacao}")
    
    # Estatísticas
    total_inteiros = Armazenamento.objects.filter(categoria_armazenamento='inteiro').count()
    total_meios = Armazenamento.objects.filter(categoria_armazenamento='meio').count()
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"Total Inteiros: {total_inteiros}")
    print(f"Total Meios: {total_meios}")
    print(f"Total Geral: {total_inteiros + total_meios}")
    
    # Endereços vazios que podem ser alterados
    enderecos_vazios = []
    for endereco in Armazenamento.objects.all()[:10]:
        ocupacao = Estoque.objects.filter(local=endereco).count()
        if ocupacao == 0:
            enderecos_vazios.append(endereco)
    
    print(f"\n🔄 ENDEREÇOS VAZIOS (Podem ser alterados): {len(enderecos_vazios)}")
    for endereco in enderecos_vazios[:3]:
        print(f"  ID {endereco.id}: {endereco} - Tipo: {endereco.categoria_armazenamento}")

if __name__ == "__main__":
    testar_alteracao_tipo()
