from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profesionales', '0003_especialidad_fk'),
        ('usuarios', '0002_perfil_puede_admin_centros_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='profesional',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='perfiles', to='profesionales.profesional'),
        ),
    ]
