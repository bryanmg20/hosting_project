document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('cta');
  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  btn?.addEventListener('click', () => {
    alert('¡Hola! Esto corre desde Docker + Nginx 🚀');
  });
});
