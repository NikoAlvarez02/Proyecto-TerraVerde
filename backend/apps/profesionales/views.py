from rest_framework import viewsets
from .models import Profesional
from .serializers import ProfesionalSerializer

class ProfesionalViewSet(viewsets.ModelViewSet):
    queryset = Profesional.objects.all()
    serializer_class = ProfesionalSerializer
