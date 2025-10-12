from io import BytesIO
from datetime import datetime
from django.template.loader import render_to_string
from django.conf import settings

try:
    from weasyprint import HTML, CSS  # type: ignore
except Exception:  # pragma: no cover
    HTML = None  # fallback a reportlab

try:
    from reportlab.pdfgen import canvas  # type: ignore
    from reportlab.lib.pagesizes import A4, LETTER, legal
    from reportlab.lib.pagesizes import landscape, portrait
except Exception:  # pragma: no cover
    canvas = None


def _page_size(size: str, orient: str):
    sizes = {
        'A4': (595.27, 841.89),  # points
        'Letter': (612, 792),
        'Legal': (612, 1008),
    }
    base = sizes.get(size, sizes['A4'])
    if orient == 'landscape':
        return (base[1], base[0])
    return base


def _weasy_pdf_from_template(template_name: str, context: dict, params: dict) -> bytes | None:
    if HTML is None:
        return None
    html_str = render_to_string(template_name, context)
    base_url = str(getattr(settings, 'ROOT_DIR', settings.BASE_DIR))  # acceso a estáticos/plantillas
    buf = BytesIO()
    try:
        HTML(string=html_str, base_url=base_url).write_pdf(target=buf)
        return buf.getvalue()
    except Exception:
        return None


def _simple_pdf(title: str, lines: list[str], size='A4', orient='portrait') -> bytes:
    buf = BytesIO()
    if canvas:
        ps = _page_size(size, orient)
        c = canvas.Canvas(buf, pagesize=ps)
        width, height = ps
        c.setTitle(title)
        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, title)
        c.setFont("Helvetica", 10)
        y -= 30
        for ln in lines:
            if y < 60:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
            c.drawString(40, y, str(ln))
            y -= 14
        c.showPage()
        c.save()
        return buf.getvalue()
    # Fallback textual
    buf.write((title + "\n\n").encode("utf-8"))
    for ln in lines:
        buf.write((str(ln) + "\n").encode("utf-8"))
    return buf.getvalue()


def generate_patient_history_pdf(paciente, observaciones, params: dict, summary: dict | None = None) -> bytes:
    ctx = {
        'generado': datetime.now(),
        'paciente': paciente,
        'observaciones': observaciones,
        'params': params,
        'sum_prof': (summary or {}).get('profesionales', []),
        'sum_diag': (summary or {}).get('diagnosticos', []),
        'sum_estudios': (summary or {}).get('estudios', []),
    }
    pdfb = _weasy_pdf_from_template('reports/pdf/patient_history.html', ctx, params)
    if pdfb:
        return pdfb
    # Fallback simple
    title = f"Historia Clínica - {paciente}"
    lines = [
        f"Generado: {datetime.now():%Y-%m-%d %H:%M}",
        f"Paciente: {paciente}",
        f"Total observaciones: {len(observaciones)}",
    ]
    # Resumen en texto
    if summary:
        lines.append("Profesionales:")
        for p in summary.get('profesionales', []):
            lines.append(f"  - {p.get('profesional')} ({p.get('c')})")
        lines.append("Diagnósticos:")
        for d in summary.get('diagnosticos', []):
            dx = d.get('diagnostico_texto') or ''
            code = d.get('diagnostico_codigo') or ''
            lines.append(f"  - {dx} {f'({code})' if code else ''} · {d.get('c')}")
        lines.append("Estudios:")
        for e in summary.get('estudios', []):
            lines.append(f"  - {e.get('nombre')} · {e.get('c')}")
    for o in observaciones:
        lines.append(f"{o.fecha_hora:%Y-%m-%d %H:%M} - {o.profesional}: {o.motivo} / {o.diagnostico_texto}")
    return _simple_pdf(title, lines, params.get('tamano_pagina','A4'), params.get('orientacion','portrait'))


def generate_epicrisis_pdf(paciente, resumen: dict, params: dict) -> bytes:
    ctx = {
        'generado': datetime.now(),
        'paciente': paciente,
        'resumen': resumen,
        'params': params,
    }
    pdfb = _weasy_pdf_from_template('reports/pdf/epicrisis.html', ctx, params)
    if pdfb:
        return pdfb
    # Fallback a contenido simple
    title = f"Epicrisis - {paciente}"
    lines = [f"{k}: {v}" for k, v in resumen.items()]
    return _simple_pdf(title, lines, params.get('tamano_pagina','A4'), params.get('orientacion','portrait'))


def generate_certificate_pdf(paciente, profesional, datos: dict, params: dict) -> bytes:
    ctx = {
        'generado': datetime.now(),
        'paciente': paciente,
        'profesional': profesional,
        'datos': datos,
        'params': params,
    }
    pdfb = _weasy_pdf_from_template('reports/pdf/certificate.html', ctx, params)
    if pdfb:
        return pdfb
    # Fallback simple
    title = f"Certificado - {paciente}"
    lines = [
        f"Profesional: {profesional}",
        f"Diagnóstico: {datos.get('diagnostico','')} ",
        f"Reposo (días): {datos.get('reposo_dias','')}",
        f"Observaciones: {datos.get('observaciones','')} ",
    ]
    return _simple_pdf(title, lines, params.get('tamano_pagina','A4'), params.get('orientacion','portrait'))
