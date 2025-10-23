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
let t_pageSize = 10;
let t_ordering = '-fecha_hora';
let t_query = '';
let t_next = null;
let t_prev = null;
let t_fechaDesde = '';
let t_fechaHasta = '';
let t_estado = '';
let t_profesionalId = '';
let t_pacienteId = '';

// ====== helpers UI ======
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

  if (pageFlash) {
    pageFlash.style.display = 'block';
    pageFlash.style.padding = '8px';
    pageFlash.style.borderRadius = '8px';
    pageFlash.style.background = type === 'ok' ? '#e6ffed' : '#ffe6e6';
    pageFlash.style.border = '1px solid ' + (type === 'ok' ? '#89d79d' : '#e08b8b');
    pageFlash.style.color = '#333';
    pageFlash.textContent = msg;
    clearTimeout(pageFlash._t);
    pageFlash._t = setTimeout(() => (pageFlash.style.display = 'none'), 2500);
  }
}

// ====== abrir/cerrar modales ======
function openModalCreate() {
  editId = null;
  modalTitle.textContent = 'Nuevo Turno';
  form.reset();
  resetModalPosition();
  modalForm.classList.add('is-open');
  document.body.classList.add('modal-open');
  if (flash) flash.style.display = 'none';
}

function openModalEdit(t) {
  editId = t.id;
  modalTitle.textContent = 'Editar Turno';
  form.reset();

  document.getElementById('turnoId').value = t.id;
  
  // CAMBIO: usa fecha_display y hora_display del serializer
  document.getElementById('fecha').value = t.fecha_display || '';
  document.getElementById('hora').value = t.hora_display || '';
  
  document.getElementById('estado').value = t.estado || 'pendiente';
  document.getElementById('motivo').value = t.motivo || '';
  document.getElementById('observaciones').value = t.observaciones || '';

  selPaciente.value = String(t.paciente ?? '');
  selProfesional.value = String(t.profesional ?? '');

  resetModalPosition();
  modalForm.classList.add('is-open');
  document.body.classList.add('modal-open');
  if (flash) flash.style.display = 'none';
}

function closeModal() {
  modalForm.classList.remove('is-open');
  document.body.classList.remove('modal-open');
  resetModalPosition();
}

function openConfirm(id) {
  deleteId = id;
  modalConfirm.classList.add('is-open');
  document.body.classList.add('modal-open');
  if (flash) flash.style.display = 'none';
}

function closeConfirm() {
  deleteId = null;
  modalConfirm.classList.remove('is-open');
  document.body.classList.remove('modal-open');
}

// ====== API ======
async function apiList(url=null) {
  let listUrl = url || `${API_TURNOS}?page_size=${t_pageSize}&ordering=${encodeURIComponent(t_ordering)}${t_query?`&search=${encodeURIComponent(t_query)}`:''}`;
  if(t_fechaDesde) listUrl += `&fecha_hora__date__gte=${encodeURIComponent(t_fechaDesde)}`;
  if(t_fechaHasta) listUrl += `&fecha_hora__date__lte=${encodeURIComponent(t_fechaHasta)}`;
  if(t_estado) listUrl += `&estado=${encodeURIComponent(t_estado)}`;
  if(t_profesionalId) listUrl += `&profesional=${encodeURIComponent(t_profesionalId)}`;
  if(t_pacienteId) listUrl += `&paciente=${encodeURIComponent(t_pacienteId)}`;
  const resp = await fetch(listUrl, { credentials:'include' });
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

// ====== cargar selects ======
async function loadPacientes() {
  selPaciente.innerHTML = `<option value="">Cargando...</option>`;
  const resp = await fetch(`${API_PACIENTES}?page_size=500&ordering=apellido`, { credentials:'include' });
  if (!resp.ok) { selPaciente.innerHTML = `<option value="">Error</option>`; return; }
  const data = await resp.json();
  selPaciente.innerHTML = `<option value="">Seleccione…</option>`;
  (Array.isArray(data)?data:(data.results||[])).forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.textContent = `${p.apellido ?? ''}, ${p.nombre ?? ''} (${p.dni ?? ''})`;
    selPaciente.appendChild(opt);
  });
}

async function loadProfesionales() {
  selProfesional.innerHTML = `<option value="">Cargando...</option>`;
  const resp = await fetch(`${API_PROFESIONALES}?page_size=500&ordering=apellido`, { credentials:'include' });
  if (!resp.ok) { selProfesional.innerHTML = `<option value="">Error</option>`; return; }
  const data = await resp.json();
  selProfesional.innerHTML = `<option value="">Seleccione…</option>`;
  (Array.isArray(data)?data:(data.results||[])).forEach(p => {
    const opt = document.createElement('option');
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
    const data = await apiList();
    const list = Array.isArray(data) ? data : (data.results||[]);
    t_next = data.next || null; t_prev = data.previous || null;
    if (!Array.isArray(list) || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#666;">No hay turnos.</td></tr>`;
      return;
    }
    tbody.innerHTML = '';
    list.forEach(t => {
      const tr = document.createElement('tr');
      
      // CAMBIO: usa fecha_display y hora_display
      tr.innerHTML = `
        <td>${t.fecha_display ?? ''}</td>
        <td>${t.hora_display ?? ''}</td>
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
          await ensureOptions();
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

// ====== Drag del modal ======
function resetModalPosition() {
  const card = document.querySelector('#modalForm .card');
  if (!card) return;
  card.style.position = 'relative';
  card.style.left = '';
  card.style.top = '';
  card.style.margin = '0 auto';
  card.classList.remove('dragging');
}

function makeModalDraggable() {
  const overlay = document.getElementById('modalForm');
  const card = document.querySelector('#modalForm .card');
  const handle = document.querySelector('#modalForm .drag-handle');
  if (!overlay || !card || !handle) return;

  let isDown = false;
  let offsetX = 0, offsetY = 0;

  const pointer = (e) => e.touches ? e.touches[0] : e;

  function onDown(e){
    const p = pointer(e);
    const rect = card.getBoundingClientRect();
    
    card.style.position = 'absolute';
    card.style.margin = '0';
    card.style.left = rect.left + 'px';
    card.style.top  = rect.top  + 'px';
    
    isDown = true;
    offsetX = p.clientX - rect.left;
    offsetY = p.clientY - rect.top;
    card.classList.add('dragging');
    overlay.classList.add('dragging');
    e.preventDefault();
  }
  
  function onMove(e){
    if(!isDown) return;
    const p = pointer(e);
    let nx = p.clientX - offsetX;
    let ny = p.clientY - offsetY;

    const minPad = 8;
    const maxX = window.innerWidth  - card.offsetWidth  - minPad;
    const maxY = window.innerHeight - card.offsetHeight - minPad;

    nx = Math.max(minPad, Math.min(nx, maxX));
    ny = Math.max(minPad, Math.min(ny, maxY));

    card.style.left = nx + 'px';
    card.style.top  = ny + 'px';
    e.preventDefault();
  }
  
  function onUp(){
    isDown = false;
    card.classList.remove('dragging');
    overlay.classList.remove('dragging');
  }

  handle.addEventListener('mousedown', onDown);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onUp);

  handle.addEventListener('touchstart', onDown, { passive:false });
  window.addEventListener('touchmove', onMove, { passive:false });
window.addEventListener('touchend', onUp);
}

// ====== init ======
document.addEventListener('DOMContentLoaded', () => {
  // filtros
  const t_inputQ = document.getElementById('t_q');
  const t_selectOrden = document.getElementById('t_orden');
  const t_btnBuscar = document.getElementById('t_buscar');
  const t_btnPrev = document.getElementById('t_prev');
  const t_btnNext = document.getElementById('t_next');
  const t_pageInfoEl = document.getElementById('t_pageInfo');
  const t_inputDesde = document.getElementById('t_desde');
  const t_inputHasta = document.getElementById('t_hasta');
  const t_selectEstado = document.getElementById('t_estado');
  const t_selectPac = document.getElementById('t_pac');
  const t_selectProf = document.getElementById('t_prof');
  const t_btnHoy = document.getElementById('t_hoy');
  const t_btnSemana = document.getElementById('t_semana');
  const t_btnMes = document.getElementById('t_mes');
  const t_btnLimpiar = document.getElementById('t_limpiar');

  if(t_btnBuscar){ t_btnBuscar.addEventListener('click', async ()=>{ 
    t_query=(t_inputQ?.value||'').trim(); 
    t_ordering=t_selectOrden?.value||'-fecha_hora'; 
    t_fechaDesde = t_inputDesde?.value || ''; 
    t_fechaHasta = t_inputHasta?.value || ''; 
    t_estado = t_selectEstado?.value || ''; 
    t_pacienteId = t_selectPac?.value || '';
    t_profesionalId = t_selectProf?.value || '';
    await renderList(); 
  }); }

  // Rápidos de rango
  function fmt(d){ const y=d.getFullYear(); const m=String(d.getMonth()+1).padStart(2,'0'); const day=String(d.getDate()).padStart(2,'0'); return `${y}-${m}-${day}`; }
  if(t_btnHoy){ t_btnHoy.addEventListener('click', ()=>{ const d=new Date(); t_inputDesde.value=fmt(d); t_inputHasta.value=fmt(d); }); }
  if(t_btnSemana){ t_btnSemana.addEventListener('click', ()=>{ const d=new Date(); const dow=d.getDay()||7; const start=new Date(d); start.setDate(d.getDate()-(dow-1)); const end=new Date(start); end.setDate(start.getDate()+6); t_inputDesde.value=fmt(start); t_inputHasta.value=fmt(end); }); }
  if(t_btnMes){ t_btnMes.addEventListener('click', ()=>{ const d=new Date(); const start=new Date(d.getFullYear(), d.getMonth(), 1); const end=new Date(d.getFullYear(), d.getMonth()+1, 0); t_inputDesde.value=fmt(start); t_inputHasta.value=fmt(end); }); }

  // Limpiar filtros
  if(t_btnLimpiar){ t_btnLimpiar.addEventListener('click', async ()=>{
    if(t_inputQ) t_inputQ.value=''; if(t_inputDesde) t_inputDesde.value=''; if(t_inputHasta) t_inputHasta.value='';
    if(t_selectEstado) t_selectEstado.value=''; if(t_selectOrden) t_selectOrden.value='-fecha_hora';
    if(t_selectPac) t_selectPac.value=''; if(t_selectProf) t_selectProf.value='';
    t_query=t_fechaDesde=t_fechaHasta=t_estado=t_pacienteId=t_profesionalId='';
    await renderList();
  }); }

  // Cargar opciones en filtros de Paciente/Profesional
  (async ()=>{
    try{
      if(t_selectPac){ const r=await fetch('/pacientes/api/pacientes/?page_size=500&ordering=apellido', {credentials:'include'}); if(r.ok){ const d=await r.json(); const list=Array.isArray(d)?d:(d.results||[]); t_selectPac.innerHTML='<option value="">Paciente (todos)</option>'; list.forEach(p=>{ const opt=document.createElement('option'); opt.value=p.id; opt.textContent=`${p.apellido||''}, ${p.nombre||''}`; t_selectPac.appendChild(opt); }); }}
      if(t_selectProf){ const r=await fetch('/profesionales/api/profesionales/?page_size=500&ordering=apellido', {credentials:'include'}); if(r.ok){ const d=await r.json(); const list=Array.isArray(d)?d:(d.results||[]); t_selectProf.innerHTML='<option value="">Profesional (todos)</option>'; list.forEach(p=>{ const opt=document.createElement('option'); opt.value=p.id; opt.textContent=`${p.apellido||''}, ${p.nombre||''}`; t_selectProf.appendChild(opt); }); }}
    }catch(e){ console.error('cargar filtros turno', e); }
  })();
  if(t_btnPrev){ t_btnPrev.addEventListener('click', async ()=>{ if(t_prev){ const d=await apiList(t_prev); t_next=d.next; t_prev=d.previous; await renderList(); } }); }
  if(t_btnNext){ t_btnNext.addEventListener('click', async ()=>{ if(t_next){ const d=await apiList(t_next); t_next=d.next; t_prev=d.previous; await renderList(); } }); }

  renderList();
  makeModalDraggable();
});
