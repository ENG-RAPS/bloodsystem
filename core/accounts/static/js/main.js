

const API_BASE = "http://127.0.0.1:8000/api";

// You should replace this with real JWT token later
const token = localStorage.getItem("token");

// =============================
// AUTH HEADER
// =============================
function getHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": token ? `Bearer ${token}` : ""
    };
}

// =============================
// LOAD DASHBOARD DATA
// =============================
document.addEventListener("DOMContentLoaded", () => {
    loadUser();
    loadRequests();
    loadNotifications();
    loadStats();
});

// =============================
// USER INFO
// =============================
function loadUser() {
    fetch(`${API_BASE}/users/profile/`, {
        headers: getHeaders()
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("userName").innerText = data.username;
    })
    .catch(err => console.log(err));
}

// =============================
// REQUESTS TABLE
// =============================
function loadRequests() {
    fetch(`${API_BASE}/requests/`, {
        headers: getHeaders()
    })
    .then(res => res.json())
    .then(data => {
        const tbody = document.querySelector("#requestsTable tbody");
        tbody.innerHTML = "";

        let pendingCount = 0;
        let emergencyCount = 0;

        data.forEach(req => {
            if (req.status === "pending") pendingCount++;
            if (req.request_type === "emergency") emergencyCount++;

            const row = `
                <tr>
                    <td>${req.requester}</td>
                    <td>${req.blood_type}</td>
                    <td>${req.request_type}</td>
                    <td>${req.status}</td>
                    <td>
                        <button class="btn btn-success btn-sm" onclick="approveRequest(${req.id})">Approve</button>
                        <button class="btn btn-danger btn-sm" onclick="rejectRequest(${req.id})">Reject</button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });

        document.getElementById("pendingRequests").innerText = pendingCount;
        document.getElementById("emergencyRequests").innerText = emergencyCount;
        document.getElementById("totalRequests").innerText = data.length;
    });
}

// =============================
// APPROVE REQUEST
// =============================
function approveRequest(id) {
    fetch(`${API_BASE}/requests/${id}/approve/`, {
        method: "POST",
        headers: getHeaders()
    })
    .then(() => loadRequests());
}

// =============================
// REJECT REQUEST
// =============================
function rejectRequest(id) {
    fetch(`${API_BASE}/requests/${id}/reject/`, {
        method: "POST",
        headers: getHeaders()
    })
    .then(() => loadRequests());
}

// =============================
// NOTIFICATIONS
// =============================
function loadNotifications() {
    fetch(`${API_BASE}/notifications/`, {
        headers: getHeaders()
    })
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById("notificationsList");
        container.innerHTML = "";

        data.forEach(n => {
            container.innerHTML += `
                <div class="alert alert-info">
                    <strong>${n.title}</strong><br>
                    ${n.message}
                </div>
            `;
        });
    });
}

// =============================
// BLOOD INVENTORY STATS
// =============================
function loadStats() {
    fetch(`${API_BASE}/inventory/`, {
        headers: getHeaders()
    })
    .then(res => res.json())
    .then(data => {
        let totalUnits = 0;

        data.forEach(item => {
            totalUnits += item.units_available;
        });

        document.getElementById("availableUnits").innerText = totalUnits;
    });
}