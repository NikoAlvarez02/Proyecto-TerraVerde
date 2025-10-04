// ====== CSRF ======
function getCookie(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? decodeURIComponent(m.pop()) : null;
}
const csrftoken = getCookie('csrftoken');

// ====== refs ======
const tbody = document.getElementById('usuarios-tbody');
const flash = document.getElementById('flash');

const modalForm = document.getElementById('modalForm');
const modalTitle = document.getElementById('modalTitle');
const form = document.getElementById('formUsuario');
const btnNuevo = document.getElementById('btnNuevo');
const btnCancelar = document.getElementById('btnCancelar');
const btnCerrarModal = document.getElementById('btnCerrarModal');

const modalConfirm = document.getElementById('modalConfirm');
const btnNo = document.getElementById('btnNo');
const btnSi = document.getElementById('btnSi');

let editId = null;
let deleteId = null;

const API_BASE = '/usuarios/api/usuarios/';

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
  modalTitle.textContent = 'Nuevo Usuario';
  form.reset();
  document.getElementById('is_active').checked = true;
  document.getElementById('is_staff').checked = false;
  document.getElementById('is_superuser').checked = false;
  modalForm.style.display = 'block';
}

function openModalEdit(u) {
  editId = u.id;
  modalTitle.textContent = 'Editar Usuario';
  form.reset();

  document.getElementById('usuarioId').value = u.id ?? '';
  document.getElementById('username').value = u.username ?? '';
  document.getElementById('email').value = u.email ?? '';
  document.getElementById('first_name').value = u.first_name ?? '';
  document.getElementById('last_name').value = u.last_name ?? '';

  document.getElementById('password').value = '';
  document.getElementById('password2').value = '';

  document.getElementById('is_active').checked = !!u.is_active;
  document.getElementById('is_staff').checked = !!u.is_staff;
  document.getElementById('is_superuser').checked = !!u.is_superuser;

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
    // Si no sos staff, el backend te devolverá sólo TU usuario
    if (!Array.isArray(list) || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#666;">Sin usuarios.</td></tr>`;
      return;
    }
    tbody.innerHTML = '';
    list.forEach(u => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${u.username ?? ''}</td>
        <td>${u.full_name ?? ''}</td>
        <td>${u.email ?? ''}</td>
        <td>${u.is_active ? 'Sí' : 'No'}</td>
        <td>${u.is_staff ? 'Sí' : 'No'}</td>
        <td style="white-space:nowrap; display:flex; gap:6px;">
          <button class="btn btn-editar" data-edit="${u.id}">Editar</button>
          <button class="btn btn-eliminar" data-del="${u.id}">Eliminar</button>
        </td>
      `;
      tr.querySelector('[data-edit]').addEventListener('click', async () => {
        try {
          const full = await apiGet(u.id);
          openModalEdit(full);
        } catch (e) {
          console.error(e);
          showFlash('No se pudo cargar el usuario', 'error');
        }
      });
      tr.querySelector('[data-del]').addEventListener('click', () => openConfirm(u.id));
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
    tbody.innerHTML = `<tr><td colspan="6" style="color:#c00;">Error cargando usuarios</td></tr>`;
  }
}

// ====== submit form ======
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // validación mínima
  const username = document.getElementById('username').value.trim();
  const email = document.getElementById('email').value.trim();
  if (!username || !email) {
    showFlash('Username y Email son obligatorios', 'error');
    return;
  }

  const first_name = document.getElementById('first_name').value || '';
  const last_name  = document.getElementById('last_name').value || '';
  const is_active = document.getElementById('is_active').checked;
  const is_staff = document.getElementById('is_staff').checked;
  const is_superuser = document.getElementById('is_superuser').checked;

  const password = document.getElementById('password').value;
  const password2 = document.getElementById('password2').value;

  if (editId === null) { // crear
    if (!password) {
      showFlash('Password es obligatorio al crear', 'error');
      return;
    }
    if (password !== password2) {
      showFlash('Las contraseñas no coinciden', 'error');
      return;
    }
  } else { // editar
    if (password || password2) {
      if (password !== password2) {
        showFlash('Las contraseñas no coinciden', 'error');
        return;
      }
    }
  }

  // payload base
  const payload = {
    username, email, first_name, last_name,
    is_active, is_staff, is_superuser,
  };
  // incluir password sólo si corresponde
  if (password) payload.password = password;

  try {
    if (editId === null) {
      await apiCreate(payload);
      showFlash('Usuario creado');
    } else {
      await apiUpdate(editId, payload);
      showFlash('Usuario actualizado');
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
      showFlash('No se pudo guardar el usuario (¿tenés permisos?)', 'error');
    }
  }
});

// ====== eventos ======
btnNuevo.addEventListener('click', openModalCreate);
btnCancelar.addEventListener('click', closeModal);
btnCerrarModal.addEventListener('click', closeModal);

btnNo.addEventListener('click', closeConfirm);
btnSi.addEventListener('click', async () => {
  if (deleteId == null) return;
  try {
    await apiDelete(deleteId);
    showFlash('Usuario eliminado');
    closeConfirm();
    await renderList();
  } catch (e) {
    console.error(e);
    showFlash('No se pudo eliminar (¿permisos?)', 'error');
  }
});

// ====== init ======
document.addEventListener('DOMContentLoaded', renderList);
