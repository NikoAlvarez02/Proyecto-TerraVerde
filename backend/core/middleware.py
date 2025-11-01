from django.utils.deprecation import MiddlewareMixin


class NoStoreCacheMiddleware(MiddlewareMixin):
    """Evita que el navegador guarde en caché páginas con sesión.

    - Aplica encabezados de no-caché a respuestas HTML.
    - Mitiga volver atrás/adelante tras cerrar sesión (bfcache y caché).
    """

    def process_response(self, request, response):
        ctype = response.headers.get("Content-Type", "")
        if ctype.startswith("text/html"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

