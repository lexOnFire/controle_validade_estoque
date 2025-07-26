#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/workspaces/controle_validade_estoque')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Produto
from produtos.forms import ProdutoForm

def testar_cadastro():
    print("=== TESTE DE CADASTRO DE PRODUTO ===")
    
    # Testar com dados válidos
    dados_teste = {
        'codigo': '117',
        'nome': 'Produto Teste 117',
        'peso': '1kg',
        'categoria': 'Teste',
        'fornecedor': 'Fornecedor Teste'
    }
    
    print(f"\n1. Testando cadastro com dados: {dados_teste}")
    
    form = ProdutoForm(dados_teste)
    print(f"Form is valid: {form.is_valid()}")
    
    if not form.is_valid():
        print(f"Erros do formulário: {form.errors}")
        print(f"Erros por campo:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
    else:
        print("Formulário válido! Salvando...")
        try:
            produto = form.save()
            print(f"Produto criado com sucesso! ID: {produto.id}, Nome: {produto.nome}")
        except Exception as e:
            print(f"Erro ao salvar: {e}")
    
    # Verificar se já existe produto com código 117
    print(f"\n2. Verificando se existe produto com código '117':")
    produtos_existentes = Produto.objects.filter(codigo='117')
    print(f"Produtos encontrados: {produtos_existentes.count()}")
    for p in produtos_existentes:
        print(f"  - ID: {p.id}, Nome: {p.nome}, Código: {p.codigo}")
    
    print(f"\n3. Total de produtos cadastrados: {Produto.objects.count()}")

if __name__ == '__main__':
    testar_cadastro()
