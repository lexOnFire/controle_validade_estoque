from django.urls import path
from . import views
from .views import cadastrar_produto

urlpatterns = [path('buscar/',views.buscar_produto,name='buscar_produto'),
               path('perguntar/<int:produto_id>/',views.perguntar_armazenar,name='perguntar_armazenar'),
               path('armazenar/<int:produto_id>/',views.armazenar_produto,name='armazenar_produto'),
               path('relatorio/',views.relatorio_estoque,name='relatorio_estoque'),           
               path('painel/',views.painel, name='painel'),
               path('remover/<int:estoque_id>/',views.remover_produto,name='remover_produto'),
               path('cadastrar_produto/',cadastrar_produto,name='cadastrar_produto'),
               path('cadastrar-endereco/', views.cadastrar_enderecos, name='cadastrar_enderecos'),
               path('editar-endereco/<int:endereco_id>/', views.editar_endereco, name='editar_endereco'),
               path('exportar-estoque/', views.exportar_estoque_csv, name='exportar_estoque'),
               path('armazenar/', views.armazenar_produto, name='armazenar_produto'),
               path('armazenar/<int:produto_id>/', views.armazenar_produto, name='armazenar_produto'),
               path('relatorio_completo/', views.relatorio_completo, name='relatorio_completo'),
               path('editar_lote/<int:lote_id>/', views.editar_lote, name='editar_lote'),
               ]