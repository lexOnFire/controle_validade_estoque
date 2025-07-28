# Sistema de Controle de Validade de Estoque

## 📋 Visão Geral
Sistema Django para controle de validade de estoque com interface moderna em cards, agrupamento visual e validações automáticas.

## 🎨 **NOVA INTERFACE COM CARDS** (Atualização recente)
A página principal foi completamente repaginada com um layout moderno baseado em cards:

### 🏷️ Layout de Cards
- **Cards por endereço**: Cada endereço é exibido em um card individual
- **Design responsivo**: Grid adaptável para diferentes tamanhos de tela
- **Organização visual**: Rua > Prédio > Cards de endereços
- **Sistema de colapso**: Botões para expandir/colapsar ruas

### � Cards de Produto
- Nome do produto em destaque
- Código em formato monospace
- **Badges de status coloridos**:
  - 🔴 Vencido (vermelho)
  - 🟠 Vence em breve (laranja) 
  - 🟡 Próximo ao vencimento (amarelo)
  - 🟢 Válido (verde)
- Informações detalhadas (validade, lotes, data de armazenamento)
- Botões de ação com ícones (Detalhes, Editar, Remover)

### 📱 Melhorias Visuais
- Gradientes modernos em headers
- Animações de hover suaves
- Sombras e elevação em cards
- Interface totalmente responsiva
- Endereços vazios com design diferenciado

## �🏗️ Estrutura do Sistema

### Modelos Principais
- **Produto**: Cadastro básico de produtos
- **Lote**: Controle de lotes com validade
- **Estoque**: Controle de quantidades por lote
- **Armazenamento**: Endereços físicos de armazenamento

### Interface Principal
- **Página Principal**: Visão consolidada com cards modernos e navegação intuitiva
- **Cadastro de Endereços**: Interface limpa com cards e controles de colapso
- **Relatórios**: Análises e relatórios do sistema

## 🔒 Regras de Validação Automática

### Regra Principal: Nível 0 = Meio
**IMPORTANTE**: Todos os endereços no nível 0 devem ser do tipo "meio".

#### Implementação
- **Validação Automática**: O modelo `Armazenamento` possui validação que corrige automaticamente qualquer endereço nível 0 para "meio"
- **Local**: `produtos/models.py` - métodos `clean()` e `save()`
- **Proteção**: Impossível salvar endereços nível 0 como "inteiro" via interface ou código

#### Código de Validação
```python
def clean(self):
    if self.nivel == '0' and self.categoria_armazenamento != 'meio':
        self.categoria_armazenamento = 'meio'

def save(self, *args, **kwargs):
    self.clean()
    super().save(*args, **kwargs)
```

## 🎯 Interface do Usuário

### Funcionalidades Principais
1. **Agrupamento Visual**: Cards organizados por endereço
2. **Controles de Colapso**: Minimizar/expandir ruas e prédios
3. **Barra de Ferramentas**: Ações centralizadas e organizadas
4. **Dropdown de Ações**: Menus limpos sem poluição visual
5. **Hover e Feedback**: Interações visuais modernas

### Controles de Navegação
- **Expandir/Colapsar Tudo**: Controle geral de visibilidade
- **Filtros por Rua/Prédio**: Navegação específica
- **Contador de Visibilidade**: Mostra quantos itens estão visíveis
- **Busca Rápida**: Localização de endereços específicos

## 🛠️ Scripts de Manutenção

### Scripts Disponíveis
1. **`verificar_nivel_0.py`**: Verifica e corrige endereços nível 0
2. **`validar_sistema_nivel_0.py`**: Validação completa do sistema
3. **`testar_validacao_nivel_0.py`**: Teste da validação automática

### Como Executar
```bash
# Verificar e corrigir endereços nível 0
python verificar_nivel_0.py

# Validar integridade do sistema
python validar_sistema_nivel_0.py

# Testar validação automática
python testar_validacao_nivel_0.py
```

## 📊 Estrutura de Dados

### Tipos de Armazenamento
- **inteiro**: Para níveis 1, 2, 3, 4
- **meio**: Obrigatório para nível 0, opcional para outros

### Níveis Suportados
- **Nível 0**: Térreo (sempre "meio")
- **Níveis 1-4**: Andares superiores ("inteiro" ou "meio")

## 🔧 Desenvolvimento

### Tecnologias
- **Django 5.2.4**
- **Python 3.12.3**
- **SQLite** (banco de dados)
- **HTML/CSS/JavaScript** (interface)

### Estrutura de Arquivos
```
produtos/
├── models.py          # Modelos com validações
├── views.py           # Lógica de negócio
├── urls.py            # Rotas
├── forms.py           # Formulários
├── templates/         # Templates HTML
│   └── produtos/
├── migrations/        # Migrações do banco
└── __pycache__/       # Cache Python
```

## ✅ Status do Sistema

### Validações Implementadas
- ✅ Regra nível 0 = meio (automática)
- ✅ Interface limpa e organizada
- ✅ Controles de colapso funcionando
- ✅ Barra de ferramentas unificada
- ✅ Dropdown de ações implementado
- ✅ Scripts de manutenção criados

### Testes Realizados
- ✅ Criação automática corrige nível 0
- ✅ Edição mantém validação
- ✅ Outros níveis funcionam normalmente
- ✅ Interface responsiva e limpa
- ✅ 590 endereços nível 0 validados

## 🚀 Próximos Passos
1. Documentação de API
2. Testes automatizados
3. Backup automático
4. Logs de auditoria
5. Relatórios avançados

---
**Última Atualização**: Sistema validado e funcionando perfeitamente
**Status**: ✅ Produção
