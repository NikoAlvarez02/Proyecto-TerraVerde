// CSRF
function getCookie(name){ const m=document.cookie.match('(^|;)\\s*'+name+'\\s*=\\s*([^;]+)'); return m?decodeURIComponent(m.pop()):null; }
const csrftoken = getCookie('csrftoken');

// Refs
const tbody = document.getElementById('o_tbody');
const flash = document.getElementById('flash');
const btnNueva = document.getElementById('btnNuevaObra');
const modal = document.getElementById('modalObra');
const modalTitle = document.getElementById('o_modalTitle');
const btnCerrar = document.getElementById('o_cerrar');
const btnCancelar = document.getElementById('o_cancelar');
const confirmModal = document.getElementById('o_modalConfirm');
const btnNo = document.getElementById('o_no');
const btnSi = document.getElementById('o_si');
const form = document.getElementById('o_form');

let editId = null; let deleteId = null;

// API
const API_BASE = '/obras/api/obras-sociales/';
let o_ordering = 'nombre'; let o_query=''; let o_activo='';

function showFlash(msg, type='ok'){
  flash.style.display='block'; flash.style.padding='8px'; flash.style.borderRadius='8px';
  flash.style.background = type==='ok' ? '#e6ffed' : '#ffe6e6';
  flash.style.border = '1px solid ' + (type==='ok' ? '#89d79d' : '#e08b8b');
  flash.textContent = msg; setTimeout(()=>flash.style.display='none', 2200);
}

function openModalCreate(){ editId=null; modalTitle.textContent='Nueva Obra Social'; form.reset(); document.getElementById('o_activo_chk').checked=true; modal.classList.add('is-open'); document.body.classList.add('modal-open'); }
function openModalEdit(o){ editId=o.id; modalTitle.textContent='Editar Obra Social'; form.reset();
  document.getElementById('o_id').value=o.id||''; document.getElementById('o_nombre').value=o.nombre||''; document.getElementById('o_codigo').value=o.codigo||''; document.getElementById('o_activo_chk').checked=!!o.activo; modal.classList.add('is-open'); document.body.classList.add('modal-open'); }
function closeModal(){ modal.classList.remove('is-open'); document.body.classList.remove('modal-open'); }
function openConfirm(id){ deleteId=id; confirmModal.classList.add('is-open'); document.body.classList.add('modal-open'); }
function closeConfirm(){ deleteId=null; confirmModal.classList.remove('is-open'); document.body.classList.remove('modal-open'); }

function buildQuery(){ const p=new URLSearchParams(); p.set('page_size','200'); if(o_ordering) p.set('ordering',o_ordering); if(o_query) p.set('search',o_query); if(o_activo) p.set('activo', o_activo==='true' ? 'true' : 'false'); return p.toString(); }

async function apiList(){ const r=await fetch(API_BASE+'?'+buildQuery(), {credentials:'include'}); if(!r.ok) throw new Error('GET '+r.status); return await r.json(); }
async function apiGet(id){ const r=await fetch(API_BASE+id+'/', {credentials:'include'}); if(!r.ok) throw new Error('GET id '+r.status); return await r.json(); }
async function apiCreate(payload){ const r=await fetch(API_BASE,{method:'POST',credentials:'include',headers:{'Content-Type':'application/json','X-CSRFToken':csrftoken},body:JSON.stringify(payload)}); if(r.status===400) throw {type:'validation',detail:await r.json()}; if(!r.ok) throw new Error('POST '+r.status); return await r.json(); }
async function apiUpdate(id,payload){ const r=await fetch(API_BASE+id+'/',{method:'PUT',credentials:'include',headers:{'Content-Type':'application/json','X-CSRFToken':csrftoken},body:JSON.stringify(payload)}); if(r.status===400) throw {type:'validation',detail:await r.json()}; if(!r.ok) throw new Error('PUT '+r.status); return await r.json(); }
async function apiDelete(id){ const r=await fetch(API_BASE+id+'/',{method:'DELETE',credentials:'include',headers:{'X-CSRFToken':csrftoken}}); if(!r.ok) throw new Error('DELETE '+r.status); }

async function renderList(){ tbody.innerHTML='<tr><td colspan="4">Cargando...</td></tr>'; try{ const data=await apiList(); const list=Array.isArray(data)?data:(data.results||[]); if(!list.length){ tbody.innerHTML='<tr><td colspan="4" style="text-align:center;color:#666;">Sin registros</td></tr>'; return;} tbody.innerHTML=''; list.forEach(o=>{ const tr=document.createElement('tr'); tr.innerHTML=`
  <td>${o.codigo||''}</td>
  <td>${o.nombre||''}</td>
  <td>${o.activo?'Sí':'No'}</td>
  <td style="white-space:nowrap; display:flex; gap:6px;">
    <button class="btn btn-editar" data-edit="${o.id}">Editar</button>
    <button class="btn btn-eliminar" data-del="${o.id}">Eliminar</button>
  </td>`; tr.querySelector('[data-edit]').addEventListener('click', async()=>{ try{ const full=await apiGet(o.id); openModalEdit(full);}catch(e){console.error(e);showFlash('No se pudo cargar','error');}}); tr.querySelector('[data-del]').addEventListener('click',()=> openConfirm(o.id)); tbody.appendChild(tr); }); }catch(e){ console.error(e); tbody.innerHTML='<tr><td colspan="4" style="color:#c00;">Error cargando</td></tr>'; } }

// eventos
document.getElementById('o_buscar').addEventListener('click', ()=>{ o_query=(document.getElementById('o_q').value||'').trim(); o_ordering=document.getElementById('o_orden').value||'nombre'; o_activo=document.getElementById('o_activo').value||''; renderList(); });
btnNueva.addEventListener('click', openModalCreate); btnCerrar.addEventListener('click', closeModal); btnCancelar.addEventListener('click', closeModal); btnNo.addEventListener('click', closeConfirm);
btnSi.addEventListener('click', async()=>{ if(deleteId==null) return; try{ await apiDelete(deleteId); showFlash('Obra Social eliminada'); closeConfirm(); await renderList(); }catch(e){ console.error(e); showFlash('No se pudo eliminar','error'); }});

// importar desde SNRS
document.getElementById('btnImportar')?.addEventListener('click', async ()=>{
  try{
    const r = await fetch('/obras/api/import/snrs/', {credentials:'include'});
    if(!r.ok){ const t=await r.text(); throw new Error(t); }
    const j = await r.json();
    showFlash(`Importadas: ${j.imported || 0} (nuevas: ${j.created || 0}, actualizadas: ${j.updated || 0})`);
    await renderList();
  }catch(e){ console.error(e); showFlash('Falló la importación (verifica red/credenciales)', 'error'); }
});

form.addEventListener('submit', async(e)=>{ e.preventDefault(); const payload={ nombre:document.getElementById('o_nombre').value.trim(), codigo:document.getElementById('o_codigo').value.trim(), activo:document.getElementById('o_activo_chk').checked }; if(!payload.nombre){ showFlash('El nombre es obligatorio','warning'); return; } try{ if(editId===null){ await apiCreate(payload); showFlash('Obra Social creada'); } else { await apiUpdate(editId,payload); showFlash('Obra Social actualizada'); } closeModal(); await renderList(); }catch(err){ console.error(err); showFlash('No se pudo guardar','error'); } });

// init
document.addEventListener('DOMContentLoaded', ()=>{ renderList(); document.addEventListener('keydown',(ev)=>{ if(ev.key==='Escape'){ if(confirmModal.classList.contains('is-open')) closeConfirm(); else if(modal.classList.contains('is-open')) closeModal(); }}); [modal,confirmModal].forEach(ov=>{ ov?.addEventListener('click',(e)=>{ if(e.target===ov){ ov.id==='o_modalConfirm'?closeConfirm():closeModal(); } }); }); });

// ---- soporte extra: importar CSV local (sin red) ----
try{
  var btnCSV = document.getElementById('btnImportarCSV');
  var fileCSV = document.getElementById('o_file');
  if(btnCSV && fileCSV){
    btnCSV.addEventListener('click', function(){ fileCSV.click(); });
    fileCSV.addEventListener('change', async function(ev){
      var f = ev.target.files && ev.target.files[0];
      if(!f) return;
      var fd = new FormData(); fd.append('file', f);
      try{
        const r = await fetch('/obras/api/import/snrs/', {method:'POST', body: fd, credentials:'include', headers:{'X-CSRFToken': csrftoken}});
        if(!r.ok){ const t=await r.text(); throw new Error(t); }
        const j = await r.json();
        showFlash('CSV importado (nuevas: ' + (j.created||0) + ', actualizadas: ' + (j.updated||0) + ')');
        await renderList();
      }catch(e){ console.error(e); showFlash('No se pudo importar el CSV', 'error'); }
    });
  }
}catch(e){ console.warn('csv import init', e); }
