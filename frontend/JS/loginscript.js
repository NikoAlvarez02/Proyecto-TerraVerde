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
    loginForm.addEventListener('submit', (e) => {
      if (!usernameInput.value.trim() || !passwordInput.value.trim()) {
        e.preventDefault();
        alert('Completá usuario y contraseña.');
      }
      // si ambos tienen valor, no hacemos preventDefault -> Django procesa
    });
  }
});
