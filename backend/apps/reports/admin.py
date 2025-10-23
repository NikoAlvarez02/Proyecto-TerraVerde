from django.contrib import admin
from .models import ReportTemplate, GeneratedReport, ScheduledReport


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('nombre', 'template_path')


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'fecha_generacion', 'usuario_generador', 'centro')
    list_filter = ('tipo', 'fecha_generacion')
    search_fields = ('tipo',)


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'frecuencia', 'activo', 'ultimo_envio')
    list_filter = ('frecuencia', 'activo')
    search_fields = ('tipo',)

