from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('obras', '0001_initial'),
        ('pacientes', '0005_paciente_obra_social_legacy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paciente',
            name='obra_social',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='pacientes',
                to='obras.obrasocial',
            ),
        ),
    ]
