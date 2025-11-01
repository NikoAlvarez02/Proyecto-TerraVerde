from django.contrib import admin
from .models import Center, Holiday


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo', 'matriz')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre', 'direccion', 'email')


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'nombre', 'laborable')
    list_filter = ('laborable',)
    search_fields = ('nombre',)

