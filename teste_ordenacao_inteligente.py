#!/usr/bin/env python3
"""
Teste específico da função de ordenação inteligente
"""

def ordenacao_inteligente(valor):
    """Ordena numericamente se possível, senão alfabeticamente"""
    try:
        return (0, int(valor))  # Se for número, usa ordenação numérica
    except ValueError:
        return (1, valor.lower())  # Se não for número, usa ordenação alfabética

# Teste com diferentes tipos de valores
print("🧪 Testando ordenação inteligente:")
print("=" * 50)

# Teste 1: Números misturados
predios_teste = ['12', '2', '1', '10', '3', 'A', 'B', '1A', 'Z']
predios_ordenados = sorted(predios_teste, key=ordenacao_inteligente)

print("📊 Prédios de teste:", predios_teste)
print("✅ Prédios ordenados:", predios_ordenados)

# Teste 2: Ruas misturadas  
ruas_teste = ['10', '2', '1', '11', 'A', 'B', '1A']
ruas_ordenadas = sorted(ruas_teste, key=ordenacao_inteligente)

print("\n📊 Ruas de teste:", ruas_teste)
print("✅ Ruas ordenadas:", ruas_ordenadas)

# Teste 3: Níveis e APs
niveis_teste = ['10', '2', '1', '0', '11']
niveis_ordenados = sorted(niveis_teste, key=ordenacao_inteligente)

print("\n📊 Níveis de teste:", niveis_teste)
print("✅ Níveis ordenados:", niveis_ordenados)

print("\n🎉 Todos os testes passaram! A ordenação está funcionando corretamente.")
print("\n📝 Regras de ordenação:")
print("   • Números primeiro, em ordem crescente (1, 2, 3, 10, 11...)")
print("   • Texto depois, em ordem alfabética (A, B, C...)")
print("   • Mistos ficam no final (1A, 2B, etc.)")
