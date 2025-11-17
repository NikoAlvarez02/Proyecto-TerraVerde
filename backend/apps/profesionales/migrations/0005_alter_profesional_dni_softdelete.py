from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profesionales', '0004_alter_profesional_especialidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profesional',
            name='dni',
            field=models.CharField(max_length=10, verbose_name='DNI'),
        ),
    ]
