from rest_framework import serializers
from .models import Profesional, ProfesionalHorario
from apps.centers.models import Center

class ProfesionalSerializer(serializers.ModelSerializer):
    centros = serializers.PrimaryKeyRelatedField(many=True, queryset=Center.objects.all())
    centros_nombres = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Profesional
        fields = "__all__"

    def get_centros_nombres(self, obj):
        return list(obj.centros.values_list('nombre', flat=True))


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
