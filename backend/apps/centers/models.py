from django.db import models


class Center(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)
    matriz = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sucursales')

    class Meta:
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

