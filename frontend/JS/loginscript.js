document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.querySelector('.login-form');
  const usernameInput = document.getElementById('id_username');
  const passwordInput = document.getElementById('id_password');
  const togglePassword = document.getElementById('togglePassword');
  // Este link ahora navega a /password-reset/ (no se intercepta)
  // const forgotPasswordLink = document.querySelector('.forgot-password-link');

  // Mostrar/ocultar contraseña
  if (togglePassword && passwordInput) {
    togglePassword.addEventListener('click', function () {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      this.classList.toggle('fa-eye-slash');
      this.classList.toggle('fa-eye');
    });
  }

  // Validación mínima y dejar que Django maneje el login
  if (loginForm && usernameInput && passwordInput) {
    const submitBtn = loginForm.querySelector('button[type="submit"]');
    loginForm.addEventListener('submit', (e) => {
      // Si el botón está deshabilitado (bloqueo por intentos), impedir envío
      if (submitBtn && submitBtn.hasAttribute('disabled')) {
        e.preventDefault();
        if (typeof window.showToast === 'function') window.showToast('Acceso bloqueado por múltiples intentos fallidos.', 'error');
        else alert('Acceso bloqueado por múltiples intentos fallidos.');
        return;
      }
      if (!usernameInput.value.trim() || !passwordInput.value.trim()) {
        e.preventDefault();
        if (typeof window.showToast === 'function') window.showToast('Completá usuario y contraseña.', 'warning');
        else alert('Completá usuario y contraseña.');
      }
      // si ambos tienen valor, no hacemos preventDefault -> Django procesa
    });
  }
});
