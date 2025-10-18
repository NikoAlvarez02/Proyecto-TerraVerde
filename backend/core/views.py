# # backend/core/views.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# @login_required
# def vista_admin_mod(request):
#     # Solo admins pueden entrar a esta pantalla
#     if not hasattr(request.user, "perfil") or request.user.perfil.rol != "admin":
#         # plantilla simple de “no autorizado”
#         return render(request, "administracion/no_autorizado.html", status=403)
#     return render(request, "administracion/administrador.html")
import logging
import traceback
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Avg
from django.db.utils import DatabaseError, ProgrammingError

from apps.turnos.models import Turno
from apps.pacientes.models import Paciente
from apps.feedback.models import Satisfaccion

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
    except Exception as e:
        logger.exception("[weasy] Error generando PDF")
        if settings.DEBUG:
            # Mostrar traza en pantalla para diagnóstico rápido
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

    # Pacientes activos
    pacientes_activos = Paciente.objects.filter(activo=True).count()

    # Sesiones (turnos) de hoy
    turnos_hoy_qs = Turno.objects.filter(fecha_hora__date=hoy)
    sesiones_hoy_total = turnos_hoy_qs.count()
    sesiones_hoy_completadas = turnos_hoy_qs.filter(estado='atendido').count()
    sesiones_hoy_pendientes = turnos_hoy_qs.filter(estado__in=['pendiente', 'confirmado']).count()
    sesiones_hoy_pct = int(round((sesiones_hoy_completadas / sesiones_hoy_total) * 100)) if sesiones_hoy_total else 0

    # Progreso: % atendidos últimos 30 días
    hace_30 = hoy - timezone.timedelta(days=30)
    turnos_30_qs = Turno.objects.filter(fecha_hora__date__gte=hace_30, fecha_hora__date__lte=hoy)
    total_30 = turnos_30_qs.count()
    atendidos_30 = turnos_30_qs.filter(estado='atendido').count()
    tasa_progreso = int(round((atendidos_30 / total_30) * 100)) if total_30 else 0

    # Satisfacción: promedio últimos 30 días (1 a 5)
    # Cálculo robusto: si la tabla aún no existe (sin migrar), evitar caída
    try:
        sats_qs = Satisfaccion.objects.filter(fecha__date__gte=hace_30, fecha__date__lte=hoy)
        promedio = sats_qs.aggregate(avg=Avg('puntaje')).get('avg')
    except (DatabaseError, ProgrammingError):
        promedio = None
    satisfaccion = round(promedio, 1) if promedio else None
    satisfaccion_pct = int(round((promedio / 5) * 100)) if promedio else 0
    satisfaccion_pct = 0

    # Próximas sesiones de hoy (futuras a partir de ahora)
    proximas = (
        turnos_hoy_qs
        .filter(fecha_hora__gte=ahora)
        .select_related('paciente')
        .order_by('fecha_hora')[:5]
    )

    # Notificación próxima sesión real (si ocurre en la próxima hora)
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

    # Estadísticas semanales: últimos 7 días (incluye hoy)
    dias = []
    for i in range(6, -1, -1):
        dia = hoy - timezone.timedelta(days=i)
        cnt = Turno.objects.filter(fecha_hora__date=dia).count()
        dias.append((dia, cnt))

    max_cnt = max((c for _, c in dias), default=1)
    nombres = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    weekly = []
    for dia, cnt in dias:
        idx = dia.weekday()  # 0=Lun .. 6=Dom
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
    }

    return render(request, 'paginaprincipal.html', ctx)
