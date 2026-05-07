document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem('luxmind_token');
    const userId = localStorage.getItem('luxmind_user_id');
    const role = localStorage.getItem('luxmind_role');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content'); // НОВЕ

    if (!token || !userId || (role !== 'operator' && role !== 'admin')) {
        window.location.href = '/';
        return;
    }

    document.getElementById('user-greeting').textContent = `ID: ${userId} (${role})`;

    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = '/';
    });

    const dashboardSelect = document.getElementById('dashboard-select');
    const zoneSelect = document.getElementById('zone-select');
    const lampsContainer = document.getElementById('lamps-container');
    const outagesContainer = document.getElementById('outages-container');

    let currentLamps = [];

    function getResults(data) {
        return data.results !== undefined ? data.results : data;
    }

    function showToast(message, isSuccess = true) {
        const toastEl = document.getElementById('liveToast');
        const header = document.getElementById('toast-header');
        document.getElementById('toast-body').textContent = message;

        header.className = `toast-header text-white ${isSuccess ? 'bg-success' : 'bg-danger'}`;
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    }

    async function loadDashboards() {
        try {
            const response = await fetch(`/api/v1/dashboards/?id=${userId}`);
            const dashboards = getResults(await response.json());
            dashboardSelect.innerHTML = `<option value="">${window.I18N.selectDashboard}</option>`;
            if (dashboards.length === 0) {
                dashboardSelect.innerHTML = `<option value="">${window.I18N.noDashboards}</option>`;
                return;
            }
            dashboards.forEach(db => {
                dashboardSelect.innerHTML += `<option value="${db.id}">${db.name}</option>`;
            });
        } catch (error) { console.error("Error", error); }
    }

    dashboardSelect.addEventListener('change', async (e) => {
        const dashboardId = e.target.value;
        zoneSelect.innerHTML = `<option value="">${window.I18N.selectZone}</option>`;
        lampsContainer.innerHTML = `<div class="alert alert-info">${window.I18N.selectZoneLeft}</div>`;
        outagesContainer.innerHTML = `<p class="text-muted small">${window.I18N.selectZone}</p>`;

        if (!dashboardId) { zoneSelect.disabled = true; return; }

        try {
            zoneSelect.disabled = false;
            const response = await fetch(`/api/v1/zones/?id=${dashboardId}`);
            const zones = getResults(await response.json());
            zones.forEach(zone => {
                zoneSelect.innerHTML += `<option value="${zone.id}">${zone.name} (${zone.type})</option>`;
            });
        } catch (error) { console.error("Error", error); }
    });

    zoneSelect.addEventListener('change', (e) => {
        const zoneId = e.target.value;
        if (!zoneId) return;
        loadLamps(zoneId);
        loadOutages();
    });

    async function loadLamps(zoneId) {
        lampsContainer.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
        try {
            const response = await fetch(`/api/v1/lamps/?id=${zoneId}`);
            currentLamps = getResults(await response.json());
            renderLamps('all'); // Рендеримо всі при завантаженні
        } catch (error) { console.error("Error", error); }
    }

    function renderLamps(filterType) {
        lampsContainer.innerHTML = '';

        let filteredLamps = currentLamps;
        if (filterType !== 'all') {
            filteredLamps = currentLamps.filter(lamp => lamp.status === filterType);
        }

        if (filteredLamps.length === 0) {
            lampsContainer.innerHTML = `<div class="alert alert-warning">${window.I18N.noLamps}</div>`;
            return;
        }

        filteredLamps.forEach(lamp => {
            const statusClass = `status-${lamp.status}`;
            const isFaulty = lamp.status === 'faulty';

            // Інтерактивний повзунок яскравості
            const card = `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card lamp-card shadow-sm border-0 ${isFaulty ? 'border-danger border-2' : ''}">
                        <div class="card-body">
                            <h5 class="card-title d-flex justify-content-between">
                                <span>SN: ${lamp.serial_number}</span>
                                <span class="badge ${isFaulty ? 'bg-danger' : 'bg-success'}">${lamp.status.toUpperCase()}</span>
                            </h5>
                            
                            <label class="form-label mb-0 mt-2">${window.I18N.brightness}: <span id="val-${lamp.id}"><strong>${lamp.current_brightness}%</strong></span></label>
                            <div class="d-flex align-items-center mb-3">
                                <input type="range" class="form-range me-2" id="range-${lamp.id}" 
                                    min="0" max="100" value="${lamp.current_brightness}" 
                                    ${isFaulty ? 'disabled' : ''} 
                                    oninput="document.getElementById('val-${lamp.id}').innerHTML = '<strong>' + this.value + '%</strong>'">
                                
                                <button class="btn btn-sm btn-primary" ${isFaulty ? 'disabled' : ''} 
                                    onclick="updateBrightness(${lamp.id})">${window.I18N.saveBtn}</button>
                            </div>

                            <button class="btn btn-sm btn-outline-info w-100" onclick="viewSensors(${lamp.id}, '${lamp.serial_number}')">
                                ${window.I18N.sensorsBtn}
                            </button>
                        </div>
                    </div>
                </div>
            `;
            lampsContainer.innerHTML += card;
        });
    }

    document.querySelectorAll('#lamp-filters button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Зміна активної кнопки
            document.querySelectorAll('#lamp-filters button').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');

            renderLamps(e.target.getAttribute('data-filter'));
        });
    });

    window.updateBrightness = async function(lampId) {
        const newValue = document.getElementById(`range-${lampId}`).value;
        try {
            const response = await fetch(`/api/v1/lamps/${lampId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ current_brightness: parseInt(newValue) })
            });

            if (response.ok) {
                showToast(window.I18N.updateSuccess, true);
                const lampIndex = currentLamps.findIndex(l => l.id === lampId);
                if (lampIndex > -1) currentLamps[lampIndex].current_brightness = parseInt(newValue);
            } else {
                showToast(window.I18N.updateError, false);
            }
        } catch (error) {
            showToast(window.I18N.updateError, false);
        }
    }

    async function loadOutages() {
        try {
            const response = await fetch(`/api/v1/outage-schedules/?active=true`);
            const outages = getResults(await response.json());
            if (outages.length === 0) {
                outagesContainer.innerHTML = `<p class="text-success small">${window.I18N.noOutages}</p>`;
                return;
            }
            outagesContainer.innerHTML = '';
            outages.forEach(outage => {
                outagesContainer.innerHTML += `
                    <div class="alert alert-danger p-2 mb-2">
                        <strong>${window.I18N.zoneId}: ${outage.zone}</strong><br>
                        <small>${new Date(outage.start_time).toLocaleString()} - ${new Date(outage.end_time).toLocaleString()}</small><br>
                        <small>${outage.description || window.I18N.outageDesc}</small>
                    </div>`;
            });
        } catch (error) { console.error(error); }
    }

    window.viewSensors = async function(lampId, serialNumber) {
        document.getElementById('modal-lamp-id').textContent = serialNumber;
        const container = document.getElementById('sensors-container');
        container.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
        const modal = new bootstrap.Modal(document.getElementById('sensorModal'));
        modal.show();
        try {
            const response = await fetch(`/api/v1/sensors/?id=${lampId}`);
            const sensors = getResults(await response.json());
            if (sensors.length === 0) {
                container.innerHTML = `<p class="text-muted">${window.I18N.noSensors}</p>`;
                return;
            }
            container.innerHTML = '<ul class="list-group"></ul>';
            const ul = container.querySelector('ul');
            sensors.forEach(sensor => {
                ul.innerHTML += `<li class="list-group-item d-flex justify-content-between align-items-center">
                    ${sensor.type.toUpperCase()} <span class="badge bg-primary rounded-pill">ID: ${sensor.id}</span>
                </li>`;
            });
        } catch (error) { container.innerHTML = `<p class="text-danger">${window.I18N.loadError}</p>`; }
    }

    loadDashboards();
});