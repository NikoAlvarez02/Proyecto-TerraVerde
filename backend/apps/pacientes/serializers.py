from rest_framework import serializers
from .models import Paciente    


class PacienteSerializer(serializers.ModelSerializer):
    centro_nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Paciente
        fields = '__all__'

    def get_centro_nombre(self, obj):
        return getattr(obj.centro, 'nombre', None)
