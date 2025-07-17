from django.test import TestCase


from django.urls import reverse
from django.test import TestCase, Client
from .models import Produto, Armazenamento, Estoque
from django.contrib.auth.models import User
from datetime import date, timedelta

class ProdutoModelTest(TestCase):
    def test_criacao_produto(self):
        produto = Produto.objects.create(
            codigo='123', nome='Teste', validade=date.today()+timedelta(days=10),
            data_fabricacao=date.today(), peso='1kg', lote='A1', quantidade=5
        )
        self.assertEqual(str(produto), 'Teste (5 unidades)')
        self.assertFalse(produto.vencidos())

class ArmazenamentoModelTest(TestCase):
    def test_criacao_endereco(self):
        armaz = Armazenamento.objects.create(rua='A', predio='1', nivel='2', ap='3')
        self.assertTrue(armaz.livre)
        self.assertIn('Rua A', str(armaz))

class EstoqueModelTest(TestCase):
    def test_criacao_estoque(self):
        produto = Produto.objects.create(
            codigo='123', nome='Teste', validade=date.today()+timedelta(days=10),
            data_fabricacao=date.today(), peso='1kg', lote='A1', quantidade=5
        )
        armaz = Armazenamento.objects.create(rua='A', predio='1', nivel='2', ap='3')
        estoque = Estoque.objects.create(produto=produto, local=armaz)
        self.assertIn('Teste', str(estoque))

class PainelViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()

    def test_painel_login_required(self):
        response = self.client.get(reverse('painel'))
        self.assertEqual(response.status_code, 302)  # redirect to login
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('painel'))
        self.assertEqual(response.status_code, 200)
