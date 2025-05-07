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

function renderDashboard(user) {
    app.innerHTML = `
        <div class="dashboard">
            <aside class="sidebar">
                <nav>
                    <ul>
                        <li><a href="#" class="nav-link" data-section="overview">Overview</a></li>
                        <li><a href="#" class="nav-link" data-section="accounts">Accounts</a></li>
                        <li><a href="#" class="nav-link" data-section="journal">Journal Entries</a></li>
                        <li><a href="#" class="nav-link" data-section="reports">Financial Reports</a></li>
                    </ul>
                </nav>
            </aside>
            <main class="content">
                <div id="overview" class="section active">
                    <h2>Welcome, ${user.username}</h2>
                    <div class="overview-panels">
                        <div class="panel" id="balance-panel">
                            <h3>Account Balances</h3>
                            <div class="loading">Loading...</div>
                        </div>
                        <div class="panel" id="recent-entries-panel">
                            <h3>Recent Journal Entries</h3>
                            <div class="loading">Loading...</div>
                        </div>
                    </div>
                </div>
                <div id="accounts" class="section">
                    <h2>Chart of Accounts</h2>
                    <div class="toolbar">
                        <button id="new-account-btn">New Account</button>
                    </div>
                    <div id="accounts-list" class="loading">Loading accounts...</div>
                </div>
                <div id="journal" class="section">
                    <h2>Journal Entries</h2>
                    <div class="toolbar">
                        <button id="new-journal-btn">New Journal Entry</button>
                    </div>
                    <div id="journal-entries-list" class="loading">Loading journal entries...</div>
                </div>
                <div id="reports" class="section">
                    <h2>Financial Reports</h2>
                    <div class="reports-menu">
                        <button data-report="trial-balance">Trial Balance</button>
                        <button data-report="income-statement">Income Statement</button>
                        <button data-report="balance-sheet">Balance Sheet</button>
                    </div>
                    <div id="report-container">
                        <p>Select a report to view</p>
                    </div>
                </div>
            </main>
        </div>
    `;

    // Handle navigation
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSection = link.getAttribute('data-section');
            
            // Hide all sections and deactivate all links
            sections.forEach(section => section.classList.remove('active'));
            navLinks.forEach(navLink => navLink.classList.remove('active'));
            
            // Show the target section and activate the clicked link
            document.getElementById(targetSection).classList.add('active');
            link.classList.add('active');
            
            // Load the appropriate data for the selected section
            if (targetSection === 'overview') {
                Overview.loadOverviewData();
            } else if (targetSection === 'accounts') {
                Accounts.loadAccountsData();
            } else if (targetSection === 'journal') {
                Journal.loadJournalEntries();
            }
        });
    });

    // Set default active section
    document.querySelector('.nav-link[data-section="overview"]').classList.add('active');
    document.getElementById('overview').classList.add('active');

    // Initialize the overview section data
    Overview.loadOverviewData();

    // Set up event listeners for buttons
    document.getElementById('new-account-btn').addEventListener('click', Accounts.showNewAccountForm);
    document.getElementById('new-journal-btn').addEventListener('click', Journal.showNewJournalEntryForm);
    
    // Set up report buttons
    document.querySelectorAll('.reports-menu button').forEach(btn => {
        btn.addEventListener('click', () => Reports.loadReport(btn.getAttribute('data-report')));
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
            renderDashboard(result.data.user);
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
        renderDashboard(user);
    } else {
        renderLogin();
    }
}

main();