import React from 'react';

function App() {
  return (
    <div className="app">
      <h1>React + Vite + Docker</h1>
      <p>
        Plantilla básica lista para usar en producción dentro de un contenedor Docker.
      </p>
      <ul>
        <li>Bundler: Vite</li>
        <li>Vista: React</li>
        <li>Servidor en producción: Nginx</li>
      </ul>
    </div>
  );
}

export default App;