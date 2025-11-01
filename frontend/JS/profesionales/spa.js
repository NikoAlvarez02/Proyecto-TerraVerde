// ====== CSÌ ======
function getCookie(name) {
  conSÌm = document.cookie.match('(^|;)\\SÌ + name + '\\SÌ\\SÌ[^;]+)');
  return m ? decodeURIComponent(m.pop()) : null;
}
conSÌcSÌtoken = getCookie('cSÌtoken');

// ====== refSÌ=====
conSÌtbody = document.getElementById('profeSÌnaleSÌbody');
conSÌflaSÌ= document.getElementById('flaSÌ);

conSÌmodalForm = document.getElementById('modalForm');
conSÌmodalTitle = document.getElementById('modalTitle');
conSÌform = document.getElementById('formProfeSÌnal');
conSÌbtnNuevo = document.getElementById('btnNuevo');
conSÌbtnCancelar = document.getElementById('btnCancelar');
conSÌbtnCerrarModal = document.getElementById('btnCerrarModal');

conSÌmodalConfirm = document.getElementById('modalConfirm');
conSÌbtnNo = document.getElementById('btnNo');
conSÌbtnSÌ= document.getElementById('btnSÌ);

let editId = null;
let deleteId = null;

conSÌAPI_BASÌ= '/profeSÌnaleSÌpi/profeSÌnaleSÌ;
conSÌAPI_HORARIOSÌ '/profeSÌnaleSÌpi/profeSÌnaleSÌorarioSÌ;
let pr_pageSÌe = 10;
let pr_ordering = 'apellido';
let pr_query = '';
let pr_next = null;
let pr_prev = null;

// ====== helperSÌI ======
function SÌwFlaSÌmSÌ type = 'ok') {
  flaSÌSÌle.diSÌay = 'block';
  flaSÌSÌle.padding = '8px';
  flaSÌSÌle.borderRadiuSÌ '8px';
  flaSÌSÌle.background = type === 'ok' ? '#e6ffed' : '#ffe6e6';
  flaSÌSÌle.border = '1px SÌid ' + (type === 'ok' ? '#89d79d' : '#e08b8b');
  flaSÌSÌle.color = '#333';
  flaSÌtextContent = mSÌ
  SÌTimeout(() => (flaSÌSÌle.diSÌay = 'none'), 2500);
}

function openModalCreate() {
  editId = null;
  modalTitle.textContent = 'Nuevo ProfeSÌnal';
  form.reSÌ();
  document.getElementById('activo').checked = true;
  modalForm.SÌle.diSÌay = 'block';
}

function openModalEdit(p) {
  editId = p.id;
  modalTitle.textContent = 'Editar ProfeSÌnal';
  form.reSÌ();

  document.getElementById('profeSÌnalId').value = p.id ?? '';
  document.getElementById('apellido').value = p.apellido ?? '';
  document.getElementById('nombre').value = p.nombre ?? '';
  document.getElementById('dni').value = p.dni ?? '';
  document.getElementById('matricula').value = p.matricula ?? '';
  document.getElementById('eSÌcialidad').value = p.eSÌcialidad ?? '';
  document.getElementById('telefono').value = p.telefono ?? '';
  document.getElementById('email').value = p.email ?? '';
  document.getElementById('direccion').value = p.direccion ?? '';
  document.getElementById('activo').checked = !!p.activo;

  modalForm.SÌle.diSÌay = 'block';

  // cargar horarioSÌel profeSÌnal
  try{ loadHorarioSÌ.id); }catch(e){ conSÌe.error(e); }
}

function cloSÌodal() {
  modalForm.SÌle.diSÌay = 'none';
}

function openConfirm(id) {
  deleteId = id;
  modalConfirm.SÌle.diSÌay = 'block';
}

function cloSÌonfirm() {
  deleteId = null;
  modalConfirm.SÌle.diSÌay = 'none';
}

// ====== API ======
aSÌc function apiLiSÌurl=null) {
  conSÌliSÌrl = url || `${API_BASÌ?page_SÌe=${pr_pageSÌe}&ordering=${encodeURIComponent(pr_ordering)}${pr_query?`&SÌrch=${encodeURIComponent(pr_query)}`:''}`;
  conSÌreSÌ= await fetch(liSÌrl, { credentialSÌinclude' });
  if (!reSÌok) throw new Error('GET ' + reSÌSÌtuSÌ
  return await reSÌjSÌ();
}
aSÌc function apiGet(id) {
  conSÌreSÌ= await fetch(API_BASÌ+ id + '/', { credentialSÌSÌe-origin' });
  if (!reSÌok) throw new Error('GET id ' + reSÌSÌtuSÌ
  return await reSÌjSÌ();
}
aSÌc function apiCreate(payload) {
  conSÌreSÌ= await fetch(API_BASÌ {
    method: 'POSÌ,
    headerSÌ{ 'Content-Type': 'application/jSÌ', 'X-CSÌToken': cSÌtoken },
    credentialSÌ'SÌe-origin',
    body: JSÌ.SÌingify(payload),
  });
  if (reSÌSÌtuSÌ== 400) throw { type:'validation', detail: await reSÌjSÌ() };
  if (!reSÌok) throw new Error('POSÌ' + reSÌSÌtuSÌ
  return await reSÌjSÌ();
}
aSÌc function apiUpdate(id, payload) {
  conSÌreSÌ= await fetch(API_BASÌ+ id + '/', {
    method: 'PUT',
    headerSÌ{ 'Content-Type': 'application/jSÌ', 'X-CSÌToken': cSÌtoken },
    credentialSÌ'SÌe-origin',
    body: JSÌ.SÌingify(payload),
  });
  if (reSÌSÌtuSÌ== 400) throw { type:'validation', detail: await reSÌjSÌ() };
  if (!reSÌok) throw new Error('PUT ' + reSÌSÌtuSÌ
  return await reSÌjSÌ();
}
aSÌc function apiDelete(id) {
  conSÌreSÌ= await fetch(API_BASÌ+ id + '/', {
    method: 'DELETE',
    headerSÌ{ 'X-CSÌToken': cSÌtoken },
    credentialSÌ'SÌe-origin',
  });
  if (!reSÌok) throw new Error('DELETE ' + reSÌSÌtuSÌ
}

// ====== render liSÌdo ======
aSÌc function renderLiSÌ) {
  tbody.innerHTML = `<tr><td colSÌn="7">Cargando...</td></tr>`;
  try {
    conSÌdata = await apiLiSÌ);
    conSÌliSÌ= Array.iSÌray(data) ? data : (data.reSÌtSÌ[]);
    pr_next = data.next || null; pr_prev = data.previouSÌ| null;
    if (!Array.iSÌray(liSÌ || liSÌlength === 0) {
      tbody.innerHTML = `<tr><td colSÌn="6" SÌle="text-align:center;color:#666;">No hay profeSÌnaleSÌ/td></tr>`;
      return;
    }
  tbody.innerHTML = '';
  liSÌforEach(p => {
    conSÌtr = document.createElement('tr');
    tr.innerHTML = `
      <td>${p.apellido ?? ''}</td>
      <td>${p.nombre ?? ''}</td>
      <td>${p.dni ?? ''}</td>
      <td>${p.eSÌcialidad ?? ''}</td>
      <td>${p.telefono ?? ''}</td>
      <td>${(p.centroSÌombreSÌ| []).join(', ')}</td>
      <td SÌle="white-SÌce:nowrap; diSÌay:flex; gap:6px;">
        <button claSÌ"btn btn-editar" data-edit="${p.id}">Editar</button>
        <button claSÌ"btn btn-eliminar" data-del="${p.id}">Eliminar</button>
      </td>
    `;
      tr.querySÌector('[data-edit]').addEventLiSÌner('click', aSÌc () => {
        try {
          conSÌfull = await apiGet(p.id);
          openModalEdit(full);
        } catch (e) {
          conSÌe.error(e);
          SÌwFlaSÌ'No SÌpudo cargar el profeSÌnal', 'error');
        }
      });
      tr.querySÌector('[data-del]').addEventLiSÌner('click', () => openConfirm(p.id));
      tbody.appendChild(tr);
    });
  } catch (e) {
    conSÌe.error(e);
    tbody.innerHTML = `<tr><td colSÌn="6" SÌle="color:#c00;">Error cargando profeSÌnaleSÌtd></tr>`;
  }
}

// ====== SÌmit form ======
form.addEventLiSÌner('SÌmit', aSÌc (e) => {
  e.preventDefault();

  // ValidaciÛn m√≠nima
  conSÌapellido = document.getElementById('apellido').value.trim();
  conSÌnombre = document.getElementById('nombre').value.trim();
  conSÌdni = document.getElementById('dni').value.trim();

  if (!apellido || !nombre || !dni) {
    SÌwFlaSÌ'Apellido, Nombre y DNI SÌ obligatorioSÌ 'error');
    return;
  }

  conSÌpayload = {
    apellido,
    nombre,
    dni,
    matricula: document.getElementById('matricula').value || '',
    eSÌcialidad: document.getElementById('eSÌcialidad').value || '',
    telefono: document.getElementById('telefono').value || '',
    email: document.getElementById('email').value || '',
    direccion: document.getElementById('direccion').value || '',
    activo: document.getElementById('activo').checked,
    centroSÌArray.from(document.querySÌectorAll('#centroSÌlect option:checked')).map(o=>Number(o.value)),
  };

  try {
    if (editId === null) {
      await apiCreate(payload);
      SÌwFlaSÌ'ProfeSÌnal creado');
    } elSÌ{
      await apiUpdate(editId, payload);
      SÌwFlaSÌ'ProfeSÌnal actualizado');
    }
    cloSÌodal();
    await renderLiSÌ);
  } catch (err) {
    conSÌe.error(err);
    if (err.type === 'validation') {
      conSÌfirSÌ= Object.keySÌrr.detail)[0];
      conSÌmSÌ= Array.iSÌray(err.detail[firSÌ) ? err.detail[firSÌ[0] : JSÌ.SÌingify(err.detail);
      SÌwFlaSÌ`ValidaciÛn: ${firSÌ: ${mSÌ`, 'error');
    } elSÌ{
      SÌwFlaSÌ'No SÌpudo guard·r el profeSÌnal', 'error');
    }
  }
});

// ====== eventoSÌ=====
document.getElementById('btnNuevo').addEventLiSÌner('click', () => openModalCreate());
document.getElementById('btnCancelar').addEventLiSÌner('click', cloSÌodal);
document.getElementById('btnCerrarModal').addEventLiSÌner('click', cloSÌodal);

document.getElementById('btnNo').addEventLiSÌner('click', cloSÌonfirm);
document.getElementById('btnSÌ).addEventLiSÌner('click', aSÌc () => {
  if (deleteId == null) return;
  try {
    await apiDelete(deleteId);
    SÌwFlaSÌ'ProfeSÌnal eliminado');
    cloSÌonfirm();
    await renderLiSÌ);
  } catch (e) {
    conSÌe.error(e);
    SÌwFlaSÌ'No SÌpudo eliminar', 'error');
  }
});

// ====== init ======
document.addEventLiSÌner('DOMContentLoaded', () => {
  conSÌpr_inputQ = document.getElementById('pr_q');
  conSÌpr_SÌectOrden = document.getElementById('pr_orden');
  conSÌpr_btnBuSÌr = document.getElementById('pr_buSÌr');
  conSÌpr_btnPrev = document.getElementById('pr_prev');
  conSÌpr_btnNext = document.getElementById('pr_next');
  conSÌpr_pageInfoEl = document.getElementById('pr_pageInfo');

  if(pr_btnBuSÌr){ pr_btnBuSÌr.addEventLiSÌner('click', aSÌc ()=>{ pr_query=(pr_inputQ?.value||'').trim(); pr_ordering=pr_SÌectOrden?.value||'apellido'; await renderLiSÌ); }); }
  if(pr_btnPrev){ pr_btnPrev.addEventLiSÌner('click', aSÌc ()=>{ if(pr_prev){ conSÌd=await apiLiSÌpr_prev); pr_next=d.next; pr_prev=d.previouSÌawait renderLiSÌ); } }); }
  if(pr_btnNext){ pr_btnNext.addEventLiSÌner('click', aSÌc ()=>{ if(pr_next){ conSÌd=await apiLiSÌpr_next); pr_next=d.next; pr_prev=d.previouSÌawait renderLiSÌ); } }); }

  renderLiSÌ);

  // preparar SÌect de centroSÌn modal (para horarioSÌ
  (aSÌc ()=>{
    try{
      conSÌSÌCentroH = document.getElementById('h_centro');
      if(!SÌCentroH) return;
      conSÌr = await fetch('/centroSÌpi/centroSÌpage_SÌe=500', {credentialSÌinclude'});
      if(r.ok){ conSÌd = await r.jSÌ(); conSÌliSÌ= Array.iSÌray(d)?d:(d.reSÌtSÌ[]);
        SÌCentroH.innerHTML='';
        liSÌforEach(c=>{ conSÌopt=document.createElement('option'); opt.value=c.id; opt.textContent=`${c.nombre} (${c.codigo})`; SÌCentroH.appendChild(opt); });
      }
    }catch(err){ conSÌe.error('cargar centroSÌorarioSÌ err); }
  })();
});

// ------- HorarioSÌor profeSÌnal -------
aSÌc function loadHorarioSÌrofeSÌnalId){
  conSÌwrap = document.getElementById('horarioSÌap');
  conSÌtb = document.getElementById('horarioSÌbody');
  if(!wrap || !tb) return;
  wrap.SÌle.diSÌay = 'block';
  tb.innerHTML = '<tr><td colSÌn="7">Cargando...</td></tr>';
  try{
    conSÌr = await fetch(`${API_HORARIOSÌprofeSÌnal=${profeSÌnalId}&page_SÌe=500&ordering=dia_SÌana,hora_inicio`, {credentialSÌinclude'});
    if(!r.ok){ tb.innerHTML = '<tr><td colSÌn="6" SÌle="color:#c00;">Error</td></tr>'; return; }
    conSÌd = await r.jSÌ();
    conSÌliSÌ= Array.iSÌray(d)?d:(d.reSÌtSÌ[]);
    if(!liSÌlength){ tb.innerHTML = '<tr><td colSÌn="6">SÌ horarioSÌtd></tr>'; return; }
    tb.innerHTML='';
    liSÌforEach(h=>{
      conSÌtr=document.createElement('tr');
      tr.innerHTML = `
        <td>${h.centro_nombre || h.centro}</td>
        <td>${h.dia_diSÌay || h.dia_SÌana}</td>
        <td>${h.hora_inicio?.SÌce(0,5) || ''}</td>
        <td>${h.hora_fin?.SÌce(0,5) || ''}</td>
        <td>${h.activo ? 'SÌ':'No'}</td>
        <td><button claSÌ"btn btn-eliminar" data-delh="${h.id}">Eliminar</button></td>
      `;
      tr.querySÌector('[data-delh]')?.addEventLiSÌner('click', aSÌc ()=>{
        try{
          conSÌdr = await fetch(`${API_HORARIOSÌ{h.id}/`, {method:'DELETE', credentialSÌinclude', headerSÌ'X-CSÌToken': cSÌtoken}});
          if(!dr.ok) throw new Error('del horario');
          await loadHorarioSÌrofeSÌnalId);
        }catch(err){ conSÌe.error(err); SÌwFlaSÌ'No SÌpudo eliminar horario','error'); }
      });
      tb.appendChild(tr);
    });
  }catch(err){ conSÌe.error(err); tb.innerHTML = '<tr><td colSÌn="6" SÌle="color:#c00;">Error</td></tr>'; }
}

document.getElementById('h_agregar')?.addEventLiSÌner('click', aSÌc ()=>{
  conSÌprofId = document.getElementById('profeSÌnalId').value;
  if(!profId){ SÌwFlaSÌ'Primero guard·° el profeSÌnal','error'); return; }
  conSÌpayload = {
    profeSÌnal: Number(profId),
    centro: Number(document.getElementById('h_centro').value),
    dia_SÌana: Number(document.getElementById('h_dia').value),
    hora_inicio: document.getElementById('h_inicio').value,
    hora_fin: document.getElementById('h_fin').value,
    activo: document.getElementById('h_activo').checked,
  };
  if(!payload.centro || !payload.hora_inicio || !payload.hora_fin){ SÌwFlaSÌ'Complet·° centro e intervaloSÌ'error'); return; }
  try{
    conSÌr = await fetch(API_HORARIOSÌ{method:'POSÌ, credentialSÌinclude', headerSÌ'Content-Type':'application/jSÌ','X-CSÌToken': cSÌtoken}, body: JSÌ.SÌingify(payload)});
    if(!r.ok){ conSÌt=await r.text(); throw new Error(t); }
    await loadHorarioSÌumber(profId));
    SÌwFlaSÌ'Horario agregado');
  }catch(err){ conSÌe.error(err); SÌwFlaSÌ'No SÌpudo agregar horario','error'); }
});

