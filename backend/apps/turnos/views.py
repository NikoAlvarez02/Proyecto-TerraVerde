from rest_framework import viewsets
from .models import Turno
from .serializers import TurnoSerializer   # <- acá el cambio

class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
