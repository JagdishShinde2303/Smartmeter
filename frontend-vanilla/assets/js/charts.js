/* Charts.js */

// Initialize power consumption chart
function initPowerChart(data = []) {
    const ctx = document.getElementById('powerChart');
    if (!ctx) return;

    if (powerChart) {
        powerChart.destroy();
    }

    const labels = data.length > 0 
        ? data.map(r => new Date(r.timestamp).toLocaleTimeString())
        : [];
    
    const values = data.length > 0
        ? data.map(r => r.power_w)
        : [];

    powerChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Power (W)',
                data: values,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#2563eb'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    labels: { usePointStyle: true }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + ' W';
                        }
                    }
                }
            }
        }
    });
}

// Initialize daily consumption chart
function initConsumptionChart(data = []) {
    const ctx = document.getElementById('consumptionChart');
    if (!ctx) return;

    if (consumptionChart) {
        consumptionChart.destroy();
    }

    const labels = data.length > 0
        ? data.map(d => d.date)
        : [];
    
    const values = data.length > 0
        ? data.map(d => d.consumption)
        : [];

    consumptionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily Consumption (kWh)',
                data: values,
                backgroundColor: '#10b981',
                borderColor: '#059669',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + ' kWh';
                        }
                    }
                }
            }
        }
    });
}

// Fetch and update charts
async function updateCharts(deviceId) {
    try {
        // Last 24 hours power chart
        const toDate = new Date().toISOString();
        const fromDate = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
        
        const readingsData = await fetchReadings(deviceId, fromDate, toDate);
        
        if (readingsData && readingsData.readings) {
            initPowerChart(readingsData.readings);
        }

        // Last 30 days consumption
        const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
        const pastReadings = await fetchReadings(deviceId, thirtyDaysAgo, toDate);
        
        if (pastReadings && pastReadings.readings) {
            // Group by day
            const dailyData = {};
            pastReadings.readings.forEach(r => {
                const date = new Date(r.timestamp).toLocaleDateString();
                if (!dailyData[date]) {
                    dailyData[date] = [];
                }
                dailyData[date].push(r);
            });

            // Calculate daily consumption
            const consumptionData = Object.entries(dailyData).map(([date, readings]) => {
                const consumption = readings.length > 0 
                    ? readings[readings.length - 1].energy_kwh - readings[0].energy_kwh
                    : 0;
                return { date, consumption: Math.max(consumption, 0) };
            });

            initConsumptionChart(consumptionData);
        }
    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

// Add animation to stylesheet
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
