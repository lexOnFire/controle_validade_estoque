from django import forms
from .models import Produto, Armazenamento
from django.core.exceptions import ValidationError

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'codigo', 'peso', 'categoria', 'fornecedor']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto (não pode ser apenas números)'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código único'}),
            'peso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Peso/Medida'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoria (opcional)'}),
            'fornecedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fornecedor (opcional)'}),
        }

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if nome.strip().isdigit():
            raise ValidationError('O nome do produto não pode ser apenas números.')
        if len(nome.strip()) < 2:
            raise ValidationError('O nome do produto deve ter pelo menos 2 caracteres.')
        return nome.strip()

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        if self.instance.pk:
            # Verifica se já existe outro produto com o mesmo código (exceto o atual)
            if Produto.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Já existe um produto com esse código.")
        else:
            # Novo produto
            if Produto.objects.filter(codigo=codigo).exists():
                raise forms.ValidationError("Já existe um produto com esse código.")
        return codigo

class ArmazenamentoForm(forms.ModelForm):
    class Meta:
        model = Armazenamento
        fields = ['categoria_armazenamento', 'rua', 'predio', 'nivel', 'ap', 'capacidade_maxima', 'observacoes']
        widgets = {
            'categoria_armazenamento': forms.Select(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da rua'}),
            'predio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome/Número do prédio'}),
            'nivel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Andar/Nível'}),
            'ap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartamento/Sala'}),
            'capacidade_maxima': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Capacidade máxima', 'min': '1'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações (opcional)'}),
        }
        labels = {
            'categoria_armazenamento': 'Tipo de Armazenamento',
            'rua': 'Rua',
            'predio': 'Prédio',
            'nivel': 'Nível',
            'ap': 'Apartamento',
            'capacidade_maxima': 'Capacidade Máxima',
            'observacoes': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Autocomplete para todos os campos de endereçamento
        ruas = list(Armazenamento.objects.values_list('rua', flat=True).distinct().order_by('rua'))
        predios = list(Armazenamento.objects.values_list('predio', flat=True).distinct().order_by('predio'))
        niveis = list(Armazenamento.objects.values_list('nivel', flat=True).distinct().order_by('nivel'))
        aps = list(Armazenamento.objects.values_list('ap', flat=True).distinct().order_by('ap'))

        # Adiciona atributos para datalist (autocomplete)
        if ruas:
            self.fields['rua'].widget.attrs['list'] = 'ruas-list'
        if predios:
            self.fields['predio'].widget.attrs['list'] = 'predios-list'
        if niveis:
            self.fields['nivel'].widget.attrs['list'] = 'niveis-list'
        if aps:
            self.fields['ap'].widget.attrs['list'] = 'aps-list'
        
        # Armazena as listas para uso no template
        self.ruas = ruas
        self.predios = predios
        self.niveis = niveis
        self.aps = aps

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
        rua = cleaned_data.get('rua')
        predio = cleaned_data.get('predio')
        nivel = cleaned_data.get('nivel')
        ap = cleaned_data.get('ap')
        
        # Verifica duplicatas apenas se não for uma edição do mesmo registro
        if rua and predio and nivel and ap:
            existing = Armazenamento.objects.filter(
                rua=rua,
                predio=predio,
                nivel=nivel,
                ap=ap
            )
            
            # Se estamos editando, exclui o próprio registro da verificação
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError("Endereço já cadastrado.")
        
        return cleaned_data