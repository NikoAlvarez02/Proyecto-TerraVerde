from rest_framework import serializers
from .models import Observation, ObservationAttachment, ObservationRevision


class ObservationAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationAttachment
        fields = ['id', 'archivo', 'nombre', 'subido']
        read_only_fields = ['id', 'subido']


class ObservationRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationRevision
        fields = ['id', 'datos_json', 'editado_por', 'editado_en']
        read_only_fields = ['id', 'editado_en']


class ObservationSerializer(serializers.ModelSerializer):
    adjuntos = ObservationAttachmentSerializer(many=True, required=False)

    class Meta:
        model = Observation
        fields = '__all__'

    def create(self, validated_data):
        adjuntos_data = validated_data.pop('adjuntos', [])
        obs = Observation.objects.create(**validated_data)
        for ad in adjuntos_data:
            ObservationAttachment.objects.create(observation=obs, **ad)
        return obs

    def update(self, instance, validated_data):
        request = self.context.get('request')
        # snapshot previo
        ObservationRevision.objects.create(
            observation=instance,
            datos_json=self.to_representation(instance),
            editado_por=getattr(request, 'user', None)
        )
        adjuntos_data = validated_data.pop('adjuntos', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if isinstance(adjuntos_data, list):
            # política simple: no borramos; solo agregamos si vienen nuevos con archivo
            for ad in adjuntos_data:
                if ad.get('archivo'):
                    ObservationAttachment.objects.create(observation=instance, **ad)
        return instance

