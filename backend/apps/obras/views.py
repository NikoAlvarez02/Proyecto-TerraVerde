from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from django.conf import settings
from urllib.request import urlopen, Request
import json, csv, io
from .models import ObraSocial, PlanObraSocial
from .serializers import ObraSocialSerializer, PlanObraSocialSerializer


class ObraSocialViewSet(viewsets.ModelViewSet):
    queryset = ObraSocial.objects.all().order_by('nombre')
    serializer_class = ObraSocialSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'codigo']
    ordering_fields = ['nombre', 'codigo']
    pagination_class = None


class PlanObraSocialViewSet(viewsets.ModelViewSet):
    serializer_class = PlanObraSocialSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'codigo', 'obra_social__nombre']
    ordering_fields = ['nombre', 'codigo']
    pagination_class = None

    def get_queryset(self):
        qs = PlanObraSocial.objects.select_related('obra_social').all().order_by('obra_social__nombre', 'nombre')
        obra_id = self.request.query_params.get('obra_social')
        if obra_id:
            qs = qs.filter(obra_social_id=obra_id)
        return qs


@extend_schema(exclude=True)
class ObraSocialImportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        url = request.GET.get('url') or getattr(settings, 'OBRAS_SNRS_URL', None)
        csv_url = request.GET.get('csv_url')
        if not url and not csv_url:
            return Response({"detail": "No hay URL configurada. Pasa ?url= o configura OBRAS_SNRS_URL."}, status=status.HTTP_400_BAD_REQUEST)

        created = 0
        updated = 0
        items = []
        try:
            if csv_url:
                req = Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urlopen(req, timeout=30) as resp:
                    data = resp.read()
                text = data.decode('utf-8', errors='ignore')
                reader = csv.DictReader(io.StringIO(text))
                for row in reader:
                    nombre = (row.get('nombre') or row.get('razon_social') or row.get('RAZON SOCIAL') or row.get('descripcion') or '').strip()
                    codigo = (row.get('codigo') or row.get('CODIGO') or row.get('rnos') or row.get('RNOS') or '').strip()
                    if not nombre:
                        continue
                    items.append({"nombre": nombre, "codigo": codigo})
            else:
                req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urlopen(req, timeout=30) as resp:
                    raw = resp.read().decode('utf-8', errors='ignore')
                try:
                    payload = json.loads(raw)
                except Exception:
                    return Response({"detail": "La respuesta no es JSON", "raw": raw[:500]}, status=status.HTTP_502_BAD_GATEWAY)

                if isinstance(payload, dict) and 'resultado' in payload:
                    data_list = payload.get('resultado') or []
                elif isinstance(payload, list):
                    data_list = payload
                else:
                    data_list = []

                for it in data_list:
                    if not isinstance(it, dict):
                        continue
                    nombre = (it.get('nombre') or it.get('obraSocial') or it.get('descripcion') or '').strip()
                    val_id = it.get('codigo') if 'codigo' in it else it.get('id')
                    codigo = str(val_id) if val_id is not None else ''
                    if not nombre:
                        continue
                    items.append({"nombre": nombre, "codigo": codigo})

            for it in items:
                nombre = it['nombre']
                codigo = it.get('codigo', '')
                obj = ObraSocial.objects.filter(nombre__iexact=nombre).first()
                if obj:
                    changed = False
                    if codigo and obj.codigo != codigo:
                        obj.codigo = codigo
                        changed = True
                    if not obj.activo:
                        obj.activo = True
                        changed = True
                    if changed:
                        obj.save(update_fields=['codigo', 'activo'])
                        updated += 1
                else:
                    ObraSocial.objects.create(nombre=nombre, codigo=codigo, activo=True)
                    created += 1

            return Response({"imported": len(items), "created": created, "updated": updated})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    def post(self, request):
        """Importa desde un archivo CSV subido o texto CSV en el cuerpo.

        - multipart/form-data con campo `file` (CSV)
        - application/json con campo `csv_text`
        Columnas esperadas (flexible): nombre/razon_social/descripcion y codigo/rnos
        """
        file = request.FILES.get('file')
        csv_text = ''
        if file and hasattr(file, 'read'):
            csv_text = file.read().decode('utf-8', errors='ignore')
        elif request.content_type and 'application/json' in request.content_type:
            data = request.data or {}
            csv_text = (data.get('csv_text') or '').strip()
        if not csv_text:
            return Response({"detail": "Falta CSV (subí un archivo o envía 'csv_text')."}, status=status.HTTP_400_BAD_REQUEST)

        reader = csv.DictReader(io.StringIO(csv_text))
        created = 0
        updated = 0
        for row in reader:
            nombre = (row.get('nombre') or row.get('razon_social') or row.get('RAZON SOCIAL') or row.get('descripcion') or '').strip()
            codigo = (row.get('codigo') or row.get('CODIGO') or row.get('rnos') or row.get('RNOS') or '').strip()
            if not nombre:
                continue
            obj = ObraSocial.objects.filter(nombre__iexact=nombre).first()
            if obj:
                changed = False
                if codigo and obj.codigo != codigo:
                    obj.codigo = codigo
                    changed = True
                if not obj.activo:
                    obj.activo = True
                    changed = True
                if changed:
                    obj.save(update_fields=['codigo', 'activo'])
                    updated += 1
            else:
                ObraSocial.objects.create(nombre=nombre, codigo=codigo, activo=True)
                created += 1
        return Response({"created": created, "updated": updated})
