from django.db import models


BLOOD_TYPES = (
    ("A+", "A+"), ("A-", "A-"),
    ("B+", "B+"), ("B-", "B-"),
    ("AB+", "AB+"), ("AB-", "AB-"),
    ("O+", "O+"), ("O-", "O-"),
)

GENDERS = (
    ("M", "Masculino"),
    ("F", "Femenino"),
    ("X", "Otro/No binario"),
)


class Paciente(models.Model):
    dni = models.CharField("DNI", max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True)
    obra_social = models.ForeignKey('obras.ObraSocial', on_delete=models.SET_NULL, null=True, blank=True, related_name='pacientes')
    plan = models.ForeignKey('obras.PlanObraSocial', on_delete=models.SET_NULL, null=True, blank=True, related_name='pacientes')

    # Columna legacy que quedó de una migración inicial (CharField NOT NULL)
    # La mantenemos solo a nivel de modelo para completar '' en INSERT y evitar
    # errores de integridad en entornos donde la columna persiste.
    obra_social_legacy = models.CharField(max_length=50, blank=True, default='', db_column='obra_social', editable=False)

    centro = models.ForeignKey('centers.Center', on_delete=models.PROTECT, related_name='pacientes', null=True, blank=True)
    contacto_emergencia_nombre = models.CharField(max_length=100, blank=True)
    contacto_emergencia_telefono = models.CharField(max_length=20, blank=True)
    alergias = models.TextField(blank=True)
    grupo_sanguineo = models.CharField(max_length=3, choices=BLOOD_TYPES, blank=True)
    antecedentes = models.TextField(blank=True)
    genero = models.CharField(max_length=1, choices=GENDERS, blank=True)
    foto = models.ImageField(upload_to='pacientes/fotos/', null=True, blank=True)

    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_baja = models.DateTimeField(blank=True, null=True)
    profesionales_asignados = models.ManyToManyField(
        'profesionales.Profesional', related_name='pacientes_asignados', blank=True
    )

    class Meta:
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.dni})"

