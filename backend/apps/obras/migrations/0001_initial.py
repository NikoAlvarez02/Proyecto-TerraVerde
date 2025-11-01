from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ObraSocial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('codigo', models.CharField(blank=True, max_length=20)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={'ordering': ['nombre']},
        ),
        migrations.CreateModel(
            name='PlanObraSocial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('codigo', models.CharField(blank=True, max_length=20)),
                ('activo', models.BooleanField(default=True)),
                ('obra_social', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='planes', to='obras.obrasocial')),
            ],
            options={'ordering': ['obra_social', 'nombre']},
        ),
        migrations.AlterUniqueTogether(name='planobrasocial', unique_together={('obra_social', 'nombre')}),
    ]

