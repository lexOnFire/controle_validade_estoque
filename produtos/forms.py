from django import forms
from .models import Produto, Armazenamento




class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome','codigo','peso']

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        if Produto.objects.filter(codigo=codigo).exists():
            raise forms.ValidationError("Já existe um produto com esse código.")
        return codigo

class ArmazenamentoForm(forms.ModelForm):
    class Meta:
        model = Armazenamento
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Autocomplete para todos os campos de endereçamento
        ruas = Armazenamento.objects.values_list('rua', flat=True).distinct()
        predios = Armazenamento.objects.values_list('predio', flat=True).distinct()
        niveis = Armazenamento.objects.values_list('nivel', flat=True).distinct()
        aps = Armazenamento.objects.values_list('ap', flat=True).distinct()

        self.fields['rua'].widget.attrs.update({
            'list': 'ruas-list',
            'autocomplete': 'on',
        })
        self.fields['predio'].widget.attrs.update({
            'list': 'predios-list',
            'autocomplete': 'on',
        })
        self.fields['nivel'].widget.attrs.update({
            'list': 'niveis-list',
            'autocomplete': 'on',
        })
        self.fields['ap'].widget.attrs.update({
            'list': 'aps-list',
            'autocomplete': 'on',
        })

        self.ruas_choices = ruas
        self.predios_choices = predios
        self.niveis_choices = niveis
        self.aps_choices = aps

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