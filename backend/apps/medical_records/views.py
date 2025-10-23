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

