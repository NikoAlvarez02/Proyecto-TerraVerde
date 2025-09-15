import { useState } from "react";

export default function PacienteForm() {
  const [form, setForm] = useState({
    nombre: "",
    apellido: "",
    dni: "",
    fecha_nacimiento: "",
    telefono: "",
    direccion: "",
    nacionalidad: "",
    email: "",
    tiene_representante: false,
    rep_nombre: "",
    rep_dni: "",
    rep_telefono: "",
  });

  const [errors, setErrors] = useState({});
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const update = (k, v) => setForm((s) => ({ ...s, [k]: v }));

  const validar = () => {
    const e = {};
    const req = ["nombre","apellido","dni","fecha_nacimiento","telefono","direccion","nacionalidad"];
    req.forEach((k) => { if (!String(form[k]).trim()) e[k] = "Requerido"; });
    if (form.dni && !/^\d{7,9}$/.test(form.dni)) e.dni = "DNI inválido";
    if (form.email && !/.+@.+\..+/.test(form.email)) e.email = "Email inválido";
    if (form.tiene_representante && form.rep_dni && !/^\d{7,9}$/.test(form.rep_dni)) e.rep_dni = "DNI inválido";
    return e;
  };

  const onSubmit = async (ev) => {
    ev.preventDefault();
    setSuccessMsg(""); 
    setErrorMsg("");

    const e = validar();
    setErrors(e);
    if (Object.keys(e).length > 0) {
      setErrorMsg("Complete todos los campos obligatorios");
      return;
    }

    const ok = window.confirm("¿Desea confirmar estos datos?");
    if (!ok) return;

    try {
      // Simulación de guardado (luego se conecta al backend)
      await new Promise((r) => setTimeout(r, 400));
      setSuccessMsg("Paciente registrado con éxito");
      setForm({
        nombre: "", apellido: "", dni: "", fecha_nacimiento: "",
        telefono: "", direccion: "", nacionalidad: "", email: "",
        tiene_representante: false, rep_nombre: "", rep_dni: "", rep_telefono: ""
      });
      setErrors({});
    } catch {
      setErrorMsg("Error al guardar los datos. Intente nuevamente");
    }
  };

  return (
    <form onSubmit={onSubmit}>
      <div className="form-grid">
        <div className="field">
          <label>Nombre</label>
          <input className="input" value={form.nombre} onChange={e=>update("nombre", e.target.value)} />
          {errors.nombre && <div className="error-text">{errors.nombre}</div>}
        </div>

        <div className="field">
          <label>Apellido</label>
          <input className="input" value={form.apellido} onChange={e=>update("apellido", e.target.value)} />
          {errors.apellido && <div className="error-text">{errors.apellido}</div>}
        </div>

        <div className="field">
          <label>DNI</label>
          <input className="input" value={form.dni} onChange={e=>update("dni", e.target.value)} />
          {errors.dni && <div className="error-text">{errors.dni}</div>}
        </div>

        <div className="field">
          <label>Fecha de nacimiento</label>
          <input type="date" className="input" value={form.fecha_nacimiento} onChange={e=>update("fecha_nacimiento", e.target.value)} />
          {errors.fecha_nacimiento && <div className="error-text">{errors.fecha_nacimiento}</div>}
        </div>

        <div className="field">
          <label>Teléfono</label>
          <input className="input" value={form.telefono} onChange={e=>update("telefono", e.target.value)} />
          {errors.telefono && <div className="error-text">{errors.telefono}</div>}
        </div>

        <div className="field">
          <label>Dirección</label>
          <input className="input" value={form.direccion} onChange={e=>update("direccion", e.target.value)} />
          {errors.direccion && <div className="error-text">{errors.direccion}</div>}
        </div>

        <div className="field">
          <label>Nacionalidad</label>
          <input className="input" value={form.nacionalidad} onChange={e=>update("nacionalidad", e.target.value)} />
          {errors.nacionalidad && <div className="error-text">{errors.nacionalidad}</div>}
        </div>

        <div className="field">
          <label>Email (opcional)</label>
          <input type="email" className="input" value={form.email} onChange={e=>update("email", e.target.value)} />
          {errors.email && <div className="error-text">{errors.email}</div>}
          <div className="helper">Solo si corresponde</div>
        </div>
      </div>

      <div className="inline">
        <input
          id="rep"
          type="checkbox"
          checked={form.tiene_representante}
          onChange={e=>update("tiene_representante", e.target.checked)}
        />
        <label htmlFor="rep">¿Cuenta con representante legal?</label>
      </div>

      {form.tiene_representante && (
        <div className="form-grid three" style={{ marginTop: 12 }}>
          <div className="field">
            <label>Nombre Rep.</label>
            <input className="input" value={form.rep_nombre} onChange={e=>update("rep_nombre", e.target.value)} />
          </div>
          <div className="field">
            <label>DNI Rep.</label>
            <input className="input" value={form.rep_dni} onChange={e=>update("rep_dni", e.target.value)} />
            {errors.rep_dni && <div className="error-text">{errors.rep_dni}</div>}
          </div>
          <div className="field">
            <label>Teléfono Rep.</label>
            <input className="input" value={form.rep_telefono} onChange={e=>update("rep_telefono", e.target.value)} />
          </div>
        </div>
      )}

      {errorMsg && <div className="alert danger">{errorMsg}</div>}
      {successMsg && <div className="alert success">{successMsg}</div>}

      <div className="actions">
        <button type="submit" className="btn btn-primary">Guardar</button>
        <button
          type="button"
          className="btn btn-ghost"
          onClick={()=>{
            setForm({
              nombre:"", apellido:"", dni:"", fecha_nacimiento:"",
              telefono:"", direccion:"", nacionalidad:"", email:"",
              tiene_representante:false, rep_nombre:"", rep_dni:"", rep_telefono:""
            });
            setErrors({}); setErrorMsg(""); setSuccessMsg("");
          }}
        >
          Cancelar
        </button>
      </div>
    </form>
  );
}
