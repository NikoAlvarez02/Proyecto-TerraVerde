from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('centers', '0003_alter_center_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(unique=True)),
                ('nombre', models.CharField(max_length=120)),
                ('laborable', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Feriado',
                'verbose_name_plural': 'Feriados',
                'ordering': ['fecha'],
            },
        ),
        migrations.AddIndex(
            model_name='holiday',
            index=models.Index(fields=['fecha'], name='centers_hol_fecha_idx'),
        ),
    ]
