from django.test import TestCase
from .models import Produto, Lote, Estoque, Armazenamento
from datetime import date

class ProdutoTestCase(TestCase):
    def setUp(self):
        self.produto = Produto.objects.create(
            nome="Produto Teste",
            codigo="123",
            peso="1kg"
        )

    def test_criar_produto(self):
        self.assertEqual(Produto.objects.count(), 1)
        self.assertEqual(self.produto.nome, "Produto Teste")

class EstoqueTestCase(TestCase):
    def setUp(self):
        self.produto = Produto.objects.create(
            nome="Produto Estoque",
            codigo="456",
            peso="2kg"
        )
        self.lote = Lote.objects.create(
            produto=self.produto,
            validade=date.today(),
            numero_lote="L001"
        )
        self.local = Armazenamento.objects.create(
            rua="A",
            predio="1",
            nivel="1",
            ap="101",
            livre=True
        )
        self.estoque = Estoque.objects.create(
            lote=self.lote,
            local=self.local,
            data_armazenado=date.today()
        )

    def test_criar_estoque(self):
        self.assertEqual(Estoque.objects.count(), 1)
        self.assertEqual(self.estoque.lote.produto.nome, "Produto Estoque")

