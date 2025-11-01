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
import logging
from drf_spectacular.utils import extend_schema, OpenApiTypes


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
    """Convierte valores a algo serializable (dict/list) y fechas a ISO."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def _can_access_patient(user, paciente):
    perfil = getattr(user, "perfil", None)
    if not perfil:
        return False
    if perfil.rol == "admin":
        return True
    if perfil.rol == "prof":
        prof = getattr(perfil, "profesional", None)
        if not prof:
            return False
        return paciente.profesionales_asignados.filter(pk=getattr(prof, "pk", None)).exists()
    return False


class PatientReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, require_perfil_attr("puede_generar_reportes")]
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication, JWTAuthentication]

    @extend_schema(
        request=ReportParametersSerializer,
        responses=GeneratedReportSerializer,
        description="Genera PDF de Historia Clínica del paciente"
    )
    @decorators.action(methods=["post"], detail=False, url_path="historia")
    def historia(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=True)
            paciente_id = request.data.get("paciente")
            paciente = Paciente.objects.get(pk=paciente_id)
            if not _can_access_patient(request.user, paciente):
                return response.Response({"detail": "No autorizado para este paciente"}, status=403)
            obs_qs = Observation.objects.filter(paciente=paciente).order_by("fecha_hora")
            desde = request.data.get("desde"); hasta = request.data.get("hasta")
            if desde:
                obs_qs = obs_qs.filter(fecha_hora__date__gte=desde)
            if hasta:
                obs_qs = obs_qs.filter(fecha_hora__date__lte=hasta)
            pdf_bytes = pdf.generate_patient_history_pdf(paciente, list(obs_qs), params.validated_data, None)
            if not pdf_bytes:
                return response.Response({"detail": "No se pudo generar el PDF"}, status=500)
            nombre = request.data.get("nombre_archivo") or f"Historia_{slugify(str(paciente))}_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(
                tipo="historia_completa",
                parametros_json=_json_safe(params.validated_data),
                usuario_generador=request.user,
            )
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes)); gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={"request": request}).data, status=201)
        except Paciente.DoesNotExist:
            return response.Response({"detail": "Paciente no encontrado"}, status=404)
        except Exception as e:
            return response.Response({"detail": f"Error generando PDF: {e}"}, status=500)

    @extend_schema(
        request=ReportParametersSerializer,
        responses=GeneratedReportSerializer,
        description="Genera PDF de Epicrisis / Resumen"
    )
    @decorators.action(methods=["post"], detail=False, url_path="epicrisis")
    def epicrisis(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=True)
            paciente_id = request.data.get("paciente")
            paciente = Paciente.objects.get(pk=paciente_id)
            if not _can_access_patient(request.user, paciente):
                return response.Response({"detail": "No autorizado para este paciente"}, status=403)
            resumen = {
                "paciente": str(paciente),
                "observaciones": Observation.objects.filter(paciente=paciente).count(),
            }
            pdf_bytes = pdf.generate_epicrisis_pdf(paciente, resumen, params.validated_data)
            if not pdf_bytes:
                return response.Response({"detail": "No se pudo generar el PDF"}, status=500)
            nombre = request.data.get("nombre_archivo") or f"Epicrisis_{slugify(str(paciente))}_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(
                tipo="epicrisis",
                parametros_json=_json_safe(params.validated_data),
                usuario_generador=request.user,
            )
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes)); gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={"request": request}).data, status=201)
        except Paciente.DoesNotExist:
            return response.Response({"detail": "Paciente no encontrado"}, status=404)
        except Exception as e:
            return response.Response({"detail": f"Error generando PDF: {e}"}, status=500)

    @extend_schema(
        request=ReportParametersSerializer,
        responses=GeneratedReportSerializer,
        description="Genera Certificado Médico en PDF"
    )
    @decorators.action(methods=["post"], detail=False, url_path="certificado")
    def certificado(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=False)
            paciente_id = request.data.get("paciente")
            profesional_id = request.data.get("profesional")
            datos = {
                "diagnostico": request.data.get("diagnostico") or "",
                "reposo_dias": request.data.get("reposo_dias") or "",
                "observaciones": request.data.get("observaciones") or "",
            }
            paciente = Paciente.objects.get(pk=paciente_id)
            if not _can_access_patient(request.user, paciente):
                return response.Response({"detail": "No autorizado para este paciente"}, status=403)
            profesional = None
            if profesional_id:
                profesional = Profesional.objects.filter(pk=profesional_id).first()
            profesional_display = profesional or request.user.get_username()
            pdf_bytes = pdf.generate_certificate_pdf(paciente, profesional_display, datos, request.data)
            if not pdf_bytes:
                return response.Response({"detail": "No se pudo generar el PDF"}, status=500)
            nombre = request.data.get("nombre_archivo") or f"Certificado_{slugify(str(paciente))}_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(
                tipo="certificado",
                parametros_json=_json_safe(request.data),
                usuario_generador=request.user,
            )
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes)); gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={"request": request}).data, status=201)
        except Paciente.DoesNotExist:
            return response.Response({"detail": "Paciente no encontrado"}, status=404)
        except Exception as e:
            return response.Response({"detail": f"Error generando PDF: {e}"}, status=500)

class StatisticsReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, require_perfil_attr('puede_ver_estadisticas')]
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication, JWTAuthentication]
    logger = logging.getLogger(__name__)

    @extend_schema(request=ReportParametersSerializer, responses=GeneratedReportSerializer,
                   description='Genera PDF: Gestión de Turnos y Asistencia')
    @decorators.action(methods=['post'], detail=False, url_path='atenciones-por-centro')
    def atenciones_por_centro(self, request):
        params = ReportParametersSerializer(data=request.data)
        params.is_valid(raise_exception=True)
        resumen = rdata.get_attendance_statistics(params.validated_data)
        # GrÃƒÂƒÃ‚Â¡fico: barras por centro
        charts = []
        try:
            labels = [it.get('centro__nombre') or 'N/A' for it in resumen.get('por_centro', [])]
            values = [it.get('c', 0) for it in resumen.get('por_centro', [])]
            from .utils import pdf_generator as _pg
            ch = _pg.generate_chart_image('Gestión de Turnos y Asistencia', labels, values)
            if ch: charts.append(ch)
        except Exception:
            pass
        try:
            pdf_bytes = pdf.generate_statistical_report_pdf('Gestión de Turnos y Asistencia', resumen, params.validated_data, charts)
            if not pdf_bytes:
                return response.Response({'detail': 'No se pudo generar el PDF (bytes vacÃƒÂƒÃ‚Â­os)'}, status=500)
            try:
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'reportes'), exist_ok=True)
            except Exception:
                pass
            nombre = request.data.get('nombre_archivo') or f"Gestion_Turnos_Asistencia_{datetime.now():%Y-%m-%d}.pdf"
            params_json = _json_safe(params.validated_data) or {}
            if params_json is None:
                params_json = {}
            self.logger.info("[REPORTES] Guardando GeneratedReport atenciones params=%r (%s)", params_json, type(params_json))
            gr = GeneratedReport(tipo='estadistico', parametros_json=params_json, usuario_generador=request.user)
            # Guardar primero para asegurar PK y columnas NOT NULL
            gr.save()
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes))
            gr.save(update_fields=['archivo_pdf'])
            return response.Response(GeneratedReportSerializer(gr, context={'request': request}).data, status=201)
        except Exception as e:
            return response.Response({'detail': f'Error generando PDF: {e}'}, status=500)

    @extend_schema(responses=OpenApiTypes.OBJECT, description='JSON: estadísticas de atenciones')
    @decorators.action(methods=['get'], detail=False, url_path='atenciones/datos')
    def atenciones_datos(self, request):
        """Devuelve JSON de estadísticas de atenciones (para exportar CSV/Excel)."""
        try:
            params = {
                'desde': request.query_params.get('desde') or None,
                'hasta': request.query_params.get('hasta') or None,
            }
            resumen = rdata.get_attendance_statistics(params)
            return response.Response(resumen, status=200)
        except Exception as e:
            return response.Response({'detail': f'Error obteniendo datos: {e}'}, status=500)

    @extend_schema(request=ReportParametersSerializer, responses=GeneratedReportSerializer,
                   description='Genera PDF: Productividad por Profesional')
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
            ch = _pg.generate_chart_image('Desempeño por profesional', labels, values)
            if ch: charts.append(ch)
        except Exception:
            pass
        try:
            pdf_bytes = pdf.generate_statistical_report_pdf('Desempeño por profesional', resumen, params.validated_data, charts)
            if not pdf_bytes:
                return response.Response({'detail': 'No se pudo generar el PDF (bytes vacÃƒÂƒÃ‚Â­os)'}, status=500)
            try:
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'reportes'), exist_ok=True)
            except Exception:
                pass
            nombre = request.data.get('nombre_archivo') or f"Desempeno_por_profesional_{datetime.now():%Y-%m-%d}.pdf"
            params_json = _json_safe(params.validated_data) or {}
            if params_json is None:
                params_json = {}
            self.logger.info("[REPORTES] Guardando GeneratedReport productividad params=%r (%s)", params_json, type(params_json))
            gr = GeneratedReport(tipo='estadistico', parametros_json=params_json, usuario_generador=request.user)
            gr.save()
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes))
            gr.save(update_fields=['archivo_pdf'])
            return response.Response(GeneratedReportSerializer(gr, context={'request': request}).data, status=201)
        except Exception as e:
            return response.Response({'detail': f'Error generando PDF: {e}'}, status=500)

    @extend_schema(responses=OpenApiTypes.OBJECT, description='JSON: productividad por profesional')
    @decorators.action(methods=['get'], detail=False, url_path='productividad/datos')
    def productividad_datos(self, request):
        """Devuelve JSON de productividad por profesional (solo productividad)."""
        try:
            params = {
                'desde': request.query_params.get('desde') or None,
                'hasta': request.query_params.get('hasta') or None,
            }
            resumen = rdata.get_professional_productivity(params)
            return response.Response(resumen, status=200)
        except Exception as e:
            return response.Response({'detail': f'Error obteniendo datos: {e}'}, status=500)

    @extend_schema(request=ReportParametersSerializer, responses=GeneratedReportSerializer,
                   description='Genera PDF: Distribución por Diagnósticos')
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
            ch = _pg.generate_chart_image('Pacientes y Seguimiento Clínico', labels, values)
            if ch: charts.append(ch)
        except Exception:
            pass
        pdf_bytes = pdf.generate_statistical_report_pdf('Pacientes y Seguimiento Clínico', resumen, params.validated_data, charts)
        nombre = request.data.get('nombre_archivo') or f"Pacientes_Seguimiento_Clinico_{datetime.now():%Y-%m-%d}.pdf"
        params_json = _json_safe(params.validated_data) or {}
        if params_json is None:
            params_json = {}
        logging.getLogger(__name__).info("[REPORTES] Guardando GeneratedReport diagnosticos params=%r (%s)", params_json, type(params_json))
        gr = GeneratedReport(tipo='estadistico', parametros_json=params_json, usuario_generador=request.user)
        gr.save()
        gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes))
        gr.save(update_fields=['archivo_pdf'])
        return response.Response(GeneratedReportSerializer(gr).data, status=201)

    @extend_schema(responses=OpenApiTypes.OBJECT, description='JSON: distribución por diagnósticos')
    @decorators.action(methods=['get'], detail=False, url_path='diagnosticos/datos')
    def diagnosticos_datos(self, request):
        """Devuelve JSON de distribución por diagnósticos (clínico/seguimiento)."""
        try:
            params = {
                'desde': request.query_params.get('desde') or None,
                'hasta': request.query_params.get('hasta') or None,
            }
            resumen = rdata.get_diagnostic_distribution(params)
            return response.Response(resumen, status=200)
        except Exception as e:
            return response.Response({'detail': f'Error obteniendo datos: {e}'}, status=500)
    

class AdministrativeReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=ReportParametersSerializer, responses=GeneratedReportSerializer,
                   description='Genera PDF Administrativo')
    @decorators.action(methods=['post'], detail=False, url_path='generar')
    def generar(self, request):
        params = ReportParametersSerializer(data=request.data)
        params.is_valid(raise_exception=True)
        # Placeholder administrativo
        pdf_bytes = pdf.generate_statistical_report_pdf('Reporte Administrativo', {'estado': 'OK'}, params.validated_data)
        nombre = request.data.get('nombre_archivo') or f"Administrativo_{datetime.now():%Y-%m-%d}.pdf"
        params_json = _json_safe(params.validated_data) or {}
        if params_json is None:
            params_json = {}
        logging.getLogger(__name__).info("[REPORTES] Guardando GeneratedReport administrativo params=%r (%s)", params_json, type(params_json))
        gr = GeneratedReport(tipo='administrativo', parametros_json=params_json, usuario_generador=request.user)
        gr.save()
        gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes))
        gr.save(update_fields=['archivo_pdf'])
        return response.Response(GeneratedReportSerializer(gr).data, status=201)















