from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'

    def ready(self):
        try:
            from . import audit_signals  # noqa: F401
        except Exception:
            pass
