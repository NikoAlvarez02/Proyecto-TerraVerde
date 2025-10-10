from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Perfil


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
    list_display = ('user', 'rol')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')


# Re-registrar User con la configuración personalizada
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)