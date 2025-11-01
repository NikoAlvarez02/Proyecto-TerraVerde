from django.db import models


class ObraSocial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        indexes = [models.Index(fields=["activo"]), models.Index(fields=["nombre"])]

    def __str__(self):
        return self.nombre


class PlanObraSocial(models.Model):
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.CASCADE, related_name='planes')
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["obra_social", "nombre"]
        unique_together = ("obra_social", "nombre")

    def __str__(self):
        return f"{self.obra_social} - {self.nombre}"

