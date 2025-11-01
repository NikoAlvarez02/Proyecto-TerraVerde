from urllib.parse import urlencode
from urllib.request import urlopen, Request
from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import permissions, status


GEOREF_BASE = getattr(settings, 'GEOREF_BASE_URL', 'https://apis.datos.gob.ar/georef/api/')


def _http_json(path: str, params: dict, ttl: int = 60 * 60):
    """Simple GET JSON with cache by full URL."""
    qs = urlencode({k: v for k, v in params.items() if v not in (None, '', [])})
    url = GEOREF_BASE.rstrip('/') + '/' + path.strip('/') + (('?' + qs) if qs else '')
    cache_key = f"georef:{url}"
    data = cache.get(cache_key)
    if data is None:
        req = Request(url, headers={'User-Agent': 'TerraVerde/1.0'})
        try:
            with urlopen(req, timeout=20) as resp:
                data = resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            raise RuntimeError(f"Error al consultar Georef: {e}")
        cache.set(cache_key, data, ttl)
    return data


@extend_schema(exclude=True)
class ProvinciasView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        params = {
            'nombre': request.GET.get('nombre'),
            'campos': request.GET.get('campos'),
            'max': request.GET.get('max', '1000'),
        }
        try:
            raw = _http_json('provincias', params)
            from json import loads
            return Response(loads(raw), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_502_BAD_GATEWAY)


@extend_schema(exclude=True)
class MunicipiosView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        params = {
            'provincia': request.GET.get('provincia'),
            'nombre': request.GET.get('nombre'),
            'campos': request.GET.get('campos'),
            'max': request.GET.get('max', '1000'),
        }
        try:
            raw = _http_json('municipios', params)
            from json import loads
            return Response(loads(raw), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_502_BAD_GATEWAY)


@extend_schema(exclude=True)
class LocalidadesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        params = {
            'provincia': request.GET.get('provincia'),
            'municipio': request.GET.get('municipio'),
            'departamento': request.GET.get('departamento'),
            'nombre': request.GET.get('nombre'),
            'campos': request.GET.get('campos'),
            'max': request.GET.get('max', '1000'),
        }
        try:
            raw = _http_json('localidades', params)
            from json import loads
            return Response(loads(raw), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_502_BAD_GATEWAY)


@extend_schema(exclude=True)
class DepartamentosView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        params = {
            'provincia': request.GET.get('provincia'),
            'nombre': request.GET.get('nombre'),
            'campos': request.GET.get('campos'),
            'max': request.GET.get('max', '1000'),
        }
        try:
            raw = _http_json('departamentos', params)
            from json import loads
            return Response(loads(raw), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
