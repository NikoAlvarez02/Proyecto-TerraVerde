from django.utils.deprecation import MiddlewareMixin
from .models import AuditoriaLog
from .request_local import set_current_request, clear_current_request


class AuditMiddleware(MiddlewareMixin):
    """Registra accesos básicos y expone el request a señales."""

    def process_request(self, request):
        set_current_request(request)

    def process_response(self, request, response):
        try:
            path = request.path or ''
            if path.startswith('/static') or path.startswith('/media'):
                return response
            if path.startswith('/login') or path.startswith('/logout'):
                return response
            user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
            accion = self._infer_accion(request.method)
            AuditoriaLog.objects.create(
                usuario=user,
                accion=accion,
                ruta=path[:255],
                metodo=request.method,
                ip=self._get_ip(request),
                user_agent=str(request.META.get('HTTP_USER_AGENT', ''))[:255],
                detalle=f"{request.method} {response.status_code}",
                exitoso=response.status_code < 400
            )
        except Exception:
            pass
        finally:
            clear_current_request()
        return response

    def process_exception(self, request, exception):
        clear_current_request()

    def _infer_accion(self, method):
        m = (method or '').upper()
        if m == 'POST':
            return 'create'
        if m in ('PUT', 'PATCH'):
            return 'update'
        if m == 'DELETE':
            return 'delete'
        return 'access'

    def _get_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
