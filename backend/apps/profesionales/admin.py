# apps/profesionales/admin.py
from django.contrib import admin
from .models import Profesional, Especialidad

@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ('dni', 'apellido', 'nombre', 'matricula', 'especialidad', 'email', 'activo')
    list_filter = ('activo', 'especialidad')
    search_fields = ('dni', 'nombre', 'apellido', 'matricula', 'email')
    ordering = ('apellido', 'nombre')
    readonly_fields = ('fecha_alta',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('dni', 'nombre', 'apellido', 'email', 'telefono', 'direccion')
        }),
        ('Información Profesional', {
            'fields': ('matricula', 'especialidad')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_alta', 'fecha_baja')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Si el profesional ya existe, el DNI no se puede modificar
        if obj:
            return self.readonly_fields + ('dni',)
        return self.readonly_fields


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
