from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Perfil, AuditoriaLog


# Inline para mostrar Perfil dentro de User
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'


# Extender el UserAdmin existente
class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_rol')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'perfil__rol')
    
    def get_rol(self, obj):
        try:
            return obj.perfil.get_rol_display()
        except Perfil.DoesNotExist:
            return '-'
    get_rol.short_description = 'Rol'


# Registrar el modelo Perfil por separado también
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'puede_ver_estadisticas', 'puede_generar_reportes', 'puede_ver_auditoria')
    list_filter = ('rol','puede_ver_estadisticas','puede_generar_reportes','puede_ver_auditoria')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    fieldsets = (
        (None, {'fields': ('user','rol')}),
        ('Administración', {'fields': ('puede_admin_usuarios','puede_admin_especialidades','puede_admin_centros','puede_admin_roles'), 'classes': ('collapse',)}),
        ('Pacientes', {'fields': ('puede_crear_pacientes','puede_ver_pacientes','puede_editar_pacientes','puede_eliminar_pacientes'), 'classes': ('collapse',)}),
        ('Historia Clínica', {'fields': ('puede_crear_historias','puede_ver_historias','puede_editar_historias','puede_ver_historias_otros'), 'classes': ('collapse',)}),
        ('Turnos', {'fields': ('puede_crear_turnos','puede_ver_calendario','puede_gestionar_turnos','puede_cancelar_turnos'), 'classes': ('collapse',)}),
        ('Reportes y Auditoría', {'fields': ('puede_generar_reportes','puede_ver_estadisticas','puede_exportar_datos','puede_ver_auditoria')}),
    )


# Re-registrar User con la configuración personalizada
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(AuditoriaLog)
class AuditoriaLogAdmin(admin.ModelAdmin):
    list_display = ('fecha','usuario','accion','modelo','objeto_id','ruta','ip')
    list_filter = ('accion','fecha')
    search_fields = ('usuario__username','modelo','objeto_id','ruta','detalle')
