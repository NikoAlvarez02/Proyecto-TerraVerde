from rest_framework import viewsets, permissions, decorators, response, status
from core.permissions import require_perfil_attr
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.files.base import ContentFile
from django.utils.text import slugify
from datetime import datetime, date, time
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
from apps.usuarios.models import AuditoriaLog
from django.db.models import Count, Q
from django.conf import settings
from django.http import HttpResponse
import os
import logging
import base64
from pathlib import Path
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
        description="Genera PDF de Epicrisis del paciente"
    )
    @decorators.action(methods=["post"], detail=False, url_path="epicrisis")
    def epicrisis(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=True)
            paciente = Paciente.objects.get(pk=request.data.get("paciente"))
            if not _can_access_patient(request.user, paciente):
                return response.Response({"detail": "No autorizado para este paciente"}, status=403)
            obs_qs = Observation.objects.filter(paciente=paciente).order_by("fecha_hora")
            pdf_bytes = pdf.generate_epicrisis_pdf(paciente, list(obs_qs), params.validated_data)
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
        description="Genera PDF de Certificado médico"
    )
    @decorators.action(methods=["post"], detail=False, url_path="certificado")
    def certificado(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=True)
            paciente = Paciente.objects.get(pk=request.data.get("paciente"))
            if not _can_access_patient(request.user, paciente):
                return response.Response({"detail": "No autorizado para este paciente"}, status=403)
            prof = None
            if request.data.get("profesional"):
                prof = Profesional.objects.get(pk=request.data.get("profesional"))
            pdf_bytes = pdf.generate_certificate_pdf(paciente, prof, params.validated_data)
            if not pdf_bytes:
                return response.Response({"detail": "No se pudo generar el PDF"}, status=500)
            nombre = request.data.get("nombre_archivo") or f"Certificado_{slugify(str(paciente))}_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(
                tipo="certificado",
                parametros_json=_json_safe(params.validated_data),
                usuario_generador=request.user,
            )
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes)); gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={"request": request}).data, status=201)
        except Paciente.DoesNotExist:
            return response.Response({"detail": "Paciente no encontrado"}, status=404)
        except Profesional.DoesNotExist:
            return response.Response({"detail": "Profesional no encontrado"}, status=404)
        except Exception as e:
            return response.Response({"detail": f"Error generando PDF: {e}"}, status=500)


class StatisticsReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, require_perfil_attr("puede_generar_reportes")]
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication, JWTAuthentication]

    @decorators.action(methods=["post"], detail=False, url_path="atenciones")
    def atenciones_por_centro(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=True)
            generator = getattr(rdata, "generate_atenciones_por_centro", None) or getattr(rdata, "get_attendance_statistics", None)
            if not generator:
                return response.Response({"detail": "No se encuentra el generador de datos de atenciones (utils.report_data)."}, status=500)
            data = generator(request.data)
            pdf_bytes = pdf.generate_statistics_pdf("Atenciones por centro", data, request.data)
            if not pdf_bytes:
                return response.Response({"detail": "No se pudo generar el PDF"}, status=500)
            nombre = f"Atenciones_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(
                tipo="estadistico",
                parametros_json=_json_safe(params.validated_data),
                usuario_generador=request.user,
            )
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes)); gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={"request": request}).data, status=201)
        except Exception as e:
            return response.Response({"detail": f"Error generando PDF: {e}"}, status=500)

    @decorators.action(methods=["get"], detail=False, url_path="atenciones/datos")
    def atenciones_datos(self, request):
        generator = getattr(rdata, "generate_atenciones_por_centro", None) or getattr(rdata, "get_attendance_statistics", None)
        if not generator:
            return response.Response({"detail": "No se encuentra el generador de datos de atenciones (utils.report_data)."}, status=500)
        data = generator(request.GET)
        return response.Response(data)

    @decorators.action(methods=["post"], detail=False, url_path="productividad")
    def productividad_profesional(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=True)
            generator = getattr(rdata, "generate_productividad_por_profesional", None) or getattr(rdata, "get_professional_productivity", None)
            if not generator:
                return response.Response({"detail": "No se encuentra el generador de productividad (utils.report_data)."}, status=500)
            data = generator(request.data)
            pdf_bytes = pdf.generate_statistics_pdf("Productividad por profesional", data, request.data)
            if not pdf_bytes:
                return response.Response({"detail": "No se pudo generar el PDF"}, status=500)
            nombre = f"Productividad_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(
                tipo="estadistico",
                parametros_json=_json_safe(params.validated_data),
                usuario_generador=request.user,
            )
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes)); gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={"request": request}).data, status=201)
        except Exception as e:
            return response.Response({"detail": f"Error generando PDF: {e}"}, status=500)

    @decorators.action(methods=["get"], detail=False, url_path="productividad/datos")
    def productividad_datos(self, request):
        generator = getattr(rdata, "generate_productividad_por_profesional", None) or getattr(rdata, "get_professional_productivity", None)
        if not generator:
            return response.Response({"detail": "No se encuentra el generador de productividad (utils.report_data)."}, status=500)
        data = generator(request.GET)
        return response.Response(data)

    @decorators.action(methods=["post"], detail=False, url_path="diagnosticos")
    def diagnosticos(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=True)
            generator = getattr(rdata, "generate_diagnosticos", None) or getattr(rdata, "get_diagnostic_distribution", None) or getattr(rdata, "get_epidemiological_data", None)
            if not generator:
                return response.Response({"detail": "No se encuentra el generador de diagnósticos (utils.report_data)."}, status=500)
            data = generator(request.data)
            pdf_bytes = pdf.generate_statistics_pdf("Pacientes y seguimiento clínico", data, request.data)
            nombre = f"Diagnosticos_{datetime.now():%Y-%m-%d}.pdf"
            gr = GeneratedReport(
                tipo="estadistico",
                parametros_json=_json_safe(params.validated_data),
                usuario_generador=request.user,
            )
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes)); gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={"request": request}).data, status=201)
        except Exception as e:
            return response.Response({"detail": f"Error generando PDF: {e}"}, status=500)

    @decorators.action(methods=["get"], detail=False, url_path="diagnosticos/datos")
    def diagnosticos_datos(self, request):
        generator = getattr(rdata, "generate_diagnosticos", None) or getattr(rdata, "get_diagnostic_distribution", None) or getattr(rdata, "get_epidemiological_data", None)
        if not generator:
            return response.Response({"detail": "No se encuentra el generador de diagnósticos (utils.report_data)."}, status=500)
        data = generator(request.GET)
        return response.Response(data)


class AdministrativeReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication, JWTAuthentication]

    @extend_schema(request=ReportParametersSerializer, responses=GeneratedReportSerializer,
        description="Genera reportes administrativos (placeholder)"
    )
    def generar(self, request):
        try:
            params = ReportParametersSerializer(data=request.data)
            params.is_valid(raise_exception=True)
            # Aqu� ir�a la l�gica real de reportes administrativos
            params_json = _json_safe(params.validated_data)
            gr = GeneratedReport(
                tipo='administrativo',
                parametros_json=params_json,
                usuario_generador=request.user
            )
            # Generar PDF de ejemplo
            pdf_bytes = pdf.generate_statistics_pdf("Reporte administrativo", {}, params.validated_data)
            nombre = f"Administrativo_{datetime.now():%Y-%m-%d}.pdf"
            gr.archivo_pdf.save(nombre, ContentFile(pdf_bytes))
            gr.save()
            return response.Response(GeneratedReportSerializer(gr, context={'request': request}).data, status=201)
        except Exception as e:
            return response.Response({"detail": str(e)}, status=500)


# ============== Vista auditoría (filtros + export) =================
class AuditLogView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _filter_qs(self, request):
        qs = AuditoriaLog.objects.select_related('usuario').all()
        accion = request.GET.get('accion')
        usuario_id = request.GET.get('usuario')
        fecha_gte = request.GET.get('fecha_desde') or request.GET.get('fecha_gte')
        fecha_lte = request.GET.get('fecha_hasta') or request.GET.get('fecha_lte')
        hora_gte = request.GET.get('hora_desde')
        hora_lte = request.GET.get('hora_hasta')
        q = (request.GET.get('q') or '').strip()
        if accion:
            qs = qs.filter(accion=accion)
        if usuario_id:
            qs = qs.filter(usuario_id=usuario_id)
        if fecha_gte:
            qs = qs.filter(fecha__date__gte=fecha_gte)
        if fecha_lte:
            qs = qs.filter(fecha__date__lte=fecha_lte)
        if hora_gte:
            try:
                h, m = hora_gte.split(':')[:2]; qs = qs.filter(fecha__time__gte=time(int(h), int(m)))
            except Exception:
                pass
        if hora_lte:
            try:
                h, m = hora_lte.split(':')[:2]; qs = qs.filter(fecha__time__lte=time(int(h), int(m)))
            except Exception:
                pass
        if q:
            qs = qs.filter(
                Q(detalle__icontains=q) |
                Q(ruta__icontains=q) |
                Q(modelo__icontains=q) |
                Q(objeto_id__icontains=q) |
                Q(usuario__username__icontains=q)
            )
        return qs.order_by('-fecha')

    def list(self, request):
        qs = self._filter_qs(request)
        export = (request.GET.get('export') or '').lower()
        if export in ('csv','xlsx','excel'):
            return self._export_csv(qs, export)
        if export == 'pdf':
            return self._export_pdf(qs, request)
        limit = int(request.GET.get('limit') or 200)
        data = [{
            'fecha': a.fecha.isoformat(),
            'usuario': a.usuario.username if a.usuario else 'anon',
            'accion': a.accion,
            'modelo': a.modelo,
            'objeto_id': a.objeto_id,
            'ruta': a.ruta,
            'metodo': a.metodo,
            'ip': a.ip,
            'user_agent': a.user_agent,
            'detalle': a.detalle,
        } for a in qs[:max(1, min(limit, 1000))]]
        return response.Response(data)

    def _export_csv(self, qs, export):
        import csv
        resp = HttpResponse(content_type='text/csv')
        ext = 'xlsx' if export in ('xlsx','excel') else 'csv'
        resp['Content-Disposition'] = f'attachment; filename="auditorias.{ext}"'
        writer = csv.writer(resp)
        writer.writerow(['fecha','usuario','accion','modelo','objeto_id','ruta','metodo','ip','user_agent','detalle'])
        for a in qs.iterator():
            writer.writerow([
                a.fecha.strftime('%Y-%m-%d %H:%M:%S'),
                a.usuario.username if a.usuario else 'anon',
                a.accion, a.modelo, a.objeto_id, a.ruta, a.metodo, a.ip, a.user_agent, a.detalle
            ])
        return resp

    def _export_pdf(self, qs, request):
        from weasyprint import HTML, CSS

        def _logo_data_uri():
            # 1) intentar con helper central
            try:
                from .utils import pdf_generator as pdfgen
                loader = getattr(pdfgen, "_load_logo_base64", None)
                if loader:
                    b64 = loader()
                    if b64:
                        return "data:image/png;base64," + b64
            except Exception:
                pass
            # 2) rutas conocidas (BASE_DIR apunta a backend)
            candidates = [
                Path(settings.BASE_DIR).parent / "frontend" / "ASSETS" / "terraverde.png",
                Path(settings.BASE_DIR) / "frontend" / "ASSETS" / "terraverde.png",
                Path(settings.BASE_DIR).parent / "frontend" / "ASSETS" / "logo.png",
            ]
            for p in candidates:
                try:
                    if p.exists():
                        return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()
                except Exception:
                    continue
            return ""

        logo_b64 = _logo_data_uri()

        def safe(text):
            return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        rows = "".join([
            f"""
            <tr>
                <td>{a.fecha.strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>{safe(a.usuario.username if a.usuario else 'anon')}</td>
                <td>{safe(a.accion)}</td>
                <td>{safe(a.modelo)}</td>
                <td>{safe(str(a.objeto_id))}</td>
                <td>{safe(a.ruta)}</td>
                <td>{safe(a.metodo)}</td>
                <td>{safe(a.ip)}</td>
                <td>{safe(a.detalle)}</td>
            </tr>
            """ for a in qs[:1000]
        ])

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Helvetica', Arial, sans-serif; font-size: 12px; color: #1b1b1b; }}
                .header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }}
                .header img {{ height: 42px; }}
                .title {{ font-size: 18px; font-weight: 700; color: #215728; }}
                .subtitle {{ font-size: 12px; color: #4a4a4a; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 6px 8px; border: 1px solid #d8e2d8; text-align: left; }}
                th {{ background: #eaf4ea; color: #214722; font-weight: 700; }}
                tr:nth-child(even) {{ background: #f8fbf8; }}
            </style>
        </head>
        <body>
            <div class="header">
                {f'<img src="{logo_b64}" alt="TerraVerde">' if logo_b64 else ''}
                <div>
                    <div class="title">Auditorías del sistema</div>
                    <div class="subtitle">Exportado {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                </div>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Usuario</th>
                  <th>Acción</th>
                  <th>Modelo</th>
                  <th>Objeto</th>
                  <th>Ruta</th>
                  <th>Método</th>
                  <th>IP</th>
                  <th>Detalle</th>
                </tr>
              </thead>
              <tbody>{rows}</tbody>
            </table>
        </body>
        </html>"""

        pdf_bytes = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="auditorias.pdf"'
        return resp
