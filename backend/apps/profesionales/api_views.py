from rest_framework import viewsets
from .models import Profesional
from .serializers import ProfesionalSerializer

class ProfesionalViewSet(viewsets.ModelViewSet):
    queryset = Profesional.objects.all().order_by("apellido", "nombre")
    serializer_class = ProfesionalSerializer
