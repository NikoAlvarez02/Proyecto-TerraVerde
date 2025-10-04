// ====== CSRF ======
function getCookie(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? decodeURIComponent(m.pop()) : null;
}
const csrftoken = getCookie('csrftoken');

// ====== refs ======
const tbody = document.getElementById('turnos-tbody');
const flash = document.getElementById('flash');

const modalForm = document.getElementById('modalForm');
const modalTitle = document.getElementById('modalTitle');
const form = document.getElementById('formTurno');
const btnNuevo = document.getElementById('btnNuevo');
const btnCancelar = document.getElementById('btnCancelar');
const btnCerrarModal = document.getElementById('btnCerrarModal');

const modalConfirm = document.getElementById('modalConfirm');
const btnNo = document.getElementById('btnNo');
const btnSi = document.getElementById('btnSi');

const selPaciente = document.getElementById('paciente');
const selProfesional = document.getElementById('profesional');

let editId = null;
let deleteId = null;

const API_TURNOS = '/turnos/api/turnos/';
const API_PACIENTES = '/pacientes/api/pacientes/';
const API_PROFESIONALES = '/profesionales/api/profesionales/';

// ====== helpers UI ======
function showFlash(msg, type = 'ok') {
  flash.style.display = 'block';
  flash.style.padding = '8px';
  flash.style.borderRadius = '8px';
  flash.style.background = type === 'ok' ? '#e6ffed' : '#ffe6e6';
  flash.style.border = '1px solid ' + (type === 'ok' ? '#89d79d' : '#e08b8b');
  flash.style.color = '#333';
  flash.textContent = msg;
  setTimeout(() => (flash.style.display = 'none'), 2500);
}

function openModalCreate() {
  editId = null;
  modalTitle.textContent = 'Nuevo Turno';
  form.reset();
  modalForm.style.display = 'block';
}

function openModalEdit(t) {
  editId = t.id;
  modalTitle.textContent = 'Editar Turno';
  form.reset();

  // set fields
  document.getElementById('turnoId').value = t.id;
  document.getElementById('fecha').value = (t.fecha || '').slice(0,10);
  document.getElementById('hora').value = (t.hora || '').slice(0,5);
  document.getElementById('estado').value = t.estado || 'pendiente';
  document.getElementById('motivo').value = t.motivo || '';
  document.getElementById('observaciones').value = t.observaciones || '';

  // selects (asegurate que ya estén cargados)
  selPaciente.value = t.paciente || '';
  selProfesional.value = t.profesional || '';

  modalForm.style.display = 'block';
}

function closeModal() {
  modalForm.style.display = 'none';
}

function openConfirm(id) {
  deleteId = id;
  modalConfirm.style.display = 'block';
}

function closeConfirm() {
  deleteId = null;
  modalConfirm.style.display = 'none';
}

// ====== API base ======
async function apiList() {
  const resp = await fetch(API_TURNOS, { credentials:'same-origin' });
  if (!resp.ok) throw new Error('GET ' + resp.status);
  return await resp.json();
}
async function apiGet(id) {
  const resp = await fetch(API_TURNOS + id + '/', { credentials:'same-origin' });
  if (!resp.ok) throw new Error('GET id ' + resp.status);
  return await resp.json();
}
async function apiCreate(payload) {
  const resp = await fetch(API_TURNOS, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  if (resp.status === 400) throw { type:'validation', detail: await resp.json() };
  if (!resp.ok) throw new Error('POST ' + resp.status);
  return await resp.json();
}
async function apiUpdate(id, payload) {
  const resp = await fetch(API_TURNOS + id + '/', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  if (resp.status === 400) throw { type:'validation', detail: await resp.json() };
  if (!resp.ok) throw new Error('PUT ' + resp.status);
  return await resp.json();
}
async function apiDelete(id) {
  const resp = await fetch(API_TURNOS + id + '/', {
    method: 'DELETE',
    headers: { 'X-CSRFToken': csrftoken },
    credentials: 'same-origin',
  });
  if (!resp.ok) throw new Error('DELETE ' + resp.status);
}

// ====== cargar selects (pacientes / profesionales) ======
async function loadPacientes() {
  selPaciente.innerHTML = `<option value="">Cargando...</option>`;
  const resp = await fetch(API_PACIENTES, { credentials:'same-origin' });
  if (!resp.ok) { selPaciente.innerHTML = `<option value="">Error</option>`; return; }
  const data = await resp.json();
  selPaciente.innerHTML = `<option value="">Seleccione…</option>`;
  data.forEach(p => {
    const opt = document.createElement('option');
    // Ajustá label según tus campos reales
    opt.value = p.id;
    opt.textContent = `${p.apellido ?? ''}, ${p.nombre ?? ''} (${p.dni ?? ''})`;
    selPaciente.appendChild(opt);
  });
}
async function loadProfesionales() {
  selProfesional.innerHTML = `<option value="">Cargando...</option>`;
  const resp = await fetch(API_PROFESIONALES, { credentials:'same-origin' });
  if (!resp.ok) { selProfesional.innerHTML = `<option value="">Error</option>`; return; }
  const data = await resp.json();
  selProfesional.innerHTML = `<option value="">Seleccione…</option>`;
  data.forEach(p => {
    const opt = document.createElement('option');
    // Ajustá label según tus campos reales
    opt.value = p.id;
    opt.textContent = `${p.apellido ?? ''}, ${p.nombre ?? ''}`;
    selProfesional.appendChild(opt);
  });
}
async function ensureOptions() {
  await Promise.all([loadPacientes(), loadProfesionales()]);
}

// ====== render listado ======
async function renderList() {
  tbody.innerHTML = `<tr><td colspan="6">Cargando...</td></tr>`;
  try {
    const list = await apiList();
    if (!Array.isArray(list) || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#666;">No hay turnos.</td></tr>`;
      return;
    }
    tbody.innerHTML = '';
    list.forEach(t => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${t.fecha ?? ''}</td>
        <td>${(t.hora || '').slice(0,5)}</td>
        <td>${t.paciente_nombre ?? t.paciente}</td>
        <td>${t.profesional_nombre ?? t.profesional}</td>
        <td>${t.estado ?? ''}</td>
        <td style="white-space:nowrap; display:flex; gap:6px;">
          <button class="btn btn-editar" data-edit="${t.id}">Editar</button>
          <button class="btn btn-eliminar" data-del="${t.id}">Eliminar</button>
        </td>
      `;
      tr.querySelector('[data-edit]').addEventListener('click', async () => {
        try {
          const full = await apiGet(t.id);
          await ensureOptions();        // asegurá opciones cargadas
          openModalEdit(full);
        } catch (e) {
          console.error(e);
          showFlash('No se pudo cargar el turno', 'error');
        }
      });
      tr.querySelector('[data-del]').addEventListener('click', () => openConfirm(t.id));
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
    tbody.innerHTML = `<tr><td colspan="6" style="color:#c00;">Error cargando turnos</td></tr>`;
  }
}

// ====== submit form ======
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // validación mínima
  const fecha = document.getElementById('fecha').value;
  const hora = document.getElementById('hora').value;
  const paciente = selPaciente.value;
  const profesional = selProfesional.value;
  const estado = document.getElementById('estado').value;

  if (!fecha || !hora || !paciente || !profesional || !estado) {
    showFlash('Fecha, hora, paciente, profesional y estado son obligatorios', 'error');
    return;
  }

  const payload = {
    fecha,
    hora,
    paciente: Number(paciente),
    profesional: Number(profesional),
    estado,
    motivo: document.getElementById('motivo').value || '',
    observaciones: document.getElementById('observaciones').value || '',
  };

  // Si tu modelo usa fecha_hora (DateTimeField), usá esto en su lugar:
  // const payload = {
  //   paciente: Number(paciente),
  //   profesional: Number(profesional),
  //   estado,
  //   motivo: ...,
  //   observaciones: ...,
  //   fecha_hora: `${fecha}T${hora}:00`, // o construir un ISO completo
  // };

  try {
    if (editId === null) {
      await apiCreate(payload);
      showFlash('Turno creado');
    } else {
      await apiUpdate(editId, payload);
      showFlash('Turno actualizado');
    }
    closeModal();
    await renderList();
  } catch (err) {
    console.error(err);
    if (err.type === 'validation') {
      const first = Object.keys(err.detail)[0];
      const msg = Array.isArray(err.detail[first]) ? err.detail[first][0] : JSON.stringify(err.detail);
      showFlash(`Validación: ${first}: ${msg}`, 'error');
    } else {
      showFlash('No se pudo guardar el turno', 'error');
    }
  }
});

// ====== eventos ======
btnNuevo.addEventListener('click', async () => { await ensureOptions(); openModalCreate(); });
btnCancelar.addEventListener('click', closeModal);
btnCerrarModal.addEventListener('click', closeModal);

btnNo.addEventListener('click', closeConfirm);
btnSi.addEventListener('click', async () => {
  if (deleteId == null) return;
  try {
    await apiDelete(deleteId);
    showFlash('Turno eliminado');
    closeConfirm();
    await renderList();
  } catch (e) {
    console.error(e);
    showFlash('No se pudo eliminar', 'error');
  }
});

// ====== init ======
document.addEventListener('DOMContentLoaded', renderList);
