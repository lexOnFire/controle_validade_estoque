import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Produto, Lote, Estoque

print("🔍 INVESTIGAÇÃO COMPLETA: PRODUTO 618")
print("=" * 60)

try:
    produto = Produto.objects.get(codigo='618')
    print(f"✅ Produto: {produto.nome}")
    print(f"   Código: {produto.codigo}")
    print()
    
    # 1. VERIFICAR LOTES
    print("📦 LOTES DO PRODUTO:")
    lotes = Lote.objects.filter(produto=produto).order_by('validade')
    for i, lote in enumerate(lotes, 1):
        validade_str = lote.validade.strftime('%d/%m/%Y') if lote.validade else 'Sem validade'
        ano = lote.validade.year if lote.validade else None
        status = "⚠️ 2025" if ano == 2025 else "✅ 2026+" if ano and ano >= 2026 else f"📅 {ano}"
        print(f"   {i}. {lote.numero_lote}: {validade_str} {status}")
    
    print()
    
    # 2. VERIFICAR ESTOQUES
    print("📍 ESTOQUES DO PRODUTO:")
    estoques = Estoque.objects.filter(produto=produto).order_by('data_validade')
    
    for i, estoque in enumerate(estoques, 1):
        endereco = f"{estoque.local.rua}-{estoque.local.predio}-{estoque.local.nivel}-{estoque.local.ap}"
        
        if estoque.data_validade:
            validade_str = estoque.data_validade.strftime('%d/%m/%Y')
            ano = estoque.data_validade.year
            status = "⚠️ 2025 - AQUI ESTÁ O PROBLEMA!" if ano == 2025 else "✅ 2026+" if ano >= 2026 else f"📅 {ano}"
        else:
            validade_str = 'Sem validade'
            status = "⚪"
        
        print(f"   {i}. Endereço: {endereco}")
        print(f"      Data armazenado: {estoque.data_armazenado}")
        print(f"      Data validade: {validade_str} {status}")
        print(f"      Usuário: {estoque.usuario_responsavel or 'N/A'}")
        print()
    
    # 3. ANÁLISE
    print("🎯 ANÁLISE:")
    estoques_2025 = estoques.filter(data_validade__year=2025).count()
    estoques_2026 = estoques.filter(data_validade__year=2026).count()
    
    print(f"   📊 Estoques com validade em 2025: {estoques_2025}")
    print(f"   📊 Estoques com validade em 2026: {estoques_2026}")
    print()
    
    if estoques_2025 > 0:
        print("🔍 PROBLEMA IDENTIFICADO:")
        print("   ❌ A tabela ESTOQUE tem registros com data_validade em 2025")
        print("   ✅ A tabela LOTE tem registros com validade em 2026")
        print("   📺 A INTERFACE mostra os dados da tabela ESTOQUE")
        print()
        print("💡 SOLUÇÃO:")
        print("   Sincronizar as datas entre as tabelas ESTOQUE e LOTE")
        print("   ou")
        print("   Corrigir a interface para mostrar dados dos LOTES")
    else:
        print("✅ Não há problema nas datas de validade")
    
    # 4. VERIFICAR PRÓXIMA VALIDADE (método usado na interface)
    print()
    print("🔍 VERIFICANDO MÉTODO DA INTERFACE:")
    proxima_validade = produto.proxima_validade()
    if proxima_validade:
        print(f"   📅 Próxima validade (via Lotes): {proxima_validade.strftime('%d/%m/%Y')}")
        print(f"   🎯 Ano: {proxima_validade.year}")
    else:
        print("   ⚪ Nenhuma validade encontrada via Lotes")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
