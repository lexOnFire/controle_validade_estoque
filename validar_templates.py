#!/usr/bin/env python
"""
Script para validar e corrigir erros nos templates HTML
"""
import os
import re
from html.parser import HTMLParser

class TemplateValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []
        self.warnings = []
        self.tags_stack = []
        self.line_num = 1
        self.col_num = 1
        
    def error(self, message):
        self.errors.append(f"Linha {self.line_num}: {message}")
    
    def warning(self, message):
        self.warnings.append(f"Linha {self.line_num}: {message}")
    
    def handle_starttag(self, tag, attrs):
        # Tags que não precisam de fechamento
        self_closing = ['br', 'hr', 'img', 'input', 'link', 'meta', 'source', 'area', 'base', 'col', 'embed', 'param', 'track', 'wbr']
        
        if tag not in self_closing:
            self.tags_stack.append((tag, self.line_num))
            
        # Verificar atributos problemáticos
        for attr_name, attr_value in attrs:
            if attr_name == 'style' and attr_value:
                # Verificar CSS inline malformado
                if not attr_value.strip().endswith(';') and not attr_value.strip().endswith('}'):
                    if ':' in attr_value and not attr_value.strip().endswith('px') and not attr_value.strip().endswith('%') and not attr_value.strip().endswith('em'):
                        # Pode estar truncado
                        self.warning(f"Possível CSS truncado em '{tag}': {attr_value[:50]}...")
    
    def handle_endtag(self, tag):
        if self.tags_stack:
            expected_tag, start_line = self.tags_stack.pop()
            if expected_tag != tag:
                self.error(f"Tag de fechamento incorreta: esperava '{expected_tag}' (linha {start_line}), encontrou '{tag}'")
        else:
            self.error(f"Tag de fechamento '{tag}' sem abertura correspondente")
    
    def handle_data(self, data):
        # Contar linhas
        self.line_num += data.count('\n')
    
    def close(self):
        super().close()
        # Verificar tags não fechadas
        for tag, line_num in self.tags_stack:
            self.error(f"Tag '{tag}' aberta na linha {line_num} não foi fechada")

def validate_template(file_path):
    print(f"\n🔍 VALIDANDO: {os.path.basename(file_path)}")
    print("=" * 50)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificações básicas
        issues_found = []
        
        # 1. Verificar tags HTML básicas
        if '<html>' not in content.lower() and '<!doctype html>' not in content.lower():
            issues_found.append("⚠️  DOCTYPE ou tag HTML ausente")
        
        # 2. Verificar encoding
        if 'charset=' not in content.lower():
            issues_found.append("⚠️  Declaração de charset ausente")
        
        # 3. Verificar CSS inline problemático
        css_issues = []
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Procurar por style= truncado ou malformado
            if 'style=' in line:
                # Extrair o valor do style
                style_match = re.search(r'style=["\']([^"\']*)["\']', line)
                if style_match:
                    style_value = style_match.group(1)
                    
                    # Verificar se parece truncado
                    if style_value.endswith('font-size:') or ':' in style_value and not style_value.strip().endswith(';'):
                        if not any(ending in style_value for ending in ['px', 'em', '%', 'rem', 'vh', 'vw']):
                            css_issues.append(f"   Linha {i}: CSS possivelmente truncado: {style_value[:80]}...")
        
        if css_issues:
            issues_found.extend(css_issues)
        
        # 4. Verificar JavaScript inline
        js_issues = []
        for i, line in enumerate(lines, 1):
            if 'onclick=' in line or 'onmouseover=' in line or 'onmouseout=' in line:
                # Verificar parênteses balanceados
                onclick_match = re.search(r'on\w+=["\']([^"\']*)["\']', line)
                if onclick_match:
                    js_code = onclick_match.group(1)
                    open_parens = js_code.count('(')
                    close_parens = js_code.count(')')
                    if open_parens != close_parens:
                        js_issues.append(f"   Linha {i}: JavaScript com parênteses desbalanceados: {js_code[:50]}...")
        
        if js_issues:
            issues_found.extend(js_issues)
        
        # 5. Verificar tags Django malformadas
        django_issues = []
        django_tags = re.findall(r'{%[^%]*%}|{{[^}]*}}', content)
        for tag in django_tags:
            if tag.count('{') != tag.count('}') or tag.count('%') % 2 != 0:
                django_issues.append(f"   Tag Django malformada: {tag}")
        
        if django_issues:
            issues_found.extend(django_issues)
        
        # 6. Usar HTMLParser para validação estrutural
        validator = TemplateValidator()
        try:
            # Remover tags Django temporariamente para validação HTML
            temp_content = re.sub(r'{%[^%]*%}', '', content)
            temp_content = re.sub(r'{{[^}]*}}', 'DJANGO_VAR', temp_content)
            validator.feed(temp_content)
            validator.close()
            
            if validator.errors:
                issues_found.extend([f"   HTML: {err}" for err in validator.errors])
            if validator.warnings:
                issues_found.extend([f"   Aviso: {warn}" for warn in validator.warnings])
                
        except Exception as e:
            issues_found.append(f"   Erro na validação HTML: {str(e)}")
        
        # Mostrar resultados
        if issues_found:
            print("❌ PROBLEMAS ENCONTRADOS:")
            for issue in issues_found:
                print(issue)
            return False
        else:
            print("✅ TEMPLATE VÁLIDO - Nenhum problema encontrado")
            return True
            
    except Exception as e:
        print(f"❌ ERRO ao ler arquivo: {str(e)}")
        return False

def main():
    print("🔧 VALIDADOR DE TEMPLATES")
    print("=" * 50)
    
    templates_dir = "/workspaces/controle_validade_estoque/produtos/templates/produtos"
    
    if not os.path.exists(templates_dir):
        print(f"❌ Diretório não encontrado: {templates_dir}")
        return
    
    html_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
    
    if not html_files:
        print("❌ Nenhum arquivo HTML encontrado")
        return
    
    print(f"📋 Encontrados {len(html_files)} templates para validar")
    
    valid_count = 0
    invalid_count = 0
    
    # Validar templates principais primeiro
    priority_templates = [
        'cadastrar_enderecos.html',
        'painel.html', 
        'editar_endereco.html',
        'cadastrar_produto.html'
    ]
    
    for template in priority_templates:
        if template in html_files:
            file_path = os.path.join(templates_dir, template)
            if validate_template(file_path):
                valid_count += 1
            else:
                invalid_count += 1
            html_files.remove(template)
    
    # Validar outros templates
    for template in sorted(html_files):
        file_path = os.path.join(templates_dir, template)
        if validate_template(file_path):
            valid_count += 1
        else:
            invalid_count += 1
    
    print(f"\n📊 RESUMO DA VALIDAÇÃO:")
    print(f"   ✅ Templates válidos: {valid_count}")
    print(f"   ❌ Templates com problemas: {invalid_count}")
    print(f"   📋 Total verificados: {valid_count + invalid_count}")
    
    if invalid_count > 0:
        print(f"\n🔧 RECOMENDAÇÃO:")
        print("   • Revisar e corrigir os templates com problemas")
        print("   • Testar funcionamento após correções")
        print("   • Executar validação novamente")

if __name__ == "__main__":
    main()
