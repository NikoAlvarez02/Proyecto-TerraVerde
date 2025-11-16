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
const selectOS = document.getElementById('os_filter');
let nextUrl = null;
let prevUrl = null;
let totalCount = 0;
let currentPage = 1;
let pageSize = 10;
let currentOrdering = '-fecha_registro';
let currentQuery = '';
let currentOS = '';

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

const API_OBRAS = '/obras/api/obras-sociales/';

// ---------- helpers UI ----------
function showFlash(msg, type = 'ok') {
  const toast = document.getElementById('toast');
  const pageFlash = document.getElementById('flash');
  const modalOpen = modalForm?.classList.contains('is-open') || modalConfirm?.classList.contains('is-open');
  if (modalOpen && toast) {
    toast.className = type === 'ok' ? 'toast-ok' : 'toast-error';
    toast.textContent = msg;
    toast.style.display = 'block';
    clearTimeout(showFlash._t);
    showFlash._t = setTimeout(() => (toast.style.display = 'none'), 3500);
    return;
  }
  if (typeof window.showToast === 'function') { window.showToast(msg, type === 'ok' ? 'ok' : 'error'); return; }
  if (pageFlash) {
    pageFlash.style.display = 'block';
    pageFlash.style.padding = '8px';
    pageFlash.style.borderRadius = '8px';
    pageFlash.style.background = type === 'ok' ? '#e6ffed' : '#ffe6e6';
    pageFlash.style.border = '1px solid ' + (type === 'ok' ? '#89d79d' : '#e08b8b');
    pageFlash.style.color = '#333';
    pageFlash.textContent = msg;
    clearTimeout(showFlash._p);
    showFlash._p = setTimeout(() => (pageFlash.style.display = 'none'), 2500);
  }
}

function openModalCreate() {
  editId = null;
  modalTitle.textContent = 'Registrar Paciente';
  form.reset();
  resetModalPosition();
  modalForm.classList.add('is-open');
  modalForm.style.display = 'flex';
  document.body.classList.add('modal-open');
  // Llevar foco al primer campo y scrollear al tope
  setTimeout(() => { document.getElementById('apellido')?.focus(); modalForm.scrollTop = 0; }, 0);
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
  // obras sociales
  try { const os = document.getElementById('obra_social'); if (os) os.innerHTML = os.innerHTML; if (os) os.value = p.obra_social || ''; } catch (e) {}

  resetModalPosition();
  modalForm.classList.add('is-open');
  modalForm.style.display = 'flex';
  document.body.classList.add('modal-open');
  setTimeout(() => { document.getElementById('apellido')?.focus(); modalForm.scrollTop = 0; }, 0);
}

function closeModal() {
  modalForm.classList.remove('is-open');
  modalForm.style.display = 'none';
  document.body.classList.remove('modal-open');
}

function openConfirm(id) {
  deleteId = id;
  modalConfirm.classList.add('is-open');
  document.body.classList.add('modal-open');
}

function closeConfirm() {
  deleteId = null;
  modalConfirm.classList.remove('is-open');
  document.body.classList.remove('modal-open');
}

// ---------- API base ----------
const API_BASE = '/pacientes/api/pacientes/';

function buildQuery(){
  const params = new URLSearchParams();
  params.set('page_size', String(pageSize));
  if(currentOrdering) params.set('ordering', currentOrdering);
  if(currentQuery) params.set('search', currentQuery);
  if(currentOS) params.set('obra_social', currentOS);
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
      'Accept': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  if (resp.status === 400) {
    const err = await resp.json();
    throw { type: 'validation', detail: err };
  }
  if (!resp.ok) {
    let text = '';
    try { text = await resp.text(); } catch(_) {}
    throw { type: 'http', status: resp.status, body: text };
  }
  return await resp.json();
}

async function apiUpdate(id, payload) {
  const resp = await fetch(API_BASE + id + '/', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  if (resp.status === 400) {
    const err = await resp.json();
    throw { type: 'validation', detail: err };
  }
  if (!resp.ok) {
    let text = '';
    try { text = await resp.text(); } catch(_) {}
    throw { type: 'http', status: resp.status, body: text };
  }
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

// ---------- drag del modal ----------
function resetModalPosition(){
  const card = document.querySelector('#modalForm .card');
  if(!card) return;
  card.style.position='relative';
  card.style.left='';
  card.style.top='';
  card.style.margin='0 auto';
  card.classList.remove('dragging');
}

function makeModalDraggable(){
  const overlay = document.getElementById('modalForm');
  const card = document.querySelector('#modalForm .card');
  const handle = document.querySelector('#modalForm .drag-handle');
  if(!overlay || !card || !handle) return;

  let isDown=false; let offsetX=0, offsetY=0;
  const pointer = (e)=> e.touches ? e.touches[0] : e;

  function onDown(e){
    const p = pointer(e);
    const rect = card.getBoundingClientRect();
    card.style.position='absolute';
    card.style.margin='0';
    card.style.left = rect.left + 'px';
    card.style.top  = rect.top  + 'px';
    isDown=true; offsetX=p.clientX-rect.left; offsetY=p.clientY-rect.top;
    card.classList.add('dragging'); overlay.classList.add('dragging');
    e.preventDefault();
  }
  function onMove(e){
    if(!isDown) return; const p = pointer(e);
    let nx=p.clientX-offsetX, ny=p.clientY-offsetY;
    const pad=8, vw=window.innerWidth, vh=window.innerHeight, cw=card.offsetWidth, ch=card.offsetHeight;
    // X dentro de la pantalla, permitiendo algo de negativo si es más ancho
    const minX=Math.min(pad, vw - cw - pad), maxX=Math.max(pad, vw - cw - pad);
    // Y libre: poder subir por encima del viewport (hasta ocultar casi todo)
    const minY = -ch + pad;         // arriba libre
    const maxY = vh - pad;          // abajo casi al borde
    nx=Math.min(Math.max(nx, minX), maxX);
    ny=Math.min(Math.max(ny, minY), maxY);
    card.style.left=nx+'px'; card.style.top=ny+'px'; e.preventDefault();
  }
  function onUp(){ isDown=false; card.classList.remove('dragging'); overlay.classList.remove('dragging'); }

  handle.addEventListener('mousedown', onDown);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onUp);
  handle.addEventListener('touchstart', onDown, {passive:false});
  window.addEventListener('touchmove', onMove, {passive:false});
  window.addEventListener('touchend', onUp);
  // Doble clic en el encabezado centra nuevamente el modal
  handle.addEventListener('dblclick', resetModalPosition);
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
        <td>${p.obra_social_nombre || ''}</td>
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
  if (typeof form.checkValidity === 'function' && !form.checkValidity()) {
    form.reportValidity?.();
    return;
  }

  // validación básica
  const apellido = document.getElementById('apellido').value.trim();
  const nombre = document.getElementById('nombre').value.trim();
  const dni = document.getElementById('dni').value.trim();

  if (!apellido || !nombre || !dni) {
    showFlash('Apellido, Nombre y DNI son obligatorios', 'warning');
    return;
  }

  // normalizar fecha: soportar dd/mm/yyyy -> yyyy-mm-dd
  const rawDate = document.getElementById('fecha_nacimiento').value || '';
  function normalizeDate(v){
    if(!v) return null;
    const m = v.match(/^\s*(\d{2})\/(\d{2})\/(\d{4})\s*$/);
    if(m){ const d=m[1], mo=m[2], y=m[3]; return `${y}-${mo.padStart(2,'0')}-${d.padStart(2,'0')}`; }
    return v; // assume yyyy-mm-dd
  }
  const alergiasInput = document.getElementById('alergias');
  const alergias = alergiasInput ? alergiasInput.value : '';
  const payload = {
    apellido,
    nombre,
    dni,
    fecha_nacimiento: normalizeDate(rawDate),
    telefono: document.getElementById('telefono').value || '',
    direccion: document.getElementById('direccion').value || '',
    email: document.getElementById('email').value || '',
    centro: document.getElementById('centro')?.value ? Number(document.getElementById('centro').value) : null,
    obra_social: document.getElementById('obra_social')?.value ? Number(document.getElementById('obra_social').value) : null,
    genero: document.getElementById('genero').value || '',
    grupo_sanguineo: document.getElementById('grupo_sanguineo').value || '',
    alergias,
    antecedentes: document.getElementById('antecedentes').value || '',
    contacto_emergencia_nombre: document.getElementById('contacto_emergencia_nombre').value || '',
    contacto_emergencia_telefono: document.getElementById('contacto_emergencia_telefono').value || '',
  };

  try {
    // Evitar DNI duplicado al crear
    if (editId === null && dni) {
      try {
        const r = await fetch(`/pacientes/api/pacientes/?page_size=1&search=${encodeURIComponent(dni)}`, {credentials:'include'});
        if (r.ok) {
          const d = await r.json();
          const list = Array.isArray(d) ? d : (d.results || []);
          if (list.some(p => String(p.dni) === dni)) {
            showFlash('Error de validación: dni: Ya existe un paciente con este DNI', 'error');
            return;
          }
        }
      } catch(_) {}
    }
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
      // Mostrar todos los errores de DRF en una sola línea
      try{
        const parts = Object.entries(err.detail).map(([k,v]) => `${k}: ${Array.isArray(v)?v.join(', '):String(v)}`);
        showFlash(`Error de validación: ${parts.join(' | ')}`, 'error');
      }catch(_){
        const firstField = Object.keys(err.detail)[0];
        const msg = Array.isArray(err.detail[firstField]) ? err.detail[firstField][0] : JSON.stringify(err.detail);
        showFlash(`Error de validación: ${firstField}: ${msg}`, 'error');
      }
    } else if (err.type === 'http') {
      showFlash(`Error HTTP ${err.status}: ${err.body?.slice(0,140) || 'sin detalle'}`, 'error');
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
document.addEventListener('DOMContentLoaded', () => {
  renderList();
  makeModalDraggable();
  // Cerrar por ESC y al clickear fuera de la tarjeta
  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape') {
      if (modalConfirm.classList.contains('is-open')) closeConfirm();
      else if (modalForm.classList.contains('is-open')) closeModal();
    }
  });
  [modalForm, modalConfirm].forEach(overlay => {
    overlay?.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.id === 'modalConfirm' ? closeConfirm() : closeModal();
      }
    });
  });
});

// Controles de filtros y paginación
if(btnBuscar){
  btnBuscar.addEventListener('click', async ()=>{
    currentQuery = (inputQ?.value || '').trim();
    currentOrdering = selectOrden?.value || '-fecha_registro';
    currentOS = (selectOS?.value || '').trim();
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

  // cargar obras sociales
  const selObra = document.getElementById('obra_social');
  const selOSFilter = document.getElementById('os_filter');
  if (selObra) {
    fetch('/obras/api/obras-sociales/?page_size=500&ordering=nombre', {credentials:'include'})
      .then(r=>r.ok?r.json():null)
      .then(d=>{
        const list = Array.isArray(d)?d:(d?.results||[]);
        selObra.innerHTML = '<option value="">(sin obra social)</option>';
        list.forEach(o=>{ const opt=document.createElement('option'); opt.value=o.id; opt.textContent=o.nombre; selObra.appendChild(opt); });
        if (selOSFilter) {
          selOSFilter.innerHTML = '<option value="">Obra Social (todas)</option>';
          list.forEach(o=>{ const opt=document.createElement('option'); opt.value=o.id; opt.textContent=o.nombre; selOSFilter.appendChild(opt); });
        }
      }).catch(()=>{});
  }
});
