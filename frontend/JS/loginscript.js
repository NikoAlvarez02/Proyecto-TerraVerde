document.addEventListener('DOMContentLoaded', () => {
    const loginContainer = document.querySelector('.login-form-container');
    const forgotPasswordContainer = document.querySelector('.forgot-password-container');
    const forgotPasswordLink = document.querySelector('.forgot-password-link');
    const backToLoginLink = document.querySelector('.back-to-login-link');
    const loginForm = document.querySelector('.login-form');
    const forgotPasswordForm = document.querySelector('.forgot-password-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const togglePassword = document.getElementById('togglePassword');
    
    let loginAttempts = 0;
    const maxAttempts = 5;
    const validUsername = 'profesional';
    const validPassword = '12345';

    // Función para alternar entre los formularios
    function toggleForms(showLogin) {
        if (showLogin) {
            loginContainer.classList.add('active');
            forgotPasswordContainer.classList.remove('active');
        } else {
            loginContainer.classList.remove('active');
            forgotPasswordContainer.classList.add('active');
        }
    }

    // Mostrar el formulario de login por defecto
    toggleForms(true);

    // Lógica para cambiar al formulario de recuperación
    forgotPasswordLink.addEventListener('click', (e) => {
        e.preventDefault();
        toggleForms(false);
    });

    // Lógica para volver al formulario de login
    backToLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        toggleForms(true);
    });

    // Lógica para mostrar/ocultar la contraseña
    togglePassword.addEventListener('click', function (e) {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.classList.toggle('fa-eye-slash');
        this.classList.toggle('fa-eye');
    });

    // Lógica de validación del login (se mantiene igual)
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        if (!username || !password) {
            alert('Hay campos sin completar. Por favor, ingrese sus datos.');
            return;
        }

        loginAttempts++;

        if (loginAttempts > maxAttempts) {
            alert('Ha superado la máxima cantidad de intentos permitidos de inicio de sesión. Contacte al administrador.');
            loginForm.reset();
            document.querySelector('button[type="submit"]').disabled = true;
            return;
        }

        if (username === validUsername && password === validPassword) {
            alert('Has iniciado la sesión con éxito.');
            loginAttempts = 0;
        } else {
            if (username !== validUsername && password !== validPassword) {
                alert('Datos incorrectos.');
            } else if (username !== validUsername) {
                alert('Nombre de usuario incorrecto.');
            } else if (password !== validPassword) {
                alert('Contraseña incorrecta.');
            }
        }
    });

    // Lógica para el formulario de recuperación de contraseña (simulado)
    forgotPasswordForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const recoveryEmail = document.getElementById('recovery-email').value;
        if (recoveryEmail) {
            alert(`Se ha enviado un mensaje de recuperación a ${recoveryEmail}.`);
            toggleForms(true); // Vuelve al login después de enviar
        } else {
            alert('Por favor, ingrese un correo electrónico.');
        }
    });
});