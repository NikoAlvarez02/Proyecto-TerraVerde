from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from .serializers import UsuarioSerializer
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

User = get_user_model()

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]


@login_required
def usuarios_admin_view(request):
    u = request.user
    perfil = getattr(u, 'perfil', None)
    is_admin = (u.is_staff or (perfil and (getattr(perfil, 'rol', None) == 'admin' or getattr(perfil, 'puede_admin_usuarios', False))))
    if not is_admin:
        raise PermissionDenied("No autorizado")
    return render(request, 'usuarios/usuarios_list.html')
