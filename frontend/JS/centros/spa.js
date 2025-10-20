// ====== CSRF ======
function getCookie(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? decodeURIComponent(m.pop()) : null;
}
const csrftoken = getCookie('csrftoken');

// ====== refs ======
const tbody = document.getElementById('tbody');
const flash = document.getElementById('flash');
const modal = document.getElementById('modalCentro');
const modalConfirm = document.getElementById('modalConfirm');
const modalTitle = document.getElementById('modalTitle');
const form = document.getElementById('formCentro');
const btnNuevo = document.getElementById('btnNuevoCentro');
const btnCerrar = document.getElementById('btnCerrarCentro');
const btnCancelar = document.getElementById('btnCancelarCentro');
const btnNo = document.getElementById('btnNo');
const btnSi = document.getElementById('btnSi');

let editId = null;
let deleteId = null;

// ====== helpers ======
function showFlash(msg, type='ok'){
  flash.style.display='block';
  flash.style.padding='8px';
  flash.style.borderRadius='8px';
  flash.style.background = type==='ok' ? '#e6ffed' : '#ffe6e6';
  flash.style.border = '1px solid ' + (type==='ok' ? '#89d79d' : '#e08b8b');
  flash.textContent = msg;
  setTimeout(()=>flash.style.display='none', 2200);
}

function openModalCreate(){
  editId = null;
  modalTitle.textContent = 'Nuevo Centro';
  form.reset();
  document.getElementById('c_id').value = '';
  document.getElementById('c_activo_chk').checked = true;
  modal.classList.add('is-open');
}
function openModalEdit(c){
  editId = c.id;
  modalTitle.textContent = 'Editar Centro';
  form.reset();
  document.getElementById('c_id').value = c.id;
  document.getElementById('c_codigo').value = c.codigo || '';
  document.getElementById('c_nombre').value = c.nombre || '';
  document.getElementById('c_direccion').value = c.direccion || '';
  document.getElementById('c_telefono').value = c.telefono || '';
  document.getElementById('c_email').value = c.email || '';
  document.getElementById('c_activo_chk').checked = !!c.activo;
  modal.classList.add('is-open');
}
function closeModal(){ modal.classList.remove('is-open'); }

function openConfirm(id){ deleteId = id; modalConfirm.classList.add('is-open'); }
function closeConfirm(){ deleteId = null; modalConfirm.classList.remove('is-open'); }

// ====== API ======
const API_BASE = '/centros/api/centros/';
let c_ordering = 'nombre';
let c_query = '';
let c_activo = '';

function buildQuery(){
  const p = new URLSearchParams();
  p.set('page_size', '200');
  if(c_ordering) p.set('ordering', c_ordering);
  if(c_query) p.set('search', c_query);
  if(c_activo){ p.set('activo', c_activo === 'true' ? 'true' : 'false'); }
  return p.toString();
}

async function apiList(){
  const resp = await fetch(API_BASE + '?' + buildQuery(), { credentials:'include' });
  if(!resp.ok) throw new Error('GET ' + resp.status);
  return await resp.json();
}
async function apiGet(id){
  const r = await fetch(API_BASE + id + '/', { credentials:'include' });
  if(!r.ok) throw new Error('GET id ' + r.status);
  return await r.json();
}
async function apiCreate(payload){
  const r = await fetch(API_BASE, { method:'POST', credentials:'include', headers:{'Content-Type':'application/json','X-CSRFToken': csrftoken}, body: JSON.stringify(payload) });
  if(r.status===400) throw {type:'validation', detail: await r.json()};
  if(!r.ok) throw new Error('POST ' + r.status);
  return await r.json();
}
async function apiUpdate(id, payload){
  const r = await fetch(API_BASE + id + '/', { method:'PUT', credentials:'include', headers:{'Content-Type':'application/json','X-CSRFToken': csrftoken}, body: JSON.stringify(payload) });
  if(r.status===400) throw {type:'validation', detail: await r.json()};
  if(!r.ok) throw new Error('PUT ' + r.status);
  return await r.json();
}
async function apiDelete(id){
  const r = await fetch(API_BASE + id + '/', { method:'DELETE', credentials:'include', headers:{'X-CSRFToken': csrftoken} });
  if(!r.ok) throw new Error('DELETE ' + r.status);
}

// ====== render ======
async function renderList(){
  tbody.innerHTML = `<tr><td colspan="5">Cargando...</td></tr>`;
  try{
    const data = await apiList();
    const list = Array.isArray(data) ? data : (data.results||[]);
    if(!list.length){ tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#666;">Sin registros</td></tr>`; return; }
    tbody.innerHTML='';
    list.forEach(c => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${c.codigo ?? ''}</td>
        <td>${c.nombre ?? ''}</td>
        <td>${c.direccion ?? ''}</td>
        <td>${c.activo ? 'Sí' : 'No'}</td>
        <td style="white-space:nowrap; display:flex; gap:6px;">
          <button class="btn btn-editar" data-edit="${c.id}">Editar</button>
          <button class="btn btn-eliminar" data-del="${c.id}">Eliminar</button>
        </td>`;
      tr.querySelector('[data-edit]').addEventListener('click', async ()=>{
        try{ const full = await apiGet(c.id); openModalEdit(full); }catch(e){ console.error(e); showFlash('No se pudo cargar el centro','error'); }
      });
      tr.querySelector('[data-del]').addEventListener('click', ()=> openConfirm(c.id));
      tbody.appendChild(tr);
    });
  }catch(e){ console.error(e); tbody.innerHTML = `<tr><td colspan="5" style="color:#c00;">Error cargando centros</td></tr>`; }
}

// ====== events ======
document.getElementById('c_buscar').addEventListener('click', ()=>{
  c_query = (document.getElementById('c_q').value || '').trim();
  c_ordering = document.getElementById('c_orden').value || 'nombre';
  c_activo = document.getElementById('c_activo').value || '';
  renderList();
});

btnNuevo.addEventListener('click', openModalCreate);
btnCerrar.addEventListener('click', closeModal);
btnCancelar.addEventListener('click', closeModal);
btnNo.addEventListener('click', closeConfirm);
btnSi.addEventListener('click', async ()=>{
  if(deleteId == null) return;
  try{ await apiDelete(deleteId); showFlash('Centro eliminado'); closeConfirm(); await renderList(); }catch(e){ console.error(e); showFlash('No se pudo eliminar', 'error'); }
});

form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const payload = {
    codigo: document.getElementById('c_codigo').value.trim(),
    nombre: document.getElementById('c_nombre').value.trim(),
    direccion: document.getElementById('c_direccion').value.trim(),
    telefono: document.getElementById('c_telefono').value.trim(),
    email: document.getElementById('c_email').value.trim(),
    activo: document.getElementById('c_activo_chk').checked,
  };
  if(!payload.codigo || !payload.nombre){ showFlash('Código y Nombre son obligatorios','error'); return; }
  try{
    if(editId === null){ await apiCreate(payload); showFlash('Centro creado'); }
    else { await apiUpdate(editId, payload); showFlash('Centro actualizado'); }
    closeModal();
    await renderList();
  }catch(err){ console.error(err); showFlash('No se pudo guardar el centro','error'); }
});

document.addEventListener('DOMContentLoaded', renderList);
