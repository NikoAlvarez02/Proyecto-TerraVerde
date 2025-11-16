from rest_framework import viewsets, permissions, filters
from django.utils import timezone
from .models import Profesional, ProfesionalHorario, Especialidad
from .serializers import ProfesionalSerializer, ProfesionalHorarioSerializer, EspecialidadSerializer

class ProfesionalViewSet(viewsets.ModelViewSet):
    queryset = Profesional.objects.all().order_by("apellido", "nombre")
    serializer_class = ProfesionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["dni", "nombre", "apellido", "matricula", "especialidad__nombre", "email"]
    filterset_fields = ["activo", "especialidad", "centros"]
    ordering_fields = ["apellido", "nombre", "dni", "matricula", "fecha_alta"]
    pagination_class = None

    def perform_destroy(self, instance):
        instance.activo = False
        instance.fecha_baja = timezone.now()
        instance.save(update_fields=["activo", "fecha_baja"])

    def get_queryset(self):
        qs = super().get_queryset()
        include_inactive = str(self.request.query_params.get('include_inactive', '')).lower() in ('1', 'true', 'yes')
        if not include_inactive:
            qs = qs.filter(activo=True)
        return qs


class ProfesionalHorarioViewSet(viewsets.ModelViewSet):
    queryset = ProfesionalHorario.objects.all()
    serializer_class = ProfesionalHorarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["profesional", "centro", "dia_semana", "activo"]
    ordering_fields = ["profesional", "centro", "dia_semana", "hora_inicio"]
    pagination_class = None


class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all().order_by('nombre')
    serializer_class = EspecialidadSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['nombre']
    pagination_class = None
