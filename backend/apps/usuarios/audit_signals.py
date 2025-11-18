import sys
from django.db import connection
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from .models import AuditoriaLog
from .request_local import get_current_request


def _model_label(instance):
    ct = ContentType.objects.get_for_model(instance.__class__)
    return ct.app_label, ct.model


def _table_exists(table_name: str) -> bool:
    try:
        with connection.cursor() as cursor:
            return table_name in connection.introspection.table_names(cursor)
    except Exception:
        return False


def _request_user_meta():
    req = get_current_request()
    if not req:
        return None, None, '', ''
    user = req.user if getattr(req, 'user', None) and req.user.is_authenticated else None
    ip = req.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or req.META.get('REMOTE_ADDR')
    ua = str(req.META.get('HTTP_USER_AGENT', ''))[:255]
    ruta = (req.path or '')[:255]
    metodo = getattr(req, 'method', '')
    return user, ip, ruta, ua, metodo


@receiver(post_save, dispatch_uid="usuarios_audit_post_save")
def log_post_save(sender, instance, created, **kwargs):
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
        user, ip, ruta, ua, metodo = _request_user_meta()
        accion = 'create' if created else 'update'
        AuditoriaLog.objects.create(
            usuario=user,
            accion=accion,
            app_label=app_label,
            modelo=model,
            objeto_id=str(getattr(instance, 'pk', '')),
            ruta=ruta,
            metodo=metodo,
            ip=ip,
            user_agent=ua,
            detalle=f"{model} {accion}"
        )
    except Exception:
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
        user, ip, ruta, ua, metodo = _request_user_meta()
        AuditoriaLog.objects.create(
            usuario=user,
            accion='delete',
            app_label=app_label,
            modelo=model,
            objeto_id=str(getattr(instance, 'pk', '')),
            ruta=ruta,
            metodo=metodo,
            ip=ip,
            user_agent=ua,
            detalle=f"{model} delete"
        )
    except Exception:
        pass
