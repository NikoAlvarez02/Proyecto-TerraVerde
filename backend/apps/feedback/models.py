from django.db import models


class Satisfaccion(models.Model):
    PUNTAJES = [(i, str(i)) for i in range(1, 6)]

    paciente = models.ForeignKey(
        'pacientes.Paciente',
        on_delete=models.CASCADE,
        related_name='calificaciones'
    )
    profesional = models.ForeignKey(
        'profesionales.Profesional',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calificaciones'
    )
    turno = models.ForeignKey(
        'turnos.Turno',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calificaciones'
    )
    puntaje = models.PositiveSmallIntegerField(choices=PUNTAJES)
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['puntaje']),
        ]

    def __str__(self):
        return f"{self.paciente} - {self.puntaje}⭐ ({self.fecha:%Y-%m-%d})"

