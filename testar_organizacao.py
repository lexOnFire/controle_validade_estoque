#!/usr/bin/env python3
"""
Script para testar a organização de endereços por rua e prédio
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Armazenamento

def testar_organizacao_enderecos():
    """Testa a organização dos endereços"""
    
    print("📍 TESTANDO ORGANIZAÇÃO DE ENDEREÇOS...")
    
    # Função de ordenação inteligente
    def ordenacao_inteligente(valor):
        try:
            return (0, int(valor))
        except ValueError:
            return (1, valor.lower())
    
    # Agrupar endereços
    enderecos_agrupados = {}
    for endereco in Armazenamento.objects.all():
        rua = endereco.rua
        predio = endereco.predio
        
        if rua not in enderecos_agrupados:
            enderecos_agrupados[rua] = {}
        
        if predio not in enderecos_agrupados[rua]:
            enderecos_agrupados[rua][predio] = []
        
        enderecos_agrupados[rua][predio].append(endereco)
    
    # Mostrar estrutura organizada
    print("\n=== ESTRUTURA ORGANIZADA ===")
    
    ruas_ordenadas = sorted(enderecos_agrupados.keys(), key=ordenacao_inteligente)
    
    for rua in ruas_ordenadas[:3]:  # Mostrar apenas 3 primeiras ruas
        predios_count = len(enderecos_agrupados[rua])
        total_enderecos = sum(len(enderecos) for enderecos in enderecos_agrupados[rua].values())
        
        print(f"\n🛣️  RUA: {rua} ({predios_count} prédios, {total_enderecos} endereços)")
        
        predios_ordenados = sorted(enderecos_agrupados[rua].keys(), key=ordenacao_inteligente)
        
        for predio in predios_ordenados[:2]:  # Mostrar apenas 2 primeiros prédios
            enderecos = enderecos_agrupados[rua][predio]
            enderecos_ordenados = sorted(
                enderecos,
                key=lambda x: (ordenacao_inteligente(str(x.nivel)), ordenacao_inteligente(str(x.ap)))
            )
            
            print(f"   🏢 PRÉDIO: {predio} ({len(enderecos)} endereços)")
            
            for endereco in enderecos_ordenados[:3]:  # Mostrar apenas 3 primeiros
                tipo = "Inteiro" if endereco.categoria_armazenamento == 'inteiro' else "Meio"
                print(f"      • Nível {endereco.nivel}, AP {endereco.ap} ({tipo})")
            
            if len(enderecos_ordenados) > 3:
                print(f"      ... e mais {len(enderecos_ordenados) - 3} endereços")
    
    print(f"\n📊 ESTATÍSTICAS GERAIS:")
    print(f"Total de ruas: {len(ruas_ordenadas)}")
    total_predios = sum(len(predios) for predios in enderecos_agrupados.values())
    print(f"Total de prédios: {total_predios}")
    print(f"Total de endereços: {Armazenamento.objects.count()}")

if __name__ == "__main__":
    testar_organizacao_enderecos()
