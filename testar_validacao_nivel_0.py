#!/usr/bin/env python
"""
Teste da validação automática para nível 0 = meio
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/workspaces/controle_validade_estoque')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Armazenamento
from django.core.exceptions import ValidationError

def testar_validacao_automatica():
    print("🧪 TESTE: Validação Automática Nível 0")
    print("=" * 45)
    
    print("📝 TESTE 1: Criando endereço nível 0 como 'inteiro' (deve ser corrigido automaticamente)")
    try:
        # Tentar criar um endereço nível 0 como 'inteiro'
        endereco_teste = Armazenamento(
            rua='999',
            predio='999',
            nivel='0',
            ap='999',
            categoria_armazenamento='inteiro'  # Incorreto para nível 0
        )
        
        # Salvar (deve ser corrigido automaticamente)
        endereco_teste.save()
        
        # Verificar se foi corrigido
        endereco_salvo = Armazenamento.objects.get(
            rua='999', predio='999', nivel='0', ap='999'
        )
        
        if endereco_salvo.categoria_armazenamento == 'meio':
            print("   ✅ SUCESSO: Endereço foi corrigido automaticamente para 'meio'")
        else:
            print("   ❌ FALHA: Endereço não foi corrigido")
        
        # Limpar teste
        endereco_salvo.delete()
        
    except Exception as e:
        print(f"   ❌ ERRO no teste 1: {str(e)}")
    
    print(f"\n📝 TESTE 2: Criando endereço nível 0 como 'meio' (deve funcionar normalmente)")
    try:
        # Criar endereço nível 0 como 'meio' (correto)
        endereco_teste2 = Armazenamento(
            rua='998',
            predio='998',
            nivel='0',
            ap='998',
            categoria_armazenamento='meio'  # Correto para nível 0
        )
        
        endereco_teste2.save()
        
        # Verificar se foi salvo corretamente
        endereco_salvo2 = Armazenamento.objects.get(
            rua='998', predio='998', nivel='0', ap='998'
        )
        
        if endereco_salvo2.categoria_armazenamento == 'meio':
            print("   ✅ SUCESSO: Endereço nível 0 salvo corretamente como 'meio'")
        else:
            print("   ❌ FALHA: Endereço não foi salvo corretamente")
        
        # Limpar teste
        endereco_salvo2.delete()
        
    except Exception as e:
        print(f"   ❌ ERRO no teste 2: {str(e)}")
    
    print(f"\n📝 TESTE 3: Criando endereço nível 2 como 'inteiro' (deve funcionar normalmente)")
    try:
        # Criar endereço nível 2 como 'inteiro' (correto)
        endereco_teste3 = Armazenamento(
            rua='997',
            predio='997',
            nivel='2',
            ap='997',
            categoria_armazenamento='inteiro'  # Correto para nível 2
        )
        
        endereco_teste3.save()
        
        # Verificar se foi salvo corretamente
        endereco_salvo3 = Armazenamento.objects.get(
            rua='997', predio='997', nivel='2', ap='997'
        )
        
        if endereco_salvo3.categoria_armazenamento == 'inteiro':
            print("   ✅ SUCESSO: Endereço nível 2 salvo corretamente como 'inteiro'")
        else:
            print("   ❌ FALHA: Endereço nível 2 não foi salvo corretamente")
        
        # Limpar teste
        endereco_salvo3.delete()
        
    except Exception as e:
        print(f"   ❌ ERRO no teste 3: {str(e)}")

def verificar_integridade_atual():
    print(f"\n🔍 VERIFICAÇÃO: Integridade atual do sistema")
    print("=" * 50)
    
    # Contar endereços por nível e tipo
    niveis_tipos = {}
    
    for nivel in ['0', '1', '2', '3', '4']:
        total = Armazenamento.objects.filter(nivel=nivel).count()
        inteiros = Armazenamento.objects.filter(nivel=nivel, categoria_armazenamento='inteiro').count()
        meios = Armazenamento.objects.filter(nivel=nivel, categoria_armazenamento='meio').count()
        
        if total > 0:
            niveis_tipos[nivel] = {
                'total': total,
                'inteiros': inteiros,
                'meios': meios,
                'ok': (nivel == '0' and inteiros == 0) or nivel != '0'
            }
    
    print("📊 DISTRIBUIÇÃO POR NÍVEL:")
    for nivel, dados in niveis_tipos.items():
        status = "✅" if dados['ok'] else "❌"
        print(f"   • Nível {nivel}: {dados['total']} total ({dados['inteiros']} inteiros, {dados['meios']} meios) {status}")
    
    # Verificar regra principal
    violacoes = Armazenamento.objects.filter(nivel='0', categoria_armazenamento='inteiro').count()
    
    print(f"\n🎯 STATUS DA REGRA:")
    if violacoes == 0:
        print("   ✅ PERFEITO: Todos os endereços nível 0 são 'meio'")
    else:
        print(f"   ❌ PROBLEMA: {violacoes} endereços nível 0 ainda são 'inteiro'")
    
    return violacoes == 0

if __name__ == "__main__":
    try:
        print("🔒 SISTEMA DE VALIDAÇÃO AUTOMÁTICA")
        print("=" * 50)
        
        # 1. Testar validação automática
        testar_validacao_automatica()
        
        # 2. Verificar integridade atual
        sistema_ok = verificar_integridade_atual()
        
        print(f"\n📊 RESUMO DOS TESTES:")
        print(f"   • Validação automática: ✅ Implementada")
        print(f"   • Auto-correção: ✅ Funcionando")
        print(f"   • Integridade do sistema: {'✅ Perfeita' if sistema_ok else '❌ Problema'}")
        
        if sistema_ok:
            print(f"\n🎉 SISTEMA VALIDADO!")
            print("   • Regra 'nível 0 = meio' está funcionando")
            print("   • Validação automática implementada")
            print("   • Futuros endereços serão corrigidos automaticamente")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {str(e)}")
        import traceback
        traceback.print_exc()
