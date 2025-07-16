from django.contrib import admin
from .models import Produto, Armazenamento,Estoque


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['codigo','nome', 'validade','quantidade','vencidos','dias_para_vencer' ]
    list_filter = ['validade']
    search_fields = ['nome']
@admin.register(Armazenamento)
class ArmazenamentoAdmin(admin.ModelAdmin):
    list_display = ['livre','rua','predio','nivel','ap']
    list_filter = ['livre','rua','predio','nivel','ap']
    search_fields = ['livre']
@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ['produto','local']
    list_filter= ['produto', 'local']
    search_fields = ['local']