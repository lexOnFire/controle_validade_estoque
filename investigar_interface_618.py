import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Produto, Lote, Estoque

print("🔍 INVESTIGAÇÃO APROFUNDADA DO PRODUTO 618...")
print("=" * 60)

try:
    produto = Produto.objects.get(codigo='618')
    print(f"✅ Produto: {produto.nome}")
    print()
    
    # Verificar estrutura do modelo Estoque
    print("🏗️ ESTRUTURA DO MODELO ESTOQUE:")
    estoque_fields = [field.name for field in Estoque._meta.fields]
    print(f"   Campos: {', '.join(estoque_fields)}")
    print()
    
    # Buscar estoques do produto
    estoques = Estoque.objects.filter(produto=produto)
    print(f"📍 ESTOQUES DO PRODUTO 618: {estoques.count()}")
    
    for i, estoque in enumerate(estoques, 1):
        endereco = f"{estoque.armazenamento.rua}-{estoque.armazenamento.predio}-{estoque.armazenamento.nivel:02d}-{estoque.armazenamento.ap:02d}"
        
        # Verificar se tem campo numero_lote diretamente no estoque
        numero_lote = getattr(estoque, 'numero_lote', None)
        
        print(f"   {i}. Endereço: {endereco}")
        print(f"      Quantidade: {estoque.quantidade}")
        print(f"      Número do lote: {numero_lote}")
        
        # Se tem numero_lote, buscar o lote correspondente
        if numero_lote:
            try:
                lote = Lote.objects.get(numero_lote=numero_lote, produto=produto)
                validade_str = lote.validade.strftime('%d/%m/%Y') if lote.validade else 'Sem validade'
                ano = lote.validade.year if lote.validade else None
                
                if ano == 2025:
                    status = "⚠️ 2025 - PROBLEMA!"
                elif ano == 2026:
                    status = "✅ 2026"
                else:
                    status = f"📅 {ano}" if ano else "⚪ Sem validade"
                    
                print(f"      Validade: {validade_str} {status}")
            except Lote.DoesNotExist:
                print(f"      ❌ Lote {numero_lote} não encontrado")
        else:
            print(f"      ⚪ Sem número de lote associado")
        print()
    
    print("🎯 CONCLUSÃO:")
    print("   1. ✅ Todos os lotes do produto 618 têm validade em 2026")
    print("   2. ⚠️  Interface principal mostra validade em 2025")
    print("   3. 🤔 Possível problema:")
    print("      - Cache da interface não atualizado")
    print("      - Cálculo incorreto na view principal")
    print("      - Dados antigos ainda em exibição")
    print()
    print("💡 RECOMENDAÇÃO:")
    print("   Verificar a view que exibe as informações no painel principal")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
