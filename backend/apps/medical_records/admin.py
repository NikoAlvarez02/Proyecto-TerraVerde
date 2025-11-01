from django.contrib import admin
from .models import Observation, ObservationAttachment, ObservationRevision


class ObservationAttachmentInline(admin.TabularInline):
    model = ObservationAttachment
    extra = 0


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'profesional', 'centro', 'fecha_hora', 'diagnostico_texto')
    list_filter = ('centro', 'profesional', 'fecha_hora')
    search_fields = ('paciente__apellido', 'paciente__nombre', 'diagnostico_texto', 'motivo')
    inlines = [ObservationAttachmentInline]


@admin.register(ObservationRevision)
class ObservationRevisionAdmin(admin.ModelAdmin):
    list_display = ('observation', 'editado_por', 'editado_en')
    list_filter = ('editado_en',)

