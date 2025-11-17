from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils import timezone
import re
from .models import Paciente
from apps.profesionales.models import Profesional


class PacienteSerializer(serializers.ModelSerializer):
    # Acepta tanto YYYY-MM-DD como DD/MM/YYYY
    fecha_nacimiento = serializers.DateField(
        input_formats=["%Y-%m-%d", "%d/%m/%Y"], required=True
    )
    dni = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Paciente.objects.filter(activo=True),
                message="Ya existe un paciente con este DNI activo"
            )
        ]
    )
    centro_nombre = serializers.SerializerMethodField(read_only=True)
    obra_social_nombre = serializers.SerializerMethodField(read_only=True)
    profesionales_asignados = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Profesional.objects.all(), required=False
    )
    profesionales_asignados_nombres = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Paciente
        fields = [
            'id', 'dni', 'nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'email', 'direccion',
            'nacionalidad', 'tiene_representante',
            'rep_nombre', 'rep_apellido', 'rep_edad', 'rep_telefono', 'rep_nacionalidad',
            'centro', 'centro_nombre',
            'obra_social', 'obra_social_nombre',
            'contacto_emergencia_nombre', 'contacto_emergencia_telefono',
            'grupo_sanguineo', 'alergias', 'antecedentes', 'genero', 'foto',
            'activo', 'fecha_registro', 'fecha_baja',
            'profesionales_asignados', 'profesionales_asignados_nombres',
        ]
        extra_kwargs = {
            'fecha_nacimiento': {
                'error_messages': {
                    'required': 'La fecha de nacimiento es obligatoria',
                    'null': 'La fecha de nacimiento es obligatoria',
                    'invalid': 'Formato inválido. Usá dd/mm/aaaa o yyyy-mm-dd',
                }
            },
            'email': {
                'validators': [
                    UniqueValidator(
                        queryset=Paciente.objects.all(),
                        message='Ya existe un paciente con ese correo'
                    )
                ],
                'required': False,
                'allow_null': True,
                'allow_blank': True,
            },
        }

    def to_internal_value(self, data):
        # Ignorar campos legados/no mapeados para que requests antiguos no fallen
        cleaned = data.copy()
        cleaned.pop('obra_social_legacy', None)
        return super().to_internal_value(cleaned)

    def validate_email(self, value):
        # Permitir vacío o None
        return value or None

    def validate_dni(self, value: str) -> str:
        v = (value or '').strip()
        # Exigir exactamente 8 dígitos numéricos
        if not re.fullmatch(r"\d{8}", v):
            raise serializers.ValidationError('El DNI debe tener exactamente 8 dígitos numéricos')
        # Validar manualmente duplicados solo en activos
        qs = Paciente.objects.filter(dni=v, activo=True)
        # En update, excluir el propio
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe un paciente activo con este DNI')
        return v

    def validate_telefono(self, value: str) -> str:
        v = (value or '').strip()
        if not v:
            return v
        digits = re.sub(r"[^\d]", "", v)
        if len(digits) < 8 or len(digits) > 15:
            raise serializers.ValidationError('El teléfono debe tener entre 8 y 15 dígitos')
        return v

    def _solo_letras(self, value: str) -> str:
        v = (value or '').strip()
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúñÑüÜ\s']+", v):
            raise serializers.ValidationError('Solo se permiten letras y espacios')
        return v

    def validate_nombre(self, value: str) -> str:
        return self._solo_letras(value)

    def validate_apellido(self, value: str) -> str:
        return self._solo_letras(value)

    def get_centro_nombre(self, obj):
        return getattr(obj.centro, 'nombre', None)

    def get_obra_social_nombre(self, obj):
        return getattr(obj.obra_social, 'nombre', None)

    def get_profesionales_asignados_nombres(self, obj):
        try:
            return [f"{p.apellido}, {p.nombre}" for p in obj.profesionales_asignados.all()]
        except Exception:
            return []

    # Validaciones adicionales para evitar IntegrityError y retornar 400 descriptivo
    def validate(self, attrs):
        # Apellido y nombre obligatorios
        for f in ('apellido', 'nombre'):
            if not (attrs.get(f) or '').strip():
                raise serializers.ValidationError({f: 'Este campo es obligatorio'})

        # Fecha de nacimiento obligatoria y en rango lógico
        fnac = attrs.get('fecha_nacimiento')
        if not fnac:
            raise serializers.ValidationError({'fecha_nacimiento': 'La fecha de nacimiento es obligatoria'})
        hoy = timezone.localdate()
        if fnac > hoy:
            raise serializers.ValidationError({'fecha_nacimiento': 'La fecha no puede ser futura'})
        # Rango inferior básico
        try:
            if fnac.year < 1900:
                raise serializers.ValidationError({'fecha_nacimiento': 'La fecha es demasiado antigua'})
        except Exception:
            pass

        # Representante requerido para menores de 18: usamos los campos de contacto de emergencia
        edad = hoy.year - fnac.year - ((hoy.month, hoy.day) < (fnac.month, fnac.day))
        if edad < 18:
            if not (attrs.get('contacto_emergencia_nombre') or '').strip():
                raise serializers.ValidationError({'contacto_emergencia_nombre': 'Obligatorio para menores'})
            tel_rep = (attrs.get('contacto_emergencia_telefono') or '').strip()
            if not tel_rep:
                raise serializers.ValidationError({'contacto_emergencia_telefono': 'Obligatorio para menores'})
            digits = re.sub(r"[^\d]", "", tel_rep)
            if len(digits) < 8:
                raise serializers.ValidationError({'contacto_emergencia_telefono': 'El teléfono del representante es inválido'})

        return attrs

    def create(self, validated_data):
        if not validated_data.get('fecha_nacimiento'):
            raise serializers.ValidationError({'fecha_nacimiento': 'La fecha de nacimiento es obligatoria'})
        profs = validated_data.pop('profesionales_asignados', None)
        instance = super().create(validated_data)
        if isinstance(profs, list):
            instance.profesionales_asignados.set(profs)
        return instance

    def update(self, instance, validated_data):
        if 'fecha_nacimiento' in validated_data and not validated_data.get('fecha_nacimiento'):
            raise serializers.ValidationError({'fecha_nacimiento': 'La fecha de nacimiento es obligatoria'})
        profs = validated_data.pop('profesionales_asignados', None)
        instance = super().update(instance, validated_data)
        if isinstance(profs, list):
            instance.profesionales_asignados.set(profs)
        return instance
