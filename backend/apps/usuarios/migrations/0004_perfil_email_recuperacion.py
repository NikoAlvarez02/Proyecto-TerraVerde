from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0003_perfil_profesional_fk"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfil",
            name="email_recuperacion",
            field=models.EmailField(null=True, blank=True, max_length=254, verbose_name="Email de recuperacion"),
        ),
    ]
