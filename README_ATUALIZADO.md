# Sistema Controle de Validade de Estoque 🏭

Sistema completo para controle de validade de produtos em estoque, desenvolvido em Django com interface moderna e funcionalidades avançadas.

## 🎯 Principais Características

### ✨ **Múltiplas Validades por Produto**
- **Interface dinâmica** para adicionar/remover validades
- **Quantidades individuais** por validade
- **Criação automática** de lotes únicos
- **Preservação de contexto** após operações

### 🔄 **Sistema FIFO Inteligente**
- **First In, First Out** automático por validade
- **Transferência automática** Nível 2 → Nível 0
- **Atualização automática** de datas mais antigas
- **Controle total** de movimentações

### 🏢 **Endereçamento Avançado**
- **Organização inteligente** por Rua-Prédio-Nível-AP
- **Códigos únicos** gerados automaticamente
- **Busca contextual** por endereços vazios
- **QR Codes** para integração com coletores

### 🎨 **Interface Moderna**
- **Cards responsivos** com hover effects
- **Busca em tempo real** (AJAX)
- **Botões contextuais** por lote/endereço
- **Feedback visual** instantâneo

## 🚀 **Últimas Atualizações (Janeiro 2025)**

### 🆕 **Funcionalidades Implementadas**
- ✅ **Múltiplas validades** em uma única operação
- ✅ **JavaScript dinâmico** para campos de validade
- ✅ **Preservação de filtros** na busca avançada
- ✅ **Botões contextuais** EDITAR por lote/endereço
- ✅ **Validações aprimoradas** client/server-side
- ✅ **Interface responsiva** para dispositivos móveis

### 🔧 **Melhorias Técnicas**
- ✅ **Backend otimizado** para processamento em lote
- ✅ **Queries otimizadas** com select_related
- ✅ **Tratamento de erros** robusto
- ✅ **Logs detalhados** de operações
- ✅ **Tokens CSRF** em todos os formulários

## 📦 **Módulos do Sistema**

### 🏷️ **Gestão de Produtos**
```python
# Funcionalidades
- CRUD completo com validações
- Importação em lote via CSV
- Busca avançada por código/nome/categoria
- Múltiplas validades por produto
- Controle de fornecedores
```

### 🏭 **Gestão de Armazenamento**
```python
# Funcionalidades
- Endereçamento automático RUA-PRÉDIO-NÍVEL-AP
- Controle de capacidade por endereço
- Busca por endereços vazios/ocupados
- Organização visual por localização
- Regra automática: Nível 0 = Área de Saída
```

### 📊 **Controle de Estoque**
```python
# Funcionalidades
- FIFO automático por validade
- Transferência inteligente entre níveis
- Alertas de vencimento
- Histórico completo de movimentações
- Dashboard com métricas em tempo real
```

### 🎯 **Sistema de Lotes**
```python
# Funcionalidades
- Criação automática de lotes únicos
- Controle de quantidades por lote
- Numeração sequencial inteligente
- Validações por data de validade
- Rastreabilidade completa
```

## 🛠️ **Tecnologias Utilizadas**

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Django** | 5.2.4 | Framework web principal |
| **Python** | 3.13.3 | Linguagem de programação |
| **SQLite** | 3.x | Banco de dados |
| **Bootstrap** | 5.x | Framework CSS |
| **Font Awesome** | 6.x | Ícones |
| **JavaScript** | ES6+ | Interatividade frontend |

## 📋 **Arquitetura de Dados**

### 🗂️ **Modelos Principais**

```python
# Produto
- nome, codigo (único), peso
- categoria, fornecedor
- timestamps de auditoria
- métodos: proxima_validade(), esta_vencido()

# Armazenamento
- rua, predio, nivel, apartamento
- categoria (inteiro/meio), capacidade
- codigo único auto-gerado
- validação: nível 0 = meio (automático)

# Estoque
- produto, local, data_armazenado
- data_validade, observacoes
- auditoria de alterações

# Lote
- produto, validade, quantidade
- numero_lote (único), data_fabricacao
- ordenação por FIFO

# HistoricoMovimentacao
- origem/destino, tipo_operacao
- usuario, observacoes, timestamp
- rastreabilidade completa
```

## 🎯 **Regras de Negócio**

### 🔄 **FIFO Automático**
- Produtos com **validade mais próxima** saem primeiro
- **Transferência automática** do estoque para expedição
- **Atualização inteligente** de datas mais antigas

### 🏢 **Hierarquia de Níveis**
- **Nível 2**: Armazenamento (Palete Fechado)
- **Nível 0**: Expedição (Área de Saída) - **AUTOMÁTICO**
- **Validação**: Impossível alterar tipo do nível 0

### 📊 **Controle de Capacidade**
- **Limite configurável** por endereço
- **Alertas visuais** de lotação
- **Taxa de ocupação** em tempo real

## 🚀 **Instalação e Configuração**

### 1️⃣ **Clone do Repositório**
```bash
git clone https://github.com/lexOnFire/controle_validade_estoque.git
cd controle_validade_estoque
```

### 2️⃣ **Ambiente Virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3️⃣ **Dependências**
```bash
pip install django==5.2.4
pip install pillow  # Para imagens (opcional)
```

### 4️⃣ **Configuração do Banco**
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5️⃣ **Execução**
```bash
python manage.py runserver
```

Acesse: `http://127.0.0.1:8000`

## 📱 **Guia de Uso**

### ➕ **Cadastro de Produtos com Múltiplas Validades**
1. Acesse **Busca Avançada de Endereços**
2. Selecione um **endereço vazio**
3. Clique em **"Armazenar Produto"**
4. Digite o **código do produto**
5. **Adicione múltiplas validades** com o botão "+"
6. Defina **quantidades individuais** para cada validade
7. Sistema **cria lotes automaticamente**

### 🔄 **Movimentação FIFO**
1. Acesse **Movimentação de Estoque**
2. Digite o **código do produto**
3. Sistema mostra **localização atual**
4. Use **"Abastecer"** para Nível 2 → Nível 0
5. **FIFO automático** aplica produto mais antigo

### 📊 **Dashboard e Relatórios**
- **Painel Principal**: Visão geral por ruas/prédios
- **Detalhes do Produto**: Histórico completo por produto
- **Busca Avançada**: Filtros múltiplos e exportação
- **Alertas**: Produtos próximos ao vencimento

## 🎨 **Interface Moderna**

### 🌟 **Características Visuais**
- **Cards interativos** com hover effects
- **Cores intuitivas**: Verde (válido), Amarelo (próximo), Vermelho (vencido)
- **Ícones Font Awesome** para melhor UX
- **Animações suaves** CSS3
- **Responsivo** para mobile/desktop

### ⚡ **Interatividade**
- **AJAX** para busca em tempo real
- **JavaScript dinâmico** para campos múltiplos
- **Confirmações visuais** para ações críticas
- **Feedback instantâneo** de operações

## 🔒 **Segurança e Performance**

### 🛡️ **Segurança**
- **Autenticação obrigatória** (@login_required)
- **Tokens CSRF** em todos os formulários
- **Validações server-side** robustas
- **Sanitização** de inputs

### ⚡ **Performance**
- **Queries otimizadas** com select_related/prefetch_related
- **Paginação automática** em listas grandes
- **Índices no banco** para consultas rápidas
- **Cache** para consultas frequentes

## 📈 **Métricas e Monitoramento**

### 📊 **Dashboard Analytics**
- **Total de produtos** cadastrados
- **Taxa de ocupação** dos endereços
- **Produtos próximos** ao vencimento
- **Movimentações** do dia/semana/mês

### 🔔 **Sistema de Alertas**
- **Produtos vencidos** (vermelho)
- **Próximos ao vencimento** (amarelo)
- **Estoque baixo** (informativo)
- **Endereços lotados** (atenção)

## 🤝 **Contribuição**

### 🔄 **Processo de Contribuição**
1. **Fork** o repositório
2. Crie uma **branch** para sua feature
3. **Commit** suas alterações
4. **Push** para sua branch
5. Abra um **Pull Request**

### 📝 **Padrões de Código**
- **PEP 8** para Python
- **Docstrings** em funções complexas
- **Comentários** em lógicas de negócio
- **Testes** para novas funcionalidades

## 📞 **Suporte e Documentação**

### 📋 **Documentação Técnica**
- `GUIA_ARMAZENAR_PRODUTO_POR_CODIGO.md`
- `RELATORIO_FINAL_ENDERECAMENTO.md`
- `SOLUCAO_ENDERECOS_VAZIOS_PAINEL.md`

### 🆘 **Suporte**
- **Issues** no GitHub para bugs
- **Discussions** para dúvidas gerais
- **Wiki** para documentação extendida

## 📄 **Licença**

Este projeto está sob a **licença MIT**. Veja o arquivo `LICENSE` para detalhes.

---

## 🏆 **Estatísticas do Projeto**

- ⭐ **+40 views** implementadas
- 📊 **5 modelos** principais inter-relacionados
- 🎨 **Interface 100% responsiva**
- 🔄 **Sistema FIFO** completamente automatizado
- 📱 **Múltiplas validades** por operação
- 🚀 **Performance otimizada** para grandes volumes

**Desenvolvido com ❤️ usando Django 5.2.4 e tecnologias modernas**

*Última atualização: Janeiro 2025*
