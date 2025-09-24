from django.db import models

class Turno(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('atendido', 'Atendido'),
        ('cancelado', 'Cancelado'),
        ('ausente', 'Ausente'),
    )

    # 👇 Clave: usar 'pacientes.Paciente' y 'profesionales.Profesional'
    paciente = models.ForeignKey('pacientes.Paciente', on_delete=models.PROTECT, related_name='turnos')
    profesional = models.ForeignKey('profesionales.Profesional', on_delete=models.PROTECT, related_name='turnos')

    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=12, choices=ESTADOS, default='pendiente')
    motivo = models.CharField(max_length=200, blank=True)
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fecha_hora']
        indexes = [models.Index(fields=['fecha_hora']), models.Index(fields=['estado'])]
        unique_together = ('profesional', 'fecha_hora')

    def __str__(self):
        return f'{self.paciente} con {self.profesional} — {self.fecha_hora:%d/%m/%Y %H:%M}'
