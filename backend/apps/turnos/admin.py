# apps/turnos/admin.py
from django.contrib import admin
from .models import Turno

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'profesional', 'fecha_hora', 'estado', 'motivo')
    list_filter = ('estado', 'fecha_hora', 'profesional')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'profesional__nombre', 'motivo')
    date_hierarchy = 'fecha_hora'
    ordering = ('-fecha_hora',)
    readonly_fields = ('creado', 'actualizado')
    
    fieldsets = (
        ('Información del Turno', {
            'fields': ('paciente', 'profesional', 'fecha_hora', 'estado')
        }),
        ('Detalles', {
            'fields': ('motivo', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )