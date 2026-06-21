// ============================================
// TREMOR MONITORING DASHBOARD
// Simple HTTP Polling Architecture
// ============================================

// Global State
const state = {
    lastSensorUpdate: Date.now(),
    lastChartUpdate: 0,  // Track last chart update time
    thresholds: {
        temperature: { warning_low: 15, warning_high: 30, danger_low: 10, danger_high: 35 },
        humidity: { warning_low: 30, warning_high: 75, danger_low: 20, danger_high: 85 }
    },
    charts: {
        realtime: null,
        trend: null
    },
    realtimeData: {
        labels: [],
        temperatures: [],
        humidities: []
    }
};

// ============================================
// CLOCK & TIME DISPLAY
// ============================================

function updateClock() {
    const now = new Date();
    
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    
    const monthNames = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
    const date = String(now.getDate()).padStart(2, '0');
    const month = monthNames[now.getMonth()];
    const year = now.getFullYear();
    
    const clockDisplay = document.getElementById('clockDisplay');
    const dateDisplay = document.getElementById('dateDisplay');
    
    if (clockDisplay) {
        clockDisplay.textContent = `${hours}:${minutes}:${seconds}`;
    }
    if (dateDisplay) {
        dateDisplay.textContent = `${date}-${month}-${year}`;
    }
}

// ============================================
// CHARTS INITIALIZATION
// ============================================

function initCharts() {
    // Real-time Series Chart (Temperature & Humidity) - Line Chart, Updated per 1 minute
    const realtimeCtx = document.getElementById('realtimeChart');
    if (realtimeCtx && realtimeCtx.tagName !== 'CANVAS') {
        // Create canvas inside the div
        const canvas = document.createElement('canvas');
        realtimeCtx.appendChild(canvas);
        
        state.charts.realtime = new Chart(canvas, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Temperature (°C)',
                        data: [],
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.15)',
                        borderWidth: 3,
                        tension: 0.45,
                        yAxisID: 'y',
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: '#ef4444',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        fill: true,
                        stepped: false
                    },
                    {
                        label: 'Humidity (%)',
                        data: [],
                        borderColor: '#0ea5e9',
                        backgroundColor: 'rgba(14, 165, 233, 0.15)',
                        borderWidth: 3,
                        tension: 0.45,
                        yAxisID: 'y1',
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: '#0ea5e9',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        fill: true,
                        stepped: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { 
                        display: true, 
                        position: 'top',
                        labels: {
                            padding: 20,
                            font: { size: 14, weight: 'bold' },
                            usePointStyle: true
                        }
                    },
                    filler: { propagate: true }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'Temperature (°C)', font: { size: 13, weight: 'bold' } },
                        min: 10,
                        max: 40,
                        ticks: { font: { size: 12 } },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'Humidity (%)', font: { size: 13, weight: 'bold' } },
                        min: 0,
                        max: 100,
                        ticks: { font: { size: 12 } },
                        grid: { drawOnChartArea: false }
                    },
                    x: {
                        ticks: { font: { size: 12 } },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    }
                }
            }
        });
    }

    // Hourly Average Chart (Bar Chart) - Full Size
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        state.charts.trend = new Chart(trendCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Avg Temperature (°C)',
                        data: [],
                        backgroundColor: 'rgba(239, 68, 68, 0.8)',
                        borderColor: '#ef4444',
                        borderWidth: 0,
                        borderRadius: 8
                    },
                    {
                        label: 'Avg Humidity (%)',
                        data: [],
                        backgroundColor: 'rgba(14, 165, 233, 0.8)',
                        borderColor: '#0ea5e9',
                        borderWidth: 0,
                        borderRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { font: { size: 12 } },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    x: {
                        ticks: { font: { size: 12 } },
                        grid: { drawOnChartArea: false }
                    }
                },
                plugins: {
                    legend: { 
                        display: true, 
                        position: 'top',
                        labels: {
                            padding: 20,
                            font: { size: 14, weight: 'bold' },
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
}

// ============================================
// SENSOR DATA POLLING & HANDLING
// ============================================

function pollSensorData() {
    fetch('/api/latest/', { credentials: 'same-origin' })
        .then(response => {
            if (!response.ok) throw new Error(`API error: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data && data.temperature !== undefined) {
                handleSensorData(data);
            }
        })
        .catch(error => {
            console.error('❌ Polling error:', error);
            updateConnectionStatus('disconnected');
        });
}

function handleSensorData(data) {
    state.lastSensorUpdate = Date.now();
    
    const temp = parseFloat(data.temperature);
    const humidity = parseFloat(data.humidity);
    
    // Update temperature display
    const tempEl = document.getElementById('currentValue');
    if (tempEl) {
        tempEl.textContent = temp.toFixed(1);
        tempEl.style.color = '#f87171'; // Soft red for temperature
    }
    
    // Update humidity display
    const humEl = document.getElementById('currentHumidity');
    if (humEl) {
        humEl.textContent = humidity.toFixed(1);
        humEl.style.color = '#0ea5e9'; // Blue for humidity
    }
    
    // Update temperature status
    const statusEl = document.getElementById('statusMessage');
    if (statusEl) {
        const tempStatus = data.temp_status === 'normal' ? '✅ Normal' : 
                          data.temp_status === 'warning' ? '⚠️ Warning' : 
                          '❌ Danger';
        statusEl.textContent = `Temperature: ${tempStatus}`;
        statusEl.className = `reading-status status-${data.temp_status}`;
    }
    
    // Update humidity status
    const humStatusEl = document.getElementById('humidityStatusMessage');
    if (humStatusEl) {
        const humStatus = data.humidity_status === 'normal' ? '✅ Normal' : 
                         data.humidity_status === 'warning' ? '⚠️ Warning' : 
                         '❌ Danger';
        humStatusEl.textContent = `Humidity: ${humStatus}`;
        humStatusEl.className = `reading-status status-${data.humidity_status}`;
    }
    
    // Update last update time
    const updateTimeEl = document.getElementById('updateTime');
    if (updateTimeEl) {
        updateTimeEl.textContent = `Update: ${new Date().toLocaleTimeString('id-ID')}`;
    }
    
    console.log(`✅ Data updated: ${temp}°C, ${humidity}%`);
    updateConnectionStatus('connected');
    
    // Update realtime chart (per 1 minute, not every 3 seconds)
    updateRealtimeChart(data);
}

function updateRealtimeChart(data) {
    if (!state.charts.realtime) return;
    
    // Only update chart every 60 seconds (1 minute)
    const now = Date.now();
    if (now - state.lastChartUpdate < 60000) {
        return;  // Skip update if less than 1 minute has passed
    }
    state.lastChartUpdate = now;
    
    const timeLabel = new Date().toLocaleTimeString('id-ID');
    
    // Keep only last 60 data points (1 hour if updated every minute)
    if (state.realtimeData.labels.length >= 60) {
        state.realtimeData.labels.shift();
        state.realtimeData.temperatures.shift();
        state.realtimeData.humidities.shift();
    }
    
    state.realtimeData.labels.push(timeLabel);
    state.realtimeData.temperatures.push(data.temperature);
    state.realtimeData.humidities.push(data.humidity);
    
    state.charts.realtime.data.labels = state.realtimeData.labels;
    state.charts.realtime.data.datasets[0].data = state.realtimeData.temperatures;
    state.charts.realtime.data.datasets[1].data = state.realtimeData.humidities;
    state.charts.realtime.update('none');
}



// ============================================
// CONNECTION STATUS
// ============================================

function updateConnectionStatus(status) {
    const statusEl = document.getElementById('systemStatus');
    if (statusEl) {
        if (status === 'connected') {
            statusEl.innerHTML = '<i class="fas fa-circle" style="color: #10b981;"></i> Active';
            statusEl.style.color = '#10b981';
        } else {
            statusEl.innerHTML = '<i class="fas fa-circle" style="color: #ef4444;"></i> Inactive';
            statusEl.style.color = '#ef4444';
        }
    }
}

function checkSensorConnectionStatus() {
    fetch('/api/sensor-status/', { credentials: 'same-origin' })
        .then(response => response.json())
        .then(data => {
            updateConnectionStatus(data.is_connected ? 'connected' : 'disconnected');
        })
        .catch(error => {
            console.error('Status error:', error);
            updateConnectionStatus('disconnected');
        });
}

// ============================================
// HISTORY & ALERTS
// ============================================

function loadHistoryData() {
    fetch('/api/history/?hours=24&limit=50', { credentials: 'same-origin' })
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data)) return;
            
            // Populate history table
            const historyTable = document.getElementById('historyTable');
            if (historyTable) {
                historyTable.innerHTML = '';
                data.slice(0, 20).forEach(reading => {
                    const row = document.createElement('tr');
                    const timestamp = new Date(reading.timestamp).toLocaleString('id-ID');
                    const statusText = reading.temp_status === 'danger' ? '🔴 DANGER' : 
                                      reading.temp_status === 'warning' ? '🟡 WARNING' : '🟢 NORMAL';
                    row.innerHTML = `
                        <td>${timestamp}</td>
                        <td>${reading.temperature.toFixed(1)}°C</td>
                        <td>${reading.humidity.toFixed(1)}%</td>
                        <td>${statusText}</td>
                    `;
                    historyTable.appendChild(row);
                });
            }
            
            // Update hourly trend chart
            updateHourlyTrend(data);
        })
        .catch(error => console.error('History error:', error));
}

function updateHourlyTrend(data) {
    if (!state.charts.trend) return;
    
    // Group data by hour
    const hourlyData = {};
    data.forEach(reading => {
        const date = new Date(reading.timestamp);
        const hour = `${String(date.getHours()).padStart(2, '0')}:00`;
        
        if (!hourlyData[hour]) {
            hourlyData[hour] = { temps: [], humidities: [] };
        }
        hourlyData[hour].temps.push(reading.temperature);
        hourlyData[hour].humidities.push(reading.humidity);
    });
    
    // Calculate averages - last 12 hours
    const labels = Object.keys(hourlyData).sort().slice(-12);
    const avgTemps = labels.map(hour => {
        const temps = hourlyData[hour].temps;
        return temps.reduce((a, b) => a + b, 0) / temps.length;
    });
    const avgHumidities = labels.map(hour => {
        const hums = hourlyData[hour].humidities;
        return hums.reduce((a, b) => a + b, 0) / hums.length;
    });
    
    // Clear and update chart data (prevent duplicates on refresh)
    state.charts.trend.data.labels = labels;
    state.charts.trend.data.datasets[0].data = avgTemps;
    state.charts.trend.data.datasets[1].data = avgHumidities;
    state.charts.trend.update();
}

function loadAlertsData() {
    fetch('/api/history/?hours=24&limit=100', { credentials: 'same-origin' })
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data)) return;
            
            // Filter only danger/warning readings
            const alerts = data.filter(r => r.temp_status !== 'normal' || r.humidity_status !== 'normal');
            
            // Populate trigger history
            const triggerList = document.getElementById('triggerListContainer');
            if (triggerList && alerts.length > 0) {
                triggerList.innerHTML = '';
                alerts.slice(0, 10).forEach(alert => {
                    const timestamp = new Date(alert.timestamp).toLocaleString('id-ID');
                    const badge = alert.temp_status === 'danger' || alert.humidity_status === 'danger' 
                        ? 'badge-danger' : 'badge-warning';
                    const badgeText = alert.temp_status === 'danger' || alert.humidity_status === 'danger' 
                        ? 'DANGER' : 'WARNING';
                    
                    const triggerItem = document.createElement('div');
                    triggerItem.className = 'trigger-item';
                    triggerItem.innerHTML = `
                        <div>
                            <i class="fas fa-${alert.temp_status !== 'normal' ? 'thermometer-half' : 'tint'}"></i> 
                            <strong>${alert.temp_status !== 'normal' ? 'Temperature' : 'Humidity'} Alert</strong>
                            <br>
                            <span style="font-size:12px;">${timestamp}</span>
                        </div>
                        <span class="badge ${badge}">${badgeText}</span>
                    `;
                    triggerList.appendChild(triggerItem);
                });
            }
        })
        .catch(error => console.error('Alerts error:', error));
}

// ============================================
// EVENT LISTENERS
// ============================================

function setupEventListeners() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('Logout?')) {
                window.location.href = '/logout/';
            }
        });
    }
    
    // Page navigation
    const pages = ['dashboardPage', 'triggerHistoryPage', 'reportsPage', 'thresholdPage', 'exportPage', 'logsPage', 'docsPage'];
    const menuItems = document.querySelectorAll('.menu-item:not(.zabbix-link)');
    menuItems.forEach(btn => {
        btn.addEventListener('click', () => {
            const page = btn.getAttribute('data-page');
            
            // Hide all pages
            pages.forEach(p => {
                const el = document.getElementById(p);
                if (el) el.style.display = 'none';
            });
            
            // Remove active class
            menuItems.forEach(b => b.classList.remove('active'));
            
            // Show selected page
            if (page === 'dashboard') {
                document.getElementById('dashboardPage').style.display = 'block';
                btn.classList.add('active');
            } else if (page === 'trigger-history') {
                document.getElementById('triggerHistoryPage').style.display = 'block';
                btn.classList.add('active');
                loadAlertsData(); // Reload alerts when navigating
            } else if (page === 'reports') {
                document.getElementById('reportsPage').style.display = 'block';
                btn.classList.add('active');
                loadHistoryData(); // Reload history data
            } else if (page === 'threshold') {
                document.getElementById('thresholdPage').style.display = 'block';
                btn.classList.add('active');
            } else if (page === 'export') {
                document.getElementById('exportPage').style.display = 'block';
                btn.classList.add('active');
            } else if (page === 'logs') {
                document.getElementById('logsPage').style.display = 'block';
                btn.classList.add('active');
            } else if (page === 'docs') {
                document.getElementById('docsPage').style.display = 'block';
                btn.classList.add('active');
            }
        });
    });
}

function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// ============================================
// DASHBOARD INITIALIZATION
// ============================================

function initDashboard() {
    console.log('🚀 Dashboard initialized!');
    
    // Prevent double initialization
    if (window.dashboardInitialized) {
        console.log('Dashboard already initialized, skipping init');
        return;
    }
    window.dashboardInitialized = true;
    
    // Setup event listeners
    setupEventListeners();
    
    // Start clock
    updateClock();
    setInterval(updateClock, 1000);
    
    // Initialize charts (with empty data to start fresh)
    initCharts();
    
    // Load history and alerts
    loadHistoryData();
    loadAlertsData();
    
    // Refresh history every 30 seconds
    setInterval(() => {
        loadHistoryData();
        loadAlertsData();
    }, 30000);
    
    // Start polling sensor data (every 3 seconds)
    console.log('📊 Starting sensor data polling every 3 seconds...');
    pollSensorData();
    setInterval(pollSensorData, 3000);
    
    // Check connection status
    checkSensorConnectionStatus();
    setInterval(checkSensorConnectionStatus, 3000);
}

// ============================================
// STARTUP
// ============================================

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 DOM loaded - initializing dashboard');
    initDashboard();
});

// Restore theme preference
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    document.body.classList.add('dark');
}
