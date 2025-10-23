from .models import AuditoriaLog
from django.utils.deprecation import MiddlewareMixin


class AuditMiddleware(MiddlewareMixin):
    """Registra accesos básicos (RNF4) al final del ciclo para no interferir con sesiones.
    """

    def process_response(self, request, response):
        try:
            # Evitar interferir con /login/ y /logout/ durante el ciclo de autenticación
            path = request.path or ''
            if path.startswith('/login') or path.startswith('/logout'):
                return response
            user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
            AuditoriaLog.objects.create(
                usuario=user,
                accion='access',
                ruta=path[:255],
                ip=self._get_ip(request),
                detalle=f"{request.method} {response.status_code}"
            )
        except Exception:
            pass
        return response

    def _get_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
