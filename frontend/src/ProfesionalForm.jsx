import { useState } from "react";
// import { api } from "./api"; // cuando conectes backend

export default function ProfesionalForm() {
  const [form, setForm] = useState({
    nombre: "", apellido: "", titulo: "", telefono: "", email: "",
  });
  const [errors, setErrors] = useState({});
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const update = (k, v) => setForm((s) => ({ ...s, [k]: v }));

  const validar = () => {
    const e = {};
    const req = ["nombre", "apellido", "titulo", "telefono", "email"];
    req.forEach((k) => { if (!String(form[k]).trim()) e[k] = "Requerido"; });
    if (form.email && !/.+@.+\..+/.test(form.email)) e.email = "Email inválido";
    return e;
  };

  const onSubmit = async (ev) => {
    ev.preventDefault();
    setSuccessMsg(""); setErrorMsg("");
    const e = validar();
    setErrors(e);
    if (Object.keys(e).length > 0) { setErrorMsg("Complete todos los campos obligatorios"); return; }

    const ok = window.confirm("¿Desea confirmar estos datos?");
    if (!ok) return;

    try {
      // Simulación (reemplazar por api.post("/api/profesionales", form))
      await new Promise(r => setTimeout(r, 400));
      setSuccessMsg("Profesional registrado con éxito");
      setForm({ nombre:"", apellido:"", titulo:"", telefono:"", email:"" });
      setErrors({});
    } catch (err) {
      const apiMsg = err?.response?.data?.detail;
      if (apiMsg === "Ya existe un profesional con ese correo institucional") {
        setErrorMsg(apiMsg);
      } else {
        setErrorMsg("Error al guardar los datos. Intente nuevamente");
      }
    }
  };

  return (
    <form onSubmit={onSubmit}>
      <div className="form-grid">
        <div className="field">
          <label>Nombre</label>
          <input className="input" placeholder="María" value={form.nombre} onChange={e=>update("nombre", e.target.value)} />
          {errors.nombre && <div className="error-text">{errors.nombre}</div>}
        </div>

        <div className="field">
          <label>Apellido</label>
          <input className="input" placeholder="Pérez" value={form.apellido} onChange={e=>update("apellido", e.target.value)} />
          {errors.apellido && <div className="error-text">{errors.apellido}</div>}
        </div>

        <div className="field">
          <label>Título</label>
          <input className="input" placeholder="Lic. en Psicopedagogía" value={form.titulo} onChange={e=>update("titulo", e.target.value)} />
          {errors.titulo && <div className="error-text">{errors.titulo}</div>}
        </div>

        <div className="field">
          <label>Teléfono</label>
          <input className="input" placeholder="+54 9 ..." value={form.telefono} onChange={e=>update("telefono", e.target.value)} />
          {errors.telefono && <div className="error-text">{errors.telefono}</div>}
        </div>

        <div className="field">
          <label>Correo Electrónico</label>
          <input type="email" className="input" placeholder="nombre@centro.edu.ar" value={form.email} onChange={e=>update("email", e.target.value)} />
          {errors.email && <div className="error-text">{errors.email}</div>}
          <div className="helper">Usá el correo institucional</div>
        </div>
      </div>

      {errorMsg && <div className="alert danger">{errorMsg}</div>}
      {successMsg && <div className="alert success">{successMsg}</div>}

      <div className="actions">
        <button type="submit" className="btn btn-primary">Guardar</button>
        <button type="button" className="btn btn-ghost" onClick={()=>{
          setForm({ nombre:"", apellido:"", titulo:"", telefono:"", email:"" });
          setErrors({}); setErrorMsg(""); setSuccessMsg("");
        }}>Cancelar</button>
      </div>
    </form>
  );
}
