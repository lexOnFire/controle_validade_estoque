#!/usr/bin/env python
"""
Sistema de validação para garantir que nível 0 = meio
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/workspaces/controle_validade_estoque')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Armazenamento
from django.db.models.signals import pre_save
from django.dispatch import receiver

def validar_regra_nivel_0():
    """Validação completa da regra: nível 0 deve ser 'meio'"""
    print("✅ VALIDAÇÃO: Regra Nível 0 = Meio")
    print("=" * 40)
    
    # Verificar todos os endereços nível 0
    total_nivel_0 = Armazenamento.objects.filter(nivel=0).count()
    corretos_nivel_0 = Armazenamento.objects.filter(nivel=0, categoria_armazenamento='meio').count()
    incorretos_nivel_0 = Armazenamento.objects.filter(nivel=0, categoria_armazenamento='inteiro').count()
    
    print(f"📊 ESTATÍSTICAS:")
    print(f"   • Total de endereços nível 0: {total_nivel_0}")
    print(f"   • Corretos (meio): {corretos_nivel_0}")
    print(f"   • Incorretos (inteiro): {incorretos_nivel_0}")
    
    if incorretos_nivel_0 == 0:
        print(f"\n🎉 PERFEITO! Todos os endereços nível 0 estão corretos!")
    else:
        print(f"\n⚠️  ATENÇÃO! {incorretos_nivel_0} endereços nível 0 estão incorretos!")
    
    # Verificar outros níveis para comparação
    print(f"\n📋 DISTRIBUIÇÃO POR NÍVEL:")
    for nivel in range(0, 5):  # Verificar níveis 0-4
        total = Armazenamento.objects.filter(nivel=nivel).count()
        inteiros = Armazenamento.objects.filter(nivel=nivel, categoria_armazenamento='inteiro').count()
        meios = Armazenamento.objects.filter(nivel=nivel, categoria_armazenamento='meio').count()
        
        if total > 0:
            status = "✅" if (nivel == 0 and meios == total) or nivel > 0 else "⚠️"
            print(f"   • Nível {nivel}: {total} total ({inteiros} inteiros, {meios} meios) {status}")
    
    return incorretos_nivel_0 == 0

def criar_validacao_automatica():
    """Cria um sistema de validação automática para novos endereços"""
    print(f"\n🛡️  IMPLEMENTANDO VALIDAÇÃO AUTOMÁTICA...")
    
    # Criar um decorator/função de validação
    validacao_code = '''
# Adicionar ao models.py - Validação automática para nível 0
from django.core.exceptions import ValidationError

def clean(self):
    """Validação customizada para endereços"""
    if self.nivel == 0 and self.categoria_armazenamento != 'meio':
        raise ValidationError({
            'categoria_armazenamento': 'Endereços no nível 0 devem ser do tipo "meio" (saída).'
        })
    super().clean()

# Adicionar ao save() do modelo
def save(self, *args, **kwargs):
    # Auto-correção: se nível 0, forçar como 'meio'
    if self.nivel == 0:
        self.categoria_armazenamento = 'meio'
    super().save(*args, **kwargs)
    '''
    
    print("📝 Código de validação gerado (para implementar no models.py)")
    return validacao_code

def testar_logica_negocio():
    """Testa a lógica de negócio dos tipos de endereço"""
    print(f"\n🧠 LÓGICA DE NEGÓCIO:")
    print("=" * 30)
    
    print("📦 TIPOS DE ENDEREÇO:")
    print("   • 🔵 INTEIRO (Palete Fechado):")
    print("     - Para produtos em paletes completos")
    print("     - Geralmente em níveis superiores (1, 2, 3+)")
    print("     - Armazenamento de longo prazo")
    
    print("   • 🟡 MEIO (Saída):")
    print("     - Para produtos em picking/expedição")
    print("     - SEMPRE no nível 0 (térreo/saída)")
    print("     - Fácil acesso para retirada")
    
    print(f"\n📏 REGRA FUNDAMENTAL:")
    print("   ✅ Nível 0 = SEMPRE 'meio' (área de saída)")
    print("   ✅ Níveis 1+ = podem ser 'inteiro' ou 'meio'")
    
    # Verificar se a regra está sendo seguida
    violacoes = Armazenamento.objects.filter(
        nivel=0, 
        categoria_armazenamento='inteiro'
    ).count()
    
    print(f"\n🎯 STATUS DA REGRA:")
    if violacoes == 0:
        print("   ✅ REGRA RESPEITADA: Todos os níveis 0 são 'meio'")
    else:
        print(f"   ❌ VIOLAÇÕES: {violacoes} endereços nível 0 como 'inteiro'")
    
    return violacoes == 0

if __name__ == "__main__":
    try:
        print("🔍 SISTEMA DE VALIDAÇÃO - NÍVEL 0")
        print("=" * 50)
        
        # 1. Validar regra atual
        regra_ok = validar_regra_nivel_0()
        
        # 2. Testar lógica de negócio
        logica_ok = testar_logica_negocio()
        
        # 3. Gerar código de validação
        if regra_ok:
            codigo_validacao = criar_validacao_automatica()
        
        print(f"\n📊 RESUMO FINAL:")
        print(f"   • Regra nível 0 = meio: {'✅ OK' if regra_ok else '❌ Pendente'}")
        print(f"   • Lógica de negócio: {'✅ Consistente' if logica_ok else '❌ Inconsistente'}")
        print(f"   • Sistema validado: {'✅ Completo' if regra_ok and logica_ok else '⚠️ Necessita atenção'}")
        
        if regra_ok and logica_ok:
            print(f"\n🎉 SISTEMA PERFEITO!")
            print("   • Todos os endereços nível 0 estão como 'meio'")
            print("   • Regra de negócio está sendo respeitada")
            print("   • Armazém organizado corretamente")
        
    except Exception as e:
        print(f"\n❌ Erro durante a validação: {str(e)}")
        import traceback
        traceback.print_exc()
