document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem('luxmind_token');
    const userId = localStorage.getItem('luxmind_user_id');
    const role = localStorage.getItem('luxmind_role');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    if (!token || role !== 'admin') {
        window.location.href = '/';
        return;
    }

    document.getElementById('user-greeting').textContent = `Admin ID: ${userId}`;
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = '/';
    });

    function getResults(data) {
        return data.results !== undefined ? data.results : data;
    }

    function showToast(message, isSuccess = true) {
        const toastEl = document.getElementById('liveToast');
        document.getElementById('toast-header').className = `toast-header text-white ${isSuccess ? 'bg-success' : 'bg-danger'}`;
        document.getElementById('toast-body').textContent = message;
        new bootstrap.Toast(toastEl).show();
    }

    async function loadSystemHealth() {
        try {
            const response = await fetch('/api/v1/admin/system-health/');
            const data = await response.json();

            const html = `
                <div class="col-md-4"><div class="card stat-card text-bg-info mb-3" onclick="viewDetails('dashboards')"><div class="card-body">
                    <h5 class="card-title">${data.total_dashboards || 0}</h5><p class="card-text">${window.I18N.totalDashboards}</p>
                </div></div></div>
                <div class="col-md-4"><div class="card stat-card text-bg-secondary mb-3" onclick="viewDetails('zones')"><div class="card-body">
                    <h5 class="card-title">${data.total_zones || 0}</h5><p class="card-text">${window.I18N.totalZones}</p>
                </div></div></div>
                <div class="col-md-4"><div class="card stat-card text-bg-primary mb-3" onclick="viewDetails('lamps')"><div class="card-body">
                    <h5 class="card-title">${data.total_lamps}</h5><p class="card-text">${window.I18N.totalLamps}</p>
                </div></div></div>
                <div class="col-md-4"><div class="card stat-card text-bg-danger mb-3" onclick="viewDetails('faulty_lamps')"><div class="card-body">
                    <h5 class="card-title">${data.faulty_lamps}</h5><p class="card-text">${window.I18N.faultyLamps}</p>
                </div></div></div>
                <div class="col-md-4"><div class="card stat-card text-bg-warning mb-3" onclick="viewDetails('outages')"><div class="card-body">
                    <h5 class="card-title">${data.active_outages}</h5><p class="card-text">${window.I18N.activeOutages}</p>
                </div></div></div>
                <div class="col-md-4"><div class="card stat-card text-bg-success mb-3" onclick="viewDetails('users')"><div class="card-body">
                    <h5 class="card-title">${data.total_users}</h5><p class="card-text">${window.I18N.totalUsers}</p>
                </div></div></div>
            `;
            document.getElementById('health-container').innerHTML = html;
        } catch (error) {
            console.error(error);
        }
    }

    window.viewDetails = async function (type) {
        const titleEl = document.getElementById('dataDetailsTitle');
        const thead = document.getElementById('details-thead');
        const tbody = document.getElementById('details-tbody');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center"><div class="spinner-border text-primary"></div></td></tr>';
        new bootstrap.Modal(document.getElementById('dataDetailsModal')).show();

        try {
            let data = [];
            if (type === 'dashboards') {
                titleEl.textContent = window.I18N.totalDashboards;
                thead.innerHTML = '<tr><th>ID</th><th>Назва</th><th>Акаунт ID</th></tr>';
                data = getResults(await (await fetch('/api/v1/dashboards/')).json());
                tbody.innerHTML = data.map(i => `<tr><td>${i.id}</td><td>${i.name}</td><td>${i.account}</td></tr>`).join('');
            } else if (type === 'zones') {
                titleEl.textContent = window.I18N.totalZones;
                thead.innerHTML = '<tr><th>ID</th><th>Назва</th><th>Тип</th></tr>';
                data = getResults(await (await fetch('/api/v1/zones/')).json());
                tbody.innerHTML = data.map(i => `<tr><td>${i.id}</td><td>${i.name}</td><td>${i.type}</td></tr>`).join('');
            } else if (type === 'lamps' || type === 'faulty_lamps') {
                titleEl.textContent = type === 'lamps' ? window.I18N.totalLamps : window.I18N.faultyLamps;
                thead.innerHTML = '<tr><th>SN</th><th>Зона</th><th>Яскравість</th><th>Статус</th></tr>';
                data = getResults(await (await fetch('/api/v1/lamps/')).json());
                if (type === 'faulty_lamps') data = data.filter(l => l.status === 'faulty');
                tbody.innerHTML = data.map(i => `<tr><td>${i.serial_number}</td><td>${i.zone}</td><td>${i.current_brightness}%</td><td><span class="badge ${i.status === 'faulty' ? 'bg-danger' : 'bg-success'}">${i.status}</span></td></tr>`).join('');
            } else if (type === 'outages') {
                titleEl.textContent = window.I18N.activeOutages;
                thead.innerHTML = '<tr><th>Зона ID</th><th>Початок</th><th>Кінець</th></tr>';
                data = getResults(await (await fetch('/api/v1/outage-schedules/?active=true')).json());
                tbody.innerHTML = data.map(i => `<tr><td>${i.zone}</td><td>${new Date(i.start_time).toLocaleString()}</td><td>${new Date(i.end_time).toLocaleString()}</td></tr>`).join('');
            } else if (type === 'users') {
                titleEl.textContent = window.I18N.totalUsers;
                thead.innerHTML = '<tr><th>ID</th><th>Логін</th><th>Роль</th></tr>';
                data = getResults(await (await fetch('/api/v1/accounts/')).json());
                tbody.innerHTML = data.map(i => `<tr><td>${i.id}</td><td>${i.username}</td><td>${i.role}</td></tr>`).join('');
            }

            if (data.length === 0) tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Дані відсутні</td></tr>';
        } catch (error) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-danger">Помилка завантаження</td></tr>';
        }
    }

    async function loadOutagesAdmin() {
        try {
            const response = await fetch('/api/v1/outage-schedules/');
            const outages = getResults(await response.json());
            const tbody = document.getElementById('outages-table-body');
            tbody.innerHTML = '';
            outages.forEach(o => {
                tbody.innerHTML += `
                    <tr>
                        <td>${o.id}</td><td>${o.zone}</td>
                        <td>${new Date(o.start_time).toLocaleString()}</td>
                        <td>${new Date(o.end_time).toLocaleString()}</td>
                        <td>${o.description || '-'}</td>
                        <td><button class="btn btn-sm btn-outline-danger" onclick="deleteOutage(${o.id})">${window.I18N.deleteBtn}</button></td>
                    </tr>`;
            });
        } catch (error) {
            console.error(error);
        }
    }

    window.loadZonesForOutages = async function () {
        const select = document.getElementById('outage-zone');
        select.innerHTML = '<option value="">Завантаження...</option>';
        try {
            const data = getResults(await (await fetch('/api/v1/zones/')).json());
            select.innerHTML = data.map(z => `<option value="${z.id}">${z.name} (ID: ${z.id})</option>`).join('');
        } catch (error) {
            select.innerHTML = '<option value="">Помилка</option>';
        }
    }

    document.getElementById('add-outage-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            zone: document.getElementById('outage-zone').value,
            start_time: document.getElementById('outage-start').value,
            end_time: document.getElementById('outage-end').value,
            description: document.getElementById('outage-desc').value
        };

        try {
            const response = await fetch('/api/v1/outage-schedules/', {
                method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                showToast(window.I18N.successAdd);
                bootstrap.Modal.getInstance(document.getElementById('addOutageModal')).hide();
                document.getElementById('add-outage-form').reset();
                loadOutagesAdmin();
                loadSystemHealth(); // Оновити лічильник на головній
            } else {
                showToast(window.I18N.errorGeneric, false);
            }
        } catch (error) {
            showToast(window.I18N.errorGeneric, false);
        }
    });

    window.deleteOutage = async function (id) {
        if (!confirm("Видалити графік відключення?")) return;
        try {
            const response = await fetch(`/api/v1/outage-schedules/${id}/`, {
                method: 'DELETE',
                headers: {'X-CSRFToken': csrfToken}
            });
            if (response.ok) {
                showToast(window.I18N.successDel);
                loadOutagesAdmin();
                loadSystemHealth();
            }
        } catch (error) {
            showToast(window.I18N.errorGeneric, false);
        }
    }

    async function loadUsers() {
        try {
            const users = getResults(await (await fetch('/api/v1/accounts/')).json());
            const tbody = document.getElementById('users-table-body');
            tbody.innerHTML = users.map(u => `<tr><td>${u.id}</td><td>${u.username}</td><td>${u.email || '-'}</td><td><span class="badge ${u.role === 'admin' ? 'bg-danger' : 'bg-primary'}">${u.role}</span></td><td><button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${u.id})" ${u.id == userId ? 'disabled' : ''}>${window.I18N.deleteBtn}</button></td></tr>`).join('');
        } catch (e) {
        }
    }

    window.deleteUser = async function (id) {
        if (!confirm("Дійсно видалити?")) return;
        const res = await fetch(`/api/v1/accounts/${id}/`, {method: 'DELETE', headers: {'X-CSRFToken': csrfToken}});
        if (res.ok) {
            showToast(window.I18N.successDel);
            loadUsers();
            loadSystemHealth();
        }
    }
    document.getElementById('add-user-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const res = await fetch('/api/v1/register/', {
            method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
            body: JSON.stringify({
                username: document.getElementById('new-username').value,
                email: document.getElementById('new-email').value,
                password_hash: document.getElementById('new-password').value,
                role: document.getElementById('new-role').value
            })
        });
        if (res.ok) {
            showToast(window.I18N.successAdd);
            bootstrap.Modal.getInstance(document.getElementById('addUserModal')).hide();
            loadUsers();
            loadSystemHealth();
        }
    });

    async function loadBackups() {
        try {
            const b = getResults(await (await fetch('/api/v1/backups/')).json());
            document.getElementById('backups-table-body').innerHTML = b.map(i => `<tr><td>${i.id}</td><td>${new Date(i.created_at).toLocaleString()}</td><td><span class="badge bg-secondary">${i.type}</span></td><td>${i.description}</td><td><code>${i.file_path}</code></td></tr>`).join('');
        } catch (e) {
        }
    }

    window.createBackup = async function (t) {
        const r = await fetch('/api/v1/backups/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
            body: JSON.stringify({id: userId, type: t})
        });
        if (r.ok) {
            showToast(window.I18N.successAdd);
            loadBackups();
        }
    }
    window.simulateImport = function (i) {
        if (i.files[0]) {
            setTimeout(() => showToast("Імпортовано!"), 1000);
            i.value = "";
        }
    }

    document.getElementById('health-tab').addEventListener('click', loadSystemHealth);
    document.getElementById('users-tab').addEventListener('click', loadUsers);
    document.getElementById('outages-tab').addEventListener('click', loadOutagesAdmin);
    document.getElementById('backups-tab').addEventListener('click', loadBackups);

    loadSystemHealth();
});