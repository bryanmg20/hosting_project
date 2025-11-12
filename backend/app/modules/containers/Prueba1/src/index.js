import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>¡Bienvenido a mi aplicación React Dockerizada!</h1>
        <p>
          Este es un ejemplo básico de cómo agregar contenido a la aplicación.
        </p>
        <button onClick={() => alert('¡Has hecho clic!')}>Haz clic aquí</button>
      </header>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
