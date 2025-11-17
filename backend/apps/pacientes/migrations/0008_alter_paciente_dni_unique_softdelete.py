from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0007_paciente_nacionalidad_representante'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paciente',
            name='dni',
            field=models.CharField(max_length=10, verbose_name='DNI'),
        ),
    ]
