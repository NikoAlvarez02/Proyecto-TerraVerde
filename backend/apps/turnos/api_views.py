from rest_framework import viewsets, permissions
from .models import Turno
from .serializers import TurnoSerializer
from datetime import datetime, timedelta, time
from django.utils import timezone
from rest_framework.response import Response


class TurnoViewSet(viewsets.ModelViewSet):
    queryset = (
        Turno.objects
        .select_related("paciente", "profesional")
        .all()
        .order_by("-fecha_hora")
    )
    serializer_class = TurnoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    # filtros y orden (rango por fecha con lookups)
    filterset_fields = {
        "estado": ["exact"],
        "profesional": ["exact"],
        "paciente": ["exact"],
        "fecha_hora": ["date__gte", "date__lte"],
    }
    search_fields = [
        "paciente__apellido", "paciente__nombre",
        "profesional__apellido", "profesional__nombre",
        "motivo", "observaciones"
    ]
    ordering_fields = ["fecha_hora", "creado", "actualizado", "estado"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, 'user', None)
        perfil = getattr(user, 'perfil', None) if user and user.is_authenticated else None
        if not perfil:
            # Sin perfil: permitir a staff/superusuario ver todo; resto, nada.
            # IMPORTANTE: no retornar aquÃ­ para permitir que se apliquen
            # los filtros de fecha/rango aunque sea staff/superuser.
            u = user
            if not (u and (u.is_staff or u.is_superuser)):
                return qs.none()
        # Profesional: ve solo sus turnos (a menos que pueda gestionar turnos)
        if perfil.rol == 'prof' and not perfil.puede_gestionar_turnos:
            if perfil.profesional:
                qs = qs.filter(profesional=perfil.profesional)
            else:
                return qs.none()
        # Prefiltro robusto por fecha exacta (?fecha=YYYY-MM-DD)
        try:
            fecha = (self.request.query_params.get('fecha') or '').strip()
            if fecha:
                d = datetime.strptime(fecha, '%Y-%m-%d').date()
                tz = timezone.get_current_timezone()
                start = timezone.make_aware(datetime.combine(d, time.min), tz)
                end = start + timedelta(days=1)
                qs = qs.filter(fecha_hora__gte=start, fecha_hora__lt=end)
        except Exception:
            pass

        # Si vienen rangos ?fecha_hora__date__gte / __lte, aplicarlos con TZ local
        try:
            d_from = (self.request.query_params.get('fecha_hora__date__gte') or '').strip()
            d_to = (self.request.query_params.get('fecha_hora__date__lte') or '').strip()
            tz = timezone.get_current_timezone()
            range_filters = {}
            if d_from:
                df = datetime.strptime(d_from, '%Y-%m-%d').date()
                start = timezone.make_aware(datetime.combine(df, time.min), tz)
                range_filters['fecha_hora__gte'] = start
            if d_to:
                dt = datetime.strptime(d_to, '%Y-%m-%d').date()
                end = timezone.make_aware(datetime.combine(dt, time.max), tz)
                # usar < (dÃ­a siguiente) para evitar problemas de precisiÃ³n
                end_excl = end + timedelta(seconds=1)
                range_filters['fecha_hora__lt'] = end_excl
            if range_filters:
                qs = qs.filter(**range_filters)
        except Exception:
            pass
        return qs

    def filter_queryset(self, queryset):
        """Aplica filtros estándar y luego, si viene `?fecha=YYYY-MM-DD`,
        fuerza el filtro por porción de fecha para retornar solo ese día.
        Esto garantiza el comportamiento incluso si otras capas no lo aplican.
        """
        qs = super().filter_queryset(queryset)
        fecha_str = (self.request.query_params.get('fecha') or '').strip()
        if fecha_str:
            try:
                d = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                qs = qs.filter(fecha_hora__date=d)
            except Exception:
                pass
        return qs



    def list(self, request, *args, **kwargs):
        """Enforce `?fecha=YYYY-MM-DD` filter at the final step to avoid
        any leakage of registros de otras fechas por efectos colaterales.
        """
        qs = self.filter_queryset(self.get_queryset())
        fecha_str = (request.query_params.get('fecha') or '').strip()
        if fecha_str:
            try:
                d = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                qs = qs.filter(fecha_hora__date=d)
            except Exception:
                pass
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
