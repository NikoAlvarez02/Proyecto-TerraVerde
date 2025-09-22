from django.contrib import admin
from .models import Profesional

@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "dni", "matricula", "especialidad", "activo")
    search_fields = ("apellido", "nombre", "dni", "matricula", "especialidad", "email")
    list_filter = ("activo", "especialidad")
