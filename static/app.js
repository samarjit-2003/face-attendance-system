const video = document.getElementById('webcam');
const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn');
const registerBtn = document.getElementById('registerBtn');
const openAdminBtn = document.getElementById('openAdminBtn');

const statusMessage = document.getElementById('statusMessage');
const toast = document.getElementById('toast');

// Modals
const registerModal = document.getElementById('registerModal');
const adminLoginModal = document.getElementById('adminLoginModal');
const adminDashboardModal = document.getElementById('adminDashboardModal');

// Inputs
const newUsername = document.getElementById('newUsername');
const adminPassword = document.getElementById('adminPassword');

// Setup Webcam
async function setupWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        console.error("Error accessing webcam:", err);
        showToast("Webcam access denied or unavailable", "error");
    }
}

// Capture Image from Video
function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    return new Promise((resolve) => {
        canvas.toBlob((blob) => {
            resolve(blob);
        }, 'image/jpeg', 0.9);
    });
}

// Show Toast Notification
function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// API Handlers
async function handleAttendance(action) {
    statusMessage.textContent = "Processing...";
    const blob = await captureImage();
    const formData = new FormData();
    formData.append('file', blob, 'capture.jpg');

    try {
        const res = await fetch(`/api/${action}`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        
        if (res.ok) {
            showToast(data.message, 'success');
            statusMessage.textContent = `Success: ${data.message}`;
            
            if (action === 'login') {
                setTimeout(() => {
                    window.location.href = `/static/room.html?user=${encodeURIComponent(data.user)}`;
                }, 1500);
            }
        } else {
            showToast(data.message, 'error');
            statusMessage.textContent = `Failed: ${data.message}`;
        }
    } catch (err) {
        showToast("Network error", 'error');
        statusMessage.textContent = "Network error";
    }
}

loginBtn.addEventListener('click', () => handleAttendance('login'));
logoutBtn.addEventListener('click', () => handleAttendance('logout'));

// Register Modal Logic
registerBtn.addEventListener('click', () => registerModal.classList.add('active'));
document.getElementById('closeRegisterBtn').addEventListener('click', () => {
    registerModal.classList.remove('active');
    newUsername.value = '';
});

document.getElementById('submitRegisterBtn').addEventListener('click', async () => {
    const name = newUsername.value.trim();
    if (!name) {
        showToast("Username required", "error");
        return;
    }

    statusMessage.textContent = "Registering...";
    registerModal.classList.remove('active');
    
    const blob = await captureImage();
    const formData = new FormData();
    formData.append('name', name);
    formData.append('file', blob, 'capture.jpg');

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        
        if (res.ok) {
            showToast(data.message, 'success');
            statusMessage.textContent = "Registration Sent to Admin";
        } else {
            showToast(data.message, 'error');
            statusMessage.textContent = "Registration Failed";
        }
    } catch (err) {
        showToast("Network error", 'error');
    }
    
    newUsername.value = '';
});

// Admin Modal Logic
openAdminBtn.addEventListener('click', () => adminLoginModal.classList.add('active'));
document.getElementById('closeAdminLoginBtn').addEventListener('click', () => {
    adminLoginModal.classList.remove('active');
    adminPassword.value = '';
});

document.getElementById('submitAdminLoginBtn').addEventListener('click', async () => {
    const pwd = adminPassword.value;
    const formData = new FormData();
    formData.append('password', pwd);

    try {
        const res = await fetch('/api/admin/login', {
            method: 'POST',
            body: formData
        });
        
        if (res.ok) {
            adminLoginModal.classList.remove('active');
            adminPassword.value = '';
            loadAdminDashboard();
        } else {
            showToast("Invalid Password", "error");
        }
    } catch (err) {
        showToast("Network error", "error");
    }
});

// Admin Dashboard
async function loadAdminDashboard() {
    adminDashboardModal.classList.add('active');
    const listContainer = document.getElementById('pendingUsersList');
    listContainer.innerHTML = '<p>Loading...</p>';

    try {
        const res = await fetch('/api/admin/pending');
        const data = await res.json();
        
        listContainer.innerHTML = '';
        
        if (data.pending_users.length === 0) {
            listContainer.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 1rem;">No pending users.</p>';
            return;
        }

        data.pending_users.forEach(user => {
            const div = document.createElement('div');
            div.className = 'pending-item';
            div.innerHTML = `
                <span>${user}</span>
                <div class="pending-item-actions">
                    <button class="btn primary-btn" onclick="verifyUser('${user}')">Verify</button>
                    <button class="btn danger-btn" onclick="rejectUser('${user}')">Reject</button>
                </div>
            `;
            listContainer.appendChild(div);
        });
    } catch (err) {
        listContainer.innerHTML = '<p>Error loading users.</p>';
    }
}

document.getElementById('closeAdminDashboardBtn').addEventListener('click', () => {
    adminDashboardModal.classList.remove('active');
});

// Expose to window for inline onclick
window.verifyUser = async (username) => {
    try {
        const res = await fetch(`/api/admin/verify/${username}`, { method: 'POST' });
        if (res.ok) {
            showToast(`${username} Verified`, 'success');
            loadAdminDashboard();
        }
    } catch (err) { showToast("Error", "error"); }
};

window.rejectUser = async (username) => {
    try {
        const res = await fetch(`/api/admin/reject/${username}`, { method: 'POST' });
        if (res.ok) {
            showToast(`${username} Rejected`, 'success');
            loadAdminDashboard();
        }
    } catch (err) { showToast("Error", "error"); }
};

// Initialize
setupWebcam();

// --- IoT Door Auto-Scan Logic ---
const autoModeToggle = document.getElementById('autoModeToggle');
const doorUnlockOverlay = document.getElementById('doorUnlockOverlay');
const unlockUserText = document.getElementById('unlockUserText');

let autoScanInterval = null;
let isDoorOpen = false;

async function performAutoScan() {
    if (isDoorOpen) return;
    
    const blob = await captureImage();
    const formData = new FormData();
    formData.append('file', blob, 'capture.jpg');
    
    try {
        const res = await fetch('/api/auto_unlock', {
            method: 'POST',
            body: formData
        });
        
        if (res.ok) {
            const data = await res.json();
            isDoorOpen = true;
            
            // Format the message based on state (in/out)
            const actionText = data.state === "in" ? "Logged IN" : "Logged OUT";
            unlockUserText.textContent = `${data.user} - ${actionText}`;
            
            doorUnlockOverlay.classList.remove('hidden');
            statusMessage.textContent = data.message;
            
            if (data.state === "in") {
                // Redirect after 2 seconds to simulate walking in
                setTimeout(() => {
                    window.location.href = `/static/room.html?user=${encodeURIComponent(data.user)}`;
                }, 2000);
            } else {
                // Cooldown: keep door open for 5 seconds for logout
                setTimeout(() => {
                    doorUnlockOverlay.classList.add('hidden');
                    statusMessage.textContent = "Auto-Scanning...";
                    isDoorOpen = false;
                }, 5000);
            }
        }
    } catch (err) {
        // Ignore network errors during background scan
    }
}

autoModeToggle.addEventListener('change', (e) => {
    const actionsDiv = document.querySelector('.actions');
    if (e.target.checked) {
        actionsDiv.style.display = 'none';
        statusMessage.textContent = "Auto-Scanning...";
        autoScanInterval = setInterval(performAutoScan, 2000);
    } else {
        actionsDiv.style.display = 'flex';
        statusMessage.textContent = "Ready to authenticate";
        clearInterval(autoScanInterval);
        isDoorOpen = false;
        doorUnlockOverlay.classList.add('hidden');
    }
});
