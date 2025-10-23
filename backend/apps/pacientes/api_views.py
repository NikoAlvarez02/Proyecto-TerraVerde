# backend/apps/pacientes/api_views.py
from rest_framework import viewsets, permissions
from .models import Paciente
from .serializers import PacienteSerializer


class PacienteViewSet(viewsets.ModelViewSet):
    serializer_class = PacienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["dni", "nombre", "apellido", "email", "obra_social"]
    filterset_fields = ["activo", "obra_social"]
    ordering_fields = ["apellido", "nombre", "dni", "fecha_registro"]
    ordering = ["-fecha_registro"]
    pagination_class = None  # devolver lista plana para compatibilidad estable del frontend

    def get_queryset(self):
        return Paciente.objects.all().order_by(*self.ordering)
