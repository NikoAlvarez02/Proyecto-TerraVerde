from django.contrib import admin
from .models import Center


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo', 'matriz')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre', 'direccion', 'email')

