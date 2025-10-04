from rest_framework import serializers
from .models import Turno
from datetime import datetime, date, time

class TurnoSerializer(serializers.ModelSerializer):
    # Para mostrar nombres legibles en la grilla
    paciente_nombre = serializers.SerializerMethodField()
    profesional_nombre = serializers.SerializerMethodField()

    # Campos que el frontend envía por separado (write_only: no salen en la resp automática)
    fecha = serializers.DateField(write_only=True, required=False)
    hora  = serializers.TimeField(write_only=True, required=False)

    class Meta:
        model = Turno
        fields = [
            "id",
            "paciente", "profesional",
            "fecha_hora",     # campo real del modelo
            "estado", "motivo", "observaciones",
            "paciente_nombre", "profesional_nombre",
            "fecha", "hora",  # write-only (entrada), pero los agregamos manualmente en la salida
        ]

    # ---- Salida legible (agregar fecha y hora a la representación) ----
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        fh = rep.get("fecha_hora")
        if fh:
            # fh tipo "YYYY-MM-DDTHH:MM:SS[.fff][Z]" → partimos a mano
            rep["fecha"] = fh[:10]
            rep["hora"]  = fh[11:16]
        else:
            rep["fecha"] = None
            rep["hora"]  = None
        return rep

    # ---- Entrada: combinar fecha + hora en fecha_hora si vino separado ----
    def _ensure_fecha_hora(self, validated_data):
        # Si ya vino fecha_hora, no hacemos nada
        if validated_data.get("fecha_hora"):
            return validated_data

        f = validated_data.pop("fecha", None)
        h = validated_data.pop("hora", None)

        if f and h:
            if isinstance(f, str):
                f = date.fromisoformat(f)
            if isinstance(h, str):
                # acepta "HH:MM" o "HH:MM:SS"
                h = time.fromisoformat(h if len(h) > 5 else f"{h}:00")
            validated_data["fecha_hora"] = datetime.combine(f, h)
        return validated_data

    def create(self, validated_data):
        validated_data = self._ensure_fecha_hora(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._ensure_fecha_hora(validated_data)
        return super().update(instance, validated_data)

    # ---- Campos legibles para tabla ----
    def get_paciente_nombre(self, obj):
        try:
            return f"{obj.paciente.apellido}, {obj.paciente.nombre}"
        except Exception:
            return str(obj.paciente_id)

    def get_profesional_nombre(self, obj):
        try:
            return f"{obj.profesional.apellido}, {obj.profesional.nombre}"
        except Exception:
            return str(obj.profesional_id)
