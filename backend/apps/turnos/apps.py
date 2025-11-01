from django.apps import AppConfig


class TurnosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.turnos'

    def ready(self):
        # Importar señales
        from . import signals  # noqa: F401
