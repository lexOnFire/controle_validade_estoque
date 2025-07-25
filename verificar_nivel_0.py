#!/usr/bin/env python
"""
Script para verificar e corrigir endereços no nível 0
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/workspaces/controle_validade_estoque')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Armazenamento, Estoque

def verificar_nivel_0():
    print("🔍 VERIFICAÇÃO: Endereços Nível 0")
    print("=" * 50)
    
    # Buscar todos os endereços no nível 0
    enderecos_nivel_0 = Armazenamento.objects.filter(nivel=0)
    
    print(f"📊 Total de endereços no nível 0: {enderecos_nivel_0.count()}")
    
    # Separar por tipo
    nivel_0_inteiros = enderecos_nivel_0.filter(categoria_armazenamento='inteiro')
    nivel_0_meios = enderecos_nivel_0.filter(categoria_armazenamento='meio')
    
    print(f"\n📋 SITUAÇÃO ATUAL:")
    print(f"   • Nível 0 marcados como 'inteiro': {nivel_0_inteiros.count()}")
    print(f"   • Nível 0 marcados como 'meio': {nivel_0_meios.count()}")
    
    # Mostrar alguns endereços incorretos
    if nivel_0_inteiros.exists():
        print(f"\n⚠️  ENDEREÇOS INCORRETOS (nível 0 como 'inteiro'):")
        for endereco in nivel_0_inteiros[:10]:  # Mostrar até 10
            ocupacao = Estoque.objects.filter(local=endereco).count()
            status = f" - {ocupacao} produto(s)" if ocupacao > 0 else " - vazio"
            print(f"   • {endereco}{status}")
        
        if nivel_0_inteiros.count() > 10:
            print(f"   ... e mais {nivel_0_inteiros.count() - 10} endereços")
    
    # Mostrar endereços corretos
    if nivel_0_meios.exists():
        print(f"\n✅ ENDEREÇOS CORRETOS (nível 0 como 'meio'):")
        for endereco in nivel_0_meios[:5]:  # Mostrar até 5
            ocupacao = Estoque.objects.filter(local=endereco).count()
            status = f" - {ocupacao} produto(s)" if ocupacao > 0 else " - vazio"
            print(f"   • {endereco}{status}")
        
        if nivel_0_meios.count() > 5:
            print(f"   ... e mais {nivel_0_meios.count() - 5} endereços")
    
    return nivel_0_inteiros

def corrigir_nivel_0():
    print(f"\n🔧 CORREÇÃO: Alterando endereços nível 0 para 'meio'")
    print("=" * 55)
    
    # Buscar endereços nível 0 marcados incorretamente
    enderecos_incorretos = Armazenamento.objects.filter(
        nivel=0,
        categoria_armazenamento='inteiro'
    )
    
    if not enderecos_incorretos.exists():
        print("✅ Todos os endereços nível 0 já estão corretos!")
        return
    
    print(f"🔄 Corrigindo {enderecos_incorretos.count()} endereço(s)...")
    
    # Separar por ocupação
    enderecos_vazios = []
    enderecos_ocupados = []
    
    for endereco in enderecos_incorretos:
        ocupacao = Estoque.objects.filter(local=endereco).count()
        if ocupacao > 0:
            enderecos_ocupados.append((endereco, ocupacao))
        else:
            enderecos_vazios.append(endereco)
    
    print(f"\n📊 ANÁLISE:")
    print(f"   • Endereços vazios para corrigir: {len(enderecos_vazios)}")
    print(f"   • Endereços ocupados para corrigir: {len(enderecos_ocupados)}")
    
    # Corrigir endereços vazios
    if enderecos_vazios:
        print(f"\n✅ CORRIGINDO ENDEREÇOS VAZIOS:")
        for endereco in enderecos_vazios:
            endereco.categoria_armazenamento = 'meio'
            endereco.save()
            print(f"   • {endereco} → alterado para 'meio'")
        print(f"   ✓ {len(enderecos_vazios)} endereço(s) vazio(s) corrigidos!")
    
    # Corrigir endereços ocupados (com cuidado)
    if enderecos_ocupados:
        print(f"\n⚠️  CORRIGINDO ENDEREÇOS OCUPADOS:")
        for endereco, ocupacao in enderecos_ocupados:
            endereco.categoria_armazenamento = 'meio'
            endereco.save()
            print(f"   • {endereco} → alterado para 'meio' (tinha {ocupacao} produto(s))")
        print(f"   ✓ {len(enderecos_ocupados)} endereço(s) ocupado(s) corrigidos!")
    
    print(f"\n🎉 CORREÇÃO CONCLUÍDA!")
    
    # Verificar resultado final
    nivel_0_ainda_incorretos = Armazenamento.objects.filter(
        nivel=0,
        categoria_armazenamento='inteiro'
    ).count()
    
    nivel_0_corretos = Armazenamento.objects.filter(
        nivel=0,
        categoria_armazenamento='meio'
    ).count()
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   • Nível 0 como 'meio': {nivel_0_corretos} ✅")
    print(f"   • Nível 0 como 'inteiro': {nivel_0_ainda_incorretos} {'✅' if nivel_0_ainda_incorretos == 0 else '⚠️'}")

if __name__ == "__main__":
    try:
        # Verificar situação atual
        enderecos_incorretos = verificar_nivel_0()
        
        if enderecos_incorretos.exists():
            print(f"\n" + "="*60)
            resposta = input("🔧 Deseja corrigir os endereços incorretos? (s/n): ").lower().strip()
            
            if resposta in ['s', 'sim', 'y', 'yes']:
                corrigir_nivel_0()
            else:
                print("❌ Correção cancelada pelo usuário.")
        else:
            print(f"\n🎉 PERFEITO! Todos os endereços nível 0 já estão corretos!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a verificação: {str(e)}")
        import traceback
        traceback.print_exc()
