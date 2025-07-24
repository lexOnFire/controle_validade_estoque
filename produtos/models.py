from django.db import models
from datetime import date, timedelta

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, unique=True)
    peso = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

class Lote(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='lotes')
    validade = models.DateField()
    quantidade = models.PositiveIntegerField(default=1)
    data_fabricacao = models.DateField(null=True, blank=True)
    numero_lote = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('produto', 'validade', 'numero_lote')

    def __str__(self):
        return f"Lote {self.numero_lote or ''} - {self.produto.nome} - Validade: {self.validade}"

class Armazenamento(models.Model):
    rua = models.CharField(max_length=50)
    predio = models.CharField(max_length=50)
    nivel = models.CharField(max_length=10)
    ap = models.CharField(max_length=10)
    livre = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.rua} - {self.predio} - {self.nivel} - {self.ap}"

class Estoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    local = models.ForeignKey(Armazenamento, on_delete=models.CASCADE)
    data_armazenado = models.DateField()
    
    def __str__(self):
        return f"{self.produto.nome} em {self.local}"