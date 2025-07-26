# Copilot Instructions for Controle de Validade de Estoque

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

Este é um projeto Django 5.2.4 para controle de validade de estoque com as seguintes características:

## Estrutura do Projeto
- **Django Framework**: Versão 5.2.4
- **Banco de Dados**: SQLite (db.sqlite3)
- **App Principal**: `produtos`
- **Interface**: Sistema moderno com cards, colapso e validações automáticas

## Modelos Principais
- **Produto**: Cadastro básico de produtos
- **Lote**: Controle de lotes com validade
- **Estoque**: Controle de quantidades por lote
- **Armazenamento**: Endereços físicos de armazenamento

## Regras de Negócio Importantes
- **Regra Nível 0 = Meio**: Todos os endereços no nível 0 devem ser automaticamente configurados como tipo "meio"
- **Validação Automática**: Implementada nos métodos `clean()` e `save()` do modelo Armazenamento
- **Interface Moderna**: Cards organizados, controles de colapso, hover effects

## Padrões de Código
- Use validações automáticas nos models Django
- Mantenha interface limpa com cards e componentes visuais
- Implemente feedback visual para interações do usuário
- Siga as convenções Django para URLs, views e templates

## Tecnologias
- Django 5.2.4
- SQLite
- HTML/CSS/JavaScript para interface
- Python 3.13.3
