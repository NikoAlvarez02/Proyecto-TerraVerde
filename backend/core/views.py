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
