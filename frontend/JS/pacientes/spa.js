// ---------- util CSRF ----------
function getCookie(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? decodeURIComponent(m.pop()) : null;
}
const csrftoken = getCookie('csrftoken');

// ---------- refs ----------
const tbody = document.getElementById('pacientes-tbody');
const flash = document.getElementById('flash');

const modalForm = document.getElementById('modalForm');
const modalTitle = document.getElementById('modalTitle');
const form = document.getElementById('formPaciente');
const btnNuevo = document.getElementById('btnNuevo');
const btnCancelar = document.getElementById('btnCancelar');
const btnCerrarModal = document.getElementById('btnCerrarModal');

const modalConfirm = document.getElementById('modalConfirm');
const btnNo = document.getElementById('btnNo');
const btnSi = document.getElementById('btnSi');

let editId = null;      // null = crear, número = editar
let deleteId = null;

// ---------- helpers UI ----------
function showFlash(msg, type = 'ok') {
  // type: 'ok' | 'error'
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
  modalTitle.textContent = 'Registrar Paciente';
  form.reset();
  modalForm.style.display = 'block';
}

function openModalEdit(p) {
  editId = p.id;
  modalTitle.textContent = 'Editar Paciente';
  form.reset();

  // set values
  document.getElementById('pacienteId').value = p.id ?? '';
  document.getElementById('apellido').value = p.apellido ?? '';
  document.getElementById('nombre').value = p.nombre ?? '';
  document.getElementById('dni').value = p.dni ?? '';
  document.getElementById('fecha_nacimiento').value = (p.fecha_nacimiento || '').slice(0, 10);
  document.getElementById('telefono').value = p.telefono ?? '';
  document.getElementById('direccion').value = p.direccion ?? '';
  document.getElementById('nacionalidad').value = p.nacionalidad ?? '';
  document.getElementById('tiene_representante').checked = !!p.tiene_representante;
  document.getElementById('rep_nombre').value = p.rep_nombre ?? '';
  document.getElementById('rep_apellido').value = p.rep_apellido ?? '';
  document.getElementById('rep_edad').value = p.rep_edad ?? '';
  document.getElementById('rep_telefono').value = p.rep_telefono ?? '';
  document.getElementById('rep_nacionalidad').value = p.rep_nacionalidad ?? '';

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

// ---------- API base ----------
const API_BASE = '/pacientes/api/pacientes/';

async function apiList() {
  const resp = await fetch(API_BASE, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
    credentials: 'same-origin',
  });
  if (!resp.ok) throw new Error('GET ' + resp.status);
  return await resp.json();
}

async function apiGet(id) {
  const resp = await fetch(API_BASE + id + '/', {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
    credentials: 'same-origin',
  });
  if (!resp.ok) throw new Error('GET id ' + resp.status);
  return await resp.json();
}

async function apiCreate(payload) {
  const resp = await fetch(API_BASE, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  if (resp.status === 400) {
    const err = await resp.json();
    throw { type: 'validation', detail: err };
  }
  if (!resp.ok) throw new Error('POST ' + resp.status);
  return await resp.json();
}

async function apiUpdate(id, payload) {
  const resp = await fetch(API_BASE + id + '/', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  if (resp.status === 400) {
    const err = await resp.json();
    throw { type: 'validation', detail: err };
  }
  if (!resp.ok) throw new Error('PUT ' + resp.status);
  return await resp.json();
}

async function apiDelete(id) {
  const resp = await fetch(API_BASE + id + '/', {
    method: 'DELETE',
    headers: { 'X-CSRFToken': csrftoken },
    credentials: 'same-origin',
  });
  if (!resp.ok) throw new Error('DELETE ' + resp.status);
}

// ---------- render ----------
async function renderList() {
  tbody.innerHTML = `<tr><td colspan="5">Cargando...</td></tr>`;
  try {
    const list = await apiList();
    if (!Array.isArray(list) || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#666;">No hay pacientes cargados.</td></tr>`;
      return;
    }
    tbody.innerHTML = '';
    list.forEach(p => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${p.apellido ?? ''}</td>
        <td>${p.nombre ?? ''}</td>
        <td>${p.dni ?? ''}</td>
        <td>${p.telefono ?? ''}</td>
        <td style="white-space:nowrap; display:flex; gap:6px;">
          <button class="btn btn-editar" data-edit="${p.id}">Editar</button>
          <button class="btn btn-eliminar" data-del="${p.id}">Eliminar</button>
        </td>
      `;
      // editar
      tr.querySelector('[data-edit]').addEventListener('click', async () => {
        try {
          const full = await apiGet(p.id);
          openModalEdit(full);
        } catch (e) {
          console.error(e);
          showFlash('No se pudo cargar el paciente', 'error');
        }
      });
      // eliminar
      tr.querySelector('[data-del]').addEventListener('click', () => openConfirm(p.id));
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
    tbody.innerHTML = `<tr><td colspan="5" style="color:#c00;">Error cargando pacientes</td></tr>`;
  }
}

// ---------- form submit ----------
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // validación básica
  const apellido = document.getElementById('apellido').value.trim();
  const nombre = document.getElementById('nombre').value.trim();
  const dni = document.getElementById('dni').value.trim();

  if (!apellido || !nombre || !dni) {
    showFlash('Apellido, Nombre y DNI son obligatorios', 'error');
    return;
  }

  const payload = {
    apellido,
    nombre,
    dni,
    fecha_nacimiento: document.getElementById('fecha_nacimiento').value || null,
    telefono: document.getElementById('telefono').value || '',
    direccion: document.getElementById('direccion').value || '',
    nacionalidad: document.getElementById('nacionalidad').value || '',
    tiene_representante: document.getElementById('tiene_representante').checked,
    rep_nombre: document.getElementById('rep_nombre').value || '',
    rep_apellido: document.getElementById('rep_apellido').value || '',
    rep_edad: document.getElementById('rep_edad').value ? Number(document.getElementById('rep_edad').value) : null,
    rep_telefono: document.getElementById('rep_telefono').value || '',
    rep_nacionalidad: document.getElementById('rep_nacionalidad').value || '',
  };

  try {
    if (editId === null) {
      await apiCreate(payload);
      showFlash('Paciente creado correctamente');
    } else {
      await apiUpdate(editId, payload);
      showFlash('Paciente actualizado correctamente');
    }
    closeModal();
    await renderList();
  } catch (err) {
    console.error(err);
    if (err.type === 'validation' && err.detail) {
      // Mostrar primeros errores de DRF
      const firstField = Object.keys(err.detail)[0];
      const msg = Array.isArray(err.detail[firstField]) ? err.detail[firstField][0] : JSON.stringify(err.detail);
      showFlash(`Error de validación: ${firstField}: ${msg}`, 'error');
    } else {
      showFlash('No se pudo guardar el paciente', 'error');
    }
  }
});

// ---------- eventos UI ----------
btnNuevo.addEventListener('click', openModalCreate);
btnCancelar.addEventListener('click', closeModal);
btnCerrarModal.addEventListener('click', closeModal);

btnNo.addEventListener('click', closeConfirm);
btnSi.addEventListener('click', async () => {
  if (deleteId == null) return;
  try {
    await apiDelete(deleteId);
    showFlash('Paciente eliminado');
    closeConfirm();
    await renderList();
  } catch (e) {
    console.error(e);
    showFlash('No se pudo eliminar', 'error');
  }
});

// ---------- init ----------
document.addEventListener('DOMContentLoaded', renderList);
