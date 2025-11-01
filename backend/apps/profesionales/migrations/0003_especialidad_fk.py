from django.db import migrations, models
import django.db.models.deletion


def forward_copy_especialidad(apps, schema_editor):
    Profesional = apps.get_model('profesionales', 'Profesional')
    Especialidad = apps.get_model('profesionales', 'Especialidad')
    # Crear especialidades por cada valor textual existente
    seen = {}
    for p in Profesional.objects.all().only('id', 'especialidad'):
        nombre = (p.especialidad or '').strip()
        if not nombre:
            continue
        if nombre not in seen:
            obj, _ = Especialidad.objects.get_or_create(nombre=nombre)
            seen[nombre] = obj.id
        # asignar fk temporal
        Profesional.objects.filter(id=p.id).update(especialidad_fk_id=seen[nombre])


class Migration(migrations.Migration):

    dependencies = [
        ('profesionales', '0002_profesional_centros_profesionalhorario'),
    ]

    operations = [
        # 1) Crear tabla de especialidades
        migrations.CreateModel(
            name='Especialidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={'ordering': ['nombre']},
        ),
        # 2) Agregar columna temporal FK
        migrations.AddField(
            model_name='profesional',
            name='especialidad_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='profesionales.especialidad'),
        ),
        # 3) Migrar datos texto -> FK
        migrations.RunPython(forward_copy_especialidad, migrations.RunPython.noop),
        # 4) Eliminar columna vieja de texto
        migrations.RemoveField(
            model_name='profesional',
            name='especialidad',
        ),
        # 5) Renombrar columna temporal a nombre definitivo
        migrations.RenameField(
            model_name='profesional',
            old_name='especialidad_fk',
            new_name='especialidad',
        ),
    ]
