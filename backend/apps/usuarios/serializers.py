from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Perfil

User = get_user_model()


class PerfilNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = [
            'rol', 'profesional',
            'puede_admin_usuarios','puede_admin_especialidades','puede_admin_centros','puede_admin_roles',
            'puede_crear_pacientes','puede_ver_pacientes','puede_editar_pacientes','puede_eliminar_pacientes',
            'puede_crear_historias','puede_ver_historias','puede_editar_historias','puede_ver_historias_otros',
            'puede_crear_turnos','puede_ver_calendario','puede_gestionar_turnos','puede_cancelar_turnos',
            'puede_generar_reportes','puede_ver_estadisticas','puede_exportar_datos','puede_ver_auditoria',
        ]


class UsuarioSerializer(serializers.ModelSerializer):
    # Campo solo escritura para crear/actualizar password
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    perfil = PerfilNestedSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "is_active", "is_staff", "is_superuser", "last_login", "date_joined",
            "password", "full_name", "perfil",
        ]
        read_only_fields = ["last_login", "date_joined"]

    def get_full_name(self, obj):
        name = f"{obj.last_name or ''}, {obj.first_name or ''}".strip(", ")
        return name or obj.username

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        perfil_data = validated_data.pop("perfil", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_password(User.objects.make_random_password())
        user.save()
        perfil, _ = Perfil.objects.get_or_create(user=user)
        if perfil_data:
            rol = perfil_data.get('rol')
            if rol:
                perfil.rol = rol
                try:
                    perfil.asignar_permisos_por_rol()
                except Exception:
                    pass
            if 'profesional' in perfil_data:
                try:
                    perfil.profesional_id = perfil_data.get('profesional') or None
                except Exception:
                    pass
            for k, v in perfil_data.items():
                if k in ('rol', 'profesional'):
                    continue
                if hasattr(perfil, k) and isinstance(v, bool):
                    setattr(perfil, k, v)
            perfil.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        perfil_data = validated_data.pop("perfil", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if perfil_data is not None:
            perfil, _ = Perfil.objects.get_or_create(user=instance)
            rol = perfil_data.get('rol')
            if rol:
                perfil.rol = rol
                try:
                    perfil.asignar_permisos_por_rol()
                except Exception:
                    pass
            if 'profesional' in perfil_data:
                try:
                    perfil.profesional_id = perfil_data.get('profesional') or None
                except Exception:
                    pass
            for k, v in perfil_data.items():
                if k in ('rol', 'profesional'):
                    continue
                if hasattr(perfil, k) and isinstance(v, bool):
                    setattr(perfil, k, v)
            perfil.save()
        return instance
