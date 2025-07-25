from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('produtos', '0004_remove_produto_validade2_remove_produto_validade3'),
    ]

    operations = [
        migrations.AddField(
            model_name='armazenamento',
            name='categoria_armazenamento',
            field=models.CharField(
                max_length=10,
                choices=[('inteiro', 'Palete Fechado (Nível 2)'), ('meio', 'Saída (Nível 0)')],
                default='inteiro',
            ),
        ),
    ]
