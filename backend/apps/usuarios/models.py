from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    ROLES = (
        ('admin', 'Administrador'),
        ('prof', 'Profesional'),
        ('recep', 'Recepcionista'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=20, choices=ROLES, default="recep")

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"
