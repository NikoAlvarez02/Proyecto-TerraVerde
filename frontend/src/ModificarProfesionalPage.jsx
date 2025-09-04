import React, { useEffect, useMemo, useState } from "react";

// --- Helpers --------------------------------------------------------------
const API_BASE =
  typeof window !== "undefined" && window.__API_BASE__
    ? window.__API_BASE__
    : "/api"; // ajusta si es necesario

const initialForm = {
  id: null,
  nombres: "",
  apellidos: "",
  dni: "",
  email_institucional: "",
  telefono: "",
  fecha_nacimiento: "",
  direccion: "",
  nacionalidad: "",
  especialidad_id: "",
  rol: "Profesional",
  activo: true,
};

function validate(form) {
  const errors = {};
  if (!form.nombres?.trim()) errors.nombres = "Requerido";
  if (!form.apellidos?.trim()) errors.apellidos = "Requerido";
  if (!form.dni?.trim()) errors.dni = "Requerido";
  if (!/^[0-9.\-]+$/.test(form.dni)) errors.dni = "Solo números/puntos";
  if (!form.email_institucional?.trim()) errors.email_institucional = "Requerido";
  if (
    form.email_institucional &&
    !/^\S+@\S+\.\S+$/.test(form.email_institucional)
  )
    errors.email_institucional = "Email inválido";
  if (!form.especialidad_id) errors.especialidad_id = "Seleccione";
  if (!form.rol) errors.rol = "Seleccione";
  return errors;
}

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

// --- Mock data (opcional) -------------------------------------------------
const USE_MOCK = false; // cambia a true si quieres sin backend
const MOCK_PROS = [
  {
    id: 1,
    nombres: "Laura",
    apellidos: "Gómez",
    dni: "28123456",
    email_institucional: "laura.gomez@instituto.edu",
    telefono: "+54 11 5555-1111",
    fecha_nacimiento: "1989-05-20",
    direccion: "Av. Siempre Viva 123",
    nacionalidad: "Argentina",
    especialidad_id: 2,
    especialidad_nombre: "Psicopedagogía",
    rol: "Profesional",
    activo: true,
  },
  {
    id: 2,
    nombres: "Diego",
    apellidos: "Rossi",
    dni: "30111222",
    email_institucional: "diego.rossi@instituto.edu",
    telefono: "+54 11 5555-2222",
    fecha_nacimiento: "1985-12-01",
    direccion: "Calle Falsa 742",
    nacionalidad: "Argentina",
    especialidad_id: 1,
    especialidad_nombre: "Psicología",
    rol: "Coordinador",
    activo: true,
  },
];

const MOCK_ESPECIALIDADES = [
  { id: 1, nombre: "Psicología" },
  { id: 2, nombre: "Psicopedagogía" },
  { id: 3, nombre: "Fonoaudiología" },
];

async function fetchProfesionales() {
  if (USE_MOCK) return structuredClone(MOCK_PROS);
  return apiFetch("/profesionales");
}

async function fetchEspecialidades() {
  if (USE_MOCK) return structuredClone(MOCK_ESPECIALIDADES);
  return apiFetch("/especialidades");
}

async function updateProfesional(id, payload) {
  if (USE_MOCK) {
    // simula update
    return new Promise((resolve) => setTimeout(() => resolve(payload), 500));
  }
  return apiFetch(`/profesionales/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

// --- UI Components --------------------------------------------------------
function TextField({ label, name, value, onChange, error, type = "text", placeholder }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-700" htmlFor={name}>{label}</label>
      <input
        id={name}
        name={name}
        type={type}
        className={`rounded-xl border px-3 py-2 focus:outline-none focus:ring w-full ${
          error ? "border-red-500" : "border-gray-300"
        }`}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.name, e.target.value)}
        placeholder={placeholder}
      />
      {error && <span className="text-xs text-red-600">{error}</span>}
    </div>
  );
}

function SelectField({ label, name, value, onChange, error, children }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-700" htmlFor={name}>{label}</label>
      <select
        id={name}
        name={name}
        className={`rounded-xl border px-3 py-2 focus:outline-none focus:ring w-full ${
          error ? "border-red-500" : "border-gray-300"
        }`}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.name, e.target.value)}
      >
        {children}
      </select>
      {error && <span className="text-xs text-red-600">{error}</span>}
    </div>
  );
}

function Toggle({ label, name, checked, onChange }) {
  return (
    <label className="flex items-center gap-3 select-none">
      <span className="text-sm text-gray-700">{label}</span>
      <button
        type="button"
        onClick={() => onChange(name, !checked)}
        className={`h-6 w-11 rounded-full transition-colors ${
          checked ? "bg-green-500" : "bg-gray-300"
        } relative`}
      >
        <span
          className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
            checked ? "translate-x-5" : "translate-x-0.5"
          }`}
        />
      </button>
    </label>
  );
}

function ConfirmDialog({ open, title, message, onCancel, onConfirm, loading }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-sm text-gray-600 mb-6">{message}</p>
        <div className="flex justify-end gap-3">
          <button
            className="rounded-xl border px-4 py-2 text-gray-700 hover:bg-gray-50"
            onClick={onCancel}
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            className="rounded-xl bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-60"
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? "Guardando..." : "Confirmar"}
          </button>
        </div>
      </div>
    </div>
  );
}

// --- Página principal -----------------------------------------------------
export default function ModificarProfesionalPage() {
  const [profesionales, setProfesionales] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    fetchProfesionales().then(setProfesionales).catch(() => setProfesionales([]));
    fetchEspecialidades().then(setEspecialidades).catch(() => setEspecialidades([]));
  }, []);

  useEffect(() => {
    if (selectedId) {
      const pro = profesionales.find((p) => p.id === Number(selectedId));
      if (pro) setForm({ ...initialForm, ...pro });
    } else {
      setForm(initialForm);
    }
    setErrors({});
    setSuccessMsg("");
    setErrorMsg("");
  }, [selectedId, profesionales]);

  function handleChange(name, value) {
    setForm((f) => ({ ...f, [name]: value }));
    setErrors((e) => ({ ...e, [name]: validate({ ...form, [name]: value })[name] }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    const v = validate(form);
    setErrors(v);
    if (Object.keys(v).length === 0) {
      setDialogOpen(true);
    }
  }

  async function handleConfirm() {
    setLoading(true);
    try {
      await updateProfesional(form.id, form);
      setSuccessMsg("¡Profesional actualizado!");
      setDialogOpen(false);
      setLoading(false);
      // Actualiza la lista local
      setProfesionales((prev) =>
        prev.map((p) => (p.id === form.id ? { ...p, ...form } : p))
      );
    } catch (err) {
      setErrorMsg("Error al actualizar: " + err.message);
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">Modificar Profesional</h2>
      <div className="mb-4">
        <label className="font-medium mr-2">Seleccionar profesional:</label>
        <select
          value={selectedId || ""}
          onChange={(e) => setSelectedId(e.target.value)}
          className="border rounded-xl px-3 py-2"
        >
          <option value="">-- Seleccione --</option>
          {profesionales.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nombres} {p.apellidos} ({p.dni})
            </option>
          ))}
        </select>
      </div>
      {selectedId && (
        <form onSubmit={handleSubmit} className="space-y-4">
          <TextField
            label="Nombres"
            name="nombres"
            value={form.nombres}
            onChange={handleChange}
            error={errors.nombres}
          />
          <TextField
            label="Apellidos"
            name="apellidos"
            value={form.apellidos}
            onChange={handleChange}
            error={errors.apellidos}
          />
          <TextField
            label="DNI"
            name="dni"
            value={form.dni}
            onChange={handleChange}
            error={errors.dni}
          />
          <TextField
            label="Email institucional"
            name="email_institucional"
            value={form.email_institucional}
            onChange={handleChange}
            error={errors.email_institucional}
            type="email"
          />
          <TextField
            label="Teléfono"
            name="telefono"
            value={form.telefono}
            onChange={handleChange}
          />
          <TextField
            label="Fecha de nacimiento"
            name="fecha_nacimiento"
            value={form.fecha_nacimiento}
            onChange={handleChange}
            type="date"
          />
          <TextField
            label="Dirección"
            name="direccion"
            value={form.direccion}
            onChange={handleChange}
          />
          <TextField
            label="Nacionalidad"
            name="nacionalidad"
            value={form.nacionalidad}
            onChange={handleChange}
          />
          <SelectField
            label="Especialidad"
            name="especialidad_id"
            value={form.especialidad_id}
            onChange={handleChange}
            error={errors.especialidad_id}
          >
            <option value="">-- Seleccione --</option>
            {especialidades.map((e) => (
              <option key={e.id} value={e.id}>
                {e.nombre}
              </option>
            ))}
          </SelectField>
          <SelectField
            label="Rol"
            name="rol"
            value={form.rol}
            onChange={handleChange}
            error={errors.rol}
          >
            <option value="">-- Seleccione --</option>
            <option value="Profesional">Profesional</option>
            <option value="Coordinador">Coordinador</option>
          </SelectField>
          <Toggle
            label="Activo"
            name="activo"
            checked={form.activo}
            onChange={handleChange}
          />
          <div className="flex gap-3 mt-4">
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700"
            >
              Guardar cambios
            </button>
            <button
              type="button"
              className="bg-gray-200 text-gray-700 px-4 py-2 rounded-xl"
              onClick={() => setSelectedId(null)}
            >
              Cancelar
            </button>
          </div>
          {successMsg && (
            <div className="text-green-700 bg-green-100 rounded-xl px-3 py-2 mt-2">
              {successMsg}
            </div>
          )}
          {errorMsg && (
            <div className="text-red-700 bg-red-100 rounded-xl px-3 py-2 mt-2">
              {errorMsg}
            </div>
          )}
        </form>
      )}
      <ConfirmDialog
        open={dialogOpen}
        title="Confirmar modificación"
        message="¿Desea guardar los cambios realizados?"
        onCancel={() => setDialogOpen(false)}
        onConfirm={handleConfirm}
        loading={loading}
      />
    </div>
  );
}
