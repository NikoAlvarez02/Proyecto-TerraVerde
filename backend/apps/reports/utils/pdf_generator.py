from io import BytesIO
import logging
from datetime import datetime
from pathlib import Path
import base64

from django.template.loader import render_to_string
from django.conf import settings

try:
    from weasyprint import HTML, CSS  # type: ignore
except Exception:  # pragma: no cover
    HTML = None  # fallback a reportlab

try:
    from reportlab.pdfgen import canvas  # type: ignore
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
    # Usar file:/// para que WeasyPrint resuelva rutas relativas a ROOT_DIR
    try:
        root = Path(getattr(settings, 'ROOT_DIR', settings.BASE_DIR)).resolve()
        base_url = root.as_uri()  # file:///...
    except Exception:
        base_url = str(getattr(settings, 'ROOT_DIR', settings.BASE_DIR))
    buf = BytesIO()
    try:
        HTML(string=html_str, base_url=base_url).write_pdf(target=buf)
        return buf.getvalue()
    except Exception:
        logging.getLogger(__name__).exception("WeasyPrint fallo al generar PDF desde %s", template_name)
        return None


def _simple_pdf(title: str, lines: list[str], size='A4', orient='portrait') -> bytes:
    buf = BytesIO()
    if canvas:
        ps = _page_size(size, orient)
        from reportlab.lib.pagesizes import landscape as rl_landscape, portrait as rl_portrait  # type: ignore
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
    # Fallback textual mÃ­nimo
    buf.write((title + "\n\n").encode("utf-8"))
    for ln in lines:
        buf.write((str(ln) + "\n").encode("utf-8"))
    return buf.getvalue()


def _load_logo_base64() -> str | None:
    """Busca un logo en varias ubicaciones conocidas y lo devuelve en base64.

    Esto evita depender de rutas estÃ¡ticas absolutas ("/static/..."), que WeasyPrint
    no puede resolver en algunos despliegues. Al incrustar la imagen como data URI,
    garantizamos que aparezca en todos los PDFs.
    """
    try:
        candidates: list[Path] = []
        # 0) Usar el buscador de staticfiles si estÃ¡ disponible (post-collectstatic)
        try:
            from django.contrib.staticfiles import finders  # type: ignore
            for name in ("ASSETS/terraverde.png", "ASSETS/logo.png", "ASSETS/logo_trifusion.png"):
                fp = finders.find(name)
                if fp:
                    p = Path(fp)
                    if p.exists():
                        candidates.append(p)
        except Exception:
            pass
        root = Path(getattr(settings, 'ROOT_DIR', settings.BASE_DIR)).resolve()
        # 1) Carpeta de frontend en el repo
        fe = root / 'frontend' / 'ASSETS'
        candidates += [fe / n for n in (
            'logo.png',
            'logo_trifusion.png',
            'terraverde.png',
        )]
        # 2) STATIC_ROOT (si existe en despliegue)
        try:
            static_root = Path(getattr(settings, 'STATIC_ROOT')) if hasattr(settings, 'STATIC_ROOT') else None
            if static_root:
                se = static_root / 'ASSETS'
                candidates += [se / n for n in (
                    'logo.png', 'logo_trifusion.png', 'terraverde.png'
                )]
        except Exception:
            pass
        # 3) MEDIA_ROOT por si el logo se sube como archivo administrable
        try:
            media_root = Path(getattr(settings, 'MEDIA_ROOT', ''))
            if media_root:
                candidates += [media_root / 'logo.png', media_root / 'logo.jpg', media_root / 'logo.jpeg']
        except Exception:
            pass

        for path in candidates:
            try:
                if path and path.exists() and path.is_file():
                    data = path.read_bytes()
                    return base64.b64encode(data).decode('utf-8')
            except Exception:
                continue
    except Exception:
        pass
    return None


def _logo_file_uri() -> str | None:
    """Devuelve file:///... del logo si está disponible.
    WeasyPrint soporta URIs de archivo absolutas; esto evita depender de /static.
    """
    try:
        candidates = []
        # Buscar con staticfiles
        try:
            from django.contrib.staticfiles import finders  # type: ignore
            for name in ("ASSETS/terraverde.png", "ASSETS/logo.png", "ASSETS/logo_trifusion.png"):
                fp = finders.find(name)
                if fp:
                    candidates.append(Path(fp))
        except Exception:
            pass
        # Rutas locales del repo y STATIC_ROOT/MEDIA_ROOT
        try:
            root = Path(getattr(settings, 'ROOT_DIR', settings.BASE_DIR)).resolve()
            candidates += [root / 'frontend' / 'ASSETS' / n for n in ('terraverde.png','logo.png','logo_trifusion.png')]
        except Exception:
            pass
        try:
            static_root = Path(getattr(settings, 'STATIC_ROOT')) if hasattr(settings, 'STATIC_ROOT') else None
            if static_root:
                candidates += [static_root / 'ASSETS' / n for n in ('terraverde.png','logo.png','logo_trifusion.png')]
        except Exception:
            pass
        try:
            media_root = Path(getattr(settings, 'MEDIA_ROOT', ''))
            if media_root:
                candidates += [media_root / n for n in ('logo.png','logo.jpg','logo.jpeg')]
        except Exception:
            pass
        for p in candidates:
            try:
                if p and p.exists() and p.is_file():
                    return p.resolve().as_uri()
            except Exception:
                continue
    except Exception:
        pass
    return None


def generate_patient_history_pdf(paciente, observaciones, params: dict, summary: dict | None = None, avatar_b64: str | None = None) -> bytes:
    ctx = {
        'generado': datetime.now(),
        'paciente': paciente,
        'observaciones': observaciones,
        'params': params,
        'sum_prof': (summary or {}).get('profesionales', []),
        'sum_diag': (summary or {}).get('diagnosticos', []),
        'sum_estudios': (summary or {}).get('estudios', []),
        'logo_b64': _load_logo_base64(),
        'logo_uri': _logo_file_uri(),
        'avatar_b64': avatar_b64,
    }
    # Usar nueva plantilla UTF-8 con sello
    pdfb = _weasy_pdf_from_template('reports/pdf/patient_history_v2.html', ctx, params)
    if pdfb:
        return pdfb
    # Fallback simple
    title = f"Historia ClÃ­nica - {paciente}"
    lines = [
        f"Generado: {datetime.now():%Y-%m-%d %H:%M}",
        f"Paciente: {paciente}",
        f"Total observaciones: {len(observaciones)}",
    ]
    if summary:
        lines.append("Profesionales:")
        for p in summary.get('profesionales', []):
            lines.append(f"  - {p.get('profesional')} ({p.get('c')})")
        lines.append("DiagnÃ³sticos:")
        for d in summary.get('diagnosticos', []):
            dx = d.get('diagnostico_texto') or ''
            code = d.get('diagnostico_codigo') or ''
            lines.append(f"  - {dx} {f'({code})' if code else ''} Â· {d.get('c')}")
        lines.append("Estudios:")
        for e in summary.get('estudios', []):
            lines.append(f"  - {e.get('nombre')} Â· {e.get('c')}")
    for o in observaciones:
        lines.append(f"{o.fecha_hora:%Y-%m-%d %H:%M} - {o.profesional}: {o.motivo} / {o.diagnostico_texto}")
    return _simple_pdf(title, lines, params.get('tamano_pagina','A4'), params.get('orientacion','portrait'))


def generate_chart_image(title: str, labels: list[str], values: list[float]):
    """
    Devuelve una estructura simple de grÃ¡fico para plantillas/fallback.
    { 'title': str, 'labels': [str], 'values': [float] }
    """
    try:
        safe_labels = [str(l) for l in (labels or [])]
    except Exception:
        safe_labels = []
    safe_values = []
    for v in (values or []):
        try:
            safe_values.append(float(v))
        except Exception:
            safe_values.append(0.0)
    if len(safe_values) < len(safe_labels):
        safe_values += [0.0] * (len(safe_labels) - len(safe_values))
    if len(safe_labels) < len(safe_values):
        safe_labels += [''] * (len(safe_values) - len(safe_labels))
    return {
        'title': str(title or ''),
        'labels': safe_labels,
        'values': safe_values,
    }


def generate_statistical_report_pdf(title: str, resumen: dict, params: dict, charts=None, avatar_b64: str | None = None) -> bytes:
    """
    Genera un PDF para reportes estadÃ­sticos. Usa WeasyPrint si estÃ¡ disponible,
    cae a un PDF simple si hay errores.
    """
    # Preparar bloques de grÃ¡ficos (barras CSS) si hay datos
    chart_blocks = []
    try:
        for ch in charts or []:
            if not isinstance(ch, dict):
                continue
            labels = ch.get('labels') or []
            values = ch.get('values') or []
            vmax = max([float(v) for v in values] or [0.0]) or 1.0
            rows = []
            for lab, val in zip(labels, values):
                fv = float(val)
                perc = int(round((fv / vmax) * 100)) if vmax else 0
                rows.append({'label': str(lab), 'value': fv, 'perc': perc})
            chart_blocks.append({'title': ch.get('title') or '', 'rows': rows, 'max': vmax})
    except Exception:
        chart_blocks = []

    # Calcular total general robusto
    total = None
    try:
        total = (resumen or {}).get('total_atenciones')
        if total is None:
            total = (resumen or {}).get('total')
        if total is None:
            for key in ('por_centro', 'productividad', 'por_profesional', 'por_cie10', 'top_diagnosticos'):
                seq = (resumen or {}).get(key) or []
                if isinstance(seq, (list, tuple)) and seq:
                    total = sum(float(it.get('c', 0) or 0) for it in seq)
                    break
    except Exception:
        total = None

    ctx = {
        'generado': datetime.now(),
        'titulo': title,
        'resumen': resumen or {},
        'params': params or {},
        'charts': charts or [],
        'chart_blocks': chart_blocks,
        'total': total,
        'logo_b64': _load_logo_base64(),
        'logo_uri': _logo_file_uri(),
        'avatar_b64': avatar_b64,
    }
    for tpl in (
        'reports/pdf/statistics.html',
        'reports/pdf/statistical.html',
        'reports/pdf/estadistico.html',
    ):
        pdfb = _weasy_pdf_from_template(tpl, ctx, params or {})
        if pdfb:
            return pdfb

    lines: list[str] = []
    try:
        for k, v in (resumen or {}).items():
            if isinstance(v, (list, tuple)):
                lines.append(f"{k}:")
                for it in list(v)[:10]:
                    lines.append(f"  - {it}")
                if len(v) > 10:
                    lines.append(f"  ... (+{len(v)-10} mÃ¡s)")
            elif isinstance(v, dict):
                lines.append(f"{k}:")
                shown = 0
                for sk, sv in v.items():
                    lines.append(f"  - {sk}: {sv}")
                    shown += 1
                    if shown >= 10:
                        lines.append("  ... (mÃ¡s)")
                        break
            else:
                lines.append(f"{k}: {v}")
    except Exception:
        lines.append("[No se pudo expandir el resumen]")

    if charts:
        lines.append("")
        lines.append("GrÃ¡ficos:")
        for ch in charts:
            try:
                title_ch = (ch or {}).get('title', '') if isinstance(ch, dict) else ''
                labels = (ch or {}).get('labels', []) if isinstance(ch, dict) else []
                values = (ch or {}).get('values', []) if isinstance(ch, dict) else []
                lines.append(f"  {title_ch}")
                vmax = max([float(v) for v in values] or [0.0])
                scale = 40.0 / vmax if vmax > 0 else 1.0
                for lab, val in zip(labels, values):
                    n = int(float(val) * scale)
                    bar = '#'*n
                    lines.append(f"   - {lab}: {val} {bar}")
            except Exception:
                lines.append("  [No se pudo renderizar el grÃ¡fico]")

    return _simple_pdf(str(title or 'Reporte EstadÃ­stico'), lines, (params or {}).get('tamano_pagina','A4'), (params or {}).get('orientacion','portrait'))


def generate_epicrisis_pdf(paciente, resumen: dict, params: dict, avatar_b64: str | None = None) -> bytes:
    ctx = {
        'generado': datetime.now(),
        'paciente': paciente,
        'resumen': resumen,
        'params': params,
        'logo_b64': _load_logo_base64(),
        'logo_uri': _logo_file_uri(),
        'avatar_b64': avatar_b64,
    }
    # Plantilla nueva con sello y UTF-8
    pdfb = _weasy_pdf_from_template('reports/pdf/epicrisis_v2.html', ctx, params)
    if pdfb:
        return pdfb
    # Fallback simple
    title = f"Epicrisis - {paciente}"
    lines = [f"{k}: {v}" for k, v in resumen.items()]
    return _simple_pdf(title, lines, params.get('tamano_pagina','A4'), params.get('orientacion','portrait'))


def generate_certificate_pdf(paciente, profesional, datos: dict, params: dict, avatar_b64: str | None = None) -> bytes:
    ctx = {
        'generado': datetime.now(),
        'paciente': paciente,
        'profesional': profesional,
        'datos': datos,
        'params': params,
        'logo_b64': _load_logo_base64(),
        'logo_uri': _logo_file_uri(),
        'avatar_b64': avatar_b64,
    }
    # Plantilla nueva con sello y UTF-8
    pdfb = _weasy_pdf_from_template('reports/pdf/certificate_v2.html', ctx, params)
    if pdfb:
        return pdfb
    # Fallback simple
    title = f"Certificado - {paciente}"
    lines = [
        f"Profesional: {profesional}",
        f"DiagnÃ³stico: {datos.get('diagnostico','')} ",
        f"Reposo (dÃ­as): {datos.get('reposo_dias','')}",
        f"Observaciones: {datos.get('observaciones','')} ",
    ]
    return _simple_pdf(title, lines, params.get('tamano_pagina','A4'), params.get('orientacion','portrait'))
