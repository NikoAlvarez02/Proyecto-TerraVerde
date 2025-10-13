from rest_framework import viewsets, permissions
from .models import Center
from .serializers import CenterSerializer


class CenterViewSet(viewsets.ModelViewSet):
    queryset = Center.objects.all().order_by('nombre')
    serializer_class = CenterSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['codigo', 'nombre', 'direccion', 'email', 'telefono']
    filterset_fields = ['activo', 'matriz']
    ordering_fields = ['nombre', 'codigo']

