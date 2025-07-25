from django.db import models
from datetime import date, timedelta
from django.db.models import Count, Min
from django.core.exceptions import ValidationError
import re

def validar_nome_produto(value):
    """Validador para garantir que o nome do produto não seja apenas numérico"""
    if value.strip().isdigit():
        raise ValidationError('O nome do produto não pode ser apenas números.')
    if len(value.strip()) < 2:
        raise ValidationError('O nome do produto deve ter pelo menos 2 caracteres.')
    if not re.match(r'^[a-zA-ZÀ-ÿ\s\d\.\-\_\(\)]+$', value.strip()):
        raise ValidationError('O nome do produto contém caracteres inválidos.')

class Produto(models.Model):
    nome = models.CharField(max_length=100, validators=[validar_nome_produto])
    codigo = models.CharField(max_length=50, unique=True)
    peso = models.CharField(max_length=50)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    fornecedor = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"
    
    def proxima_validade(self):
        """Retorna a próxima data de validade do produto"""
        lote = self.lotes.order_by('validade').first()
        return lote.validade if lote else None
    
    def esta_vencido(self):
        """Verifica se o produto está vencido"""
        proxima = self.proxima_validade()
        return proxima and proxima <= date.today()
    
    def dias_ate_vencimento(self):
        """Retorna quantos dias até o vencimento"""
        proxima = self.proxima_validade()
        if proxima:
            return (proxima - date.today()).days
        return None
    
    @classmethod
    def estatisticas(cls):
        """Retorna estatísticas gerais dos produtos"""
        today = date.today()
        hoje_mais_30 = today + timedelta(days=30)
        
        total_produtos = cls.objects.count()
        produtos_com_estoque = cls.objects.filter(estoque__isnull=False).distinct().count()
        
        # Produtos vencidos
        vencidos = 0
        proximos_vencimento = 0
        
        for produto in cls.objects.all():
            proxima_validade = produto.proxima_validade()
            if proxima_validade:
                if proxima_validade <= today:
                    vencidos += 1
                elif proxima_validade <= hoje_mais_30:
                    proximos_vencimento += 1
        
        return {
            'total_produtos': total_produtos,
            'produtos_com_estoque': produtos_com_estoque,
            'produtos_vencidos': vencidos,
            'proximos_vencimento': proximos_vencimento,
            'produtos_sem_estoque': total_produtos - produtos_com_estoque,
        }

class Lote(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='lotes')
    validade = models.DateField()
    quantidade = models.PositiveIntegerField(default=1)
    data_fabricacao = models.DateField(null=True, blank=True)
    numero_lote = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = ('produto', 'validade', 'numero_lote')
        ordering = ['validade']

    def __str__(self):
        return f"Lote {self.numero_lote or ''} - {self.produto.nome} - Validade: {self.validade}"
    
    def dias_para_vencer(self):
        """Retorna quantos dias faltam para vencer"""
        return (self.validade - date.today()).days
    
    def status_validade(self):
        """Retorna o status da validade"""
        dias = self.dias_para_vencer()
        if dias < 0:
            return 'vencido'
        elif dias <= 30:
            return 'proximo_vencimento'
        else:
            return 'valido'

class Armazenamento(models.Model):
    CATEGORIA_CHOICES = [
        ('inteiro', 'Palete Fechado (Nível 2)'),
        ('meio', 'Saída (Nível 0)'),
    ]
    categoria_armazenamento = models.CharField(max_length=10, choices=CATEGORIA_CHOICES, default='inteiro')
    rua = models.CharField(max_length=50)
    predio = models.CharField(max_length=50)
    nivel = models.CharField(max_length=10)
    ap = models.CharField(max_length=10)
    livre = models.BooleanField(default=True)
    capacidade_maxima = models.PositiveIntegerField(default=1)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['predio', 'rua', 'nivel', 'ap']

    def clean(self):
        """Validação customizada para endereços"""
        super().clean()
        
        # Regra: Nível 0 deve sempre ser 'meio' (área de saída)
        if str(self.nivel) == '0' and self.categoria_armazenamento != 'meio':
            raise ValidationError({
                'categoria_armazenamento': 'Endereços no nível 0 devem ser do tipo "meio" (área de saída).'
            })
    
    def save(self, *args, **kwargs):
        """Auto-correção: força nível 0 como 'meio'"""
        # Garantir que nível 0 seja sempre 'meio'
        if str(self.nivel) == '0':
            self.categoria_armazenamento = 'meio'
        
        # Executar validação antes de salvar
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rua} - {self.predio} - {self.nivel} - {self.ap}"
    
    def ocupacao_atual(self):
        """Retorna quantos produtos estão armazenados neste local"""
        return self.estoque_set.count()
    
    def taxa_ocupacao(self):
        """Retorna a taxa de ocupação em percentual"""
        if self.capacidade_maxima > 0:
            return (self.ocupacao_atual() / self.capacidade_maxima) * 100
        return 0

class Estoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    local = models.ForeignKey(Armazenamento, on_delete=models.CASCADE)
    data_armazenado = models.DateField()
    usuario_responsavel = models.CharField(max_length=100, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-data_armazenado']
    
    def __str__(self):
        return f"{self.produto.nome} em {self.local}"

# Modelo para histórico de movimentações
class HistoricoMovimentacao(models.Model):
    TIPOS_OPERACAO = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('transferencia', 'Transferência'),
        ('ajuste', 'Ajuste de Estoque'),
        ('vencimento', 'Remoção por Vencimento'),
    ]
    
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    local_origem = models.ForeignKey(Armazenamento, on_delete=models.CASCADE, related_name='movimentacoes_origem', null=True, blank=True)
    local_destino = models.ForeignKey(Armazenamento, on_delete=models.CASCADE, related_name='movimentacoes_destino', null=True, blank=True)
    tipo_operacao = models.CharField(max_length=20, choices=TIPOS_OPERACAO)
    quantidade = models.PositiveIntegerField(default=1)
    data_operacao = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=100, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-data_operacao']
    
    def __str__(self):
        return f"{self.tipo_operacao} - {self.produto.nome} - {self.data_operacao.strftime('%d/%m/%Y %H:%M')}"

# Modelo para alertas e notificações
class Alerta(models.Model):
    TIPOS_ALERTA = [
        ('vencimento', 'Produto Próximo ao Vencimento'),
        ('vencido', 'Produto Vencido'),
        ('estoque_baixo', 'Estoque Baixo'),
        ('local_lotado', 'Local de Armazenamento Lotado'),
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('lido', 'Lido'),
        ('resolvido', 'Resolvido'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPOS_ALERTA)
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=True, blank=True)
    local = models.ForeignKey(Armazenamento, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ativo')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_leitura = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titulo}"