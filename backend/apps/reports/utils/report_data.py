from django.db.models import Count
from apps.medical_records.models import Observation


def get_attendance_statistics(params: dict) -> dict:
    qs = Observation.objects.all()
    desde = params.get('desde')
    hasta = params.get('hasta')
    if desde:
        qs = qs.filter(fecha_hora__date__gte=desde)
    if hasta:
        qs = qs.filter(fecha_hora__date__lte=hasta)
    total = qs.count()
    por_centro = qs.values('centro__nombre').annotate(c=Count('id')).order_by('-c')
    por_prof = qs.values('profesional__apellido', 'profesional__nombre').annotate(c=Count('id')).order_by('-c')
    top_diag = qs.values('diagnostico_texto').annotate(c=Count('id')).order_by('-c')[:20]
    return {
        'total_atenciones': total,
        'por_centro': list(por_centro),
        'por_profesional': list(por_prof),
        'top_diagnosticos': list(top_diag),
    }


def get_professional_productivity(params: dict) -> dict:
    qs = Observation.objects.all()
    por_prof = qs.values('profesional__apellido', 'profesional__nombre').annotate(c=Count('id')).order_by('-c')
    return {'productividad': list(por_prof)}


def get_epidemiological_data(params: dict) -> dict:
    qs = Observation.objects.all()
    por_cie = qs.values('diagnostico_codigo').annotate(c=Count('id')).order_by('-c')
    return {'por_cie10': list(por_cie)}

