Resumen de cobertura de Casos de Uso (CU) vs implementación actual

CU_001 – Registrar Paciente
- Estado: Cubierto (SPA en `frontend/HTML/pacientes/pacientes_list.html` + `frontend/JS/pacientes/spa.js`) con validación y CRUD vía DRF (`backend/apps/pacientes/api_views.py`, `serializers.py`).
- Ajustes agregados: Confirmación antes de Guardar. Validación de email único (mensaje: “Ya existe un paciente con ese correo”). Campo M2M para asignar profesionales.
- Gap menor: Campos de “Representante legal” están en el frontend pero no en el modelo; evaluar si deben persistirse.

CU_002 – Registrar Turno
- Estado: Cubierto (SPA `frontend/HTML/turnos/turnos_list.html` + `frontend/JS/turnos/spa.js`) y API (`backend/apps/turnos`). Solapamiento validado en serializer.
- Ajustes agregados: Confirmación antes de Guardar.

CU_003 – Registrar Profesional
- Estado: Cubierto (SPA `frontend/HTML/profesionales/profesionales_list.html` + `frontend/JS/profesionales/spa2.js`) y API (`backend/apps/profesionales`).
- Ajustes agregados: Confirmación antes de Guardar. Validación de email único (mensaje solicitado).

CU_004 – Consultar Historia Clínica
- Estado: Cubierto (vista `frontend/HTML/historia_clinica.html`, API `backend/apps/medical_records`). Exportación a PDF disponible en módulo de reportes.

CU_005 – Registrar Sesión
- Estado: Cubierto (formulario en `historia_clinica.html` con POST a `historias/api/observaciones/`).
- Ajustes agregados: Confirmación antes de Guardar.

CU_006 – Editar Sesión
- Estado: Parcial. API soporta PUT, se agregó edición en la UI: click en fila carga datos y guarda vía PUT.

CU_007 – Eliminar Sesión
- Estado: Parcial. API soporta DELETE, se agregó botón “Eliminar Observación” en la UI con confirmación.

CU_008 – Asignar Profesional
- Estado: Nuevo soporte básico: relación M2M `Paciente.profesionales_asignados` + campos en serializer. Falta UI específica para asignación desde el listado de pacientes (se puede consumir vía API por ahora).

CU_009 – Registrar Informe Final (Epicrisis)
- Estado: Cubierto mediante “Epicrisis” en módulo de reportes (`backend/apps/reports`) y vista `frontend/HTML/reports/report_viewer.html`.

CU_010 – Consultar Informe Final
- Estado: Cubierto (descarga/visualización de PDFs generados en reportes).

CU_011 – Modificar Turno
- Estado: Cubierto (editar en SPA + API PUT).

CU_012 – Eliminar Turno
- Estado: Cubierto (eliminar en SPA + API DELETE con confirmación).

CU_013 – Modificar Profesional
- Estado: Cubierto (editar en SPA + API PUT).

CU_014 – Eliminar Profesional
- Estado: Cubierto (eliminar en SPA + API DELETE con confirmación).

CU_015 – Modificar Paciente
- Estado: Cubierto (editar en SPA + API PUT).

CU_016 – Eliminar Paciente
- Estado: Cubierto (eliminar en SPA + API DELETE con confirmación).

CU_017 – Iniciar Sesión
- Estado: Cubierto (Django auth: `backend/core/urls.py` -> `registration/login.html`).

CU_018 – Recuperar Contraseña
- Estado: Cubierto (password reset flow y templates en `frontend/HTML/registration` y `frontend/EMAILS`).

CU_019 – Gestión de Roles y Permisos
- Estado: Parcial. Implementado con perfil y flags (`backend/apps/usuarios/models.Perfil`) y SPA de usuarios. No existe entidad “Rol” editable separada, pero se asignan permisos por perfil.

CU_020 – Gestionar Catálogos
- Estado: Cubierto (Centros, Obras Sociales, Especialidades: apps `centers`, `obras`, `profesionales` + vistas SPA).

CU_021 – Visualización de Agenda
- Estado: Parcial. Hay calendario mensual simple en dashboard y listado de turnos con filtros por rango; no hay vista semanal/mensual completa tipo calendario interactivo.

CU_022 – Exportación de Informe Final a PDF
- Estado: Cubierto (módulo `reports` con WeasyPrint; vistas para historia, epicrisis, certificado y estadísticas).


