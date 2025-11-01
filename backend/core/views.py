import logging
import traceback
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.db.models import Avg
from django.db.utils import DatabaseError, ProgrammingError

from apps.turnos.models import Turno
from apps.pacientes.models import Paciente
from apps.feedback.models import Satisfaccion
from apps.usuarios.models import LoginThrottle

logger = logging.getLogger(__name__)


def weasy_pdf_test(request):
    """Genera un PDF simple con WeasyPrint y loguea pasos/errores."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body>
        <h1 style="color:#2c3e50;font-family:Arial">WeasyPrint OK</h1>
        <p>Prueba de render directo.</p>
    </body>
    </html>
    """
    try:
        logger.info("[weasy] Intentando importar WeasyPrint…")
        from weasyprint import HTML, __version__
        logger.info(f"[weasy] Importado WeasyPrint {__version__}")
        pdf_bytes = HTML(string=html_content).write_pdf()
        logger.info(f"[weasy] PDF generado: {len(pdf_bytes)} bytes")
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = 'inline; filename="weasy-test.pdf"'
        return resp
    except Exception:
        logger.exception("[weasy] Error generando PDF")
        if settings.DEBUG:
            tb = traceback.format_exc()
            return HttpResponse(f"<pre>{tb}</pre>", status=500)
        return HttpResponse("Error generando PDF", status=500)


def weasy_diagnostico(request):
    """Chequeos básicos de entorno WeasyPrint."""
    out = []
    try:
        from weasyprint import __version__
        out.append(f"WeasyPrint: {__version__}")
    except Exception as e:
        out.append(f"WeasyPrint: ERROR {e}")
    for mod in ("cairocffi", "cffi"):
        try:
            __import__(mod)
            out.append(f"{mod}: OK")
        except Exception as e:
            out.append(f"{mod}: ERROR {e}")
    return HttpResponse("<pre>" + "\n".join(out) + "</pre>")


@login_required
def home_dashboard(request):
    """Vista de inicio con métricas reales para el dashboard."""
    hoy = timezone.localdate()
    ahora = timezone.now()

    pacientes_activos = Paciente.objects.filter(activo=True).count()

    turnos_hoy_qs = Turno.objects.filter(fecha_hora__date=hoy)
    sesiones_hoy_total = turnos_hoy_qs.count()
    sesiones_hoy_completadas = turnos_hoy_qs.filter(estado='atendido').count()
    sesiones_hoy_pendientes = turnos_hoy_qs.filter(estado__in=['pendiente', 'confirmado']).count()
    sesiones_hoy_pct = int(round((sesiones_hoy_completadas / sesiones_hoy_total) * 100)) if sesiones_hoy_total else 0

    hace_30 = hoy - timezone.timedelta(days=30)
    turnos_30_qs = Turno.objects.filter(fecha_hora__date__gte=hace_30, fecha_hora__date__lte=hoy)
    tasa_progreso = sesiones_hoy_pct

    try:
        sats_qs = Satisfaccion.objects.filter(fecha__date__gte=hace_30, fecha__date__lte=hoy)
        promedio = sats_qs.aggregate(avg=Avg('puntaje')).get('avg')
    except (DatabaseError, ProgrammingError):
        promedio = None
    satisfaccion = round(promedio, 1) if promedio else None
    satisfaccion_pct = int(round((promedio / 5) * 100)) if promedio else 0
    satisfaccion_pct = 0

    proximas = (
        turnos_hoy_qs
        .filter(fecha_hora__gte=ahora)
        .select_related('paciente')
        .order_by('fecha_hora')[:5]
    )
    turnos_hoy = (
        turnos_hoy_qs
        .select_related('paciente')
        .order_by('fecha_hora')
    )

    next_turno = proximas[0] if proximas else None
    show_notification = False
    notif_text = None
    if next_turno:
        delta_min = int((next_turno.fecha_hora - ahora).total_seconds() // 60)
        if 0 < delta_min <= 60:
            pac = f"{next_turno.paciente.apellido}, {next_turno.paciente.nombre}"
            hora_txt = next_turno.fecha_hora.strftime('%H:%M')
            motivo = next_turno.motivo or 'Sesión'
            notif_text = f"{motivo} con {pac} a las {hora_txt} (en {delta_min} min)"
            show_notification = True

    dias = []
    for i in range(6, -1, -1):
        dia = hoy - timezone.timedelta(days=i)
        cnt = Turno.objects.filter(fecha_hora__date=dia).count()
        dias.append((dia, cnt))

    max_cnt = max((c for _, c in dias), default=1)
    nombres = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    weekly = []
    for dia, cnt in dias:
        idx = dia.weekday()
        weekly.append({
            'label': nombres[idx],
            'pct': int(round((cnt / max_cnt) * 100)) if max_cnt else 0,
        })

    ctx = {
        'pacientes_activos': pacientes_activos,
        'sesiones_hoy_total': sesiones_hoy_total,
        'sesiones_hoy_completadas': sesiones_hoy_completadas,
        'sesiones_hoy_pendientes': sesiones_hoy_pendientes,
        'sesiones_hoy_pct': sesiones_hoy_pct,
        'tasa_progreso': tasa_progreso,
        'satisfaccion': satisfaccion,
        'proximas_sesiones': proximas,
        'weekly': weekly,
        'satisfaccion_pct': satisfaccion_pct,
        'show_notification': show_notification,
        'notif_text': notif_text,
        'turnos_hoy': turnos_hoy,
    }

    return render(request, 'paginaprincipal.html', ctx)


class SessionLoginView(LoginView):
    """LoginView con protección básica anti-fuerza bruta.

    - Cuenta intentos en sesión y en DB por (usuario, IP).
    - Bloquea tras 5 fallos dentro de 10 min por 15 min.
    - Resetea contadores al iniciar sesión correctamente.
    """

    session_key = 'login_fail_count'
    lock_threshold = 5
    cooldown_seconds = 15 * 60  # 15 minutos
    window_seconds = 10 * 60    # ventana de 10 minutos

    def get_fail_count(self, request):
        try:
            return int(request.session.get(self.session_key, 0))
        except Exception:
            return 0

    def set_fail_count(self, request, value):
        request.session[self.session_key] = int(value)
        request.session.modified = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        count = self.get_fail_count(self.request)
        ctx['fail_count'] = count
        ctx['fail_lock'] = count >= self.lock_threshold
        ctx['fail_threshold'] = self.lock_threshold
        # Estado de bloqueo persistente por usuario+IP
        username = (self.request.POST.get('username') or '').strip()
        ip = self._get_ip(self.request)
        if username:
            lt = LoginThrottle.objects.filter(username__iexact=username, ip=ip).first()
            if lt and lt.is_locked():
                ctx['fail_lock'] = True
                ctx['cooldown_remaining'] = lt.remaining_seconds()
        return ctx

    def form_invalid(self, form):
        count = self.get_fail_count(self.request) + 1
        self.set_fail_count(self.request, count)
        # Registrar intento fallido persistente
        username = (self.request.POST.get('username') or '').strip()
        ip = self._get_ip(self.request)
        if username:
            lt, _ = LoginThrottle.objects.get_or_create(username=username, ip=ip)
            lt.register_fail(window_seconds=self.window_seconds,
                             threshold=self.lock_threshold,
                             cooldown_seconds=self.cooldown_seconds)
        return super().form_invalid(form)

    def form_valid(self, form):
        # Credenciales correctas: resetear contador y registros
        self.set_fail_count(self.request, 0)
        username = (self.request.POST.get('username') or '').strip()
        ip = self._get_ip(self.request)
        if username:
            try:
                lt = LoginThrottle.objects.filter(username__iexact=username, ip=ip).first()
                if lt:
                    lt.count = 0
                    lt.locked_until = None
                    lt.first_attempt = lt.last_attempt = timezone.now()
                    lt.save()
            except Exception:
                pass
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        # Bloqueo por sesión
        if self.get_fail_count(request) >= self.lock_threshold:
            form = self.get_form()
            try:
                form.add_error(None, "Demasiados intentos fallidos. Restablece tu contraseña o espera.")
            except Exception:
                pass
            context = self.get_context_data(form=form)
            return self.render_to_response(context)
        # Bloqueo persistente por usuario+IP
        username = (request.POST.get('username') or '').strip()
        ip = self._get_ip(request)
        if username:
            lt = LoginThrottle.objects.filter(username__iexact=username, ip=ip).first()
            if lt and lt.is_locked():
                form = self.get_form()
                try:
                    form.add_error(None, "Demasiados intentos fallidos. Intenta más tarde o restablece tu contraseña.")
                except Exception:
                    pass
                context = self.get_context_data(form=form)
                return self.render_to_response(context)
        return super().post(request, *args, **kwargs)

    def _get_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')



def serve_static_schema(request):
    """Sirve un esquema OpenAPI estático si existe (schema.yaml/json en BASE_DIR).

    Útil en Windows cuando la vista dinámica de drf-spectacular falla
    al escribir advertencias en stderr (OSError 22).
    """
    import os
    from django.conf import settings
    base = getattr(settings, 'BASE_DIR', os.getcwd())
    yaml_path = os.path.join(base, 'schema.yaml')
    json_path = os.path.join(base, 'schema.json')
    if os.path.exists(yaml_path):
        with open(yaml_path, 'rb') as f:
            data = f.read()
        return HttpResponse(data, content_type='application/yaml')
    if os.path.exists(json_path):
        with open(json_path, 'rb') as f:
            data = f.read()
        return HttpResponse(data, content_type='application/json')
    return HttpResponse('Schema no encontrado. Generá con: manage.py spectacular --file schema.yaml', status=404)


def serve_schema_json(request):
    """Sirve exclusivamente schema.json desde BASE_DIR si existe."""
    import os
    from django.conf import settings
    base = getattr(settings, 'BASE_DIR', os.getcwd())
    json_path = os.path.join(base, 'schema.json')
    if os.path.exists(json_path):
        with open(json_path, 'rb') as f:
            data = f.read()
        return HttpResponse(data, content_type='application/json')
    return HttpResponse('schema.json no encontrado. Generá con: manage.py spectacular --file schema.json --format openapi-json', status=404)
