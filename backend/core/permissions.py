from rest_framework import permissions


class PerfilTieneAtributoPerm(permissions.BasePermission):
    """Verifica que el usuario autenticado tenga un atributo True en su perfil."""

    attr_name = None

    def __init__(self, attr_name=None):
        if attr_name:
            self.attr_name = attr_name

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        perfil = getattr(request.user, 'perfil', None)
        if not perfil or not self.attr_name:
            return False
        return bool(getattr(perfil, self.attr_name, False))


def require_perfil_attr(attr_name):
    class _Perm(PerfilTieneAtributoPerm):
        def __init__(self):
            super().__init__(attr_name)
    return _Perm


class IsAdminOrHasPerfilAttrs(permissions.BasePermission):
    """Permite acceso si el usuario es staff o si tiene al menos
    uno de los atributos True en su perfil (attrs)."""

    def __init__(self, attrs=None):
        self.attrs = attrs or []

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        perfil = getattr(user, 'perfil', None)
        if not perfil:
            return False
        return any(bool(getattr(perfil, a, False)) for a in self.attrs)


def require_any_perfil_attrs(*attrs):
    class _P(IsAdminOrHasPerfilAttrs):
        def __init__(self):
            super().__init__(list(attrs))
    return _P
