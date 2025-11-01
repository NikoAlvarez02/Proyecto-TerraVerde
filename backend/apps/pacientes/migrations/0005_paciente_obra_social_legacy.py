from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0004_paciente_profesionales_asignados'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='obra_social_legacy',
            field=models.CharField(max_length=50, blank=True, default='', editable=False),
        ),
    ]
