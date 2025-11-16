# backend/apps/pacientes/api_views.py
from rest_framework import viewsets, permissions
from django.utils import timezone
from .models import Paciente
from .serializers import PacienteSerializer


class PacienteViewSet(viewsets.ModelViewSet):
    serializer_class = PacienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["dni", "nombre", "apellido", "email", "obra_social__nombre"]
    filterset_fields = ["activo", "obra_social", "plan", "centro"]
    ordering_fields = ["apellido", "nombre", "dni", "fecha_registro"]
    ordering = ["-fecha_registro"]
    pagination_class = None  # devolver lista plana para compatibilidad del frontend

    # Defensa: registrar errores de validación para evitar 500 silenciosos
    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'server_error': str(e)})

    def perform_update(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'server_error': str(e)})

    def perform_destroy(self, instance):
        # Baja lógica: evita errores por FKs y mantiene trazabilidad
        instance.activo = False
        instance.fecha_baja = timezone.now()
        instance.save(update_fields=["activo", "fecha_baja"])

    def get_queryset(self):
        qs = Paciente.objects.all().order_by(*self.ordering)
        user = getattr(self.request, 'user', None)
        perfil = getattr(user, 'perfil', None) if user and user.is_authenticated else None
        include_inactive = str(self.request.query_params.get('include_inactive', '')).lower() in ('1', 'true', 'yes')
        if not include_inactive:
            qs = qs.filter(activo=True)
        if not perfil:
            # Sin perfil: staff/superuser ven todo; resto, nada
            return qs if (user and (user.is_staff or user.is_superuser)) else qs.none()
        # Profesionales: ven solo sus pacientes asignados (M2M)
        if perfil.rol == 'prof' and perfil.profesional:
            return qs.filter(profesionales_asignados=perfil.profesional)
        # Resto de roles: respetan flags, pero por defecto recep/admin ven todos
        return qs
