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
               path('cadastrar-endereco/', views.cadastrar_enderecos, name='cadastrar_enderecos'),]