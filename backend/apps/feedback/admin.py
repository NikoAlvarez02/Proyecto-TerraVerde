from django.contrib import admin
from .models import Satisfaccion


@admin.register(Satisfaccion)
class SatisfaccionAdmin(admin.ModelAdmin):
    list_display = ("fecha", "paciente", "profesional", "puntaje")
    list_filter = ("puntaje", "fecha")
    search_fields = ("paciente__nombre", "paciente__apellido", "profesional__nombre", "profesional__apellido")

