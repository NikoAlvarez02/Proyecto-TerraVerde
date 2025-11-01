from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0006_rename_usuarios_lo_username_9dce2a_idx_usuarios_lo_usernam_c124b0_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='foto',
            field=models.ImageField(upload_to='usuarios/avatars/', null=True, blank=True),
        ),
    ]