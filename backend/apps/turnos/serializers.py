from rest_framework import serializers
from django.conf import settings
from django.db import IntegrityError
from .models import Turno
from datetime import datetime, timedelta
from django.utils import timezone
from apps.centers.models import Center
try:
    # Feriados opcionales
    from apps.centers.models import Holiday
except Exception:
    Holiday = None

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
        dt_local = timezone.localtime(obj.fecha_hora)
        return dt_local.date().isoformat()
    
    def get_hora_display(self, obj):
        dt_local = timezone.localtime(obj.fecha_hora)
        return dt_local.time().strftime('%H:%M')
    
    def validate(self, data):
        """ValidaciÃ³n custom: fecha/hora y solapamiento de profesional."""
        # Permitir updates parciales usando valores actuales si faltan
        fecha = data.get('fecha') or (self.instance.fecha_hora.date() if getattr(self, 'instance', None) else None)
        hora = data.get('hora') or (self.instance.fecha_hora.time() if getattr(self, 'instance', None) else None)

        errors = {}
        if not fecha:
            errors['fecha'] = 'La fecha es requerida'
        if not hora:
            errors['hora'] = 'La hora es requerida'
        if errors:
            raise serializers.ValidationError(errors)

        # Profesional requerido para chequear solapamiento
        profesional = data.get('profesional') or (self.instance.profesional if getattr(self, 'instance', None) else None)
        if not profesional:
            errors['profesional'] = 'El profesional es requerido'
            raise serializers.ValidationError(errors)

        # Usar zona horaria actual para evitar desplazamientos
        tz = timezone.get_current_timezone()
        fecha_hora = timezone.make_aware(datetime.combine(fecha, hora), tz)

        # Validar horario de atenciÃ³n general (08:00 a 20:00)
        try:
            start_h = int(getattr(settings, 'BUSINESS_HOUR_START', 8))
            end_h = int(getattr(settings, 'BUSINESS_HOUR_END', 20))
        except Exception:
            start_h, end_h = 8, 20
        if not (start_h <= fecha_hora.hour < end_h):
            raise serializers.ValidationError({'hora': f'Hora fuera de atenciÃ³n ({start_h:02d}:00-{end_h:02d}:00)'})

        # No permitir turnos en el pasado salvo que el estado sea 'atendido' o 'cancelado'
        estado_in = data.get('estado') or (self.instance.estado if getattr(self, 'instance', None) else 'pendiente')
        if fecha_hora < timezone.now() and estado_in not in ('atendido', 'cancelado'):
            raise serializers.ValidationError({'fecha': 'La fecha/hora ya pasÃ³'})

        # Validar feriados (si el modelo estÃ¡ disponible)
        if Holiday is not None:
            try:
                fer = Holiday.objects.filter(fecha=fecha).first()
                if fer and not fer.laborable:
                    raise serializers.ValidationError({'fecha': f'Feriado no laborable: {fer.nombre}'})
            except Exception:
                pass

        # Regla de solapamiento: ventana configurable
        intervalo = getattr(settings, 'TURNOS_INTERVALO_MIN', 60)
        # Consideramos bloque cerrado [t - (intervalo-1), t + (intervalo-1)] para
        # cubrir la coincidencia exacta y cualquier cruce dentro del bloque.
        delta = max(0, int(intervalo) - 1)
        start = fecha_hora - timedelta(minutes=delta)
        end = fecha_hora + timedelta(minutes=delta)
        qs = Turno.objects.filter(profesional=profesional, fecha_hora__gte=start, fecha_hora__lte=end)
        if getattr(self, 'instance', None):
            qs = qs.exclude(pk=self.instance.pk)
        # No bloquear por cancelados
        qs = qs.exclude(estado='cancelado')
        if qs.exists():
            # Mensaje mÃ¡s claro e incluyendo ventana
            mins = int(getattr(settings, 'TURNOS_INTERVALO_MIN', 30))
            raise serializers.ValidationError({'hora': f'Profesional con turno en el horario (ventana {mins} min)'})

        return data
    
    def create(self, validated_data):
        # Extraer fecha y hora
        fecha = validated_data.pop('fecha')
        hora = validated_data.pop('hora')
        tz = timezone.get_current_timezone()
        validated_data['fecha_hora'] = timezone.make_aware(datetime.combine(fecha, hora), tz)
        try:
            return super().create(validated_data)
        except IntegrityError:
            # Choque exacto con la restricciÃ³n Ãºnica
            raise serializers.ValidationError({'hora': 'Profesional con turno en el horario'})
    
    def update(self, instance, validated_data):
        # Extraer fecha y hora si estÃ¡n presentes
        fecha = validated_data.pop('fecha', None)
        hora = validated_data.pop('hora', None)
        
        # Si ambos estÃ¡n presentes, combinarlos
        if fecha and hora:
            tz = timezone.get_current_timezone()
            fecha_hora = timezone.make_aware(datetime.combine(fecha, hora), tz)
            validated_data['fecha_hora'] = fecha_hora
        elif fecha:
            # Solo fecha: mantener la hora anterior
            tz = timezone.get_current_timezone()
            fecha_hora = timezone.make_aware(datetime.combine(fecha, instance.fecha_hora.astimezone(tz).time()), tz)
            validated_data['fecha_hora'] = fecha_hora
        elif hora:
            # Solo hora: mantener la fecha anterior
            tz = timezone.get_current_timezone()
            fecha_hora = timezone.make_aware(datetime.combine(instance.fecha_hora.astimezone(tz).date(), hora), tz)
            validated_data['fecha_hora'] = fecha_hora
        
        return super().update(instance, validated_data)

