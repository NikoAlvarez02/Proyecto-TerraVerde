from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('obras', '0001_initial'),
        ('pacientes', '0002_paciente_alergias_paciente_antecedentes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='obra_social',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pacientes', to='obras.obrasocial'),
        ),
        migrations.AddField(
            model_name='paciente',
            name='plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pacientes', to='obras.planobrasocial'),
        ),
    ]
