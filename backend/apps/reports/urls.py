from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from .views import (
    ReportTemplateViewSet,
    GeneratedReportViewSet,
    ScheduledReportViewSet,
    PatientReportViewSet,
    StatisticsReportViewSet,
    AdministrativeReportViewSet,
)

app_name = 'reportes'

router = DefaultRouter()
router.register(r'templates', ReportTemplateViewSet, basename='templates')
router.register(r'generados', GeneratedReportViewSet, basename='generados')
router.register(r'programados', ScheduledReportViewSet, basename='programados')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', TemplateView.as_view(template_name='reports/reports_dashboard.html'), name='dashboard'),
    path('visor/', TemplateView.as_view(template_name='reports/report_viewer.html'), name='viewer'),
    # Alias legados para compatibilidad con accesos directos a archivos
    path('report_viewer.html', TemplateView.as_view(template_name='reports/report_viewer.html'), name='viewer_file'),
    path('visor_de_reportes.html', TemplateView.as_view(template_name='reports/report_viewer.html'), name='viewer_file_alt'),
    path('api/pacientes/', PatientReportViewSet.as_view({'post': 'historia'}), name='paciente-historia'),
    path('api/pacientes/epicrisis/', PatientReportViewSet.as_view({'post': 'epicrisis'}), name='paciente-epicrisis'),
    path('api/pacientes/certificado/', PatientReportViewSet.as_view({'post': 'certificado'}), name='paciente-certificado'),
    path('api/estadisticas/atenciones/', StatisticsReportViewSet.as_view({'post': 'atenciones_por_centro'}), name='estadisticas-atenciones'),
    path('api/estadisticas/productividad/', StatisticsReportViewSet.as_view({'post': 'productividad_profesional'}), name='estadisticas-productividad'),
    path('api/estadisticas/epidemiologico/', StatisticsReportViewSet.as_view({'post': 'epidemiologico'}), name='estadisticas-epidemiologico'),
    path('api/administrativos/generar/', AdministrativeReportViewSet.as_view({'post': 'generar'}), name='administrativos-generar'),
]
