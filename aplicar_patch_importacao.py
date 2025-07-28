#!/usr/bin/env python3
"""
Script para aplicar patch na view de importação
Corrige o problema de registros duplicados durante a importação
"""

import os
import sys

def aplicar_patch_importacao():
    """Aplica patch na função de importação"""
    
    arquivo_views = r"c:\Users\alexs\controle_projeto\produtos\views.py"
    
    # Ler o arquivo atual
    with open(arquivo_views, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Código original problemático
    codigo_original = """                    # Criar registro de estoque
                    estoque, estoque_created = Estoque.objects.get_or_create(
                        produto=produto,
                        local=armazenamento,
                        defaults={
                            'data_armazenado': data_armazenado,
                            'usuario_responsavel': request.user.username if request.user.is_authenticated else 'Sistema CSV',
                            'observacoes': f'Importado via CSV - Linha {linha_num}'
                        }
                    )"""
    
    # Novo código corrigido
    codigo_corrigido = """                    # Criar registro de estoque - Corrigido para evitar duplicatas
                    try:
                        # Tentar encontrar um registro existente
                        estoque = Estoque.objects.filter(
                            produto=produto,
                            local=armazenamento
                        ).first()
                        
                        if estoque:
                            # Se encontrou, usar o existente
                            estoque_created = False
                        else:
                            # Se não encontrou, criar novo
                            estoque = Estoque.objects.create(
                                produto=produto,
                                local=armazenamento,
                                data_armazenado=data_armazenado,
                                usuario_responsavel=request.user.username if request.user.is_authenticated else 'Sistema CSV',
                                observacoes=f'Importado via CSV - Linha {linha_num}'
                            )
                            estoque_created = True
                    except Exception as e:
                        erros.append(f'Linha {linha_num}: Erro ao criar estoque: {str(e)}')
                        continue"""
    
    # Verificar se o patch já foi aplicado
    if "# Corrigido para evitar duplicatas" in conteudo:
        print("✅ Patch já foi aplicado anteriormente!")
        return
    
    # Aplicar o patch
    if codigo_original in conteudo:
        conteudo_novo = conteudo.replace(codigo_original, codigo_corrigido)
        
        # Salvar o arquivo corrigido
        with open(arquivo_views, 'w', encoding='utf-8') as f:
            f.write(conteudo_novo)
        
        print("✅ Patch aplicado com sucesso!")
        print("🔧 Problema de registros duplicados corrigido")
    else:
        print("❌ Código original não encontrado. Pode já ter sido modificado.")

def aplicar_patch_armazenamento():
    """Aplica patch para problemas de armazenamento duplicado"""
    
    arquivo_views = r"c:\Users\alexs\controle_projeto\produtos\views.py"
    
    with open(arquivo_views, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Código original do armazenamento
    codigo_armazenamento_original = """                    # Buscar ou criar endereço de armazenamento
                    armazenamento, created = Armazenamento.objects.get_or_create(
                        rua=rua,
                        predio=predio,
                        nivel=nivel,
                        ap=ap,
                        defaults={'livre': False, 'capacidade_maxima': 1}
                    )"""
    
    # Novo código corrigido para armazenamento
    codigo_armazenamento_corrigido = """                    # Buscar ou criar endereço de armazenamento - Corrigido
                    try:
                        armazenamento = Armazenamento.objects.filter(
                            rua=rua,
                            predio=predio,
                            nivel=nivel,
                            ap=ap
                        ).first()
                        
                        if armazenamento:
                            created = False
                        else:
                            armazenamento = Armazenamento.objects.create(
                                rua=rua,
                                predio=predio,
                                nivel=nivel,
                                ap=ap,
                                livre=False,
                                capacidade_maxima=1
                            )
                            created = True
                    except Exception as e:
                        erros.append(f'Linha {linha_num}: Erro ao criar endereço: {str(e)}')
                        continue"""
    
    if "# Buscar ou criar endereço de armazenamento - Corrigido" in conteudo:
        print("✅ Patch de armazenamento já aplicado!")
        return
    
    if codigo_armazenamento_original in conteudo:
        conteudo = conteudo.replace(codigo_armazenamento_original, codigo_armazenamento_corrigido)
        
        with open(arquivo_views, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print("✅ Patch de armazenamento aplicado!")
    else:
        print("⚠️  Código de armazenamento não encontrado para patch")

def main():
    print("🔧 APLICANDO PATCHES PARA CORREÇÃO DE DUPLICATAS")
    print("=" * 60)
    
    aplicar_patch_armazenamento()
    aplicar_patch_importacao()
    
    print("=" * 60)
    print("✅ PATCHES APLICADOS!")
    print("🎯 Agora a importação deve funcionar sem erros de duplicatas")
    print("📁 Teste com: FIFO_CONSOLIDADO_FORMATADO.csv")
    print("🌐 URL: http://127.0.0.1:8000/produtos/importar-abastecimento/")

if __name__ == "__main__":
    main()
