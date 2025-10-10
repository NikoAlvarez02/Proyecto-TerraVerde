from rest_framework import serializers
from .models import Turno
from datetime import datetime

class TurnoSerializer(serializers.ModelSerializer):
    # Campos separados para el frontend (solo escritura)
    fecha = serializers.DateField(write_only=True, required=True)
    hora = serializers.TimeField(write_only=True, required=True)
    
    # fecha_hora NO es requerido en el input porque lo construimos internamente
    fecha_hora = serializers.DateTimeField(read_only=True)
    
    # Campos de lectura con nombres de relaciones
    paciente_nombre = serializers.SerializerMethodField(read_only=True)
    profesional_nombre = serializers.SerializerMethodField(read_only=True)
    
    # Para compatibilidad con el frontend (devuelve fecha y hora separadas)
    fecha_display = serializers.SerializerMethodField(read_only=True)
    hora_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Turno
        fields = [
            'id', 'paciente', 'profesional', 'fecha_hora',
            'fecha', 'hora',  # write_only
            'fecha_display', 'hora_display',  # read_only
            'estado', 'motivo', 'observaciones',
            'paciente_nombre', 'profesional_nombre',
            'creado', 'actualizado'
        ]
        read_only_fields = ['id', 'creado', 'actualizado', 'fecha_hora']
        extra_kwargs = {
            'paciente': {'required': True},
            'profesional': {'required': True},
            'estado': {'required': True},
        }
    
    def get_paciente_nombre(self, obj):
        return f"{obj.paciente.apellido}, {obj.paciente.nombre}"
    
    def get_profesional_nombre(self, obj):
        return f"{obj.profesional.apellido}, {obj.profesional.nombre}"
    
    def get_fecha_display(self, obj):
        return obj.fecha_hora.date().isoformat()
    
    def get_hora_display(self, obj):
        return obj.fecha_hora.time().strftime('%H:%M')
    
    def validate(self, data):
        """Validación custom antes de crear/actualizar"""
        # Verificar que fecha y hora estén presentes
        if 'fecha' not in data or 'hora' not in data:
            raise serializers.ValidationError({
                'fecha': 'La fecha es requerida',
                'hora': 'La hora es requerida'
            })
        return data
    
    def create(self, validated_data):
        # Extraer fecha y hora
        fecha = validated_data.pop('fecha')
        hora = validated_data.pop('hora')
        
        # Combinar en fecha_hora
        fecha_hora = datetime.combine(fecha, hora)
        validated_data['fecha_hora'] = fecha_hora
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Extraer fecha y hora si están presentes
        fecha = validated_data.pop('fecha', None)
        hora = validated_data.pop('hora', None)
        
        # Si ambos están presentes, combinarlos
        if fecha and hora:
            fecha_hora = datetime.combine(fecha, hora)
            validated_data['fecha_hora'] = fecha_hora
        elif fecha:
            # Solo fecha: mantener la hora anterior
            fecha_hora = datetime.combine(fecha, instance.fecha_hora.time())
            validated_data['fecha_hora'] = fecha_hora
        elif hora:
            # Solo hora: mantener la fecha anterior
            fecha_hora = datetime.combine(instance.fecha_hora.date(), hora)
            validated_data['fecha_hora'] = fecha_hora
        
        return super().update(instance, validated_data)