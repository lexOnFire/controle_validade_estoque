from django.db import models
from datetime import date



class Produto(models.Model):
    codigo = models.CharField(max_length=50, unique= True)
    nome = models.CharField(max_length=100)
    validade = models.DateField()
    data_fabricacao = models.DateField()
    peso = models.CharField(max_length=50)
    lote = models.CharField(max_length=50)
    quantidade = models.PositiveIntegerField(default=1)

    def vencidos(self):
        return date.today() > self.validade
    
    def dias_para_vencer(self):
        return (self.validade - date.today()).days
    
    def __str__(self):
        return f"{self.nome} ({self.quantidade} unidades)"

class Armazenamento(models.Model):
    livre = models.BooleanField(default=True)
    rua = models.CharField(max_length=50)
    predio = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    ap = models.CharField(max_length=50)

    def __str__(self):
        return f"Livre {self.livre}, Rua: {self.rua}, Predio {self.predio}, Nivel {self.nivel}, Apartamento {self.ap}"
    


class Estoque(models.Model):
    produto = models.ForeignKey(Produto,on_delete=models.CASCADE)
    local = models.ForeignKey(Armazenamento, on_delete=models.CASCADE)
    data_armazenado = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.produto.nome} em {self.local} desde {self.data_armazenado}"   