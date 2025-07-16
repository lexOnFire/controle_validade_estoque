from django import forms
from .models import Produto, Armazenamento




class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome','codigo','validade','quantidade']


class ArmazenamentoForm(forms.ModelForm):
    class Meta:
        model = Armazenamento
        fields = ['rua', 'predio', 'nivel', 'ap']
