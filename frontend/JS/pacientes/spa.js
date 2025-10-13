// ---------- util CSRF ----------
function getCookie(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? decodeURIComponent(m.pop()) : null;
}
const csrftoken = getCookie('csrftoken');

// ---------- refs ----------
const tbody = document.getElementById('pacientes-tbody');
const flash = document.getElementById('flash');
const inputQ = document.getElementById('q');
const selectOrden = document.getElementById('orden');
const btnBuscar = document.getElementById('btnBuscar');
let nextUrl = null;
let prevUrl = null;
let totalCount = 0;
let currentPage = 1;
let pageSize = 10;
let currentOrdering = '-fecha_registro';
let currentQuery = '';

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
  document.getElementById('email').value = p.email ?? '';
  document.getElementById('genero').value = p.genero ?? '';
  document.getElementById('grupo_sanguineo').value = p.grupo_sanguineo ?? '';
  document.getElementById('alergias').value = p.alergias ?? '';
  document.getElementById('antecedentes').value = p.antecedentes ?? '';
  document.getElementById('contacto_emergencia_nombre').value = p.contacto_emergencia_nombre ?? '';
  document.getElementById('contacto_emergencia_telefono').value = p.contacto_emergencia_telefono ?? '';
  // centro
  if (document.getElementById('centro')) document.getElementById('centro').value = p.centro ?? '';
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

function buildQuery(){
  const params = new URLSearchParams();
  params.set('page_size', String(pageSize));
  if(currentOrdering) params.set('ordering', currentOrdering);
  if(currentQuery) params.set('search', currentQuery);
  return params.toString();
}

async function apiList(url=null) {
  const listUrl = url || (API_BASE + '?' + buildQuery());
  const resp = await fetch(listUrl, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
    credentials: 'include',
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
    const data = await apiList();
    console.log('Pacientes API payload:', data);
    const list = Array.isArray(data) ? data : (data.results || []);
    totalCount = Array.isArray(data) ? list.length : (data.count ?? list.length);
    nextUrl = data.next || null;
    prevUrl = data.previous || null;
    // page calc aproximado si viene paginado
    const pageInfo = document.getElementById('pageInfo');
    if(pageInfo){
      if(data.next || data.previous){
        // infer page from next/prev
        const qp = new URLSearchParams((new URL(window.location.origin + (data.next || data.previous || ''))).search);
        pageSize = Number(qp.get('page_size')||pageSize);
      }
      pageInfo.textContent = totalCount ? `${list.length} de ${totalCount}` : `${list.length}`;
    }
    if (!Array.isArray(list) || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#666;">No hay pacientes cargados.</td></tr>`;
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
        <td>${p.centro_nombre || (p.centro ?? '')}</td>
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
    email: document.getElementById('email').value || '',
    centro: document.getElementById('centro')?.value ? Number(document.getElementById('centro').value) : null,
    genero: document.getElementById('genero').value || '',
    grupo_sanguineo: document.getElementById('grupo_sanguineo').value || '',
    alergias: document.getElementById('alergias').value || '',
    antecedentes: document.getElementById('antecedentes').value || '',
    contacto_emergencia_nombre: document.getElementById('contacto_emergencia_nombre').value || '',
    contacto_emergencia_telefono: document.getElementById('contacto_emergencia_telefono').value || '',
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

// Controles de filtros y paginación
if(btnBuscar){
  btnBuscar.addEventListener('click', async ()=>{
    currentQuery = (inputQ?.value || '').trim();
    currentOrdering = selectOrden?.value || '-fecha_registro';
    await renderList();
  });
}

const btnPrev = document.getElementById('btnPrev');
const btnNext = document.getElementById('btnNext');
if(btnPrev){ btnPrev.addEventListener('click', async ()=>{ if(prevUrl){ await apiList(prevUrl); const data = await apiList(prevUrl); nextUrl=data.next; prevUrl=data.previous; await renderList(); } }); }
if(btnNext){ btnNext.addEventListener('click', async ()=>{ if(nextUrl){ await apiList(nextUrl); const data = await apiList(nextUrl); nextUrl=data.next; prevUrl=data.previous; await renderList(); } }); }

// Asegurar cabecera con columna Centro (por compatibilidad con plantilla actual)
document.addEventListener('DOMContentLoaded', () => {
  const headerRow = document.querySelector('#pacientes-table thead tr');
  if (headerRow) {
    const ths = headerRow.querySelectorAll('th');
    // Si hay 5 columnas (Apellido, Nombre, DNI, Tel..., Acciones), insertar Centro antes de Acciones
    if (ths.length === 5) {
      const thCentro = document.createElement('th');
      thCentro.textContent = 'Centro';
      headerRow.insertBefore(thCentro, ths[ths.length - 1]);
    }
  }
  // cargar centros en el select del formulario
  const selCentro = document.getElementById('centro');
  if (selCentro) {
    fetch('/centros/api/centros/?page_size=500', {credentials:'include'})
      .then(r=>r.ok?r.json():null)
      .then(d=>{
        const list = Array.isArray(d)?d:(d?.results||[]);
        selCentro.innerHTML = '<option value="">(sin centro)</option>';
        list.forEach(c=>{
          const opt=document.createElement('option');
          opt.value=c.id; opt.textContent=`${c.nombre} (${c.codigo})`;
          selCentro.appendChild(opt);
        });
      }).catch(()=>{});
  }
});
