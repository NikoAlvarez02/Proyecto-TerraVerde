from rest_framework import serializers
from .models import ObraSocial, PlanObraSocial


class ObraSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObraSocial
        fields = ['id', 'nombre', 'codigo', 'activo']


class PlanObraSocialSerializer(serializers.ModelSerializer):
    obra_social_nombre = serializers.CharField(source='obra_social.nombre', read_only=True)

    class Meta:
        model = PlanObraSocial
        fields = ['id', 'obra_social', 'obra_social_nombre', 'nombre', 'codigo', 'activo']

