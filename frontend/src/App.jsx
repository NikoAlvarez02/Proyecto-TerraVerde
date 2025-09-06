// src/App.jsx
/*import PacienteForm from "./PacienteForm";

export default function App() {
  return (
    <>
      <header className="site-header">
        <nav className="nav">
          <div className="logo">TV</div>
          <div className="brand">TerraVerde · Centro Psicopedagógico</div>
        </nav>
      </header>

      <main className="container">
        <div className="card">
          <h2>Registrar Paciente</h2>
          <PacienteForm />
        </div>
      </main>
    </>
  );
}*/
import ProfesionalForm from "./ProfesionalForm";

export default function App() {
  return (
    <>
      <header className="site-header">
        <nav className="nav">
          <div className="logo">TV</div>
          <div className="brand">TerraVerde · Centro Psicopedagógico</div>
        </nav>
      </header>

      <main className="container">
        <div className="breadcrumbs">
          <a href="#">TerraVerde</a><span>·</span>
          <a href="#">Administración</a><span>·</span>
          <span>Profesionales</span>
        </div>

        <div className="kicker">Operación diaria</div>
        <h1 className="page-title">Registrar Profesional</h1>
        <p className="page-sub">Cargá los datos básicos para habilitar a un/a profesional en el centro.</p>

        <section className="card split">
          <div>
            <ProfesionalForm />
          </div>

          <aside className="side">
            <div className="tip">✅ Los campos son obligatorios. El acceso se habilita luego.</div>
            <div className="tip">📧 Usá el <b>correo institucional</b>. El sistema evita duplicados.</div>
            <div className="tip">🔒 El profesional <b>no</b> ingresa hasta ser habilitado por administración.</div>
          </aside>
        </section>
      </main>
    </>
  );
}

