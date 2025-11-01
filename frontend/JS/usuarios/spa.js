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

let u_next = null;
let u_prev = null;
let u_ordering = "username";
let u_query = "";

const API_BASE = '/usuarios/api/usuarios/';

// ====== helpers UI ======
function showFlash(msg, type = 'ok') {
  const toast = document.getElementById('toast');
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
  flash.style.display = 'block';
  flash.style.padding = '8px';
  flash.style.borderRadius = '8px';
  flash.style.background = type === 'ok' ? '#e6ffed' : '#ffe6e6';
  flash.style.border = '1px solid ' + (type === 'ok' ? '#89d79d' : '#e08b8b');
  flash.style.color = '#333';
  flash.textContent = msg;
  clearTimeout(showFlash._p);
  showFlash._p = setTimeout(() => (flash.style.display = 'none'), 2500);
}

function openModalCreate() {
  editId = null;
  modalTitle.textContent = 'Nuevo Usuario';
  form.reset();
  document.getElementById('is_active').checked = true;
  document.getElementById('is_staff').checked = false;
  document.getElementById('is_superuser').checked = false;
  // defaults de perfil
  const pr = document.getElementById('perfil_rol'); if (pr) pr.value = 'recep';
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.checked = !!val; };
  set('pf_admin_usuarios', false);
  set('pf_ver_pacientes', true);
  set('pf_ver_calendario', true);
  set('pf_generar_reportes', false);
  set('pf_ver_estadisticas', false);
  resetModalPosition();
  modalForm.classList.add('is-open');
  document.body.classList.add('modal-open');
  setTimeout(()=>{ document.getElementById('username')?.focus(); modalForm.scrollTop=0; },0);
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

  // perfil
  try {
    const pr = (u.perfil || {});
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.checked = !!val; };
    const prSel = document.getElementById('perfil_rol'); if (prSel) prSel.value = pr.rol || 'recep';
    set('pf_admin_usuarios', pr.puede_admin_usuarios);
    set('pf_ver_pacientes', pr.puede_ver_pacientes);
    set('pf_ver_calendario', pr.puede_ver_calendario);
    set('pf_generar_reportes', pr.puede_generar_reportes);
    set('pf_ver_estadisticas', pr.puede_ver_estadisticas);
  } catch(e) { console.warn('perfil parse', e); }

  document.getElementById('password').value = '';
  document.getElementById('password2').value = '';

  document.getElementById('is_active').checked = !!u.is_active;
  document.getElementById('is_staff').checked = !!u.is_staff;
  document.getElementById('is_superuser').checked = !!u.is_superuser;
  resetModalPosition();
  modalForm.classList.add('is-open');
  document.body.classList.add('modal-open');
  setTimeout(()=>{ document.getElementById('username')?.focus(); modalForm.scrollTop=0; },0);
}

function closeModal() { modalForm.classList.remove('is-open'); document.body.classList.remove('modal-open'); }
function openConfirm(id) { deleteId = id; modalConfirm.classList.add('is-open'); document.body.classList.add('modal-open'); }
function closeConfirm() { deleteId = null; modalConfirm.classList.remove('is-open'); document.body.classList.remove('modal-open'); }

// drag support
function resetModalPosition(){ const card=document.querySelector('#modalForm .card'); if(!card) return; card.style.position='relative'; card.style.left=''; card.style.top=''; card.style.margin='0 auto'; card.classList.remove('dragging'); }
function makeModalDraggable(){
  const overlay=document.getElementById('modalForm'); const card=document.querySelector('#modalForm .card'); const handle=document.querySelector('#modalForm .drag-handle');
  if(!overlay||!card||!handle) return; let isDown=false,ox=0,oy=0; const P=(e)=>e.touches?e.touches[0]:e;
  function down(e){ const p=P(e); const r=card.getBoundingClientRect(); card.style.position='absolute'; card.style.margin='0'; card.style.left=r.left+'px'; card.style.top=r.top+'px'; isDown=true; ox=p.clientX-r.left; oy=p.clientY-r.top; card.classList.add('dragging'); overlay.classList.add('dragging'); e.preventDefault(); }
  function move(e){
    if(!isDown) return; const p=P(e);
    let nx=p.clientX-ox, ny=p.clientY-oy;
    const pad=8, vw=window.innerWidth, vh=window.innerHeight, cw=card.offsetWidth, ch=card.offsetHeight;
    const minX=Math.min(pad, vw - cw - pad), maxX=Math.max(pad, vw - cw - pad);
    const minY=-ch + pad, maxY=vh - pad;
    nx=Math.min(Math.max(nx, minX), maxX);
    ny=Math.min(Math.max(ny, minY), maxY);
    card.style.left=nx+'px'; card.style.top=ny+'px'; e.preventDefault();
  }
  function up(){ isDown=false; card.classList.remove('dragging'); overlay.classList.remove('dragging'); }
  handle.addEventListener('mousedown', down); window.addEventListener('mousemove', move); window.addEventListener('mouseup', up);
  handle.addEventListener('touchstart', down, {passive:false}); window.addEventListener('touchmove', move, {passive:false}); window.addEventListener('touchend', up);
}

// ====== API ======
async function apiList(url=null) {
  const listUrl = url || `${API_BASE}?page_size=20&ordering=${encodeURIComponent(u_ordering)}${u_query?`&search=${encodeURIComponent(u_query)}`:""}`;
  const resp = await fetch(listUrl, { credentials:'same-origin' });
  if (!resp.ok) throw new Error('GET ' + resp.status);
  const j = await resp.json(); console.log("usuarios list", j); return j;
}
async function apiGet(id) {
  const resp = await fetch(API_BASE + id + '/', { credentials:'same-origin' });
  if (!resp.ok) throw new Error('GET id ' + resp.status);
  const j = await resp.json(); console.log("usuarios list", j); return j;
}
async function apiCreate(payload) {
  const resp = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', 'X-CSRFToken': csrftoken },
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  if (resp.status === 400) throw { type:'validation', detail: await resp.json() };
  if (!resp.ok) throw new Error('POST ' + resp.status);
  const j = await resp.json(); console.log("usuarios list", j); return j;
}
async function apiUpdate(id, payload) {
  const resp = await fetch(API_BASE + id + '/', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', 'X-CSRFToken': csrftoken },
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  if (resp.status === 400) throw { type:'validation', detail: await resp.json() };
  if (!resp.ok) throw new Error('PUT ' + resp.status);
  const j = await resp.json(); console.log("usuarios list", j); return j;
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
async function renderList(url=null) {
  tbody.innerHTML = `<tr><td colspan="6">Cargando...</td></tr>`;
  try {
    const data = await apiList(url);
    const list = Array.isArray(data) ? data : (data.results || []);
    u_next = data.next || null; u_prev = data.previous || null;
    const infoEl = document.getElementById('u_pageInfo'); if (infoEl) infoEl.textContent = `Total: ${data.count ?? list.length}`;
    const prevBtn = document.getElementById('u_prev'); if (prevBtn) prevBtn.disabled = !u_prev;
    const nextBtn = document.getElementById('u_next'); if (nextBtn) nextBtn.disabled = !u_next;

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

  const username = document.getElementById('username').value.trim();
  const email = document.getElementById('email').value.trim();
  if (!username || !email) { showFlash('Username y Email son obligatorios', 'warning'); return; }

  const first_name = document.getElementById('first_name').value || '';
  const last_name  = document.getElementById('last_name').value || '';
  const is_active = document.getElementById('is_active').checked;
  const is_staff = document.getElementById('is_staff').checked;
  const is_superuser = document.getElementById('is_superuser').checked;

  const password = document.getElementById('password').value;
  const password2 = document.getElementById('password2').value;

  if (editId === null) {
    if (!password) { showFlash('Password es obligatorio al crear', 'warning'); return; }
    if (password !== password2) { showFlash('Las contraseñas no coinciden', 'warning'); return; }
  } else {
    if (password || password2) {
      if (password !== password2) { showFlash('Las contraseñas no coinciden', 'warning'); return; }
    }
  }

  const payload = {
    username, email, first_name, last_name,
    is_active, is_staff, is_superuser,
    perfil: {
      rol: (document.getElementById('perfil_rol')?.value) || 'recep',
      puede_admin_usuarios: document.getElementById('pf_admin_usuarios')?.checked || false,
      puede_ver_pacientes: document.getElementById('pf_ver_pacientes')?.checked || false,
      puede_ver_calendario: document.getElementById('pf_ver_calendario')?.checked || false,
      puede_generar_reportes: document.getElementById('pf_generar_reportes')?.checked || false,
      puede_ver_estadisticas: document.getElementById('pf_ver_estadisticas')?.checked || false,
    }
  };
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

// Paginación
try { const el=document.getElementById('u_prev'); if(el) el.addEventListener('click', async ()=>{ if(u_prev){ await renderList(u_prev); } }); } catch(e){}
try { const el2=document.getElementById('u_next'); if(el2) el2.addEventListener('click', async ()=>{ if(u_next){ await renderList(u_next); } }); } catch(e){}

// ====== init ======
document.addEventListener('DOMContentLoaded', () => {
  const q = document.getElementById('u_q');
  const ord = document.getElementById('u_orden');
  const btn = document.getElementById('u_buscar');
  if(btn){ btn.addEventListener('click', async ()=>{ u_query=(q?.value||'').trim(); u_ordering=ord?.value||'username'; await renderList(); }); }
  if(q){ q.addEventListener('keydown', async (e)=>{ if(e.key==='Enter'){ u_query=(q.value||'').trim(); await renderList(); } }); }
  if(ord){ ord.addEventListener('change', async ()=>{ u_ordering=ord.value||'username'; await renderList(); }); }
  renderList();
  makeModalDraggable();
  document.addEventListener('keydown', (ev)=>{ if(ev.key==='Escape'){ if(modalConfirm.classList.contains('is-open')) closeConfirm(); else if(modalForm.classList.contains('is-open')) closeModal(); }});
  [modalForm, modalConfirm].forEach(ov=>{ ov?.addEventListener('click', (e)=>{ if(e.target===ov){ ov.id==='modalConfirm' ? closeConfirm() : closeModal(); } }); });
});




