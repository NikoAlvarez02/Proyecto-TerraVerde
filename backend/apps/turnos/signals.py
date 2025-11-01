from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Turno

try:
    from apps.medical_records.models import Observation
except Exception:
    Observation = None


@receiver(post_save, sender=Turno)
def turno_asistencia_crea_observacion(sender, instance: Turno, created, **kwargs):
    if Observation is None:
        return
    try:
        if instance.estado != 'atendido':
            return
        # Evitar duplicados por FK
        if Observation.objects.filter(turno=instance).exists():
            return
        pac = instance.paciente
        prof = instance.profesional
        centro = getattr(pac, 'centro', None)
        if not centro:
            try:
                centro = prof.centros.first()
            except Exception:
                centro = None
        if not centro:
            return
        Observation.objects.create(
            paciente=pac,
            profesional=prof,
            centro=centro,
            fecha_hora=instance.fecha_hora,
            motivo=instance.motivo or 'Asistencia registrada desde Turnos',
            observaciones=instance.observaciones or '',
            turno=instance,
        )
    except Exception:
        # No interrumpir el flujo de Turnos si falla la creación de Observación
        pass

