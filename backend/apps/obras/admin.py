from django.contrib import admin
from .models import ObraSocial, PlanObraSocial


@admin.register(ObraSocial)
class ObraSocialAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre", "codigo")


@admin.register(PlanObraSocial)
class PlanObraSocialAdmin(admin.ModelAdmin):
    list_display = ("obra_social", "nombre", "codigo", "activo")
    list_filter = ("obra_social", "activo")
    search_fields = ("nombre", "codigo", "obra_social__nombre")

