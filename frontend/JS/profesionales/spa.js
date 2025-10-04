// ====== CSRF ======
function getCookie(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? decodeURIComponent(m.pop()) : null;
}
const csrftoken = getCookie('csrftoken');

// ====== refs ======
const tbody = document.getElementById('profesionales-tbody');
const flash = document.getElementById('flash');

const modalForm = document.getElementById('modalForm');
const modalTitle = document.getElementById('modalTitle');
const form = document.getElementById('formProfesional');
const btnNuevo = document.getElementById('btnNuevo');
const btnCancelar = document.getElementById('btnCancelar');
const btnCerrarModal = document.getElementById('btnCerrarModal');

const modalConfirm = document.getElementById('modalConfirm');
const btnNo = document.getElementById('btnNo');
const btnSi = document.getElementById('btnSi');

let editId = null;
let deleteId = null;

const API_BASE = '/profesionales/api/profesionales/';

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
  modalTitle.textContent = 'Nuevo Profesional';
  form.reset();
  document.getElementById('activo').checked = true;
  modalForm.style.display = 'block';
}

function openModalEdit(p) {
  editId = p.id;
  modalTitle.textContent = 'Editar Profesional';
  form.reset();

  document.getElementById('profesionalId').value = p.id ?? '';
  document.getElementById('apellido').value = p.apellido ?? '';
  document.getElementById('nombre').value = p.nombre ?? '';
  document.getElementById('dni').value = p.dni ?? '';
  document.getElementById('matricula').value = p.matricula ?? '';
  document.getElementById('especialidad').value = p.especialidad ?? '';
  document.getElementById('telefono').value = p.telefono ?? '';
  document.getElementById('email').value = p.email ?? '';
  document.getElementById('direccion').value = p.direccion ?? '';
  document.getElementById('activo').checked = !!p.activo;

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

// ====== API ======
async function apiList() {
  const resp = await fetch(API_BASE, { credentials:'same-origin' });
  if (!resp.ok) throw new Error('GET ' + resp.status);
  return await resp.json();
}
async function apiGet(id) {
  const resp = await fetch(API_BASE + id + '/', { credentials:'same-origin' });
  if (!resp.ok) throw new Error('GET id ' + resp.status);
  return await resp.json();
}
async function apiCreate(payload) {
  const resp = await fetch(API_BASE, {
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
  const resp = await fetch(API_BASE + id + '/', {
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
  const resp = await fetch(API_BASE + id + '/', {
    method: 'DELETE',
    headers: { 'X-CSRFToken': csrftoken },
    credentials: 'same-origin',
  });
  if (!resp.ok) throw new Error('DELETE ' + resp.status);
}

// ====== render listado ======
async function renderList() {
  tbody.innerHTML = `<tr><td colspan="6">Cargando...</td></tr>`;
  try {
    const list = await apiList();
    if (!Array.isArray(list) || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#666;">No hay profesionales.</td></tr>`;
      return;
    }
    tbody.innerHTML = '';
    list.forEach(p => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${p.apellido ?? ''}</td>
        <td>${p.nombre ?? ''}</td>
        <td>${p.dni ?? ''}</td>
        <td>${p.especialidad ?? ''}</td>
        <td>${p.telefono ?? ''}</td>
        <td style="white-space:nowrap; display:flex; gap:6px;">
          <button class="btn btn-editar" data-edit="${p.id}">Editar</button>
          <button class="btn btn-eliminar" data-del="${p.id}">Eliminar</button>
        </td>
      `;
      tr.querySelector('[data-edit]').addEventListener('click', async () => {
        try {
          const full = await apiGet(p.id);
          openModalEdit(full);
        } catch (e) {
          console.error(e);
          showFlash('No se pudo cargar el profesional', 'error');
        }
      });
      tr.querySelector('[data-del]').addEventListener('click', () => openConfirm(p.id));
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
    tbody.innerHTML = `<tr><td colspan="6" style="color:#c00;">Error cargando profesionales</td></tr>`;
  }
}

// ====== submit form ======
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // validación mínima
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
    matricula: document.getElementById('matricula').value || '',
    especialidad: document.getElementById('especialidad').value || '',
    telefono: document.getElementById('telefono').value || '',
    email: document.getElementById('email').value || '',
    direccion: document.getElementById('direccion').value || '',
    activo: document.getElementById('activo').checked,
  };

  try {
    if (editId === null) {
      await apiCreate(payload);
      showFlash('Profesional creado');
    } else {
      await apiUpdate(editId, payload);
      showFlash('Profesional actualizado');
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
      showFlash('No se pudo guardar el profesional', 'error');
    }
  }
});

// ====== eventos ======
document.getElementById('btnNuevo').addEventListener('click', () => openModalCreate());
document.getElementById('btnCancelar').addEventListener('click', closeModal);
document.getElementById('btnCerrarModal').addEventListener('click', closeModal);

document.getElementById('btnNo').addEventListener('click', closeConfirm);
document.getElementById('btnSi').addEventListener('click', async () => {
  if (deleteId == null) return;
  try {
    await apiDelete(deleteId);
    showFlash('Profesional eliminado');
    closeConfirm();
    await renderList();
  } catch (e) {
    console.error(e);
    showFlash('No se pudo eliminar', 'error');
  }
});

// ====== init ======
document.addEventListener('DOMContentLoaded', renderList);
