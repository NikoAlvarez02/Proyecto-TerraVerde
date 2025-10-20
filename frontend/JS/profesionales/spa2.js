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
const API_HORARIOS = '/profesionales/api/profesionales-horarios/';
let pr_pageSize = 10;
let pr_ordering = 'apellido';
let pr_query = '';
let pr_next = null;
let pr_prev = null;

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

  try { loadHorarios(p.id); } catch (e) { console.error(e); }
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
async function apiList(url=null) {
  const listUrl = url || `${API_BASE}?page_size=${pr_pageSize}&ordering=${encodeURIComponent(pr_ordering)}${pr_query?`&search=${encodeURIComponent(pr_query)}`:''}`;
  const resp = await fetch(listUrl, { credentials:'include' });
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
  tbody.innerHTML = `<tr><td colspan="7">Cargando...</td></tr>`;
  try {
    const data = await apiList();
    const list = Array.isArray(data) ? data : (data.results||[]);
    pr_next = data.next || null; pr_prev = data.previous || null;
    if (!Array.isArray(list) || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:#666;">No hay profesionales.</td></tr>`;
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
        <td>${(p.centros_nombres || []).join(', ')}</td>
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
    tbody.innerHTML = `<tr><td colspan="7" style="color:#c00;">Error cargando profesionales</td></tr>`;
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
    centros: Array.from(document.querySelectorAll('#centrosSelect option:checked')).map(o=>Number(o.value)),
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
document.addEventListener('DOMContentLoaded', () => {
  const pr_inputQ = document.getElementById('pr_q');
  const pr_selectOrden = document.getElementById('pr_orden');
  const pr_btnBuscar = document.getElementById('pr_buscar');
  const pr_btnPrev = document.getElementById('pr_prev');
  const pr_btnNext = document.getElementById('pr_next');
  const pr_pageInfoEl = document.getElementById('pr_pageInfo');

  if(pr_btnBuscar){ pr_btnBuscar.addEventListener('click', async ()=>{ pr_query=(pr_inputQ?.value||'').trim(); pr_ordering=pr_selectOrden?.value||'apellido'; await renderList(); }); }
  if(pr_btnPrev){ pr_btnPrev.addEventListener('click', async ()=>{ if(pr_prev){ const d=await apiList(pr_prev); pr_next=d.next; pr_prev=d.previous; await renderList(); } }); }
  if(pr_btnNext){ pr_btnNext.addEventListener('click', async ()=>{ if(pr_next){ const d=await apiList(pr_next); pr_next=d.next; pr_prev=d.previous; await renderList(); } }); }

  renderList();

  // preparar select de centros en modal (para horarios)
  (async ()=>{
    try{
      const selCentroH = document.getElementById('h_centro');
      if(!selCentroH) return;
      const r = await fetch('/centros/api/centros/?page_size=500', {credentials:'include'});
      if(r.ok){ const d = await r.json(); const list = Array.isArray(d)?d:(d.results||[]);
        selCentroH.innerHTML='';
        list.forEach(c=>{ const opt=document.createElement('option'); opt.value=c.id; opt.textContent=`${c.nombre} (${c.codigo})`; selCentroH.appendChild(opt); });
      }
    }catch(err){ console.error('cargar centros horarios', err); }
  })();
});

// ------- Horarios por profesional -------
async function loadHorarios(profesionalId){
  const wrap = document.getElementById('horariosWrap');
  const tb = document.getElementById('horarios-tbody');
  if(!wrap || !tb) return;
  wrap.style.display = 'block';
  tb.innerHTML = '<tr><td colspan="6">Cargando...</td></tr>';
  try{
    const r = await fetch(`${API_HORARIOS}?profesional=${profesionalId}&page_size=500&ordering=dia_semana,hora_inicio`, {credentials:'include'});
    if(!r.ok){ tb.innerHTML = '<tr><td colspan="6" style="color:#c00;">Error</td></tr>'; return; }
    const d = await r.json();
    const list = Array.isArray(d)?d:(d.results||[]);
    if(!list.length){ tb.innerHTML = '<tr><td colspan="6">Sin horarios</td></tr>'; return; }
    tb.innerHTML='';
    list.forEach(h=>{
      const tr=document.createElement('tr');
      tr.innerHTML = `
        <td>${h.centro_nombre || h.centro}</td>
        <td>${h.dia_display || h.dia_semana}</td>
        <td>${h.hora_inicio?.slice(0,5) || ''}</td>
        <td>${h.hora_fin?.slice(0,5) || ''}</td>
        <td>${h.activo ? 'Sí':'No'}</td>
        <td><button class="btn btn-eliminar" data-delh="${h.id}">Eliminar</button></td>
      `;
      tr.querySelector('[data-delh]')?.addEventListener('click', async ()=>{
        try{
          const dr = await fetch(`${API_HORARIOS}${h.id}/`, {method:'DELETE', credentials:'include', headers:{'X-CSRFToken': csrftoken}});
          if(!dr.ok) throw new Error('del horario');
          await loadHorarios(profesionalId);
        }catch(err){ console.error(err); showFlash('No se pudo eliminar horario','error'); }
      });
      tb.appendChild(tr);
    });
  }catch(err){ console.error(err); tb.innerHTML = '<tr><td colspan="6" style="color:#c00;">Error</td></tr>'; }
}

document.getElementById('h_agregar')?.addEventListener('click', async ()=>{
  const profId = document.getElementById('profesionalId').value;
  if(!profId){ showFlash('Primero guardá el profesional','error'); return; }
  const payload = {
    profesional: Number(profId),
    centro: Number(document.getElementById('h_centro').value),
    dia_semana: Number(document.getElementById('h_dia').value),
    hora_inicio: document.getElementById('h_inicio').value,
    hora_fin: document.getElementById('h_fin').value,
    activo: document.getElementById('h_activo').checked,
  };
  if(!payload.centro || !payload.hora_inicio || !payload.hora_fin){ showFlash('Completá centro e intervalos','error'); return; }
  try{
    const r = await fetch(API_HORARIOS, {method:'POST', credentials:'include', headers:{'Content-Type':'application/json','X-CSRFToken': csrftoken}, body: JSON.stringify(payload)});
    if(!r.ok){ const t=await r.text(); throw new Error(t); }
    await loadHorarios(Number(profId));
    showFlash('Horario agregado');
  }catch(err){ console.error(err); showFlash('No se pudo agregar horario','error'); }
});

