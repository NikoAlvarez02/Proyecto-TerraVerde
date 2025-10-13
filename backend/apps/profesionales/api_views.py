from rest_framework import viewsets, permissions
from .models import Profesional, ProfesionalHorario
from .serializers import ProfesionalSerializer, ProfesionalHorarioSerializer

class ProfesionalViewSet(viewsets.ModelViewSet):
    queryset = Profesional.objects.all().order_by("apellido", "nombre")
    serializer_class = ProfesionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["dni", "nombre", "apellido", "matricula", "especialidad", "email"]
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
