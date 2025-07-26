#!/usr/bin/env python3
"""
🎯 IMPLEMENTAÇÃO DO PAINEL COMPLETO
=====================================
Este script implementa a correção para exibir todos os prédios no painel,
incluindo os vazios, com indicador visual adequado.
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/workspaces/controle_validade_estoque')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'validade_estoque.settings')
django.setup()

from produtos.models import Armazenamento, Estoque, Produto

def analisar_situacao_atual():
    """Analisa a situação atual do banco de dados"""
    print("🚀 ANÁLISE DA SITUAÇÃO ATUAL")
    print("=" * 50)
    
    # Contar endereços cadastrados
    total_enderecos = Armazenamento.objects.count()
    
    # Contar endereços com estoque
    enderecos_com_estoque = Estoque.objects.values('local').distinct().count()
    
    # Contar endereços vazios
    enderecos_vazios = total_enderecos - enderecos_com_estoque
    
    print(f"📊 Total de endereços cadastrados: {total_enderecos}")
    print(f"📦 Endereços com produtos: {enderecos_com_estoque}")
    print(f"🏗️  Endereços vazios: {enderecos_vazios}")
    print(f"📈 Taxa de ocupação: {(enderecos_com_estoque/total_enderecos)*100:.1f}%")
    
    # Análise por rua
    print("\n📍 ANÁLISE POR RUA:")
    ruas = Armazenamento.objects.values_list('rua', flat=True).distinct().order_by('rua')
    
    for rua in ruas:
        predios_total = Armazenamento.objects.filter(rua=rua).values('predio').distinct().count()
        predios_com_estoque = Estoque.objects.filter(local__rua=rua).values('local__predio').distinct().count()
        predios_vazios = predios_total - predios_com_estoque
        
        print(f"   🏪 Rua {rua}: {predios_total} prédios ({predios_com_estoque} ocupados, {predios_vazios} vazios)")

def criar_view_painel_completa():
    """Cria a nova versão da view do painel que inclui prédios vazios"""
    
    view_content = '''def painel(request):
    """
    Painel principal que exibe o estoque organizando por rua e prédio.
    ATUALIZADO: Agora inclui todos os prédios, mesmo os vazios.
    """
    # Buscar todos os endereços cadastrados (não apenas com estoque)
    enderecos = Armazenamento.objects.all().order_by('rua', 'predio', 'nivel')
    
    # Organizar por ruas e prédios
    organizacao = {}
    
    for endereco in enderecos:
        rua = endereco.rua
        predio = endereco.predio
        
        # Inicializar estrutura se não existir
        if rua not in organizacao:
            organizacao[rua] = {}
        if predio not in organizacao[rua]:
            organizacao[rua][predio] = []
        
        # Buscar produtos no estoque para este endereço
        produtos_estoque = Estoque.objects.filter(local=endereco).select_related('produto')
        
        # Adicionar informações do endereço
        endereco_info = {
            'endereco': endereco,
            'produtos': list(produtos_estoque),
            'tem_produtos': produtos_estoque.exists(),
            'total_produtos': produtos_estoque.count()
        }
        
        organizacao[rua][predio].append(endereco_info)
    
    # Calcular estatísticas
    total_enderecos = Armazenamento.objects.count()
    enderecos_com_estoque = Estoque.objects.values('local').distinct().count()
    total_produtos = Estoque.objects.count()
    
    context = {
        'organizacao': organizacao,
        'total_enderecos': total_enderecos,
        'enderecos_com_estoque': enderecos_com_estoque,
        'enderecos_vazios': total_enderecos - enderecos_com_estoque,
        'total_produtos': total_produtos,
        'taxa_ocupacao': round((enderecos_com_estoque/total_enderecos)*100, 1) if total_enderecos > 0 else 0
    }
    
    return render(request, 'produtos/painel.html', context)'''
    
    print("\n💻 NOVA VIEW DO PAINEL CRIADA:")
    print("✅ Inclui todos os endereços (com e sem produtos)")
    print("✅ Mantém organização por rua/prédio")
    print("✅ Adiciona indicadores visuais")
    print("✅ Calcula estatísticas completas")
    
    return view_content

def criar_template_painel_completo():
    """Cria o template atualizado com indicadores visuais para prédios vazios"""
    
    template_content = '''{% load static %}
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel de Controle - Estoque</title>
    <style>
        /* Estilos base */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }

        .stat-label {
            color: #6c757d;
            margin-top: 5px;
        }

        .content {
            padding: 30px;
        }

        /* Estilos para ruas */
        .rua-section {
            margin-bottom: 30px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }

        .rua-header {
            background: linear-gradient(135deg, #34495e, #2c3e50);
            color: white;
            padding: 15px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }

        .rua-header:hover {
            background: linear-gradient(135deg, #2c3e50, #34495e);
        }

        .rua-title {
            font-size: 1.3em;
            font-weight: bold;
        }

        .rua-toggle {
            font-size: 1.2em;
            transition: transform 0.3s ease;
        }

        .rua-content {
            display: block;
            background: #f8f9fa;
            padding: 20px;
        }

        .rua-content.collapsed {
            display: none;
        }

        .rua-header.collapsed .rua-toggle {
            transform: rotate(-90deg);
        }

        /* Estilos para prédios */
        .predio-section {
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }

        .predio-header {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 12px 15px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }

        .predio-header.vazio {
            background: linear-gradient(135deg, #95a5a6, #7f8c8d);
            opacity: 0.8;
        }

        .predio-header:hover {
            opacity: 0.9;
        }

        .predio-title {
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .predio-status {
            font-size: 0.9em;
            padding: 3px 8px;
            border-radius: 12px;
            background: rgba(255,255,255,0.2);
        }

        .predio-toggle {
            transition: transform 0.3s ease;
        }

        .predio-content {
            display: block;
            padding: 15px;
            background: #ffffff;
        }

        .predio-content.collapsed {
            display: none;
        }

        .predio-header.collapsed .predio-toggle {
            transform: rotate(-90deg);
        }

        /* Estilos para endereços */
        .endereco-item {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            margin-bottom: 10px;
            padding: 10px;
        }

        .endereco-item.vazio {
            background: #f1f3f4;
            border-color: #dee2e6;
            opacity: 0.7;
        }

        .endereco-header {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .endereco-vazio {
            color: #6c757d;
            font-style: italic;
            text-align: center;
            padding: 20px;
        }

        /* Estilos para produtos */
        .produto-list {
            display: grid;
            gap: 10px;
            margin-top: 10px;
        }

        .produto-item {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 10px;
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: 10px;
            align-items: center;
        }

        .produto-nome {
            font-weight: bold;
            color: #2c3e50;
        }

        .produto-info {
            font-size: 0.9em;
            color: #6c757d;
        }

        /* Botões de ação */
        .actions {
            display: flex;
            gap: 5px;
        }

        .btn {
            padding: 6px 12px;
            border: 2px solid;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.85em;
            font-weight: 500;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }

        .btn-primary {
            color: #007bff;
            border-color: #007bff;
            background: transparent;
        }

        .btn-primary:hover {
            background: #007bff;
            color: white;
        }

        .btn-warning {
            color: #fd7e14;
            border-color: #fd7e14;
            background: transparent;
        }

        .btn-warning:hover {
            background: #fd7e14;
            color: white;
        }

        .btn-danger {
            color: #dc3545;
            border-color: #dc3545;
            background: transparent;
        }

        .btn-danger:hover {
            background: #dc3545;
            color: white;
        }

        /* Ícones de status */
        .status-icon {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }

        .status-ocupado {
            background: #28a745;
        }

        .status-vazio {
            background: #6c757d;
        }

        /* Responsividade */
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 10px;
            }

            .header {
                padding: 20px;
            }

            .header h1 {
                font-size: 2em;
            }

            .content {
                padding: 15px;
            }

            .stats {
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                padding: 15px;
            }

            .produto-item {
                grid-template-columns: 1fr;
                gap: 5px;
            }

            .actions {
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏪 Painel de Controle do Estoque</h1>
            <p>Sistema completo de gerenciamento - Todos os endereços</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_enderecos }}</div>
                <div class="stat-label">Total de Endereços</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ enderecos_com_estoque }}</div>
                <div class="stat-label">Com Produtos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ enderecos_vazios }}</div>
                <div class="stat-label">Vazios</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_produtos }}</div>
                <div class="stat-label">Total de Produtos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ taxa_ocupacao }}%</div>
                <div class="stat-label">Taxa de Ocupação</div>
            </div>
        </div>

        <div class="content">
            {% for rua, predios in organizacao.items %}
            <div class="rua-section">
                <div class="rua-header" onclick="toggleRua('rua-{{ rua }}')">
                    <div class="rua-title">
                        📍 Rua {{ rua }} 
                        <span class="rua-status">({{ predios|length }} prédio{% if predios|length != 1 %}s{% endif %})</span>
                    </div>
                    <div class="rua-toggle" id="toggle-rua-{{ rua }}">▼</div>
                </div>
                
                <div class="rua-content" id="rua-{{ rua }}">
                    {% for predio, enderecos in predios.items %}
                    {% with tem_produtos=enderecos.0.tem_produtos total_produtos_predio=enderecos|length %}
                    <div class="predio-section">
                        <div class="predio-header {% if not tem_produtos %}vazio{% endif %}" onclick="togglePredio('predio-{{ rua }}-{{ predio }}')">
                            <div class="predio-title">
                                <span class="status-icon {% if tem_produtos %}status-ocupado{% else %}status-vazio{% endif %}"></span>
                                🏢 Prédio {{ predio }}
                                <span class="predio-status">
                                    {% if tem_produtos %}
                                        {{ total_produtos_predio }} endereço{% if total_produtos_predio != 1 %}s{% endif %} cadastrado{% if total_produtos_predio != 1 %}s{% endif %}
                                    {% else %}
                                        Vazio - {{ total_produtos_predio }} endereço{% if total_produtos_predio != 1 %}s{% endif %} disponível{% if total_produtos_predio != 1 %}eis{% endif %}
                                    {% endif %}
                                </span>
                            </div>
                            <div class="predio-toggle" id="toggle-predio-{{ rua }}-{{ predio }}">▼</div>
                        </div>
                        
                        <div class="predio-content" id="predio-{{ rua }}-{{ predio }}">
                            {% for endereco_info in enderecos %}
                            <div class="endereco-item {% if not endereco_info.tem_produtos %}vazio{% endif %}">
                                <div class="endereco-header">
                                    📦 {{ endereco_info.endereco.rua }}-{{ endereco_info.endereco.predio }}-{{ endereco_info.endereco.nivel }}-{{ endereco_info.endereco.ap }}
                                    {% if endereco_info.tem_produtos %}
                                        <span style="color: #28a745;">({{ endereco_info.total_produtos }} produto{% if endereco_info.total_produtos != 1 %}s{% endif %})</span>
                                    {% else %}
                                        <span style="color: #6c757d;">(Disponível)</span>
                                    {% endif %}
                                </div>
                                
                                {% if endereco_info.produtos %}
                                    <div class="produto-list">
                                        {% for estoque in endereco_info.produtos %}
                                        <div class="produto-item">
                                            <div>
                                                <div class="produto-nome">{{ estoque.produto.nome }}</div>
                                                <div class="produto-info">
                                                    Data: {{ estoque.data_armazenado|date:"d/m/Y" }}
                                                </div>
                                            </div>
                                            <div class="actions">
                                                <a href="{% url 'buscar_produto' %}?produto={{ estoque.produto.nome }}" class="btn btn-primary" title="Ver detalhes">
                                                    👁️ Ver
                                                </a>
                                            </div>
                                        </div>
                                        {% endfor %}
                                    </div>
                                {% else %}
                                    <div class="endereco-vazio">
                                        🏗️ Endereço disponível para armazenamento
                                        <br>
                                        <a href="{% url 'armazenar_produto' %}?rua={{ endereco_info.endereco.rua }}&predio={{ endereco_info.endereco.predio }}&nivel={{ endereco_info.endereco.nivel }}&ap={{ endereco_info.endereco.ap }}" 
                                           class="btn btn-primary" style="margin-top: 10px;">
                                            📦 Armazenar Produto
                                        </a>
                                    </div>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endwith %}
                    {% endfor %}
                </div>
            </div>
            {% empty %}
            <div style="text-align: center; padding: 50px; color: #6c757d;">
                <h3>📭 Nenhum endereço cadastrado</h3>
                <p>Comece cadastrando endereços no sistema.</p>
                <a href="{% url 'cadastrar_enderecos' %}" class="btn btn-primary">➕ Cadastrar Endereços</a>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        function toggleRua(ruaId) {
            const content = document.getElementById(ruaId);
            const toggle = document.getElementById('toggle-' + ruaId);
            const header = toggle.closest('.rua-header');
            
            if (content.classList.contains('collapsed')) {
                content.classList.remove('collapsed');
                header.classList.remove('collapsed');
            } else {
                content.classList.add('collapsed');
                header.classList.add('collapsed');
            }
        }
        
        function togglePredio(predioId) {
            const content = document.getElementById(predioId);
            const toggle = document.getElementById('toggle-' + predioId);
            const header = toggle.closest('.predio-header');
            
            if (content.classList.contains('collapsed')) {
                content.classList.remove('collapsed');
                header.classList.remove('collapsed');
            } else {
                content.classList.add('collapsed');
                header.classList.add('collapsed');
            }
        }

        // Inicializar com todas as seções abertas
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🎯 Painel carregado com todos os endereços!');
        });
    </script>
</body>
</html>'''
    
    print("\n🎨 TEMPLATE ATUALIZADO CRIADO:")
    print("✅ Indicadores visuais para prédios vazios")
    print("✅ Estatísticas completas no header")
    print("✅ Botão para armazenar em endereços vazios")
    print("✅ Sistema de colapso mantido")
    
    return template_content

def main():
    """Função principal que executa toda a implementação"""
    print("🎯 IMPLEMENTAÇÃO DO PAINEL COMPLETO")
    print("=" * 60)
    
    # 1. Analisar situação atual
    analisar_situacao_atual()
    
    # 2. Criar nova view
    nova_view = criar_view_painel_completa()
    
    # 3. Criar novo template  
    novo_template = criar_template_painel_completo()
    
    print("\n✅ IMPLEMENTAÇÃO CONCLUÍDA!")
    print("=" * 40)
    print("📋 RESUMO DAS MELHORIAS:")
    print("   ✅ Painel agora mostra TODOS os prédios")
    print("   ✅ Prédios vazios claramente identificados")
    print("   ✅ Estatísticas completas exibidas")
    print("   ✅ Botão para armazenar em endereços vazios")
    print("   ✅ Sistema de colapso mantido")
    print("   ✅ Design responsivo e atrativo")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("   1. Aplicar a nova view no arquivo views.py")
    print("   2. Aplicar o novo template no painel.html")  
    print("   3. Testar o painel atualizado")
    
    return nova_view, novo_template

if __name__ == "__main__":
    main()
