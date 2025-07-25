# Generated by Django 5.2.4 on 2025-07-26 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0010_estoque_data_alteracao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicomovimentacao',
            name='tipo_operacao',
            field=models.CharField(choices=[('entrada', 'Entrada'), ('saida', 'Saída'), ('transferencia', 'Transferência'), ('atualizacao_fifo', 'Atualização FIFO'), ('ajuste', 'Ajuste de Estoque'), ('vencimento', 'Remoção por Vencimento')], max_length=20),
        ),
    ]
