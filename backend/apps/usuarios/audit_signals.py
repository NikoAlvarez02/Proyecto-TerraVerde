from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.conf import settings
from .models import AuditoriaLog


def _model_label(instance):
    ct = ContentType.objects.get_for_model(instance.__class__)
    return ct.app_label, ct.model


@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    # Evitar recursión y modelos que afectan sesión
    if sender is AuditoriaLog or sender._meta.app_label in ("sessions",):
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
        pass


@receiver(post_delete)
def log_post_delete(sender, instance, **kwargs):
    if sender is AuditoriaLog or sender._meta.app_label in ("sessions",):
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
        pass
