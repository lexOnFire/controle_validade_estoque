from django.core.management.base import BaseCommand
from django.db import transaction
from produtos.models import Produto, Estoque, Lote
import re

class Command(BaseCommand):
    help = 'Remove produtos com nomes apenas numéricos e valida dados de produtos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra quais produtos seriam removidos, sem remover',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Remove produtos mesmo se tiverem estoque ou lotes',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔍 Analisando produtos cadastrados...\n')
        
        # Buscar produtos com nomes problemáticos
        produtos_numericos = []
        produtos_invalidos = []
        
        for produto in Produto.objects.all():
            nome = produto.nome.strip()
            
            # Verificar se o nome é apenas números
            if re.match(r'^\d+$', nome):
                produtos_numericos.append(produto)
            
            # Verificar outros padrões inválidos
            elif len(nome) < 2:
                produtos_invalidos.append(produto)
            elif re.match(r'^[^\w\s]+$', nome):  # Apenas símbolos
                produtos_invalidos.append(produto)
            elif nome.lower() in ['null', 'nan', 'none', '', '-', 'undefined']:
                produtos_invalidos.append(produto)
        
        total_problematicos = len(produtos_numericos) + len(produtos_invalidos)
        
        if total_problematicos == 0:
            self.stdout.write(self.style.SUCCESS('✅ Nenhum produto problemático encontrado!'))
            return
        
        self.stdout.write(f'📊 Produtos problemáticos encontrados: {total_problematicos}')
        self.stdout.write(f'   - Nomes apenas numéricos: {len(produtos_numericos)}')
        self.stdout.write(f'   - Nomes inválidos: {len(produtos_invalidos)}')
        self.stdout.write('')
        
        # Mostrar detalhes dos produtos problemáticos
        if produtos_numericos:
            self.stdout.write('🔢 Produtos com nomes apenas numéricos:')
            for produto in produtos_numericos:
                tem_estoque = Estoque.objects.filter(produto=produto).exists()
                tem_lotes = Lote.objects.filter(produto=produto).exists()
                status = []
                if tem_estoque:
                    status.append('ESTOQUE')
                if tem_lotes:
                    status.append('LOTES')
                status_str = f" [{', '.join(status)}]" if status else " [SEM DEPENDÊNCIAS]"
                
                self.stdout.write(f'   - ID {produto.id}: "{produto.nome}" (Código: {produto.codigo}){status_str}')
        
        if produtos_invalidos:
            self.stdout.write('\n❌ Produtos com nomes inválidos:')
            for produto in produtos_invalidos:
                tem_estoque = Estoque.objects.filter(produto=produto).exists()
                tem_lotes = Lote.objects.filter(produto=produto).exists()
                status = []
                if tem_estoque:
                    status.append('ESTOQUE')
                if tem_lotes:
                    status.append('LOTES')
                status_str = f" [{', '.join(status)}]" if status else " [SEM DEPENDÊNCIAS]"
                
                self.stdout.write(f'   - ID {produto.id}: "{produto.nome}" (Código: {produto.codigo}){status_str}')
        
        if options['dry_run']:
            self.stdout.write('\n🔍 Modo DRY-RUN ativo - nenhum produto será removido.')
            return
        
        # Confirmar remoção
        self.stdout.write('\n⚠️  ATENÇÃO: Esta operação irá REMOVER permanentemente os produtos problemáticos!')
        self.stdout.write('❌ Produtos com estoque/lotes NÃO serão removidos (use --force para forçar)')
        
        confirm = input('\nDigite "CONFIRMAR" para prosseguir com a remoção: ')
        if confirm != 'CONFIRMAR':
            self.stdout.write('❌ Operação cancelada.')
            return
        
        # Remover produtos
        removidos = 0
        pulados = 0
        
        with transaction.atomic():
            todos_problematicos = produtos_numericos + produtos_invalidos
            
            for produto in todos_problematicos:
                tem_estoque = Estoque.objects.filter(produto=produto).exists()
                tem_lotes = Lote.objects.filter(produto=produto).exists()
                
                if (tem_estoque or tem_lotes) and not options['force']:
                    self.stdout.write(f'⏭️  Pulando produto "{produto.nome}" (ID {produto.id}) - possui dependências')
                    pulados += 1
                    continue
                
                try:
                    # Se --force, remover dependências primeiro
                    if options['force']:
                        if tem_estoque:
                            Estoque.objects.filter(produto=produto).delete()
                        if tem_lotes:
                            Lote.objects.filter(produto=produto).delete()
                    
                    nome_produto = produto.nome
                    codigo_produto = produto.codigo
                    produto.delete()
                    
                    self.stdout.write(f'🗑️  Removido: "{nome_produto}" (Código: {codigo_produto})')
                    removidos += 1
                    
                except Exception as e:
                    self.stdout.write(f'❌ Erro ao remover produto "{produto.nome}": {str(e)}')
        
        # Resumo final
        self.stdout.write('\n📊 RESUMO DA OPERAÇÃO:')
        self.stdout.write(f'   ✅ Produtos removidos: {removidos}')
        self.stdout.write(f'   ⏭️  Produtos pulados: {pulados}')
        
        if removidos > 0:
            self.stdout.write(self.style.SUCCESS(f'\n🎉 Limpeza concluída! {removidos} produtos problemáticos foram removidos.'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠️  Nenhum produto foi removido.'))
        
        # Verificar se ainda há produtos problemáticos
        produtos_restantes = 0
        for produto in Produto.objects.all():
            nome = produto.nome.strip()
            if (re.match(r'^\d+$', nome) or 
                len(nome) < 2 or 
                re.match(r'^[^\w\s]+$', nome) or 
                nome.lower() in ['null', 'nan', 'none', '', '-', 'undefined']):
                produtos_restantes += 1
        
        if produtos_restantes > 0:
            self.stdout.write(f'\n⚠️  Ainda restam {produtos_restantes} produtos problemáticos (provavelmente com dependências)')
            self.stdout.write('   Use --force para remover produtos com estoque/lotes')
        else:
            self.stdout.write(self.style.SUCCESS('\n✨ Todos os produtos problemáticos foram removidos!'))
