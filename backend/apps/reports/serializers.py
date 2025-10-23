from rest_framework import serializers
from .models import ReportTemplate, GeneratedReport, ScheduledReport


class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = '__all__'


class GeneratedReportSerializer(serializers.ModelSerializer):
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedReport
        fields = '__all__'
        read_only_fields = ['id', 'fecha_generacion', 'archivo_pdf']

    def get_archivo_url(self, obj):
        try:
            request = self.context.get('request')
        except Exception:
            request = None
        try:
            url = obj.archivo_pdf.url
        except Exception:
            return None
        return request.build_absolute_uri(url) if request else url


class ScheduledReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledReport
        fields = '__all__'


class ReportParametersSerializer(serializers.Serializer):
    # Parámetros comunes
    desde = serializers.DateField(required=False)
    hasta = serializers.DateField(required=False)
    centros = serializers.ListField(child=serializers.IntegerField(), required=False)
    profesionales = serializers.ListField(child=serializers.IntegerField(), required=False)
    especialidades = serializers.ListField(child=serializers.CharField(), required=False)
    diagnosticos = serializers.ListField(child=serializers.CharField(), required=False)
    obras_sociales = serializers.ListField(child=serializers.CharField(), required=False)
    rango_etario = serializers.ListField(child=serializers.IntegerField(), required=False)
    genero = serializers.ChoiceField(choices=[('M','M'),('F','F'),('X','X')], required=False)
    orientacion = serializers.ChoiceField(choices=[('portrait','portrait'),('landscape','landscape')], default='portrait')
    tamano_pagina = serializers.ChoiceField(choices=[('A4','A4'),('Letter','Letter'),('Legal','Legal')], default='A4')
    incluir_graficos = serializers.BooleanField(default=True)
    incluir_tablas = serializers.BooleanField(default=True)
    nombre_archivo = serializers.CharField(required=False)

    # Campos opcionales para informes médicos/epicrisis
    numero_informe = serializers.CharField(required=False, allow_blank=True)
    motivo = serializers.CharField(required=False, allow_blank=True)
    hallazgos = serializers.CharField(required=False, allow_blank=True)
    antecedentes = serializers.ListField(child=serializers.CharField(), required=False)
    impresion_diagnostica = serializers.ListField(child=serializers.CharField(), required=False)
    plan = serializers.ListField(child=serializers.CharField(), required=False)
    firma_nombre = serializers.CharField(required=False, allow_blank=True)
    firma_especialidad = serializers.CharField(required=False, allow_blank=True)
    firma_matricula = serializers.CharField(required=False, allow_blank=True)
    # Datos de paciente opcionales (si no se toman del modelo)
    paciente_nombre = serializers.CharField(required=False, allow_blank=True)
    paciente_dni = serializers.CharField(required=False, allow_blank=True)
    paciente_edad = serializers.CharField(required=False, allow_blank=True)
    paciente_fecha_nacimiento = serializers.CharField(required=False, allow_blank=True)
    paciente_obra_social = serializers.CharField(required=False, allow_blank=True)
    paciente_nro_historia = serializers.CharField(required=False, allow_blank=True)
