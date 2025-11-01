// Clean Turnos SPA script (stable)
'use strict';
console.log('[turnos] loaded spa.js');

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

// ====== state ======
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
let t_fechaURL = '';

// ====== helpers UI ======
function showFlash(msg, type = 'ok') {
  const toast = document.getElementById('toast');
  const pageFlash = document.getElementById('flash');
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
  } else if (toast) {
    toast.className = type === 'ok' ? 'toast-ok' : 'toast-error';
    toast.textContent = msg;
    toast.style.display = 'block';
    clearTimeout(showFlash._t);
    showFlash._t = setTimeout(() => (toast.style.display = 'none'), 3500);
  } else {
    alert(msg);
  }
}

// ====== abrir/cerrar modales ======
function openModalCreate() {
  editId = null;
  modalTitle.textContent = 'Nuevo Turno';
  form.reset();
  ensureEstadoOptions();
  modalForm.classList.add('is-open');
  document.body.classList.add('modal-open');
  if (flash) flash.style.display = 'none';
}

function openModalEdit(t) {
  editId = t.id;
  modalTitle.textContent = 'Editar Turno';
  form.reset();
  ensureEstadoOptions();
  document.getElementById('turnoId').value = t.id;
  document.getElementById('fecha').value = t.fecha_display || '';
  document.getElementById('hora').value = t.hora_display || '';
  document.getElementById('estado').value = t.estado || 'pendiente';
  document.getElementById('motivo').value = t.motivo || '';
  document.getElementById('observaciones').value = t.observaciones || '';
  selPaciente.value = String(t.paciente ?? '');
  selProfesional.value = String(t.profesional ?? '');
  modalForm.classList.add('is-open');
  document.body.classList.add('modal-open');
  if (flash) flash.style.display = 'none';
}

function closeModal() {
  modalForm.classList.remove('is-open');
  document.body.classList.remove('modal-open');
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
async function apiList(url = null) {
  let listUrl = url || `${API_TURNOS}?page_size=${t_pageSize}&ordering=${encodeURIComponent(t_ordering)}${t_query ? `&search=${encodeURIComponent(t_query)}` : ''}`;
  // Prefer ?fecha= from calendar, else manual range
  if (t_fechaURL) {
    listUrl += `&fecha=${encodeURIComponent(t_fechaURL)}`;
  } else {
    if (t_fechaDesde) listUrl += `&fecha_hora__date__gte=${encodeURIComponent(t_fechaDesde)}`;
    if (t_fechaHasta) listUrl += `&fecha_hora__date__lte=${encodeURIComponent(t_fechaHasta)}`;
  }
  if (t_estado) listUrl += `&estado=${encodeURIComponent(t_estado)}`;
  if (t_profesionalId) listUrl += `&profesional=${encodeURIComponent(t_profesionalId)}`;
  if (t_pacienteId) listUrl += `&paciente=${encodeURIComponent(t_pacienteId)}`;
  console.log('[turnos] apiList', listUrl);
  const resp = await fetch(listUrl, { credentials: 'include' });
  if (!resp.ok) throw new Error('GET ' + resp.status);
  return await resp.json();
}

async function apiGet(id) {
  const resp = await fetch(API_TURNOS + id + '/', { credentials: 'same-origin' });
  if (!resp.ok) throw new Error('GET id ' + resp.status);
  return await resp.json();
}

async function apiCreate(payload) {
  const resp = await fetch(API_TURNOS, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', 'X-CSRFToken': csrftoken },
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  if (resp.status === 400) throw { type: 'validation', detail: await resp.json() };
  if (!resp.ok) throw new Error('POST ' + resp.status);
  return await resp.json();
}

async function apiUpdate(id, payload) {
  const resp = await fetch(API_TURNOS + id + '/', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', 'X-CSRFToken': csrftoken },
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  if (resp.status === 400) throw { type: 'validation', detail: await resp.json() };
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
  const resp = await fetch(`${API_PACIENTES}?page_size=500&ordering=apellido`, { credentials: 'include' });
  if (!resp.ok) return;
  const data = await resp.json();
  const list = Array.isArray(data) ? data : (data.results || []);
  if (selPaciente) selPaciente.innerHTML = `<option value="">Seleccione...</option>`;
  list.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.textContent = `${p.apellido ?? ''}, ${p.nombre ?? ''}`;
    selPaciente?.appendChild(opt);
  });
}

async function loadProfesionales() {
  const resp = await fetch(`${API_PROFESIONALES}?page_size=500&ordering=apellido`, { credentials: 'include' });
  if (!resp.ok) return;
  const data = await resp.json();
  const list = Array.isArray(data) ? data : (data.results || []);
  if (selProfesional) selProfesional.innerHTML = `<option value="">Seleccione...</option>`;
  list.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.textContent = `${p.apellido ?? ''}, ${p.nombre ?? ''}`;
    selProfesional?.appendChild(opt);
  });
}

async function ensureOptions() {
  await Promise.all([loadPacientes(), loadProfesionales()]);
}

// Asegurar opciones de estado en el modal (defensa ante HTML cacheado)
function ensureEstadoOptions() {
  const sel = document.getElementById('estado');
  if (!sel) return;
  const want = [
    { v: 'pendiente', l: 'Pendiente' },
    { v: 'confirmado', l: 'Confirmado' },
    { v: 'atendido', l: 'Atendido' },
    { v: 'ausente',   l: 'Ausente' },
    { v: 'cancelado', l: 'Cancelado' },
  ];
  const have = Array.from(sel.options).map(o => o.value);
  const missing = want.filter(w => !have.includes(w.v));
  if (missing.length) {
    sel.innerHTML = want.map(w => `<option value="${w.v}">${w.l}</option>`).join('');
  }
}

// ====== Evento clic calendario ======
function setupCalendarClick() {
  const calendar = document.querySelector('.calendario');
  if (!calendar) return;

  const gotoDay = async (selectedDate, clickedEl) => {
    console.log('[turnos] Día seleccionado:', selectedDate);

    // Si no estamos en la vista de Turnos (no existe tbody), redirigir a /turnos/?fecha=...
    if (!tbody) {
      window.location.href = `/turnos/?fecha=${selectedDate}`;
      return;
    }

    // Actualizar filtros visibles y estado interno
    const desde = document.getElementById('t_desde');
    const hasta = document.getElementById('t_hasta');
    if (desde) desde.value = selectedDate;
    if (hasta) hasta.value = selectedDate;
    t_fechaDesde = selectedDate;
    t_fechaHasta = selectedDate;
    t_fechaURL = selectedDate;

    // Marcar visualmente el día seleccionado
    calendar.querySelectorAll('td, button, div').forEach(c => c.classList?.remove('selected-day'));
    clickedEl?.classList?.add('selected-day');

    await renderList();
    showFlash(`Mostrando turnos del ${selectedDate}`, 'ok');
  };

  // Preferir elementos con data-day (más explícito)
  const dayButtons = calendar.querySelectorAll('td[data-day], button[data-day], div[data-day]');
  if (dayButtons.length > 0) {
    dayButtons.forEach(btn => {
      btn.style.cursor = 'pointer';
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        const day = btn.dataset.day;
        const month = btn.dataset.month || (new Date().getMonth() + 1);
        const year = btn.dataset.year || new Date().getFullYear();
        const selectedDate = `${year}-${String(month).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
        await gotoDay(selectedDate, btn);
      });
    });
    return;
  }

  // Fallback: detectar números de día (1–31) en celdas
  const allCells = calendar.querySelectorAll('td, button, div');
  allCells.forEach(cell => {
    const text = (cell.textContent || '').trim();
    const dayNum = parseInt(text, 10);
    if (!isNaN(dayNum) && dayNum >= 1 && dayNum <= 31 && text === String(dayNum)) {
      cell.style.cursor = 'pointer';
      cell.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        // Obtener mes/año del encabezado del calendario (p.ej. "Octubre 2025")
        const monthYearText = calendar.querySelector('h2, h3, .month-year')?.textContent || '';
        const now = new Date();
        let month = now.getMonth();
        let year = now.getFullYear();
        const monthMatch = monthYearText.match(/(\w+)\s+(\d{4})/);
        if (monthMatch) {
          const months = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
          const monthName = monthMatch[1].toLowerCase();
          const monthIndex = months.indexOf(monthName);
          if (monthIndex !== -1) month = monthIndex;
          year = parseInt(monthMatch[2], 10);
        }
        const monthStr = String(month + 1).padStart(2, '0');
        const dayStr = String(dayNum).padStart(2, '0');
        const selectedDate = `${year}-${monthStr}-${dayStr}`;
        await gotoDay(selectedDate, cell);
      });
    }
  });
}

// ====== render listado ======
async function renderList() {
  if (tbody) tbody.innerHTML = `<tr><td colspan="6">Cargando...</td></tr>`;
  try {
    const data = await apiList();
    const raw = Array.isArray(data) ? data : (data.results || []);
    t_next = Array.isArray(data) ? null : (data.next || null);
    t_prev = Array.isArray(data) ? null : (data.previous || null);
    // Front-end safety filter by selected day (in case backend returns extra)
    const day = (t_fechaURL || '').trim();
    const list = day
      ? raw.filter(it => {
          const d = (it.fecha_display || '').slice(0, 10);
          return d === day;
        })
      : raw;
    if (!Array.isArray(list) || list.length === 0) {
      const msg = day ? 'No hay turnos para esta fecha.' : 'No hay turnos.';
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#666;">${msg}</td></tr>`;
      return;
    }
    tbody.innerHTML = '';
    list.forEach(t => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${t.fecha_display ?? ''}</td>
        <td>${t.hora_display ?? ''}</td>
        <td>${t.paciente_nombre ?? t.paciente}</td>
        <td>${t.profesional_nombre ?? t.profesional}</td>
        <td>${t.estado ?? ''}</td>
        <td style="white-space:nowrap; display:flex; gap:6px;">
          <button class="btn btn-editar" data-edit="${t.id}">Editar</button>
          <button class="btn btn-eliminar" data-del="${t.id}">Eliminar</button>
        </td>`;
      tr.querySelector('[data-edit]')?.addEventListener('click', async () => {
        try { const full = await apiGet(t.id); await ensureOptions(); openModalEdit(full); }
        catch (e) { console.error(e); showFlash('No se pudo cargar el turno', 'error'); }
      });
      tr.querySelector('[data-del]')?.addEventListener('click', () => openConfirm(t.id));
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
    if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="color:#c00;">Error cargando turnos</td></tr>`;
  }
}

// ====== submit form ======
form?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fecha = document.getElementById('fecha').value;
  const hora = document.getElementById('hora').value;
  const paciente = selPaciente.value;
  const profesional = selProfesional.value;
  const estado = document.getElementById('estado').value;
  if (!fecha || !hora || !paciente || !profesional || !estado) {
    showFlash('Fecha, hora, paciente, profesional y estado son obligatorios', 'warning');
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
    if (editId === null) { await apiCreate(payload); showFlash('Turno creado'); }
    else { await apiUpdate(editId, payload); showFlash('Turno actualizado'); }
    closeModal();
    await renderList();
  } catch (err) {
    console.error(err);
    if (err.type === 'validation') {
      const first = Object.keys(err.detail)[0];
      const msg = Array.isArray(err.detail[first]) ? err.detail[first][0] : JSON.stringify(err.detail);
      showFlash(`Validacion: ${first}: ${msg}`, 'error');
    } else {
      showFlash('No se pudo guardar el turno', 'error');
    }
  }
});

// ====== eventos ======
btnNuevo?.addEventListener('click', async () => { await ensureOptions(); openModalCreate(); });
btnCancelar?.addEventListener('click', closeModal);
btnCerrarModal?.addEventListener('click', closeModal);

btnNo?.addEventListener('click', closeConfirm);
btnSi?.addEventListener('click', async () => {
  if (deleteId == null) return;
  try { await apiDelete(deleteId); showFlash('Turno eliminado'); closeConfirm(); await renderList(); }
  catch (e) { console.error(e); showFlash('No se pudo eliminar', 'error'); }
});

// ====== init ======
document.addEventListener('DOMContentLoaded', async () => {
  console.log('[turnos] DOMContentLoaded');
  try {
    const qs = new URLSearchParams(location.search);
    const fecha = (qs.get('fecha') || '').trim();
    if (fecha) {
      const desde = document.getElementById('t_desde');
      const hasta = document.getElementById('t_hasta');
      if (desde) desde.value = fecha;
      if (hasta) hasta.value = fecha;
      t_fechaDesde = fecha; t_fechaHasta = fecha; t_fechaURL = fecha;
    }
  } catch (_) {}

  // Filtros
  const t_inputQ = document.getElementById('t_q');
  const t_selectOrden = document.getElementById('t_orden');
  const t_btnBuscar = document.getElementById('t_buscar');
  const t_btnPrev = document.getElementById('t_prev');
  const t_btnNext = document.getElementById('t_next');
  const t_inputDesde = document.getElementById('t_desde');
  const t_inputHasta = document.getElementById('t_hasta');
  const t_selectEstado = document.getElementById('t_estado');
  const t_selectPac = document.getElementById('t_pac');
  const t_selectProf = document.getElementById('t_prof');
  const t_btnHoy = document.getElementById('t_hoy');
  const t_btnSemana = document.getElementById('t_semana');
  const t_btnMes = document.getElementById('t_mes');
  const t_btnLimpiar = document.getElementById('t_limpiar');

  t_btnBuscar?.addEventListener('click', async () => {
    t_query = (t_inputQ?.value || '').trim();
    t_ordering = t_selectOrden?.value || '-fecha_hora';
    t_fechaDesde = t_inputDesde?.value || '';
    t_fechaHasta = t_inputHasta?.value || '';
    t_estado = t_selectEstado?.value || '';
    t_pacienteId = t_selectPac?.value || '';
    t_profesionalId = t_selectProf?.value || '';
    console.log('[turnos] calling renderList');
    await renderList();
  });

  function fmt(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }
  t_btnHoy?.addEventListener('click', () => { const d = new Date(); t_inputDesde.value = fmt(d); t_inputHasta.value = fmt(d); });
  t_btnSemana?.addEventListener('click', () => { const d = new Date(); const dow = d.getDay() || 7; const start = new Date(d); start.setDate(d.getDate() - (dow - 1)); const end = new Date(start); end.setDate(start.getDate() + 6); t_inputDesde.value = fmt(start); t_inputHasta.value = fmt(end); });
  t_btnMes?.addEventListener('click', () => { const d = new Date(); const start = new Date(d.getFullYear(), d.getMonth(), 1); const end = new Date(d.getFullYear(), d.getMonth() + 1, 0); t_inputDesde.value = fmt(start); t_inputHasta.value = fmt(end); });

  t_btnLimpiar?.addEventListener('click', async () => {
    if (t_inputQ) t_inputQ.value = '';
    if (t_inputDesde) t_inputDesde.value = '';
    if (t_inputHasta) t_inputHasta.value = '';
    if (t_selectEstado) t_selectEstado.value = '';
    if (t_selectOrden) t_selectOrden.value = '-fecha_hora';
    if (t_selectPac) t_selectPac.value = '';
    if (t_selectProf) t_selectProf.value = '';
    t_query = t_fechaDesde = t_fechaHasta = t_estado = t_pacienteId = t_profesionalId = '';
    t_fechaURL = '';
    const calendar = document.querySelector('.calendario');
    if (calendar) calendar.querySelectorAll('td, button, div').forEach(c => c.classList?.remove('selected-day'));
    console.log('[turnos] calling renderList');
    await renderList();
  });

  t_btnPrev?.addEventListener('click', async () => { if (t_prev) { const d = await apiList(t_prev); t_next = d.next; t_prev = d.previous; await renderList(); } });
  t_btnNext?.addEventListener('click', async () => { if (t_next) { const d = await apiList(t_next); t_next = d.next; t_prev = d.previous; await renderList(); } });

  console.log('[turnos] calling renderList');
  await renderList();
});

// Global error toast
window.addEventListener('error', function (e) {
  try { if (window.showToast) window.showToast('Error de script: ' + e.message, 'error', 6000); } catch (_) {}
});
