from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0004_perfil_email_recuperacion"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoginThrottle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(db_index=True, max_length=150)),
                ("ip", models.GenericIPAddressField(blank=True, null=True, db_index=True)),
                ("count", models.PositiveIntegerField(default=0)),
                ("first_attempt", models.DateTimeField(default=django.utils.timezone.now)),
                ("last_attempt", models.DateTimeField(default=django.utils.timezone.now)),
                ("locked_until", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["username", "ip"], name="usuarios_lo_username_9dce2a_idx"),
                    models.Index(fields=["locked_until"], name="usuarios_lo_locked__9f9f41_idx"),
                ],
            },
        ),
    ]
