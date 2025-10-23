from django.contrib import admin
from .models import Paciente

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "dni", "email", "activo")
    search_fields = ("apellido", "nombre", "dni", "email")
    list_filter = ("activo", "obra_social")
