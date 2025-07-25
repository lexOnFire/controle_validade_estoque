from django.contrib import admin
from .models import Produto, Estoque, Armazenamento


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'codigo', 'peso')
    search_fields = ('nome', 'codigo')


@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ('id', 'produto', 'local', 'data_armazenado')
    list_filter = ('produto', 'local')
    search_fields = ('produto__nome', 'produto__codigo')


@admin.register(Armazenamento)
class ArmazenamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'rua', 'predio', 'nivel', 'ap', 'livre')
    list_filter = ('livre',)