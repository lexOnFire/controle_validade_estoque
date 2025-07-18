from django import forms
from .models import Produto, Armazenamento




class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome','codigo','validade','quantidade','data_fabricacao','peso','lote']

    def clean_validade(self):
        validade = self.cleaned_data['validade']
        from datetime import date
        if validade < date.today():
            raise forms.ValidationError('A data de validade não pode ser no passado.')
        return validade

    def clean_quantidade(self):
        quantidade = self.cleaned_data['quantidade']
        if quantidade < 1:
            raise forms.ValidationError('A quantidade deve ser maior que zero.')
        return quantidade


class ArmazenamentoForm(forms.ModelForm):
    class Meta:
        model = Armazenamento
        fields = ['rua', 'predio', 'nivel', 'ap']

    def clean(self):
        cleaned_data = super().clean()
        for field in ['rua', 'predio', 'nivel', 'ap']:
            if not cleaned_data.get(field):
                self.add_error(field, 'Este campo é obrigatório.')
        return cleaned_data
