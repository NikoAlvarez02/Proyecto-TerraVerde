document.addEventListener('DOMContentLoaded', () => {
  // ------- Estado (sin dummies por defecto) -------
  let turnos = Array.isArray(window.INIT_TURNOS) ? [...window.INIT_TURNOS] : [];
  const horariosOcupados = Array.isArray(window.HORARIOS_OCUPADOS) ? [...window.HORARIOS_OCUPADOS] : [];

  // ------- DOM -------
  const listadoTurnosDiv   = document.getElementById('listado-turnos');
  const editFormContainer  = document.getElementById('edit-form-container');
  const turnosTableBody    = document.querySelector('#turnos-table tbody');
  const editTurnoForm      = document.getElementById('edit-turno-form');
  const formTitle          = document.getElementById('form-title');
  const btnAgregarTurno    = document.getElementById('btn-agregar-turno');
  const cancelarEditBtn    = document.querySelector('.btn-cancelar-edit');

  // Inputs del form
  const formTurnoIdInput     = document.getElementById('edit-turno-id');
  const formPacienteInput    = document.getElementById('edit-paciente');
  const formProfesionalInput = document.getElementById('edit-profesional');
  const formFechaInput       = document.getElementById('edit-fecha');
  const formHoraInput        = document.getElementById('edit-hora');
  const formDescripcionInput = document.getElementById('edit-descripcion');

  // ------- Helpers -------
  function showList() {
    editFormContainer.classList.add('hidden');
    listadoTurnosDiv.classList.remove('hidden');
  }
  function showForm() {
    listadoTurnosDiv.classList.add('hidden');
    editFormContainer.classList.remove('hidden');
  }

  function renderTurnos() {
    if (!turnosTableBody) return;
    turnosTableBody.innerHTML = '';
    if (!Array.isArray(turnos) || !turnos.length) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td colspan="5" style="text-align:center;color:#666">No hay turnos cargados.</td>`;
      turnosTableBody.appendChild(tr);
      return;
    }
    turnos.forEach(t => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${t.paciente}</td>
        <td>${t.profesional}</td>
        <td>${t.fecha}</td>
        <td>${t.hora}</td>
        <td>
          <button class="btn btn-editar" data-id="${t.id}">Editar</button>
          <button class="btn btn-eliminar" data-id="${t.id}">Eliminar</button>
        </td>`;
      turnosTableBody.appendChild(row);
    });
  }

  function setupFormForAdd() {
    formTitle.textContent = 'Registrar Turno';
    formTurnoIdInput.value = '';
    formPacienteInput.value = '';
    formProfesionalInput.value = '';
    formFechaInput.value = '';
    formHoraInput.value = '';
    formDescripcionInput.value = '';
    formPacienteInput.disabled = false;
    showForm();
  }

  function setupFormForEdit(turno) {
    formTitle.textContent = 'Modificar Turno';
    formTurnoIdInput.value = turno.id;
    formPacienteInput.value = turno.paciente;
    formProfesionalInput.value = turno.profesional;
    formFechaInput.value = turno.fecha;
    formHoraInput.value = turno.hora;
    formDescripcionInput.value = turno.descripcion;
    formPacienteInput.disabled = true; // no editamos paciente al modificar
    showForm();
  }

  // ------- Eventos -------
  if (btnAgregarTurno) btnAgregarTurno.addEventListener('click', setupFormForAdd);

  if (turnosTableBody) {
    turnosTableBody.addEventListener('click', (e) => {
      const btn = e.target.closest('button');
      if (!btn) return;

      const turnoId = parseInt(btn.dataset.id, 10);
      if (btn.classList.contains('btn-editar')) {
        const turno = turnos.find(x => x.id === turnoId);
        if (turno) setupFormForEdit(turno);
      }

      if (btn.classList.contains('btn-eliminar')) {
        if (!confirm('¿Eliminar este turno?')) return;
        const idx = turnos.findIndex(x => x.id === turnoId);
        if (idx > -1) {
          turnos.splice(idx, 1);
          renderTurnos();
        }
      }
    });
  }

  if (editTurnoForm) {
    editTurnoForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const id   = formTurnoIdInput.value.trim();
      const pac  = formPacienteInput.value.trim();
      const prof = formProfesionalInput.value.trim();
      const fecha= formFechaInput.value.trim();
      const hora = formHoraInput.value.trim();
      const desc = formDescripcionInput.value.trim();

      if (!prof || !fecha || !hora || !desc || (id === '' && !pac)) {
        alert('Completá todos los campos obligatorios.');
        return;
      }

      // Chequeo disponibilidad (si hay datos de ocupados)
      const ocupado = Array.isArray(horariosOcupados) && horariosOcupados.some(h =>
        h.profesional === prof && h.fecha === fecha && h.hora === hora
      );
      if (ocupado) {
        alert('El profesional no está disponible en ese horario.');
        return;
      }

      if (id === '') {
        // Crear
        const nuevoId = turnos.length ? Math.max(...turnos.map(t => t.id || 0)) + 1 : 1;
        turnos.push({ id: nuevoId, paciente: pac, profesional: prof, fecha, hora, descripcion: desc });
      } else {
        // Editar
        const idx = turnos.findIndex(t => String(t.id) === id);
        if (idx > -1) {
          turnos[idx] = { ...turnos[idx], profesional: prof, fecha, hora, descripcion: desc };
        }
      }

      showList();
      renderTurnos();
    });
  }

  if (cancelarEditBtn) {
    cancelarEditBtn.addEventListener('click', showList);
  }

  // Primera renderización
  renderTurnos();
});
