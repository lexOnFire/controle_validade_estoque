

from django.db import models
from datetime import date



# Modelo para múltiplas validades por estoque





class Produto(models.Model):
    codigo = models.CharField(max_length=50, unique= True)
    nome = models.CharField(max_length=100)
    validade = models.DateField()
    data_fabricacao = models.DateField()
    peso = models.CharField(max_length=50)
    lote = models.CharField(max_length=50)
    quantidade = models.PositiveIntegerField(default=1)

    def dias_para_vencer(self):
        return (self.validade - date.today()).days

    def vencidos(self):
        # Considera vencido se faltam menos de 10 dias para vencer
        return self.dias_para_vencer() < 10

    def perto_de_vencer(self):
        # Considera perto de vencer se faltam menos de 30 dias, mas não vencido
        dias = self.dias_para_vencer()
        return 10 <= dias < 30
    
    def __str__(self):
        return f"{self.nome} ({self.quantidade} unidades)"

class Armazenamento(models.Model):
    livre = models.BooleanField(default=True)
    rua = models.CharField(max_length=50)
    predio = models.CharField(max_length=50)
    nivel = models.CharField(max_length=50)
    ap = models.CharField(max_length=50)

    def __str__(self):
        return f"Rua {self.rua}, Predio {self.predio}, Nivel {self.nivel}, Apartamento {self.ap}"
    



class Estoque(models.Model):
    produto = models.ForeignKey(Produto,on_delete=models.CASCADE)
    local = models.ForeignKey(Armazenamento, on_delete=models.CASCADE)
    data_armazenado = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.produto.nome} em {self.local} desde {self.data_armazenado}"


# Modelo para múltiplas validades por estoque
class ValidadeEstoque(models.Model):
    estoque = models.ForeignKey('Estoque', on_delete=models.CASCADE, related_name='validades')
    validade = models.DateField()
    def __str__(self):
        return f"Validade: {self.validade.strftime('%d/%m/%Y')}"