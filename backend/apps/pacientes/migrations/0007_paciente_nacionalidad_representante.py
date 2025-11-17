from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0006_alter_paciente_obra_social_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='nacionalidad',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='paciente',
            name='rep_apellido',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='paciente',
            name='rep_edad',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='paciente',
            name='rep_nombre',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='paciente',
            name='rep_nacionalidad',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='paciente',
            name='rep_telefono',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='paciente',
            name='tiene_representante',
            field=models.BooleanField(default=False),
        ),
    ]
