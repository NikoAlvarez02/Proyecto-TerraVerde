from django.db import models
from django.conf import settings


class Observation(models.Model):
    paciente = models.ForeignKey('pacientes.Paciente', on_delete=models.CASCADE, related_name='observaciones')
    profesional = models.ForeignKey('profesionales.Profesional', on_delete=models.PROTECT, related_name='observaciones')
    centro = models.ForeignKey('centers.Center', on_delete=models.PROTECT, related_name='observaciones')
    fecha_hora = models.DateTimeField()
    turno = models.ForeignKey('turnos.Turno', null=True, blank=True, on_delete=models.SET_NULL, related_name='observacion')

    motivo = models.CharField(max_length=255)
    anamnesis = models.TextField(blank=True)
    examen_fisico = models.TextField(blank=True)
    diagnostico_codigo = models.CharField(max_length=20, blank=True)
    diagnostico_texto = models.CharField(max_length=255, blank=True)
    estudios_solicitados = models.TextField(blank=True)
    tratamiento = models.TextField(blank=True)
    indicaciones = models.TextField(blank=True)
    proximo_control = models.DateField(null=True, blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    class Meta:
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['fecha_hora']),
            models.Index(fields=['diagnostico_codigo']),
            models.Index(fields=['profesional']),
            models.Index(fields=['centro']),
            models.Index(fields=['turno']),
        ]

    def __str__(self):
        return f"Obs {self.paciente} - {self.fecha_hora:%Y-%m-%d %H:%M}"


class ObservationAttachment(models.Model):
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE, related_name='adjuntos')
    archivo = models.FileField(upload_to='observaciones/')
    nombre = models.CharField(max_length=255, blank=True)
    subido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre or self.archivo.name


class ObservationRevision(models.Model):
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE, related_name='revisiones')
    datos_json = models.JSONField()
    editado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    editado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-editado_en']

