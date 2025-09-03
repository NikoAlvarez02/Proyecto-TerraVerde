// src/App.jsx
import PacienteForm from "./PacienteForm";

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
}
