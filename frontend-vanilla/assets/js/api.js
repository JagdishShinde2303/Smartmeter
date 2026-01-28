/* API Calls */

// Generic fetch wrapper
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_URL}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification(`Error: ${error.message}`, 'error');
        return null;
    }
}

// DEVICES
async function fetchDevices() {
    const result = await apiCall('/devices', 'GET');
    if (result && result.devices) {
        allDevices = result.devices;
        return result.devices;
    }
    return [];
}

async function createDevice(deviceData) {
    return await apiCall('/devices', 'POST', deviceData);
}

// READINGS
async function fetchReadings(deviceId, fromDate = null, toDate = null) {
    let endpoint = `/devices/${deviceId}/readings`;
    const params = [];
    
    if (fromDate) params.push(`from=${fromDate}`);
    if (toDate) params.push(`to=${toDate}`);
    
    if (params.length > 0) {
        endpoint += '?' + params.join('&');
    }
    
    return await apiCall(endpoint, 'GET');
}

// BILLING
async function computeBill(deviceId, month) {
    return await apiCall(`/billing/${deviceId}?month=${month}`, 'GET');
}

async function fetchInvoices(deviceId) {
    return await apiCall(`/invoices/${deviceId}`, 'GET');
}

async function downloadInvoice(invoiceId) {
    return await apiCall(`/invoices/${invoiceId}/download`, 'GET');
}

// TARIFFS
async function fetchTariffs() {
    return await apiCall('/tariffs', 'GET');
}

async function updateTariffs(tariffData) {
    return await apiCall('/tariffs', 'POST', tariffData);
}

// Notification helper
function showNotification(message, type = 'info') {
    const notificationId = 'notification-' + Date.now();
    const bgColor = type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#2563eb';
    
    const notif = document.createElement('div');
    notif.id = notificationId;
    notif.textContent = message;
    notif.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: ${bgColor};
        color: white;
        padding: 15px 20px;
        border-radius: 6px;
        z-index: 10000;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notif);
    
    setTimeout(() => {
        notif.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notif.remove(), 300);
    }, 3000);
}
