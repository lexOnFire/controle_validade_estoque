#!/usr/bin/env python
"""
Script para corrigir automaticamente problemas nos templates
"""
import os
import re

def fix_confirm_messages(content):
    """Corrige mensagens de confirm() com caracteres especiais"""
    patterns = [
        (r"return confirm\('([^']*)'?\)", r"return confirm('\1')"),
        (r"return confirm\(\"([^\"]*)\"\)", r"return confirm('\1')"),
        # Remover caracteres problemáticos
        (r"'([^']*)'", lambda m: "'" + m.group(1).replace('ç', 'c').replace('ã', 'a').replace('á', 'a').replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o').replace('ô', 'o').replace('ú', 'u').replace('ü', 'u').replace('?', '') + "'"),
    ]
    
    fixed_content = content
    for pattern, replacement in patterns:
        if callable(replacement):
            fixed_content = re.sub(pattern, replacement, fixed_content)
        else:
            fixed_content = re.sub(pattern, replacement, fixed_content)
    
    return fixed_content

def fix_html_structure(content):
    """Corrige problemas estruturais do HTML"""
    # Corrigir tags não fechadas
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Corrigir self-closing tags
        line = re.sub(r'<(input|br|hr|img|meta|link)([^>]*?)(?<!/)>', r'<\1\2 />', line)
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_template(file_path):
    """Corrige um template específico"""
    print(f"🔧 Corrigindo: {os.path.basename(file_path)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplicar correções
        content = fix_confirm_messages(content)
        content = fix_html_structure(content)
        
        # Correções específicas por arquivo
        filename = os.path.basename(file_path)
        
        if filename == 'cadastrar_enderecos.html':
            # Corrigir problemas específicos
            content = content.replace(
                "onclick=\"return confirm('Excluir os endereços selecionados?')\"",
                "onclick=\"return confirm('Excluir os enderecos selecionados?')\""
            )
        
        if filename == 'painel.html':
            content = content.replace(
                "onclick=\"return confirm('Alterar tipo de armazenamento deste endereco?')\"",
                "onclick=\"return confirm('Alterar tipo de armazenamento deste endereco?')\""
            )
            content = content.replace(
                "onclick=\"return confirm('Marcar como saida (transferir para nivel 0)?')\"",
                "onclick=\"return confirm('Marcar como saida?')\""
            )
            content = content.replace(
                "onclick=\"return confirm('Remover este produto do estoque?')\"",
                "onclick=\"return confirm('Remover este produto?')\""
            )
        
        if filename == 'editar_lote.html':
            content = re.sub(
                r"onclick=\"return confirm\('([^']*)'?\)\"",
                r"onclick=\"return confirm('Confirmar alteracao?')\"",
                content
            )
        
        if filename == 'excluir_produto.html':
            content = re.sub(
                r"onclick=\"return confirm\('([^']*)'?\)\"",
                r"onclick=\"return confirm('Confirmar exclusao?')\"",
                content
            )
        
        if filename == 'listar_produtos.html':
            content = re.sub(
                r"onclick=\"return confirm\('([^']*)'?\)\"",
                r"onclick=\"return confirm('Confirmar acao?')\"",
                content
            )
        
        if filename == 'relatorio_completo.html':
            content = re.sub(
                r"onclick=\"return confirm\('([^']*)'?\)\"",
                r"onclick=\"return confirm('Confirmar acao?')\"",
                content
            )
        
        # Salvar apenas se houve mudanças
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ Corrigido com sucesso")
            return True
        else:
            print(f"   ℹ️  Nenhuma correção necessária")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return False

def main():
    print("🛠️  CORRETOR AUTOMÁTICO DE TEMPLATES")
    print("=" * 50)
    
    templates_dir = "/workspaces/controle_validade_estoque/produtos/templates/produtos"
    
    # Templates com problemas identificados
    problematic_templates = [
        'cadastrar_enderecos.html',
        'painel.html',
        'editar_lote.html',
        'excluir_produto.html',
        'listar_produtos.html',
        'relatorio_completo.html'
    ]
    
    fixed_count = 0
    
    for template in problematic_templates:
        file_path = os.path.join(templates_dir, template)
        if os.path.exists(file_path):
            if fix_template(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  Template não encontrado: {template}")
    
    print(f"\n📊 RESUMO:")
    print(f"   🔧 Templates corrigidos: {fixed_count}")
    print(f"   📋 Templates verificados: {len(problematic_templates)}")
    
    if fixed_count > 0:
        print(f"\n✅ Correções aplicadas! Execute o validador novamente para verificar.")
    else:
        print(f"\nℹ️  Nenhuma correção foi necessária.")

if __name__ == "__main__":
    main()
