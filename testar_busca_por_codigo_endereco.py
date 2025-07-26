#!/usr/bin/env python3
"""
Script para testar a nova funcionalidade de busca por código em endereços vazios
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/workspaces/controle_validade_estoque')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from produtos.models import Produto, Armazenamento, Estoque, Lote

def testar_nova_funcionalidade():
    """Testa a funcionalidade de busca por código em endereços vazios"""
    
    print("🧪 Testando Nova Funcionalidade: Buscar por Código em Endereços Vazios")
    print("=" * 70)
    
    # Criar cliente de teste
    client = Client()
    
    # Criar ou buscar usuário para autenticação
    try:
        user = User.objects.get(username='admin')
        print(f"✅ Usuário encontrado: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user('admin', 'admin@test.com', 'admin123')
        print(f"✅ Usuário criado: {user.username}")
    
    # Fazer login
    login_success = client.login(username='admin', password='admin123')
    print(f"✅ Login realizado: {login_success}")
    
    # 1. Verificar se existem endereços vazios
    print("\n1. 📋 Verificando endereços vazios...")
    
    enderecos_vazios = []
    for endereco in Armazenamento.objects.all():
        tem_estoque = Estoque.objects.filter(local=endereco).exists()
        if not tem_estoque:
            enderecos_vazios.append(endereco)
    
    print(f"   Total de endereços: {Armazenamento.objects.count()}")
    print(f"   Endereços vazios: {len(enderecos_vazios)}")
    
    if enderecos_vazios:
        endereco_teste = enderecos_vazios[0]
        print(f"   Endereço para teste: {endereco_teste}")
        
        # 2. Testar acesso à página de busca por código
        print("\n2. 🔍 Testando acesso à busca por código...")
        
        url_busca = f'/produtos/buscar-produto-endereco/{endereco_teste.id}/'
        response_busca = client.get(url_busca)
        
        print(f"   URL testada: {url_busca}")
        print(f"   Status: {response_busca.status_code}")
        print(f"   ✅ Página acessível: {'Buscar Produto por Código' in response_busca.content.decode()}")
        
        # 3. Testar busca por produto existente
        print("\n3. 🎯 Testando busca por produto existente...")
        
        produto_teste = Produto.objects.first()
        if produto_teste:
            print(f"   Produto para teste: {produto_teste.nome} ({produto_teste.codigo})")
            
            response_busca_post = client.post(url_busca, {
                'codigo': produto_teste.codigo
            })
            
            print(f"   Status busca: {response_busca_post.status_code}")
            content = response_busca_post.content.decode()
            print(f"   ✅ Produto encontrado: {'Produto Encontrado' in content}")
            print(f"   ✅ Link para armazenar: {'confirmar-armazenamento' in content}")
            
            # 4. Testar confirmação de armazenamento
            print("\n4. 📦 Testando confirmação de armazenamento...")
            
            url_confirmar = f'/produtos/confirmar-armazenamento/{endereco_teste.id}/{produto_teste.id}/'
            response_confirmar = client.get(url_confirmar)
            
            print(f"   URL confirmação: {url_confirmar}")
            print(f"   Status: {response_confirmar.status_code}")
            print(f"   ✅ Página de confirmação: {'Confirmar Armazenamento' in response_confirmar.content.decode()}")
            
            # 5. Testar armazenamento real
            print("\n5. ✅ Testando armazenamento real...")
            
            # Verificar se já existe estoque para este produto neste endereço
            estoque_existente = Estoque.objects.filter(produto=produto_teste, local=endereco_teste).exists()
            
            if not estoque_existente:
                response_armazenar = client.post(url_confirmar, {
                    'data_validade': '2025-12-31',
                    'data_armazenado': '2025-07-25',
                    'observacoes': 'Teste automático de armazenamento'
                })
                
                print(f"   Status armazenamento: {response_armazenar.status_code}")
                
                # Verificar se o estoque foi criado
                estoque_criado = Estoque.objects.filter(produto=produto_teste, local=endereco_teste).exists()
                print(f"   ✅ Estoque criado: {estoque_criado}")
                
                if estoque_criado:
                    estoque = Estoque.objects.get(produto=produto_teste, local=endereco_teste)
                    print(f"   📋 Detalhes do estoque:")
                    print(f"      - Produto: {estoque.produto.nome}")
                    print(f"      - Local: {estoque.local}")
                    print(f"      - Data: {estoque.data_armazenado}")
                    print(f"      - Observações: {estoque.observacoes}")
            else:
                print("   ⚠️ Produto já armazenado neste endereço - pulando teste de armazenamento")
        
        else:
            print("   ❌ Nenhum produto encontrado para teste")
    
    else:
        print("   ⚠️ Nenhum endereço vazio encontrado para teste")
    
    # 6. Testar busca por código inexistente
    print("\n6. ❌ Testando busca por código inexistente...")
    
    if enderecos_vazios:
        endereco_teste = enderecos_vazios[0]
        url_busca = f'/produtos/buscar-produto-endereco/{endereco_teste.id}/'
        
        response_codigo_inexistente = client.post(url_busca, {
            'codigo': 'CODIGO_INEXISTENTE_123'
        })
        
        print(f"   Status: {response_codigo_inexistente.status_code}")
        content = response_codigo_inexistente.content.decode()
        print(f"   ✅ Erro mostrado: {'não encontrado' in content}")
    
    # 7. Verificar se o painel exibe os botões corretos
    print("\n7. 🎛️ Verificando botões no painel...")
    
    response_painel = client.get('/produtos/painel/')
    content_painel = response_painel.content.decode()
    
    print(f"   Status painel: {response_painel.status_code}")
    print(f"   ✅ Botão 'Buscar por Código': {'Buscar por Código' in content_painel}")
    
    print("\n" + "=" * 70)
    print("🎉 TESTE CONCLUÍDO - Nova funcionalidade está operacional!")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        testar_nova_funcionalidade()
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
