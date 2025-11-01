from drf_spectacular.extensions import OpenApiAuthenticationExtension
from .views import CsrfExemptSessionAuthentication


class CsrfExemptSessionAuthScheme(OpenApiAuthenticationExtension):
    target_class = CsrfExemptSessionAuthentication
    name = 'SessionAuth (CSRF-exempt)'
    match_subclasses = True

    def get_security_definition(self, auto_schema):
        # Representar como cookie auth de sesión
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'sessionid',
        }

