#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/workspaces/controle_validade_estoque')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Produto, Armazenamento, Estoque

def demonstrar_painel_tabela():
    print("📊 PAINEL MODIFICADO PARA FORMATO DE TABELA!")
    print("=" * 70)
    
    print("\n🔄 MUDANÇAS REALIZADAS:")
    print("✅ Removido formato de cards expandíveis")
    print("✅ Implementado formato de tabela com colunas")
    print("✅ Organização por prédio/rua mantida")
    print("✅ Todas as funcionalidades dos botões preservadas")
    
    print("\n📋 COLUNAS DA TABELA:")
    print("1. 🛣️  Rua")
    print("2. 🏢 Prédio") 
    print("3. 📍 Nível")
    print("4. 🚪 AP")
    print("5. 🔢 Código")
    print("6. 📦 Nome do Produto")
    print("7. 📅 Val 1 (Primeira validade)")
    print("8. 📅 Val 2 (Segunda validade)")
    print("9. 📅 Val 3 (Terceira validade)")
    print("10. 🕒 Data Alteração")
    
    print("\n🎨 RECURSOS VISUAIS:")
    print("✅ Status de validade colorido:")
    print("   - 🔴 Vermelho: Vencido")
    print("   - 🟠 Laranja: Vence em breve")
    print("   - 🟡 Amarelo: Próximo ao vencimento")
    print("   - 🟢 Verde: Válido")
    print("   - ⚪ Cinza: Sem lote")
    
    print("✅ Tabela responsiva com scroll horizontal")
    print("✅ Alternância de cores nas linhas")
    print("✅ Hover effects nas linhas")
    print("✅ Cabeçalhos fixos e destacados")
    
    print("\n📊 DADOS ATUAIS:")
    total_produtos = Produto.objects.count()
    total_enderecos = Armazenamento.objects.count()
    total_estoque = Estoque.objects.count()
    
    print(f"📦 Produtos cadastrados: {total_produtos}")
    print(f"🏢 Endereços disponíveis: {total_enderecos}")
    print(f"📋 Produtos em estoque: {total_estoque}")
    
    # Contar produtos por status de validade
    from datetime import date, timedelta
    hoje = date.today()
    
    estoques = Estoque.objects.select_related('produto')
    vencidos = 0
    vence_breve = 0
    proximos = 0
    validos = 0
    sem_lote = 0
    
    for estoque in estoques:
        produto = estoque.produto
        lotes = produto.lotes.all().order_by('validade')
        
        if lotes.exists():
            primeira_validade = lotes.first().validade
            dias = (primeira_validade - hoje).days
            
            if dias < 0:
                vencidos += 1
            elif dias <= 7:
                vence_breve += 1
            elif dias <= 30:
                proximos += 1
            else:
                validos += 1
        else:
            sem_lote += 1
    
    print(f"\n📊 STATUS DE VALIDADE:")
    print(f"🔴 Vencidos: {vencidos}")
    print(f"🟠 Vence em breve (≤7 dias): {vence_breve}")
    print(f"🟡 Próximos (≤30 dias): {proximos}")
    print(f"🟢 Válidos: {validos}")
    print(f"⚪ Sem lote: {sem_lote}")
    
    print("\n🔗 ACESSO:")
    print("http://localhost:8000/ - Página principal com novo formato")
    
    print("\n" + "=" * 70)
    print("✅ PAINEL EM FORMATO DE TABELA PRONTO!")

if __name__ == '__main__':
    demonstrar_painel_tabela()
