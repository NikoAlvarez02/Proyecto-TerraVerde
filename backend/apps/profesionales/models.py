from django.db import models


class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

class Profesional(models.Model):
    dni = models.CharField("DNI", max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    matricula = models.CharField(max_length=20)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True, related_name='profesionales')
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    fecha_baja = models.DateTimeField(blank=True, null=True)
    centros = models.ManyToManyField('centers.Center', related_name='profesionales', blank=True)

    class Meta:
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.apellido}, {self.nombre} - {self.matricula}"


class ProfesionalHorario(models.Model):
    DIAS = (
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    )
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='horarios')
    centro = models.ForeignKey('centers.Center', on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['profesional', 'centro', 'dia_semana', 'hora_inicio']
        unique_together = ('profesional', 'centro', 'dia_semana', 'hora_inicio', 'hora_fin')

    def __str__(self):
        return f"{self.profesional} @ {self.centro} {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"
