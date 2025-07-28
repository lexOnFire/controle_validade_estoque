import csv
import re
from datetime import datetime

print("🔍 INVESTIGANDO ORIGEM DOS DADOS COM 2025...")
print("=" * 50)

# Ler o arquivo original para verificar as datas
with open('FIFO(ABASTECIMENTO 1).csv', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Procurar por padrões de data com 2025
pattern_2025 = r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]2025\b'
matches_2025 = re.findall(pattern_2025, content)

print(f"📅 Encontradas {len(matches_2025)} datas com 2025 no arquivo original:")
for i, match in enumerate(matches_2025[:10]):  # Mostrar apenas 10 exemplos
    print(f"   {i+1}. {match}")

if len(matches_2025) > 10:
    print(f"   ... e mais {len(matches_2025) - 10} datas")

print()

# Procurar por padrões de data com 2026
pattern_2026 = r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]2026\b'
matches_2026 = re.findall(pattern_2026, content)

print(f"📅 Encontradas {len(matches_2026)} datas com 2026 no arquivo original:")
for i, match in enumerate(matches_2026[:10]):  # Mostrar apenas 10 exemplos
    print(f"   {i+1}. {match}")

if len(matches_2026) > 10:
    print(f"   ... e mais {len(matches_2026) - 10} datas")

print()
print("📊 RESUMO:")
print(f"   2025: {len(matches_2025)} ocorrências")
print(f"   2026: {len(matches_2026)} ocorrências")

# Verificar se há outros anos
pattern_outros = r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]20(2[7-9]|[3-9]\d)\b'
matches_outros = re.findall(pattern_outros, content)
if matches_outros:
    print(f"   Outros anos: {len(matches_outros)} ocorrências")
    for i, match in enumerate(matches_outros[:5]):
        print(f"      {i+1}. {match}")

print()
print("🔧 CONCLUSÃO:")
if len(matches_2025) > 0:
    print("   ❌ O arquivo original CONTÉM datas de 2025")
    print("   ➡️  Isso NÃO é um erro de conversão, mas dados reais do arquivo")
else:
    print("   ✅ Não há datas de 2025 no arquivo original")
    print("   ➡️  O problema pode estar na conversão")
