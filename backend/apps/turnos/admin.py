from django.contrib import admin
from .models import Turno

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'profesional', 'fecha_hora', 'estado')
    list_filter = ('estado', 'profesional')
    search_fields = ('paciente__apellido', 'paciente__nombre', 'profesional__apellido', 'motivo')
    ordering = ('-fecha_hora',)
    date_hierarchy = 'fecha_hora'
    fieldsets = (
        (None, {
            'fields': ('paciente', 'profesional', 'fecha_hora', 'estado')
        }),
        ('Detalles adicionales', {
            'fields': ('motivo', 'observaciones'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('id',)
    actions = ['marcar_como_completado', 'marcar_como_cancelado']
    