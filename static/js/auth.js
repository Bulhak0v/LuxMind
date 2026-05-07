document.addEventListener("DOMContentLoaded", () => {
    // Елементи DOM
    const loginView = document.getElementById("login-view");
    const registerView = document.getElementById("register-view");
    const showRegisterBtn = document.getElementById("show-register");
    const showLoginBtn = document.getElementById("show-login");

    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const loginError = document.getElementById("login-error");
    const registerMessage = document.getElementById("register-message");

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    showRegisterBtn.addEventListener("click", (e) => {
        e.preventDefault();
        loginView.classList.add("hidden");
        registerView.classList.remove("hidden");
    });

    showLoginBtn.addEventListener("click", (e) => {
        e.preventDefault();
        registerView.classList.add("hidden");
        loginView.classList.remove("hidden");
    });

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        loginError.classList.add("hidden");

        const username = document.getElementById("login-username").value;
        const password = document.getElementById("login-password").value;

        try {
            const response = await fetch('/api/v1/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('luxmind_token', data.token);
                localStorage.setItem('luxmind_user_id', data.id);
                localStorage.setItem('luxmind_role', data.role);

                if (data.role === 'admin') {
                    window.location.href = '/admin-app/';
                } else {
                    window.location.href = '/operator-app/';
                }
            } else {
                loginError.textContent = data.error || "Помилка авторизації";
                loginError.classList.remove("hidden");
            }
        } catch (error) {
            loginError.textContent = "Помилка з'єднання з сервером";
            loginError.classList.remove("hidden");
        }
    });

    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        registerMessage.className = "alert hidden";

        const username = document.getElementById("reg-username").value;
        const email = document.getElementById("reg-email").value;
        const password = document.getElementById("reg-password").value;
        const role = document.getElementById("reg-role").value;

        try {
            const response = await fetch('/api/v1/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password_hash: password,
                    role: role
                })
            });

            const data = await response.json();

            if (response.ok) {
                registerMessage.textContent = "Акаунт успішно створено! Тепер ви можете увійти.";
                registerMessage.classList.add("alert-success");
                registerMessage.classList.remove("hidden");
                registerForm.reset();
                setTimeout(() => showLoginBtn.click(), 2000);
            } else {
                registerMessage.textContent = "Помилка: Перевірте введені дані (можливо користувач вже існує).";
                registerMessage.classList.add("alert-danger");
                registerMessage.classList.remove("hidden");
                console.error(data);
            }
        } catch (error) {
            registerMessage.textContent = "Помилка з'єднання з сервером";
            registerMessage.classList.add("alert-danger");
            registerMessage.classList.remove("hidden");
        }
    });
});