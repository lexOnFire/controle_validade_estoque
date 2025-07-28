import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Produto, Lote, Estoque

print("🔍 INVESTIGANDO PRODUTO 618...")
print("=" * 50)

# Buscar produto 618
try:
    produto = Produto.objects.get(codigo='618')
    print(f"✅ Produto encontrado: {produto.nome}")
    print(f"   Código: {produto.codigo}")
    print(f"   Categoria: {produto.categoria}")
    print()
    
    # Buscar lotes do produto 618
    lotes = Lote.objects.filter(produto=produto).order_by('validade')
    print(f"📦 LOTES ENCONTRADOS: {lotes.count()}")
    
    for i, lote in enumerate(lotes, 1):
        validade_str = lote.validade.strftime('%d/%m/%Y') if lote.validade else 'Sem validade'
        print(f"   {i}. Lote {lote.numero_lote}: {validade_str}")
        
        # Verificar ano da validade
        if lote.validade:
            ano = lote.validade.year
            if ano == 2025:
                print(f"      ⚠️  VALIDADE EM 2025!")
            elif ano == 2026:
                print(f"      ✅ Validade em 2026")
            else:
                print(f"      📅 Validade em {ano}")
    
    print()
    
    # Buscar estoques do produto 618
    estoques = Estoque.objects.filter(produto=produto)
    print(f"📍 ESTOQUES ENCONTRADOS: {estoques.count()}")
    
    for i, estoque in enumerate(estoques, 1):
        if estoque.lote and estoque.lote.validade:
            validade_str = estoque.lote.validade.strftime('%d/%m/%Y')
            ano = estoque.lote.validade.year
            status = "⚠️ 2025" if ano == 2025 else "✅ 2026+" if ano >= 2026 else f"📅 {ano}"
        else:
            validade_str = 'Sem validade'
            status = "⚪"
        
        endereco = f"{estoque.armazenamento.rua}-{estoque.armazenamento.predio}-{estoque.armazenamento.nivel:02d}-{estoque.armazenamento.ap:02d}"
        print(f"   {i}. {endereco}: Qtd {estoque.quantidade} | {validade_str} {status}")
    
    print()
    print("🔍 ANÁLISE:")
    
    # Contar por ano
    lotes_2025 = lotes.filter(validade__year=2025).count()
    lotes_2026 = lotes.filter(validade__year=2026).count()
    lotes_outros = lotes.filter(validade__year__gt=2026).count()
    lotes_sem_validade = lotes.filter(validade__isnull=True).count()
    
    print(f"   📊 Lotes em 2025: {lotes_2025}")
    print(f"   📊 Lotes em 2026: {lotes_2026}")
    print(f"   📊 Lotes outros anos: {lotes_outros}")
    print(f"   📊 Lotes sem validade: {lotes_sem_validade}")
    
    if lotes_2025 > 0:
        print("   ⚠️  CONFIRMADO: Produto 618 TEM lotes com validade em 2025")
        print("   💡 Isso explica por que aparece 25/08/2025 na interface")
    else:
        print("   ✅ Produto 618 NÃO tem lotes com validade em 2025")
        print("   🤔 A interface pode estar mostrando dados incorretos")

except Produto.DoesNotExist:
    print("❌ Produto 618 não encontrado no banco de dados")
except Exception as e:
    print(f"❌ Erro: {e}")

print()
print("✅ Investigação concluída!")
