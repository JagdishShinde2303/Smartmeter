/* Main Application Logic */

// Initialize app on page load
document.addEventListener('DOMContentLoaded', async function() {
    initializeApp();
});

async function initializeApp() {
    // Load devices
    await loadDevices();
    
    // Setup event listeners
    setupEventListeners();
    
    // Update time display
    updateTimeDisplay();
    setInterval(updateTimeDisplay, 1000);
    
    // Load initial data
    await loadDashboardData();
    
    // Refresh data every 10 seconds
    setInterval(async () => {
        if (currentDevice) {
            await updateTelemetry();
        }
    }, 10000);
}

// Setup all event listeners
function setupEventListeners() {
    // Page navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', switchPage);
    });

    // Device selection
    document.getElementById('deviceSelect').addEventListener('change', selectDevice);
    document.getElementById('billingDeviceSelect').addEventListener('change', (e) => {
        currentDevice = e.target.value;
    });

    // Add Device
    document.getElementById('addDeviceBtn').addEventListener('click', () => {
        document.getElementById('addDeviceModal').classList.add('show');
    });
    document.getElementById('addDeviceForm').addEventListener('submit', handleAddDevice);

    // Close modals
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.modal').classList.remove('show');
        });
    });

    // Billing
    document.getElementById('computeBillBtn').addEventListener('click', computeAndDisplayBill);
    document.getElementById('downloadPdfBtn').addEventListener('click', downloadBillPdf);
    document.getElementById('editTariffsBtn').addEventListener('click', openEditTariff);
    document.getElementById('editTariffForm').addEventListener('submit', handleUpdateTariff);
    document.getElementById('addSlabBtn').addEventListener('click', addSlabRow);

    // Logout
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Close modals when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('show');
        }
    });
}

// Page navigation
function switchPage(e) {
    e.preventDefault();
    const page = e.target.getAttribute('data-page');
    
    // Update active nav
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    e.target.classList.add('active');

    // Update active page
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    document.getElementById(page).classList.add('active');

    // Update title
    const titles = {
        'dashboard': 'Dashboard',
        'devices': 'Devices',
        'billing': 'Billing & Invoices',
        'tariffs': 'Tariff Configuration'
    };
    document.getElementById('pageTitle').textContent = titles[page] || 'Page';

    // Load page-specific data
    if (page === 'devices') {
        loadDevicesTable();
    } else if (page === 'billing') {
        loadBillingData();
    } else if (page === 'tariffs') {
        loadTariffDisplay();
    }
}

// Load devices
async function loadDevices() {
    const devices = await fetchDevices();
    
    if (!devices) return;

    // Update device selectors
    ['deviceSelect', 'billingDeviceSelect'].forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Select Device...</option>';
        devices.forEach(device => {
            const option = document.createElement('option');
            option.value = device.device_id;
            option.textContent = `${device.name} (${device.device_id})`;
            select.appendChild(option);
        });
    });
}

// Select device
async function selectDevice(e) {
    currentDevice = e.target.value;
    if (currentDevice) {
        await updateTelemetry();
        await updateCharts(currentDevice);
    }
}

// Load dashboard data
async function loadDashboardData() {
    if (!currentDevice) {
        const select = document.getElementById('deviceSelect');
        if (select.options.length > 1) {
            select.selectedIndex = 1;
            currentDevice = select.value;
        }
    }

    if (currentDevice) {
        await updateTelemetry();
        await updateCharts(currentDevice);
    }
}

// Update telemetry display
async function updateTelemetry() {
    if (!currentDevice) return;

    const readingsData = await fetchReadings(currentDevice);
    
    if (!readingsData || !readingsData.readings || readingsData.readings.length === 0) {
        return;
    }

    const latest = readingsData.readings[readingsData.readings.length - 1];
    
    document.getElementById('voltageValue').textContent = (latest.voltage || 0).toFixed(1);
    document.getElementById('currentValue').textContent = (latest.current || 0).toFixed(2);
    document.getElementById('powerValue').textContent = Math.round(latest.power_w || 0);
    document.getElementById('energyValue').textContent = (latest.energy_kwh || 0).toFixed(2);
}

// Devices Table
async function loadDevicesTable() {
    const devices = allDevices;
    const tbody = document.getElementById('devicesTableBody');
    
    if (!devices || devices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No devices found</td></tr>';
        return;
    }

    tbody.innerHTML = devices.map(device => {
        const lastSeen = device.last_seen 
            ? new Date(device.last_seen).toLocaleString()
            : 'Never';
        
        const statusClass = device.status === 'online' ? 'status-online' : 'status-offline';
        
        return `
            <tr>
                <td>${device.device_id}</td>
                <td>${device.name}</td>
                <td>${device.location}</td>
                <td><span class="${statusClass}">${device.status}</span></td>
                <td>${lastSeen}</td>
                <td>
                    <button class="btn btn-danger" onclick="deleteDevice('${device.device_id}')">Delete</button>
                </td>
            </tr>
        `;
    }).join('');
}

// Add device
async function handleAddDevice(e) {
    e.preventDefault();
    
    const device = {
        device_id: document.getElementById('deviceId').value,
        name: document.getElementById('deviceName').value,
        location: document.getElementById('deviceLocation').value
    };

    const result = await createDevice(device);
    
    if (result) {
        showNotification('Device added successfully', 'success');
        document.getElementById('addDeviceForm').reset();
        document.getElementById('addDeviceModal').classList.remove('show');
        await loadDevices();
        loadDevicesTable();
    }
}

// Delete device (placeholder)
function deleteDevice(deviceId) {
    if (confirm(`Delete device ${deviceId}?`)) {
        showNotification('Device deletion not yet implemented', 'info');
    }
}

// Billing data
async function loadBillingData() {
    if (!currentDevice) return;

    const invoicesData = await fetchInvoices(currentDevice);
    
    if (!invoicesData || !invoicesData.invoices) return;

    const tbody = document.getElementById('invoicesTableBody');
    
    if (invoicesData.invoices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No invoices found</td></tr>';
        return;
    }

    tbody.innerHTML = invoicesData.invoices.map(inv => {
        const date = new Date(inv.created_at).toLocaleDateString();
        return `
            <tr>
                <td>${inv.month}</td>
                <td>${inv.energy_kwh.toFixed(2)}</td>
                <td>₹${inv.total.toFixed(2)}</td>
                <td><span class="status-online">${inv.status}</span></td>
                <td>${date}</td>
                <td>
                    <button class="btn btn-primary" onclick="downloadInvoicePdf('${inv._id}')">Download</button>
                </td>
            </tr>
        `;
    }).join('');
}

// Compute and display bill
async function computeAndDisplayBill() {
    if (!currentDevice) {
        showNotification('Please select a device', 'error');
        return;
    }

    const month = document.getElementById('billingMonth').value;
    if (!month) {
        showNotification('Please select a month', 'error');
        return;
    }

    const bill = await computeBill(currentDevice, month);
    
    if (!bill) {
        showNotification('Unable to compute bill', 'error');
        return;
    }

    // Display bill
    document.getElementById('billSummary').style.display = 'block';
    document.getElementById('billEnergy').textContent = bill.energy_kwh.toFixed(2) + ' kWh';
    document.getElementById('billSubtotal').textContent = '₹' + bill.subtotal.toFixed(2);
    document.getElementById('billFixed').textContent = '₹' + bill.fixed_charge.toFixed(2);
    document.getElementById('billTax').textContent = '₹' + bill.tax.toFixed(2);
    document.getElementById('billTotal').textContent = '₹' + bill.total.toFixed(2);

    // Store current bill for PDF download
    window.currentBill = bill;
}

// Download bill PDF
function downloadBillPdf() {
    if (!window.currentBill) {
        showNotification('No bill to download', 'error');
        return;
    }

    const bill = window.currentBill;
    const doc = `
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { text-align: center; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background-color: #f2f2f2; }
        .total { font-weight: bold; font-size: 1.2em; }
    </style>
</head>
<body>
    <h1>Smart Energy Meter Invoice</h1>
    <p><strong>Device ID:</strong> ${bill.device_id}</p>
    <p><strong>Month:</strong> ${bill.month}</p>
    <p><strong>Generated:</strong> ${new Date().toLocaleDateString()}</p>
    
    <h2>Consumption</h2>
    <p><strong>Total Energy:</strong> ${bill.energy_kwh.toFixed(2)} kWh</p>
    
    <h2>Charges</h2>
    <table>
        <tr>
            <th>Slab Range</th>
            <th>Units</th>
            <th>Rate (₹/unit)</th>
            <th>Charge (₹)</th>
        </tr>
        ${bill.slabs.map(s => `
        <tr>
            <td>${s.slab}</td>
            <td>${s.units.toFixed(2)}</td>
            <td>${s.rate.toFixed(2)}</td>
            <td>₹${s.charge.toFixed(2)}</td>
        </tr>
        `).join('')}
    </table>
    
    <h2>Bill Summary</h2>
    <table>
        <tr>
            <td>Subtotal:</td>
            <td>₹${bill.subtotal.toFixed(2)}</td>
        </tr>
        <tr>
            <td>Fixed Charge:</td>
            <td>₹${bill.fixed_charge.toFixed(2)}</td>
        </tr>
        <tr>
            <td>Tax (18%):</td>
            <td>₹${bill.tax.toFixed(2)}</td>
        </tr>
        <tr class="total">
            <td>Total Amount Due:</td>
            <td>₹${bill.total.toFixed(2)}</td>
        </tr>
    </table>
</body>
</html>
    `;

    const blob = new Blob([doc], { type: 'text/html' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `invoice-${bill.device_id}-${bill.month}.html`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showNotification('Invoice downloaded', 'success');
}

function downloadInvoicePdf(invoiceId) {
    showNotification('PDF download feature coming soon', 'info');
}

// Tariff Configuration
async function loadTariffDisplay() {
    const tariff = await fetchTariffs();
    
    if (!tariff) return;

    const tbody = document.getElementById('tariffTableBody');
    tbody.innerHTML = tariff.slabs.map(slab => `
        <tr>
            <td>${slab.range} kWh</td>
            <td>₹${slab.rate.toFixed(2)}</td>
        </tr>
    `).join('');

    document.getElementById('fixedChargeDisplay').textContent = '₹' + tariff.fixed_charge.toFixed(2);
    document.getElementById('taxRateDisplay').textContent = (tariff.tax_rate * 100).toFixed(1) + '%';
}

// Open edit tariff modal
async function openEditTariff() {
    const tariff = await fetchTariffs();
    
    if (!tariff) return;

    document.getElementById('fixedCharge').value = tariff.fixed_charge;
    document.getElementById('taxRate').value = tariff.tax_rate * 100;

    // Clear and populate slabs
    const container = document.getElementById('slabsContainer');
    container.innerHTML = '';
    
    tariff.slabs.forEach((slab, idx) => {
        const row = document.createElement('div');
        row.className = 'slab-row';
        row.innerHTML = `
            <input type="text" placeholder="Range (e.g., 0-100)" value="${slab.range}" class="slab-range" data-idx="${idx}">
            <input type="number" placeholder="Rate" step="0.01" value="${slab.rate}" class="slab-rate" data-idx="${idx}">
            <button type="button" class="btn btn-danger" onclick="removeSlabRow(${idx})">Remove</button>
        `;
        container.appendChild(row);
    });

    document.getElementById('editTariffModal').classList.add('show');
}

function addSlabRow() {
    const container = document.getElementById('slabsContainer');
    const row = document.createElement('div');
    row.className = 'slab-row';
    row.innerHTML = `
        <input type="text" placeholder="Range (e.g., 0-100)" class="slab-range">
        <input type="number" placeholder="Rate" step="0.01" class="slab-rate">
        <button type="button" class="btn btn-danger" onclick="this.parentElement.remove()">Remove</button>
    `;
    container.appendChild(row);
}

function removeSlabRow(idx) {
    document.querySelector(`[data-idx="${idx}"]`).closest('.slab-row').remove();
}

// Update tariffs
async function handleUpdateTariff(e) {
    e.preventDefault();

    const slabs = [];
    document.querySelectorAll('.slab-row').forEach(row => {
        const range = row.querySelector('.slab-range').value;
        const rate = parseFloat(row.querySelector('.slab-rate').value);
        if (range && !isNaN(rate)) {
            slabs.push({ range, rate });
        }
    });

    const tariffData = {
        slabs,
        fixed_charge: parseFloat(document.getElementById('fixedCharge').value),
        tax_rate: parseFloat(document.getElementById('taxRate').value) / 100
    };

    const result = await updateTariffs(tariffData);
    
    if (result) {
        showNotification('Tariffs updated successfully', 'success');
        document.getElementById('editTariffModal').classList.remove('show');
        await loadTariffDisplay();
    }
}

// Update time display
function updateTimeDisplay() {
    const now = new Date();
    document.getElementById('timeDisplay').textContent = now.toLocaleTimeString();
}

// Logout
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        showNotification('Logged out', 'success');
        // Redirect or clear session
        // window.location.href = '/login.html';
    }
}

// Add styles for slab rows
const slabStyle = document.createElement('style');
slabStyle.textContent = `
    .slab-row {
        display: grid;
        grid-template-columns: 1fr 1fr auto;
        gap: 10px;
        margin-bottom: 10px;
        align-items: center;
    }
    
    .slab-row input {
        padding: 8px;
        border: 1px solid var(--border-color);
        border-radius: 4px;
    }
    
    .slab-row .btn {
        margin-bottom: 0;
    }
`;
document.head.appendChild(slabStyle);
