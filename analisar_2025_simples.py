import csv

print("Analisando datas de 2025...")

count_2025 = 0
exemplos_2025 = []

with open('FIFO_CONSOLIDADO_FORMATADO.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        validade = row['validade'].strip()
        if '2025' in validade:
            count_2025 += 1
            if len(exemplos_2025) < 10:
                exemplos_2025.append(f"Código {row['codigo']}: {row['nome'][:40]}... -> {validade}")

print(f"Total com 2025: {count_2025}")
print("Exemplos:")
for ex in exemplos_2025:
    print(f"  {ex}")

# Criar arquivo filtrado
with open('produtos_2025.csv', 'w', newline='', encoding='utf-8') as out_file:
    writer = csv.writer(out_file)
    writer.writerow(['codigo', 'nome', 'validade'])
    
    with open('FIFO_CONSOLIDADO_FORMATADO.csv', 'r', encoding='utf-8') as in_file:
        reader = csv.DictReader(in_file)
        for row in reader:
            if '2025' in row['validade']:
                writer.writerow([row['codigo'], row['nome'], row['validade']])

print("Arquivo produtos_2025.csv criado!")
