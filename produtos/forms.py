from django import forms
from .models import Produto, Armazenamento




class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = '__all__'

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        if Produto.objects.filter(codigo=codigo).exists():
            raise forms.ValidationError("Já existe um produto com esse código.")
        return codigo

class ArmazenamentoForm(forms.ModelForm):
    class Meta:
        model = Armazenamento
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if Armazenamento.objects.filter(
            rua=cleaned_data.get('rua'),
            predio=cleaned_data.get('predio'),
            nivel=cleaned_data.get('nivel'),
            ap=cleaned_data.get('ap')
        ).exists():
            raise forms.ValidationError("Endereço já cadastrado.")
        return cleaned_data