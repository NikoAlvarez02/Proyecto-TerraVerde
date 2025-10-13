from rest_framework import viewsets, permissions
from .models import Turno
from .serializers import TurnoSerializer


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
    # filtros y orden (rango por fecha)
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
    filterset_fields = [
        "estado", "profesional", "paciente", "fecha_hora"
    ]
    ordering_fields = ["fecha_hora", "creado", "actualizado", "estado"]
