from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.exceptions import ValidationError
import re
from .models import Profesional, ProfesionalHorario, Especialidad
from apps.centers.models import Center

class ProfesionalSerializer(serializers.ModelSerializer):
    centros = serializers.PrimaryKeyRelatedField(many=True, queryset=Center.objects.all())
    centros_nombres = serializers.SerializerMethodField(read_only=True)
    especialidad_nombre = serializers.CharField(source='especialidad.nombre', read_only=True)
    email = serializers.EmailField(validators=[
        UniqueValidator(
            queryset=Profesional.objects.all(),
            message='Ya existe un profesional con ese correo institucional'
        )
    ])
    matricula = serializers.CharField(required=True, max_length=20, validators=[
        UniqueValidator(
            queryset=Profesional.objects.all(),
            message='La matrícula ya existe para otro profesional'
        )
    ])
    class Meta:
        model = Profesional
        fields = "__all__"

    def get_centros_nombres(self, obj):
        return list(obj.centros.values_list('nombre', flat=True))

    def validate_dni(self, value: str) -> str:
        # Solo 8 dígitos
        if not re.fullmatch(r"\d{8}", (value or '').strip()):
            raise serializers.ValidationError('El DNI debe tener exactamente 8 dígitos numéricos')
        return value

    def validate_telefono(self, value: str) -> str:
        v = (value or '').strip()
        if not v:
            return v
        # Acepta +, espacios y guiones al ingresar; valida cantidad de dígitos
        digits = re.sub(r"[^\d]", "", v)
        if len(digits) < 8 or len(digits) > 15:
            raise serializers.ValidationError('El teléfono debe tener entre 8 y 15 dígitos')
        return v

    def validate(self, attrs):
        # Apellido y nombre obligatorios
        for f in ('apellido', 'nombre'):
            if not (attrs.get(f) or '').strip():
                raise serializers.ValidationError({f: 'Este campo es obligatorio'})
        # Matrícula no vacía
        if not (attrs.get('matricula') or '').strip():
            raise serializers.ValidationError({'matricula': 'La matrícula es obligatoria'})
        return attrs

    def create(self, validated_data):
        centros = validated_data.pop('centros', [])
        obj = super().create(validated_data)
        if centros is not None:
            obj.centros.set(centros)
        return obj

    def update(self, instance, validated_data):
        centros = validated_data.pop('centros', None)
        obj = super().update(instance, validated_data)
        if centros is not None:
            obj.centros.set(centros)
        return obj


class ProfesionalHorarioSerializer(serializers.ModelSerializer):
    centro_nombre = serializers.SerializerMethodField(read_only=True)
    profesional_nombre = serializers.SerializerMethodField(read_only=True)
    dia_display = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ProfesionalHorario
        fields = '__all__'

    def get_centro_nombre(self, obj):
        return getattr(obj.centro, 'nombre', None)

    def get_profesional_nombre(self, obj):
        return f"{obj.profesional.apellido}, {obj.profesional.nombre}"

    def get_dia_display(self, obj):
        return obj.get_dia_semana_display()

    def validate(self, attrs):
        hi = attrs.get('hora_inicio')
        hf = attrs.get('hora_fin')
        if hi and hf and hf <= hi:
            raise serializers.ValidationError({'hora_fin': 'La hora de fin debe ser mayor a la de inicio'})

        # Validar solapamiento para mismo profesional/centro/día
        prof = attrs.get('profesional') or getattr(self.instance, 'profesional', None)
        centro = attrs.get('centro') or getattr(self.instance, 'centro', None)
        dia = attrs.get('dia_semana') or getattr(self.instance, 'dia_semana', None)
        if prof and centro and dia is not None and hi and hf:
            qs = ProfesionalHorario.objects.filter(profesional=prof, centro=centro, dia_semana=dia)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            # hay solape si inicio < fin_existente y fin > inicio_existente
            overlap = qs.filter(hora_inicio__lt=hf, hora_fin__gt=hi).exists()
            if overlap:
                raise serializers.ValidationError('La franja horaria se solapa con otra existente')
        return attrs


class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = ['id', 'nombre', 'activo']
