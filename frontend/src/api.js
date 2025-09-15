import axios from "axios";
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
});
import React from 'react';
import './App.css';
import Login from './Login';

function App() {
  return (
    <div className="App">
      <Login />
    </div>
  );
}

export default App;
