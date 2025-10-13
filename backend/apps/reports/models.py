from django.db import models
from django.conf import settings


class ReportTemplate(models.Model):
    TIPO_CHOICES = (
        ('historia_completa', 'Historia Clínica Completa'),
        ('observacion', 'Informe de Observación'),
        ('epicrisis', 'Epicrisis / Resumen'),
        ('certificado', 'Certificado Médico'),
        ('estadistico', 'Estadístico'),
        ('administrativo', 'Administrativo'),
    )
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    template_path = models.CharField(max_length=200)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class GeneratedReport(models.Model):
    tipo = models.CharField(max_length=30)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    parametros_json = models.JSONField(default=dict)
    archivo_pdf = models.FileField(upload_to='reportes/')
    usuario_generador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    centro = models.ForeignKey('centers.Center', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.fecha_generacion:%Y-%m-%d %H:%M}"


class ScheduledReport(models.Model):
    FRECUENCIAS = (
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
    )
    tipo = models.CharField(max_length=30)
    frecuencia = models.CharField(max_length=10, choices=FRECUENCIAS)
    activo = models.BooleanField(default=False)
    proximas_ejecuciones = models.IntegerField(default=0)
    ultimo_envio = models.DateTimeField(null=True, blank=True)
    destinatarios = models.TextField(help_text='Lista de emails separados por coma', blank=True)
    parametros_json = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.tipo} [{self.frecuencia}]"

