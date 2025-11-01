from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Perfil(models.Model):
    ROLES = (
        ('admin', 'Administrador'),
        ('prof', 'Profesional'),
        ('recep', 'Recepcionista'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=20, choices=ROLES, default="recep")

    # Permisos Administración
    puede_admin_usuarios = models.BooleanField(default=False)
    puede_admin_especialidades = models.BooleanField(default=False)
    puede_admin_centros = models.BooleanField(default=False)
    puede_admin_roles = models.BooleanField(default=False)

    # Permisos Pacientes
    puede_crear_pacientes = models.BooleanField(default=False)
    puede_ver_pacientes = models.BooleanField(default=True)
    puede_editar_pacientes = models.BooleanField(default=False)
    puede_eliminar_pacientes = models.BooleanField(default=False)

    # Permisos Historia Clínica
    puede_crear_historias = models.BooleanField(default=False)
    puede_ver_historias = models.BooleanField(default=True)
    puede_editar_historias = models.BooleanField(default=False)
    puede_ver_historias_otros = models.BooleanField(default=False)

    # Permisos Turnos
    puede_crear_turnos = models.BooleanField(default=True)
    puede_ver_calendario = models.BooleanField(default=True)
    puede_gestionar_turnos = models.BooleanField(default=False)
    puede_cancelar_turnos = models.BooleanField(default=False)

    # Reportes y Auditoría
    puede_generar_reportes = models.BooleanField(default=False)
    puede_ver_estadisticas = models.BooleanField(default=False)
    puede_exportar_datos = models.BooleanField(default=False)
    puede_ver_auditoria = models.BooleanField(default=False)

    # Vínculo opcional al registro de Profesional correspondiente
    profesional = models.ForeignKey(
        'profesionales.Profesional', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='perfiles'
    )

    # Seguridad: email alternativo de recuperación
    email_recuperacion = models.EmailField("Email de recuperación", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"

    def asignar_permisos_por_rol(self):
        r = self.rol
        # reset a valores mínimos seguros
        for f in [
            'puede_admin_usuarios','puede_admin_especialidades','puede_admin_centros','puede_admin_roles',
            'puede_crear_pacientes','puede_ver_pacientes','puede_editar_pacientes','puede_eliminar_pacientes',
            'puede_crear_historias','puede_ver_historias','puede_editar_historias','puede_ver_historias_otros',
            'puede_crear_turnos','puede_ver_calendario','puede_gestionar_turnos','puede_cancelar_turnos',
            'puede_generar_reportes','puede_ver_estadisticas','puede_exportar_datos','puede_ver_auditoria',
        ]:
            setattr(self, f, False)
        # defaults por rol
        if r == 'admin':
            for f in [
                'puede_admin_usuarios','puede_admin_especialidades','puede_admin_centros','puede_admin_roles',
                'puede_crear_pacientes','puede_ver_pacientes','puede_editar_pacientes','puede_eliminar_pacientes',
                'puede_crear_historias','puede_ver_historias','puede_editar_historias','puede_ver_historias_otros',
                'puede_crear_turnos','puede_ver_calendario','puede_gestionar_turnos','puede_cancelar_turnos',
                'puede_generar_reportes','puede_ver_estadisticas','puede_exportar_datos','puede_ver_auditoria',
            ]:
                setattr(self, f, True)
        elif r == 'prof':
            self.puede_ver_pacientes = True
            self.puede_crear_historias = True
            self.puede_ver_historias = True
            self.puede_editar_historias = True
            self.puede_crear_turnos = True
            self.puede_ver_calendario = True
            self.puede_cancelar_turnos = True
            self.puede_generar_reportes = True
        elif r == 'recep':
            self.puede_crear_pacientes = True
            self.puede_ver_pacientes = True
            self.puede_editar_pacientes = True
            self.puede_crear_turnos = True
            self.puede_cancelar_turnos = True
            self.puede_ver_calendario = True


class AuditoriaLog(models.Model):
    ACCIONES = (
        ('access', 'Acceso'),
        ('create', 'Creación'),
        ('update', 'Actualización'),
        ('delete', 'Eliminación'),
        ('export', 'Exportación'),
        ('report', 'Reporte'),
    )
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    accion = models.CharField(max_length=12, choices=ACCIONES)
    app_label = models.CharField(max_length=50, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    objeto_id = models.CharField(max_length=64, blank=True)
    ruta = models.CharField(max_length=255, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    detalle = models.TextField(blank=True)
    fecha = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-fecha']
        indexes = [models.Index(fields=['fecha']), models.Index(fields=['accion'])]

    def __str__(self):
        u = self.usuario.username if self.usuario else 'anon'
        return f"{self.fecha:%Y-%m-%d %H:%M} {u} {self.accion} {self.modelo}:{self.objeto_id}"


class LoginThrottle(models.Model):
    """Registra intentos fallidos por (username, ip) con cooldown opcional."""

    username = models.CharField(max_length=150, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    count = models.PositiveIntegerField(default=0)
    first_attempt = models.DateTimeField(default=timezone.now)
    last_attempt = models.DateTimeField(default=timezone.now)
    locked_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["username", "ip"]),
            models.Index(fields=["locked_until"]),
        ]

    def register_fail(self, window_seconds=600, threshold=5, cooldown_seconds=900):
        now = timezone.now()
        # Reset ventana si pasó el tiempo
        if (now - self.first_attempt).total_seconds() > window_seconds:
            self.count = 0
            self.first_attempt = now
        self.count += 1
        self.last_attempt = now
        # Bloquear si alcanza umbral
        if self.count >= threshold:
            self.locked_until = now + timezone.timedelta(seconds=cooldown_seconds)
        self.save()

    def is_locked(self):
        if not self.locked_until:
            return False
        return timezone.now() < self.locked_until

    def remaining_seconds(self):
        if not self.locked_until:
            return 0
        delta = (self.locked_until - timezone.now()).total_seconds()
        return int(delta) if delta > 0 else 0
