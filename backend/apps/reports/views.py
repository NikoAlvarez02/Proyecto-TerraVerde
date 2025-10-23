from rest_framework import viewsets, permissions, decorators, response, status
from core.permissions import require_perfil_attr
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.files.base import ContentFile
from django.utils.text import slugify
from datetime import datetime, date
from .models import ReportTemplate, GeneratedReport, ScheduledReport
from .serializers import (
    ReportTemplateSerializer,
    GeneratedReportSerializer,
    ScheduledReportSerializer,
    ReportParametersSerializer,
)
from .utils import pdf_generator as pdf
from .utils import report_data as rdata
from apps.pacientes.models import Paciente
from apps.medical_records.models import Observation
from apps.profesionales.models import Profesional
from django.db.models import Count
from django.conf import settings
import os


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Desactiva chequeo CSRF para estas vistas (solo uso interno)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication, JWTAuthentication]


class GeneratedReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GeneratedReport.objects.all().order_by('-fecha_generacion')
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication, JWTAuthentication]


class ScheduledReportViewSet(viewsets.ModelViewSet):
    queryset = ScheduledReport.objects.all()
    serializer_class = ScheduledReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication, JWTAuthentication]


def _json_safe(value):
    """Convierte fechas a ISO y recorre estructuras para JSONField."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


class PatientReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, require_perfil_attr('puede_generar_reportes')]
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication, JWTAuthentication]

    @decorators.action(methods=['post'], detail=False, url_path='historia')
    def historia(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=True)
            paciente_id = request.data.get('paciente')
            try:
                paciente = Paciente.objects.get(pk=paciente_id)
            except Paciente.DoesNotExist:
                return response.Response({'detail': 'Paciente no encontrado'}, status=404)
            obs_qs = Observation.objects.filter(paciente=paciente).order_by('fecha_hora')
            desde = request.data.get('desde'); hasta = request.data.get('hasta')
            if desde:
                obs_qs = obs_qs.filter(fecha_hora__date__gte=desde)
            if hasta:
                obs_qs = obs_qs.filter(fecha_hora__date__lte=hasta)
            # ResÃÂºmenes
            profs = (
                obs_qs
                .values('profesional__apellido', 'profesional__nombre')
                .annotate(c=Count('id'))
                .order_by('-c')
            )
            prof_list = [
                {
                    'profesional': f"{p['profesional__apellido']}, {p['profesional__nombre']}",
                    'c': p['c']
                }
                for p in profs
            ]
            diags = (
                obs_qs.exclude(diagnostico_texto='')
                .values('diagnostico_texto', 'diagnostico_codigo')
                .annotate(c=Count('id'))
                .order_by('-c')
            )
            diag_list = list(diags)
            # estudios: dividir por comas/; y acumular
            est_counts = {}
            for o in obs_qs:
                txt = (o.estudios_solicitados or '')
                parts = [p.strip() for p in txt.replace(';', ',').split(',') if p.strip()]
                for it in parts:
                    key = it.lower()
                    est_counts[key] = est_counts.get(key, 0) + 1
            est_list = [ {'nombre': k, 'c': v} for k, v in sorted(est_counts.items(), key=lambda x: -x[1]) ]

            summary = {
                'profesionales': prof_list,
                'diagnosticos': diag_list,
                'estudios': est_list,
            }
            pdf_bytes = pdf.generate_patient_history_pdf(paciente, list(obs_qs), params.validated_data, summary)
            if not pdf_bytes:
                return response.Response({'detail': 'No se pudo generar el PDF (bytes vacÃÂ­os)'}, status=500)
            # Asegurar MEDIA_ROOT y subcarpeta
            try:
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'reportes'), exist_ok=True)
            except Exception:
                pass
            nombre = request.data.get('nombre_archivo') or f"Historia_{slugify(str(paciente))}_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(
                tipo='historia_completa',
                parametros_json=_json_safe(params.validated_data),
                usuario_generador=request.user,
            )
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes))
            gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={'request': request}).data, status=201)
        except Exception as e:
            return response.Response({'detail': f'Error generando PDF: {e}'}, status=500)

    @decorators.action(methods=['post'], detail=False, url_path='epicrisis')
    def epicrisis(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=True)
            paciente_id = request.data.get('paciente')
            try:
                paciente = Paciente.objects.get(pk=paciente_id)
            except Paciente.DoesNotExist:
                return response.Response({'detail': 'Paciente no encontrado'}, status=404)
            resumen = {
                'paciente': str(paciente),
                'observaciones': Observation.objects.filter(paciente=paciente).count(),
            }
            pdf_bytes = pdf.generate_epicrisis_pdf(paciente, resumen, params.validated_data)
            if not pdf_bytes:
                return response.Response({'detail': 'No se pudo generar el PDF (bytes vacÃÂ­os)'}, status=500)
            try:
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'reportes'), exist_ok=True)
            except Exception:
                pass
            nombre = request.data.get('nombre_archivo') or f"Epicrisis_{slugify(str(paciente))}_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(
                tipo='epicrisis',
                parametros_json=_json_safe(params.validated_data),
                usuario_generador=request.user,
            )
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes))
            gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={'request': request}).data, status=201)
        except Exception as e:
            return response.Response({'detail': f'Error generando PDF: {e}'}, status=500)

    @decorators.action(methods=['post'], detail=False, url_path='certificado')
    def certificado(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=False)  # no exige fechas
            paciente_id = request.data.get('paciente')
            profesional_id = request.data.get('profesional')
            datos = {
                'diagnostico': request.data.get('diagnostico') or '',
                'reposo_dias': request.data.get('reposo_dias') or '',
                'observaciones': request.data.get('observaciones') or '',
            }
            try:
                paciente = Paciente.objects.get(pk=paciente_id)
            except Paciente.DoesNotExist:
                return response.Response({'detail': 'Paciente no encontrado'}, status=404)
            profesional = None
            if profesional_id:
                profesional = Profesional.objects.filter(pk=profesional_id).first()
            profesional_display = profesional or request.user.get_username()
            pdf_bytes = pdf.generate_certificate_pdf(paciente, profesional_display, datos, request.data)
            if not pdf_bytes:
                return response.Response({'detail': 'No se pudo generar el PDF (bytes vacÃÂ­os)'}, status=500)
            try:
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'reportes'), exist_ok=True)
            except Exception:
                pass
            nombre = request.data.get('nombre_archivo') or f"Certificado_{slugify(str(paciente))}_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(
                tipo='certificado',
                parametros_json=request.data,
                usuario_generador=request.user,
            )
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes))
            gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={'request': request}).data, status=201)
        except Exception as e:
            return response.Response({'detail': f'Error generando PDF: {e}'}, status=500)


class StatisticsReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, require_perfil_attr('puede_ver_estadisticas')]
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication, JWTAuthentication]

    @decorators.action(methods=['post'], detail=False, url_path='atenciones-por-centro')
    def atenciones_por_centro(self, request):
        params = ReportParametersSerializer(data=request.data)
        params.is_valid(raise_exception=True)
        resumen = rdata.get_attendance_statistics(params.validated_data)
        # GrÃÂ¡fico: barras por centro
        charts = []
        try:
            labels = [it.get('centro__nombre') or 'N/A' for it in resumen.get('por_centro', [])]
            values = [it.get('c', 0) for it in resumen.get('por_centro', [])]
            from .utils import pdf_generator as _pg
            ch = _pg.generate_chart_image('Atenciones por Centro', labels, values)
            if ch: charts.append(ch)
        except Exception:
            pass
        try:
            pdf_bytes = pdf.generate_statistical_report_pdf('Atenciones por Centro', resumen, params.validated_data, charts)
            if not pdf_bytes:
                return response.Response({'detail': 'No se pudo generar el PDF (bytes vacÃÂ­os)'}, status=500)
            try:
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'reportes'), exist_ok=True)
            except Exception:
                pass
            nombre = request.data.get('nombre_archivo') or f"Atenciones_Centro_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(tipo='estadistico', parametros_json=_json_safe(params.validated_data), usuario_generador=request.user)
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes)); gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={'request': request}).data, status=201)
        except Exception as e:
            return response.Response({'detail': f'Error generando PDF: {e}'}, status=500)

    @decorators.action(methods=['post'], detail=False, url_path='productividad-profesional')
    def productividad_profesional(self, request):
        params = ReportParametersSerializer(data=request.data)
        params.is_valid(raise_exception=True)
        resumen = rdata.get_professional_productivity(params.validated_data)
        charts = []
        try:
            labels = [f"{it.get('profesional__apellido','')}, {it.get('profesional__nombre','')}" for it in resumen.get('productividad', [])]
            values = [it.get('c', 0) for it in resumen.get('productividad', [])]
            from .utils import pdf_generator as _pg
            ch = _pg.generate_chart_image('Productividad por Profesional', labels, values)
            if ch: charts.append(ch)
        except Exception:
            pass
        try:
            pdf_bytes = pdf.generate_statistical_report_pdf('Productividad por Profesional', resumen, params.validated_data, charts)
            if not pdf_bytes:
                return response.Response({'detail': 'No se pudo generar el PDF (bytes vacÃÂ­os)'}, status=500)
            try:
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'reportes'), exist_ok=True)
            except Exception:
                pass
            nombre = request.data.get('nombre_archivo') or f"Productividad_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(tipo='estadistico', parametros_json=_json_safe(params.validated_data), usuario_generador=request.user)
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes)); gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={'request': request}).data, status=201)
        except Exception as e:
            return response.Response({'detail': f'Error generando PDF: {e}'}, status=500)

    @decorators.action(methods=['post'], detail=False, url_path='diagnosticos')
    def diagnosticos(self, request):
        params = ReportParametersSerializer(data=request.data)
        params.is_valid(raise_exception=True)
        resumen = rdata.get_diagnostic_distribution(params.validated_data)
        charts = []
        try:
            labels = [it.get('diagnostico_codigo') or 'N/A' for it in resumen.get('por_cie10', [])]
            values = [it.get('c', 0) for it in resumen.get('por_cie10', [])]
            from .utils import pdf_generator as _pg
            ch = _pg.generate_chart_image('Distribucion por Diagnosticos', labels, values)
            if ch: charts.append(ch)
        except Exception:
            pass
        pdf_bytes = pdf.generate_statistical_report_pdf('Distribucion por Diagnosticos', resumen, params.validated_data, charts)
        nombre = request.data.get('nombre_archivo') or f"Distribucion_Diagnosticos_{datetime.now():%Y-%m-%d}.pdf"
        gr = GeneratedReport(tipo='estadistico', parametros_json=_json_safe(params.validated_data), usuario_generador=request.user)
        gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes)); gr.save()
        return response.Response(GeneratedReportSerializer(gr).data, status=201)
    

class AdministrativeReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(methods=['post'], detail=False, url_path='generar')
    def generar(self, request):
        params = ReportParametersSerializer(data=request.data)
        params.is_valid(raise_exception=True)
        # Placeholder administrativo
        pdf_bytes = pdf.generate_statistical_report_pdf('Reporte Administrativo', {'estado': 'OK'}, params.validated_data)
        nombre = request.data.get('nombre_archivo') or f"Administrativo_{datetime.now():%Y-%m-%d}.pdf"
        gr = GeneratedReport(tipo='administrativo', parametros_json=_json_safe(params.validated_data), usuario_generador=request.user)
        gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes)); gr.save()
        return response.Response(GeneratedReportSerializer(gr).data, status=201)


