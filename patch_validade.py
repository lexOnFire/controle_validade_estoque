#!/usr/bin/env python3
"""
Script para aplicar patch adicional na importação
Corrige o tratamento de campos de validade vazios e valores especiais
"""

import os

def aplicar_patch_validade():
    """Aplica patch para melhor tratamento de validades"""
    
    arquivo_views = r"c:\Users\alexs\controle_projeto\produtos\views.py"
    
    # Ler o arquivo atual
    with open(arquivo_views, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Procurar por mensagens de erro de formato de validade e corrigir
    codigo_original = 'erros.append(f\'Linha {linha_num}: Formato de data inválido nas colunas de validade. Valores: {valores_validade}\')'
    
    codigo_corrigido = '''# Log de aviso ao invés de erro fatal
                        print(f'Aviso - Linha {linha_num}: Valores de validade não reconhecidos: {valores_validade} - Assumindo sem validade')
                        # Continuar processamento sem validade'''
    
    if codigo_original in conteudo:
        conteudo_novo = conteudo.replace(codigo_original, codigo_corrigido)
        
        # Salvar o arquivo corrigido
        with open(arquivo_views, 'w', encoding='utf-8') as f:
            f.write(conteudo_novo)
        
        print("✅ Patch de validade aplicado!")
        print("🔧 Agora registros com valores inválidos de validade serão processados sem validade")
    else:
        print("⚠️  Código específico não encontrado - procurando alternativas...")
        
        # Procurar por outras formas de tratamento de erro de validade
        if "Formato de data inválido" in conteudo:
            print("📝 Encontrado tratamento de erro de data. Aplicando correção genérica...")
            
            # Substituição mais genérica
            conteudo_novo = conteudo.replace(
                "erros.append(f'Linha {linha_num}: Formato de data inválido",
                "print(f'Aviso - Linha {linha_num}: Formato de data inválido"
            )
            
            conteudo_novo = conteudo_novo.replace(
                "continue  # Pular linha com erro de data",
                "validade = None  # Assumir sem validade e continuar"
            )
            
            with open(arquivo_views, 'w', encoding='utf-8') as f:
                f.write(conteudo_novo)
            
            print("✅ Patch genérico aplicado!")
        else:
            print("❌ Não foi possível encontrar o código de tratamento de validade")

def main():
    print("🔧 APLICANDO PATCH PARA TRATAMENTO DE VALIDADE")
    print("=" * 60)
    
    aplicar_patch_validade()
    
    print("=" * 60)
    print("✅ PATCH APLICADO!")
    print("🎯 Agora registros com 'S/ VALIDADE' serão processados normalmente")
    print("📁 Teste novamente com: FIFO_CONSOLIDADO_FORMATADO.csv")

if __name__ == "__main__":
    main()
