from rest_framework import serializers
from rest_framework.validators import UniqueValidator
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
                queryset=Paciente.objects.all(),
                message="Ya existe un paciente con este DNI"
            )
        ]
    )
    centro_nombre = serializers.SerializerMethodField(read_only=True)
    obra_social_nombre = serializers.SerializerMethodField(read_only=True)
    plan_nombre = serializers.SerializerMethodField(read_only=True)
    profesionales_asignados = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Profesional.objects.all(), required=False
    )
    profesionales_asignados_nombres = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Paciente
        fields = [
            'id', 'dni', 'nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'email', 'direccion',
            'centro', 'centro_nombre',
            'obra_social', 'obra_social_nombre', 'plan', 'plan_nombre',
            'contacto_emergencia_nombre', 'contacto_emergencia_telefono',
            'grupo_sanguineo', 'antecedentes', 'genero', 'foto',
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

    def validate_email(self, value):
        # Permitir vacío o None
        return value or None

    def get_centro_nombre(self, obj):
        return getattr(obj.centro, 'nombre', None)

    def get_obra_social_nombre(self, obj):
        return getattr(obj.obra_social, 'nombre', None)

    def get_plan_nombre(self, obj):
        return getattr(obj.plan, 'nombre', None)

    def get_profesionales_asignados_nombres(self, obj):
        try:
            return [f"{p.apellido}, {p.nombre}" for p in obj.profesionales_asignados.all()]
        except Exception:
            return []

    # Validaciones adicionales para evitar IntegrityError y retornar 400 descriptivo
    def validate(self, attrs):
        if not attrs.get('fecha_nacimiento'):
            raise serializers.ValidationError({'fecha_nacimiento': 'La fecha de nacimiento es obligatoria'})
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
