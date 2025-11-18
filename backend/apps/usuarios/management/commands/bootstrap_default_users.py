from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.usuarios.models import Perfil`nfrom apps.profesionales.models import Profesional


class Command(BaseCommand):
    help = "Crea usuarios estándar (Administrador, Recepcionista, Profesional) con permisos preconfigurados."

    def add_arguments(self, parser):
        parser.add_argument('--password', dest='password', default=None,
                            help='Password a aplicar a los 3 usuarios. Si no se indica, se usa un valor por defecto.')

    def handle(self, *args, **options):
        User = get_user_model()
        default_password = options.get('password') or 'TerraVerde123!'

        presets = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'TerraVerde',
                'is_staff': True,
                'is_superuser': True,
                'rol': 'admin',
            },
            {
                'username': 'recepcion',
                'email': 'recepcion@example.com',
                'first_name': 'Recepcion',
                'last_name': 'TerraVerde',
                'is_staff': False,
                'is_superuser': False,
                'rol': 'recep',
            },
            {
                'username': 'profesional',
                'email': 'profesional@example.com',
                'first_name': 'Profesional',
                'last_name': 'TerraVerde',
                'is_staff': False,
                'is_superuser': False,
                'rol': 'prof',
            },
        ]

        for p in presets:
            user, created = User.objects.get_or_create(
                username=p['username'],
                defaults={
                    'email': p['email'],
                    'first_name': p['first_name'],
                    'last_name': p['last_name'],
                    'is_staff': p['is_staff'],
                    'is_superuser': p['is_superuser'],
                    'is_active': True,
                },
            )
            if created:
                user.set_password(default_password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Usuario creado: {user.username}"))
            else:
                self.stdout.write(f"Usuario existente: {user.username}")

            perfil, _ = Perfil.objects.get_or_create(user=user)
            perfil.rol = p['rol']\n            if p['rol'] == 'prof':\n                try:\n                    prof_obj, _ = Profesional.objects.get_or_create(\n                        dni='99999999',\n                        defaults={\n                            'nombre': user.first_name or 'Profesional',\n                            'apellido': user.last_name or 'Demo',\n                            'matricula': 'DEMO',\n                            'email': user.email or 'profesional@example.com',\n                        }\n                    )\n                    perfil.profesional = prof_obj\n                except Exception:\n                    pass\n            perfil.asignar_permisos_por_rol()\n            perfil.save()
            self.stdout.write(f" - Rol '{perfil.get_rol_display()}' aplicado con permisos por defecto")

        self.stdout.write(self.style.WARNING("Recuerda cambiar las contraseñas iniciales."))



