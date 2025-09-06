// frontend/src/App.jsx
import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// Carga perezosa de la pantalla de Modificar Paciente
const ModificarPacientePage = lazy(() => import("./ModificarPacientePage"));

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <header className="px-4 py-3 bg-white border-b">
          <h1 className="text-xl font-semibold">Sistema Centro Psicopedagógico</h1>
          <p className="text-sm text-gray-600">CU_0XX – Modificar Paciente</p>
        </header>

        <main className="p-4">
          <Suspense fallback={<div>Cargando...</div>}>
            <Routes>
              {/* Ruta principal del caso de uso */}
              <Route
                path="/pacientes/modificar"
                element={<ModificarPacientePage />}
              />
              {/* Redirección por defecto */}
              <Route path="*" element={<Navigate to="/pacientes/modificar" replace />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </BrowserRouter>
  );
}
