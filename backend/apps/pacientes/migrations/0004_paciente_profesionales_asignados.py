from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profesionales', '0003_especialidad_fk'),
        ('pacientes', '0003_paciente_obra_social_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='profesionales_asignados',
            field=models.ManyToManyField(blank=True, related_name='pacientes_asignados', to='profesionales.profesional'),
        ),
    ]
