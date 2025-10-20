// ====== CS� ======
function getCookie(name) {
  conS�m = document.cookie.match('(^|;)\\S� + name + '\\S�\\S�[^;]+)');
  return m ? decodeURIComponent(m.pop()) : null;
}
conS�cS�token = getCookie('cS�token');

// ====== refS�=====
conS�tbody = document.getElementById('profeS�naleS�body');
conS�flaS�= document.getElementById('flaS�);

conS�modalForm = document.getElementById('modalForm');
conS�modalTitle = document.getElementById('modalTitle');
conS�form = document.getElementById('formProfeS�nal');
conS�btnNuevo = document.getElementById('btnNuevo');
conS�btnCancelar = document.getElementById('btnCancelar');
conS�btnCerrarModal = document.getElementById('btnCerrarModal');

conS�modalConfirm = document.getElementById('modalConfirm');
conS�btnNo = document.getElementById('btnNo');
conS�btnS�= document.getElementById('btnS�);

let editId = null;
let deleteId = null;

conS�API_BAS�= '/profeS�naleS�pi/profeS�naleS�;
conS�API_HORARIOS� '/profeS�naleS�pi/profeS�naleS�orarioS�;
let pr_pageS�e = 10;
let pr_ordering = 'apellido';
let pr_query = '';
let pr_next = null;
let pr_prev = null;

// ====== helperS�I ======
function S�wFlaS�mS� type = 'ok') {
  flaS�S�le.diS�ay = 'block';
  flaS�S�le.padding = '8px';
  flaS�S�le.borderRadiuS� '8px';
  flaS�S�le.background = type === 'ok' ? '#e6ffed' : '#ffe6e6';
  flaS�S�le.border = '1px S�id ' + (type === 'ok' ? '#89d79d' : '#e08b8b');
  flaS�S�le.color = '#333';
  flaS�textContent = mS�
  S�Timeout(() => (flaS�S�le.diS�ay = 'none'), 2500);
}

function openModalCreate() {
  editId = null;
  modalTitle.textContent = 'Nuevo ProfeS�nal';
  form.reS�();
  document.getElementById('activo').checked = true;
  modalForm.S�le.diS�ay = 'block';
}

function openModalEdit(p) {
  editId = p.id;
  modalTitle.textContent = 'Editar ProfeS�nal';
  form.reS�();

  document.getElementById('profeS�nalId').value = p.id ?? '';
  document.getElementById('apellido').value = p.apellido ?? '';
  document.getElementById('nombre').value = p.nombre ?? '';
  document.getElementById('dni').value = p.dni ?? '';
  document.getElementById('matricula').value = p.matricula ?? '';
  document.getElementById('eS�cialidad').value = p.eS�cialidad ?? '';
  document.getElementById('telefono').value = p.telefono ?? '';
  document.getElementById('email').value = p.email ?? '';
  document.getElementById('direccion').value = p.direccion ?? '';
  document.getElementById('activo').checked = !!p.activo;

  modalForm.S�le.diS�ay = 'block';

  // cargar horarioS�el profeS�nal
  try{ loadHorarioS�.id); }catch(e){ conS�e.error(e); }
}

function cloS�odal() {
  modalForm.S�le.diS�ay = 'none';
}

function openConfirm(id) {
  deleteId = id;
  modalConfirm.S�le.diS�ay = 'block';
}

function cloS�onfirm() {
  deleteId = null;
  modalConfirm.S�le.diS�ay = 'none';
}

// ====== API ======
aS�c function apiLiS�url=null) {
  conS�liS�rl = url || `${API_BAS�?page_S�e=${pr_pageS�e}&ordering=${encodeURIComponent(pr_ordering)}${pr_query?`&S�rch=${encodeURIComponent(pr_query)}`:''}`;
  conS�reS�= await fetch(liS�rl, { credentialS�include' });
  if (!reS�ok) throw new Error('GET ' + reS�S�tuS�
  return await reS�jS�();
}
aS�c function apiGet(id) {
  conS�reS�= await fetch(API_BAS�+ id + '/', { credentialS�S�e-origin' });
  if (!reS�ok) throw new Error('GET id ' + reS�S�tuS�
  return await reS�jS�();
}
aS�c function apiCreate(payload) {
  conS�reS�= await fetch(API_BAS� {
    method: 'POS�,
    headerS�{ 'Content-Type': 'application/jS�', 'X-CS�Token': cS�token },
    credentialS�'S�e-origin',
    body: JS�.S�ingify(payload),
  });
  if (reS�S�tuS�== 400) throw { type:'validation', detail: await reS�jS�() };
  if (!reS�ok) throw new Error('POS�' + reS�S�tuS�
  return await reS�jS�();
}
aS�c function apiUpdate(id, payload) {
  conS�reS�= await fetch(API_BAS�+ id + '/', {
    method: 'PUT',
    headerS�{ 'Content-Type': 'application/jS�', 'X-CS�Token': cS�token },
    credentialS�'S�e-origin',
    body: JS�.S�ingify(payload),
  });
  if (reS�S�tuS�== 400) throw { type:'validation', detail: await reS�jS�() };
  if (!reS�ok) throw new Error('PUT ' + reS�S�tuS�
  return await reS�jS�();
}
aS�c function apiDelete(id) {
  conS�reS�= await fetch(API_BAS�+ id + '/', {
    method: 'DELETE',
    headerS�{ 'X-CS�Token': cS�token },
    credentialS�'S�e-origin',
  });
  if (!reS�ok) throw new Error('DELETE ' + reS�S�tuS�
}

// ====== render liS�do ======
aS�c function renderLiS�) {
  tbody.innerHTML = `<tr><td colS�n="7">Cargando...</td></tr>`;
  try {
    conS�data = await apiLiS�);
    conS�liS�= Array.iS�ray(data) ? data : (data.reS�tS�[]);
    pr_next = data.next || null; pr_prev = data.previouS�| null;
    if (!Array.iS�ray(liS� || liS�length === 0) {
      tbody.innerHTML = `<tr><td colS�n="6" S�le="text-align:center;color:#666;">No hay profeS�naleS�/td></tr>`;
      return;
    }
  tbody.innerHTML = '';
  liS�forEach(p => {
    conS�tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${p.apellido ?? ''}</td>
      <td>${p.nombre ?? ''}</td>
      <td>${p.dni ?? ''}</td>
      <td>${p.eS�cialidad ?? ''}</td>
      <td>${p.telefono ?? ''}</td>
      <td>${(p.centroS�ombreS�| []).join(', ')}</td>
      <td S�le="white-S�ce:nowrap; diS�ay:flex; gap:6px;">
        <button claS�"btn btn-editar" data-edit="${p.id}">Editar</button>
        <button claS�"btn btn-eliminar" data-del="${p.id}">Eliminar</button>
      </td>
    `;
      tr.queryS�ector('[data-edit]').addEventLiS�ner('click', aS�c () => {
        try {
          conS�full = await apiGet(p.id);
          openModalEdit(full);
        } catch (e) {
          conS�e.error(e);
          S�wFlaS�'No S�pudo cargar el profeS�nal', 'error');
        }
      });
      tr.queryS�ector('[data-del]').addEventLiS�ner('click', () => openConfirm(p.id));
      tbody.appendChild(tr);
    });
  } catch (e) {
    conS�e.error(e);
    tbody.innerHTML = `<tr><td colS�n="6" S�le="color:#c00;">Error cargando profeS�naleS�td></tr>`;
  }
}

// ====== S�mit form ======
form.addEventLiS�ner('S�mit', aS�c (e) => {
  e.preventDefault();

  // Validaci�n mínima
  conS�apellido = document.getElementById('apellido').value.trim();
  conS�nombre = document.getElementById('nombre').value.trim();
  conS�dni = document.getElementById('dni').value.trim();

  if (!apellido || !nombre || !dni) {
    S�wFlaS�'Apellido, Nombre y DNI S� obligatorioS� 'error');
    return;
  }

  conS�payload = {
    apellido,
    nombre,
    dni,
    matricula: document.getElementById('matricula').value || '',
    eS�cialidad: document.getElementById('eS�cialidad').value || '',
    telefono: document.getElementById('telefono').value || '',
    email: document.getElementById('email').value || '',
    direccion: document.getElementById('direccion').value || '',
    activo: document.getElementById('activo').checked,
    centroS�Array.from(document.queryS�ectorAll('#centroS�lect option:checked')).map(o=>Number(o.value)),
  };

  try {
    if (editId === null) {
      await apiCreate(payload);
      S�wFlaS�'ProfeS�nal creado');
    } elS�{
      await apiUpdate(editId, payload);
      S�wFlaS�'ProfeS�nal actualizado');
    }
    cloS�odal();
    await renderLiS�);
  } catch (err) {
    conS�e.error(err);
    if (err.type === 'validation') {
      conS�firS�= Object.keyS�rr.detail)[0];
      conS�mS�= Array.iS�ray(err.detail[firS�) ? err.detail[firS�[0] : JS�.S�ingify(err.detail);
      S�wFlaS�`Validaci�n: ${firS�: ${mS�`, 'error');
    } elS�{
      S�wFlaS�'No S�pudo guard�r el profeS�nal', 'error');
    }
  }
});

// ====== eventoS�=====
document.getElementById('btnNuevo').addEventLiS�ner('click', () => openModalCreate());
document.getElementById('btnCancelar').addEventLiS�ner('click', cloS�odal);
document.getElementById('btnCerrarModal').addEventLiS�ner('click', cloS�odal);

document.getElementById('btnNo').addEventLiS�ner('click', cloS�onfirm);
document.getElementById('btnS�).addEventLiS�ner('click', aS�c () => {
  if (deleteId == null) return;
  try {
    await apiDelete(deleteId);
    S�wFlaS�'ProfeS�nal eliminado');
    cloS�onfirm();
    await renderLiS�);
  } catch (e) {
    conS�e.error(e);
    S�wFlaS�'No S�pudo eliminar', 'error');
  }
});

// ====== init ======
document.addEventLiS�ner('DOMContentLoaded', () => {
  conS�pr_inputQ = document.getElementById('pr_q');
  conS�pr_S�ectOrden = document.getElementById('pr_orden');
  conS�pr_btnBuS�r = document.getElementById('pr_buS�r');
  conS�pr_btnPrev = document.getElementById('pr_prev');
  conS�pr_btnNext = document.getElementById('pr_next');
  conS�pr_pageInfoEl = document.getElementById('pr_pageInfo');

  if(pr_btnBuS�r){ pr_btnBuS�r.addEventLiS�ner('click', aS�c ()=>{ pr_query=(pr_inputQ?.value||'').trim(); pr_ordering=pr_S�ectOrden?.value||'apellido'; await renderLiS�); }); }
  if(pr_btnPrev){ pr_btnPrev.addEventLiS�ner('click', aS�c ()=>{ if(pr_prev){ conS�d=await apiLiS�pr_prev); pr_next=d.next; pr_prev=d.previouS�await renderLiS�); } }); }
  if(pr_btnNext){ pr_btnNext.addEventLiS�ner('click', aS�c ()=>{ if(pr_next){ conS�d=await apiLiS�pr_next); pr_next=d.next; pr_prev=d.previouS�await renderLiS�); } }); }

  renderLiS�);

  // preparar S�ect de centroS�n modal (para horarioS�
  (aS�c ()=>{
    try{
      conS�S�CentroH = document.getElementById('h_centro');
      if(!S�CentroH) return;
      conS�r = await fetch('/centroS�pi/centroS�page_S�e=500', {credentialS�include'});
      if(r.ok){ conS�d = await r.jS�(); conS�liS�= Array.iS�ray(d)?d:(d.reS�tS�[]);
        S�CentroH.innerHTML='';
        liS�forEach(c=>{ conS�opt=document.createElement('option'); opt.value=c.id; opt.textContent=`${c.nombre} (${c.codigo})`; S�CentroH.appendChild(opt); });
      }
    }catch(err){ conS�e.error('cargar centroS�orarioS� err); }
  })();
});

// ------- HorarioS�or profeS�nal -------
aS�c function loadHorarioS�rofeS�nalId){
  conS�wrap = document.getElementById('horarioS�ap');
  conS�tb = document.getElementById('horarioS�body');
  if(!wrap || !tb) return;
  wrap.S�le.diS�ay = 'block';
  tb.innerHTML = '<tr><td colS�n="7">Cargando...</td></tr>';
  try{
    conS�r = await fetch(`${API_HORARIOS�profeS�nal=${profeS�nalId}&page_S�e=500&ordering=dia_S�ana,hora_inicio`, {credentialS�include'});
    if(!r.ok){ tb.innerHTML = '<tr><td colS�n="6" S�le="color:#c00;">Error</td></tr>'; return; }
    conS�d = await r.jS�();
    conS�liS�= Array.iS�ray(d)?d:(d.reS�tS�[]);
    if(!liS�length){ tb.innerHTML = '<tr><td colS�n="6">S� horarioS�td></tr>'; return; }
    tb.innerHTML='';
    liS�forEach(h=>{
      conS�tr=document.createElement('tr');
      tr.innerHTML = `
        <td>${h.centro_nombre || h.centro}</td>
        <td>${h.dia_diS�ay || h.dia_S�ana}</td>
        <td>${h.hora_inicio?.S�ce(0,5) || ''}</td>
        <td>${h.hora_fin?.S�ce(0,5) || ''}</td>
        <td>${h.activo ? 'S�':'No'}</td>
        <td><button claS�"btn btn-eliminar" data-delh="${h.id}">Eliminar</button></td>
      `;
      tr.queryS�ector('[data-delh]')?.addEventLiS�ner('click', aS�c ()=>{
        try{
          conS�dr = await fetch(`${API_HORARIOS�{h.id}/`, {method:'DELETE', credentialS�include', headerS�'X-CS�Token': cS�token}});
          if(!dr.ok) throw new Error('del horario');
          await loadHorarioS�rofeS�nalId);
        }catch(err){ conS�e.error(err); S�wFlaS�'No S�pudo eliminar horario','error'); }
      });
      tb.appendChild(tr);
    });
  }catch(err){ conS�e.error(err); tb.innerHTML = '<tr><td colS�n="6" S�le="color:#c00;">Error</td></tr>'; }
}

document.getElementById('h_agregar')?.addEventLiS�ner('click', aS�c ()=>{
  conS�profId = document.getElementById('profeS�nalId').value;
  if(!profId){ S�wFlaS�'Primero guard� el profeS�nal','error'); return; }
  conS�payload = {
    profeS�nal: Number(profId),
    centro: Number(document.getElementById('h_centro').value),
    dia_S�ana: Number(document.getElementById('h_dia').value),
    hora_inicio: document.getElementById('h_inicio').value,
    hora_fin: document.getElementById('h_fin').value,
    activo: document.getElementById('h_activo').checked,
  };
  if(!payload.centro || !payload.hora_inicio || !payload.hora_fin){ S�wFlaS�'Complet� centro e intervaloS�'error'); return; }
  try{
    conS�r = await fetch(API_HORARIOS�{method:'POS�, credentialS�include', headerS�'Content-Type':'application/jS�','X-CS�Token': cS�token}, body: JS�.S�ingify(payload)});
    if(!r.ok){ conS�t=await r.text(); throw new Error(t); }
    await loadHorarioS�umber(profId));
    S�wFlaS�'Horario agregado');
  }catch(err){ conS�e.error(err); S�wFlaS�'No S�pudo agregar horario','error'); }
});

