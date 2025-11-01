from rest_framework import viewsets, permissions, decorators, response, status
from django.db.models import Q
from .models import Observation
from .serializers import ObservationSerializer


class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.select_related('paciente', 'profesional', 'centro').all()
    serializer_class = ObservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['profesional', 'centro', 'paciente', 'diagnostico_codigo']
    search_fields = ['motivo', 'diagnostico_texto', 'estudios_solicitados', 'tratamiento', 'indicaciones']
    ordering_fields = ['fecha_hora', 'creado', 'actualizado']
    ordering = ['-fecha_hora']

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, 'user', None)
        perfil = getattr(user, 'perfil', None) if user and user.is_authenticated else None
        if not perfil:
            u = user
            return qs if (u and (u.is_staff or u.is_superuser)) else qs.none()
        # Profesionales: pueden ver sus propias observaciones y/o de sus pacientes asignados
        if perfil.rol == 'prof' and perfil.profesional:
            from apps.pacientes.models import Paciente
            qs = qs.filter(
                Q(profesional=perfil.profesional) |
                Q(paciente__profesionales_asignados=perfil.profesional)
            ).distinct()
        return qs

    @decorators.action(methods=['get'], detail=False, url_path='buscar-por-fecha')
    def buscar_por_fecha(self, request):
        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')
        qs = self.get_queryset()
        if desde:
            qs = qs.filter(fecha_hora__date__gte=desde)
        if hasta:
            qs = qs.filter(fecha_hora__date__lte=hasta)
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return response.Response(ser.data)

