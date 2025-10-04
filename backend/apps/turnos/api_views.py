from rest_framework import viewsets
from .models import Turno
from .serializers import TurnoSerializer

class TurnoViewSet(viewsets.ModelViewSet):
   
    # DESPUÉS (ordena por tu DateTimeField real)
    queryset = (
    Turno.objects
    .select_related("paciente", "profesional")
    .all()
    .order_by("-fecha_hora")
)


    serializer_class = TurnoSerializer
