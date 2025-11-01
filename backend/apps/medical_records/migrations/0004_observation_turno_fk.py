from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turnos', '0002_alter_turno_unique_together_and_more'),
        ('medical_records', '0003_alter_observation_id_alter_observationattachment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='turno',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='observacion', to='turnos.turno'),
        ),
        migrations.AddIndex(
            model_name='observation',
            index=models.Index(fields=['turno'], name='medical_rec_turno_idx'),
        ),
    ]
