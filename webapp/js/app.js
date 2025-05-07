// SPA logic for login/logout and user display
const header = document.getElementById('header');
const app = document.getElementById('app');

// Helper for API calls
async function apiFetch(endpoint, options = {}) {
    const opts = {
        method: options.method || 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
    };
    if (options.body) opts.body = JSON.stringify(options.body);
    const resp = await fetch('/api' + endpoint, opts);
    let data;
    try { data = await resp.json(); } catch { data = null; }
    return { ok: resp.ok, status: resp.status, data };
}

async function getUser() {
    const result = await apiFetch('/status');
    if (result.ok && result.data && result.data.user) return result.data.user;
    return null;
}

function setUser(user) {
    // No-op: session is managed by backend
}

function renderHeader() {
    getUser().then(user => {
        if (user) {
            header.innerHTML = `
                <div>GeoFinance</div>
                <div id="user-menu">
                    <button id="user-btn">${user.username} ▼</button>
                    <ul>
                        <li id="logout-btn">Logout</li>
                    </ul>
                </div>
            `;
            const userMenu = document.getElementById('user-menu');
            const userBtn = document.getElementById('user-btn');
            userBtn.onclick = () => userMenu.classList.toggle('open');
            document.getElementById('logout-btn').onclick = async () => {
                await apiFetch('/logout', { method: 'POST' });
                renderHeader();
                renderLogin();
            };
            document.addEventListener('click', (e) => {
                if (!userMenu.contains(e.target)) userMenu.classList.remove('open');
            }, { once: true });
        } else {
            header.innerHTML = '<div>GeoFinance</div>';
        }
    });
}

function renderLogin() {
    app.innerHTML = `
        <form class="login-form">
            <h2>Login</h2>
            <div class="error" style="display:none"></div>
            <label>Username<input name="username" required></label>
            <label>Password<input name="password" type="password" required></label>
            <button type="submit">Login</button>
        </form>
    `;
    const form = app.querySelector('form');
    const errorDiv = form.querySelector('.error');
    form.onsubmit = async (e) => {
        e.preventDefault();
        errorDiv.style.display = 'none';
        const username = form.username.value;
        const password = form.password.value;
        const result = await apiFetch('/login', { method: 'POST', body: { username, password } });
        if (result.ok && result.data && result.data.user) {
            renderHeader();
            app.innerHTML = '<h2>Welcome, ' + result.data.user.username + '!</h2>';
        } else {
            errorDiv.textContent = result.data && result.data.message ? result.data.message : 'Login failed';
            errorDiv.style.display = 'block';
        }
    };
}

async function main() {
    await renderHeader();
    const user = await getUser();
    if (user) {
        app.innerHTML = '<h2>Welcome, ' + user.username + '!</h2>';
    } else {
        renderLogin();
    }
}

main();