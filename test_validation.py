#!/usr/bin/env python3
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import validar_nome_produto
from django.core.exceptions import ValidationError

# Testa alguns produtos problemáticos
nomes_teste = ['123', '456', ';', 'Arroz 5kg', 'Feijão Preto', '1', 'AB', 'Produto-Test_123', 'Maçã (Gala)']

print("🧪 Testando validação de nomes de produtos:")
print("=" * 50)

for nome in nomes_teste:
    try:
        validar_nome_produto(nome)
        print(f'✅ "{nome}" - VÁLIDO')
    except ValidationError as e:
        print(f'❌ "{nome}" - INVÁLIDO: {e}')

print("\n🔍 Testando produtos problemáticos no banco:")
print("=" * 50)

from produtos.models import Produto

# Testa alguns produtos do banco
produtos_numericos = Produto.objects.filter(nome__regex=r'^\d+$')[:5]
for produto in produtos_numericos:
    try:
        validar_nome_produto(produto.nome)
        print(f'✅ Produto ID {produto.id}: "{produto.nome}" - VÁLIDO')
    except ValidationError as e:
        print(f'❌ Produto ID {produto.id}: "{produto.nome}" - INVÁLIDO: {e}')
