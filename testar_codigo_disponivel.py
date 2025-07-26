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

def testar_codigo_disponivel():
    print("=== TESTANDO CÓDIGOS DISPONÍVEIS ===")
    
    # Encontrar um código disponível
    codigo_teste = 9999
    while Produto.objects.filter(codigo=str(codigo_teste)).exists():
        codigo_teste += 1
    
    print(f"Código disponível encontrado: {codigo_teste}")
    
    # Testar cadastro com esse código
    dados_teste = {
        'codigo': str(codigo_teste),
        'nome': f'Produto Teste {codigo_teste}',
        'peso': '1kg',
        'categoria': 'Teste',
        'fornecedor': 'Fornecedor Teste'
    }
    
    print(f"Testando cadastro com dados: {dados_teste}")
    
    form = ProdutoForm(dados_teste)
    print(f"Form is valid: {form.is_valid()}")
    
    if form.is_valid():
        produto = form.save()
        print(f"✅ Produto criado com sucesso! ID: {produto.id}, Nome: {produto.nome}, Código: {produto.codigo}")
        return codigo_teste
    else:
        print(f"❌ Erros: {form.errors}")
        return None

if __name__ == '__main__':
    codigo_disponivel = testar_codigo_disponivel()
    if codigo_disponivel:
        print(f"\n🔗 Teste manual: http://localhost:8000/produtos/cadastrar_produto/?codigo={codigo_disponivel}&endereco_retorno=175")
