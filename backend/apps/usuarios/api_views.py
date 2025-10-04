from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from .serializers import UsuarioSerializer

User = get_user_model()

class AdminOrSelfReadOnly(permissions.BasePermission):
    """
    - Lectura (GET/HEAD/OPTIONS): cualquier autenticado.
      * En objeto: puede leer su propio user o, si es staff, cualquier user.
    - Escritura (POST/PUT/PATCH/DELETE): sólo staff.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_staff or obj.pk == request.user.pk
        return request.user.is_staff

class UsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    permission_classes = [AdminOrSelfReadOnly]

    def get_queryset(self):
        # staff ve todos; no staff sólo a sí mismo
        qs = User.objects.all().order_by("username")
        if self.request.user.is_staff:
            return qs
        return qs.filter(pk=self.request.user.pk)
