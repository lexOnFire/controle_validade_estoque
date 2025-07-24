#!/usr/bin/env python3
"""
Script para testar a ordenação do painel
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Armazenamento, Estoque

def testar_ordenacao():
    """Testa a ordenação dos dados do painel"""
    
    print("🔍 Testando ordenação do painel...")
    
    # Função de ordenação inteligente (mesma da view)
    def ordenacao_inteligente(valor):
        try:
            return (0, int(valor))
        except ValueError:
            return (1, valor.lower())
    
    # Buscar dados como na view
    dados = Estoque.objects.select_related('produto', 'local').order_by('local__predio', 'local__rua', 'local__nivel', 'local__ap')
    
    if not dados.exists():
        print("❌ Nenhum dado encontrado no estoque!")
        return
    
    # Agrupar por prédio e rua
    predios = {}
    for item in dados:
        predio_nome = item.local.predio
        rua_nome = item.local.rua
        
        if predio_nome not in predios:
            predios[predio_nome] = {}
        
        if rua_nome not in predios[predio_nome]:
            predios[predio_nome][rua_nome] = []
        
        predios[predio_nome][rua_nome].append(item)
    
    print(f"\n📊 Estrutura encontrada:")
    print(f"Total de prédios: {len(predios)}")
    
    # Test ordenação
    predios_ordenados_keys = sorted(predios.keys(), key=ordenacao_inteligente)
    
    for predio_nome in predios_ordenados_keys:
        ruas_count = len(predios[predio_nome])
        total_itens = sum(len(itens) for itens in predios[predio_nome].values())
        print(f"\n🏢 Prédio: {predio_nome} ({ruas_count} ruas, {total_itens} itens)")
        
        ruas_ordenadas_keys = sorted(predios[predio_nome].keys(), key=ordenacao_inteligente)
        
        for rua_nome in ruas_ordenadas_keys:
            itens = predios[predio_nome][rua_nome]
            print(f"  🛣️  Rua: {rua_nome} ({len(itens)} itens)")
            
            # Ordenar itens por nível e AP
            itens_ordenados = sorted(
                itens, 
                key=lambda x: (ordenacao_inteligente(str(x.local.nivel)), ordenacao_inteligente(str(x.local.ap)))
            )
            
            for item in itens_ordenados[:3]:  # Mostrar apenas os primeiros 3
                print(f"    • Nível {item.local.nivel}, AP {item.local.ap}: {item.produto.nome}")
            
            if len(itens_ordenados) > 3:
                print(f"    ... e mais {len(itens_ordenados) - 3} itens")
    
    print(f"\n✅ Ordenação testada com sucesso!")

if __name__ == "__main__":
    testar_ordenacao()
