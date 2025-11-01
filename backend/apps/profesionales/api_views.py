from rest_framework import viewsets, permissions, filters
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
