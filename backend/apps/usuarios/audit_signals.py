import sys
from django.db import connection
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from .models import AuditoriaLog


def _model_label(instance):
    ct = ContentType.objects.get_for_model(instance.__class__)
    return ct.app_label, ct.model


def _table_exists(table_name: str) -> bool:
    # Compatible con distintas versiones de Django (uso explícito de cursor)
    try:
        with connection.cursor() as cursor:
            return table_name in connection.introspection.table_names(cursor)
    except Exception:
        return False


@receiver(post_save, dispatch_uid="usuarios_audit_post_save")
def log_post_save(sender, instance, created, **kwargs):
    # Evitar recursión, sesiones y comandos de gestión/migraciones
    if (
        sender is AuditoriaLog
        or sender._meta.app_label in ("sessions",)
        or any(cmd in sys.argv for cmd in ("migrate", "makemigrations", "collectstatic", "loaddata", "flush", "test"))
    ):
        return

    # Evitar si la tabla aún no existe
    if not _table_exists(AuditoriaLog._meta.db_table):
        return

    try:
        app_label, model = _model_label(instance)
        accion = 'create' if created else 'update'
        AuditoriaLog.objects.create(
            usuario=None,  # request no disponible aquí
            accion=accion,
            app_label=app_label,
            modelo=model,
            objeto_id=str(getattr(instance, 'pk', '')),
            detalle=f"{model} {accion}"
        )
    except Exception:
        # No interrumpir el flujo principal ante errores de auditoría
        pass


@receiver(post_delete, dispatch_uid="usuarios_audit_post_delete")
def log_post_delete(sender, instance, **kwargs):
    if (
        sender is AuditoriaLog
        or sender._meta.app_label in ("sessions",)
        or any(cmd in sys.argv for cmd in ("migrate", "makemigrations", "collectstatic", "loaddata", "flush", "test"))
    ):
        return

    if not _table_exists(AuditoriaLog._meta.db_table):
        return

    try:
        app_label, model = _model_label(instance)
        AuditoriaLog.objects.create(
            usuario=None,
            accion='delete',
            app_label=app_label,
            modelo=model,
            objeto_id=str(getattr(instance, 'pk', '')),
            detalle=f"{model} delete"
        )
    except Exception:
        # No interrumpir el flujo principal ante errores de auditoría
        pass
