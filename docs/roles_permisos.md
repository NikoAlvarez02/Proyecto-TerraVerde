Matriz de Roles y Permisos — TerraVerde

Roles estándar
- Administrador (`admin`): acceso total.
- Recepcionista (`recep`): gestiona pacientes (alta/edición adm.), crea/cancela turnos, ve agenda.
- Profesional (`prof`): gestiona sus sesiones, crea/cancela turnos propios, ve su agenda, reportes propios.

Flags de Perfil (backend/apps/usuarios/models.py)
- Administración: `puede_admin_usuarios`, `puede_admin_especialidades`, `puede_admin_centros`, `puede_admin_roles`.
- Pacientes: `puede_crear_pacientes`, `puede_ver_pacientes`, `puede_editar_pacientes`, `puede_eliminar_pacientes`.
- Historia clínica: `puede_crear_historias`, `puede_ver_historias`, `puede_editar_historias`, `puede_ver_historias_otros`.
- Turnos: `puede_crear_turnos`, `puede_ver_calendario`, `puede_gestionar_turnos`, `puede_cancelar_turnos`.
- Reportes/Auditoría: `puede_generar_reportes`, `puede_ver_estadisticas`, `puede_exportar_datos`, `puede_ver_auditoria`.

Asignación por rol (método `Perfil.asignar_permisos_por_rol`)
- Admin: todos los flags en True.
- Prof: ver_pacientes, crear/ver/editar_historias, crear_turnos, ver_calendario, cancelar_turnos, generar_reportes.
- Recep: crear/ver/editar_pacientes, crear_turnos, cancelar_turnos, ver_calendario.

Usuarios de ejemplo (management command)
- `python backend/manage.py bootstrap_default_users --password "<pwd>"`
  - Crea: `admin`, `recepcion`, `profesional` y asigna roles + permisos por defecto.

