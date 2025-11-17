// S&P 500 Prediction Dashboard - JavaScript
// Interactive functionality and data visualization

// Global chart instances
let confidenceChart = null;
let predictionHistoryChart = null;
let sentimentChart = null;
let featureImportanceChart = null;
let capitalGrowthChart = null;
let technicalChart = null;
let candlestickChart = null;
let currentCandlestickPeriod = 90;

// Auto-refresh variables
let autoRefreshEnabled = true;
let autoRefreshInterval = null;
let refreshIntervalSeconds = 60; // Refresh every 60 seconds

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');

    // Load saved theme
    loadTheme();

    // Load auto-refresh preference
    loadAutoRefreshPreference();

    // Update clock
    updateClock();
    setInterval(updateClock, 1000);

    // Load all data
    loadAllData();

    // Start auto-refresh if enabled
    if (autoRefreshEnabled) {
        startAutoRefresh();
    }
});

// Theme Toggle
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');

    if (body.classList.contains('dark-theme')) {
        body.classList.remove('dark-theme');
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-theme');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
        localStorage.setItem('theme', 'dark');
    }
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('theme-icon');

    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
    }
}

// Auto-Refresh Toggle
function toggleAutoRefresh() {
    autoRefreshEnabled = !autoRefreshEnabled;
    localStorage.setItem('autoRefresh', autoRefreshEnabled ? 'enabled' : 'disabled');

    const refreshIcon = document.getElementById('refresh-icon');
    const refreshStatus = document.getElementById('refresh-status');

    if (autoRefreshEnabled) {
        startAutoRefresh();
        refreshIcon.classList.add('fa-spin');
        refreshStatus.textContent = 'Auto';
        refreshStatus.style.color = '#10b981';
        console.log('Auto-refresh enabled');
    } else {
        stopAutoRefresh();
        refreshIcon.classList.remove('fa-spin');
        refreshStatus.textContent = 'Off';
        refreshStatus.style.color = '#ef4444';
        console.log('Auto-refresh disabled');
    }
}

function startAutoRefresh() {
    // Clear any existing interval
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }

    // Set up new interval
    autoRefreshInterval = setInterval(() => {
        console.log('Auto-refreshing data...');
        loadAllData();
    }, refreshIntervalSeconds * 1000);

    // Update UI
    const refreshIcon = document.getElementById('refresh-icon');
    const refreshStatus = document.getElementById('refresh-status');
    if (refreshIcon) refreshIcon.classList.add('fa-spin');
    if (refreshStatus) {
        refreshStatus.textContent = 'Auto';
        refreshStatus.style.color = '#10b981';
    }
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }

    // Update UI
    const refreshIcon = document.getElementById('refresh-icon');
    const refreshStatus = document.getElementById('refresh-status');
    if (refreshIcon) refreshIcon.classList.remove('fa-spin');
    if (refreshStatus) {
        refreshStatus.textContent = 'Off';
        refreshStatus.style.color = '#ef4444';
    }
}

function loadAutoRefreshPreference() {
    const savedPreference = localStorage.getItem('autoRefresh');

    if (savedPreference === 'disabled') {
        autoRefreshEnabled = false;
        const refreshIcon = document.getElementById('refresh-icon');
        const refreshStatus = document.getElementById('refresh-status');
        if (refreshIcon) refreshIcon.classList.remove('fa-spin');
        if (refreshStatus) {
            refreshStatus.textContent = 'Off';
            refreshStatus.style.color = '#ef4444';
        }
    } else {
        autoRefreshEnabled = true;
        const refreshIcon = document.getElementById('refresh-icon');
        const refreshStatus = document.getElementById('refresh-status');
        if (refreshIcon) refreshIcon.classList.add('fa-spin');
        if (refreshStatus) {
            refreshStatus.textContent = 'Auto';
            refreshStatus.style.color = '#10b981';
        }
    }
}

// Update live clock and market status
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('current-time').textContent = timeString;

    // Update market status
    updateMarketStatus();
}

// Update market status and countdown
function updateMarketStatus() {
    const now = new Date();

    // Convert to ET (UTC-5 or UTC-4 depending on DST)
    const etTime = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));
    const hours = etTime.getHours();
    const minutes = etTime.getMinutes();
    const day = etTime.getDay(); // 0 = Sunday, 6 = Saturday

    const currentMinutes = hours * 60 + minutes;
    const marketOpen = 9 * 60 + 30;  // 9:30 AM
    const marketClose = 16 * 60;      // 4:00 PM
    const preMarketStart = 4 * 60;    // 4:00 AM
    const afterHoursEnd = 20 * 60;    // 8:00 PM

    const statusBadge = document.getElementById('market-status-badge');
    const statusText = document.getElementById('market-status-text');
    const countdownText = document.getElementById('countdown-text');

    let status = '';
    let statusClass = '';
    let countdown = '';

    // Weekend
    if (day === 0 || day === 6) {
        status = 'CLOSED';
        statusClass = 'market-closed';
        const daysUntilMonday = day === 0 ? 1 : 2;
        countdown = `Opens Monday at 9:30 AM ET`;
    }
    // Weekday
    else {
        if (currentMinutes < preMarketStart) {
            // Before pre-market (midnight - 4:00 AM)
            status = 'CLOSED';
            statusClass = 'market-closed';
            const minutesUntil = preMarketStart - currentMinutes;
            countdown = `Pre-market opens in ${formatCountdown(minutesUntil)}`;
        }
        else if (currentMinutes >= preMarketStart && currentMinutes < marketOpen) {
            // Pre-market (4:00 AM - 9:30 AM)
            status = 'PRE-MARKET';
            statusClass = 'market-pre';
            const minutesUntil = marketOpen - currentMinutes;
            countdown = `Market opens in ${formatCountdown(minutesUntil)}`;
        }
        else if (currentMinutes >= marketOpen && currentMinutes < marketClose) {
            // Market open (9:30 AM - 4:00 PM)
            status = 'OPEN';
            statusClass = 'market-open';
            const minutesUntil = marketClose - currentMinutes;
            countdown = `Closes in ${formatCountdown(minutesUntil)}`;
        }
        else if (currentMinutes >= marketClose && currentMinutes < afterHoursEnd) {
            // After hours (4:00 PM - 8:00 PM)
            status = 'AFTER-HOURS';
            statusClass = 'market-after';
            const minutesUntil = afterHoursEnd - currentMinutes;
            countdown = `After-hours ends in ${formatCountdown(minutesUntil)}`;
        }
        else {
            // After 8:00 PM
            status = 'CLOSED';
            statusClass = 'market-closed';
            countdown = `Pre-market opens tomorrow at 4:00 AM ET`;
        }
    }

    if (statusBadge && statusText && countdownText) {
        statusBadge.className = 'market-status-badge ' + statusClass;
        statusText.textContent = status;
        countdownText.textContent = countdown;
    }
}

// Format countdown time
function formatCountdown(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    if (hours > 0) {
        return `${hours}h ${mins}m`;
    } else {
        return `${mins}m`;
    }
}

// Load all dashboard data
async function loadAllData() {
    console.log('Loading dashboard data...');

    try {
        await Promise.all([
            loadLatestPrediction(),
            loadPerformanceMetrics(),
            loadPredictionHistory(),
            loadSentimentData(),
            loadRecentPredictionsTable(),
            loadMarketStatus(),
            loadFeatureImportance(),
            loadTradingSimulation(),
            loadRollingAccuracy(),
            loadEconomicIndicators(),
            loadTechnicalIndicators(),
            loadRecentNews(),
            loadConfusionMatrix(),
            loadRiskMetrics(),
            loadBestWorstPredictions(),
            loadAIExplanation(),
            loadEconomicCalendar()
        ]);

        // Load chart separately to not block page load
        loadCandlestickChart(currentCandlestickPeriod).catch(err => {
            console.error('Chart loading failed:', err);
        });

        console.log('All data loaded successfully');
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Load latest prediction
async function loadLatestPrediction() {
    try {
        const response = await fetch('/api/latest_prediction');
        const data = await response.json();

        if (data.success && data.prediction) {
            const pred = data.prediction;

            // Update direction
            const directionIcon = document.getElementById('direction-icon');
            const directionText = document.getElementById('prediction-direction');
            const directionLabel = document.getElementById('prediction-label');

            if (pred.direction === 'UP') {
                directionIcon.innerHTML = '<i class="fas fa-arrow-up" style="font-size: 4rem;"></i>';
                directionIcon.className = 'prediction-icon up';
                directionText.textContent = 'UP';
                directionText.className = 'fw-bold mb-2 up';
                directionLabel.textContent = 'BULLISH';
            } else {
                directionIcon.innerHTML = '<i class="fas fa-arrow-down" style="font-size: 4rem;"></i>';
                directionIcon.className = 'prediction-icon down';
                directionText.textContent = 'DOWN';
                directionText.className = 'fw-bold mb-2 down';
                directionLabel.textContent = 'BEARISH';
            }

            // Update confidence
            const confidence = (pred.confidence * 100).toFixed(2);
            document.getElementById('confidence-value').textContent = confidence + '%';

            const confidenceBar = document.getElementById('confidence-bar');
            confidenceBar.style.width = confidence + '%';

            const badge = document.getElementById('confidence-badge');
            if (pred.confidence >= 0.70) {
                confidenceBar.className = 'progress-bar high';
                badge.textContent = 'HIGH';
                badge.className = 'badge high';
            } else if (pred.confidence >= 0.60) {
                confidenceBar.className = 'progress-bar medium';
                badge.textContent = 'MEDIUM';
                badge.className = 'badge medium';
            } else {
                confidenceBar.className = 'progress-bar low';
                badge.textContent = 'LOW';
                badge.className = 'badge low';
            }

            // Update probabilities
            document.getElementById('prob-up').textContent = (pred.prob_up * 100).toFixed(2) + '%';
            document.getElementById('prob-down').textContent = (pred.prob_down * 100).toFixed(2) + '%';

            // Update time
            const predDate = new Date(pred.date);
            document.getElementById('pred-time').textContent = predDate.toLocaleString();

        } else {
            console.log('No prediction available yet');
        }
    } catch (error) {
        console.error('Error loading latest prediction:', error);
    }
}

// Load performance metrics
async function loadPerformanceMetrics() {
    try {
        const response = await fetch('/api/performance_metrics');
        const data = await response.json();

        if (data.success && data.metrics) {
            const m = data.metrics;

            document.getElementById('model-accuracy').textContent = m.model_accuracy.toFixed(2) + '%';
            document.getElementById('edge-over-random').textContent = '+' + m.edge_over_random.toFixed(2) + 'pp';
            document.getElementById('total-predictions').textContent = m.total_predictions;
            document.getElementById('avg-confidence').textContent = (m.avg_confidence * 100).toFixed(1) + '%';
            document.getElementById('up-down-ratio').textContent = m.up_predictions + ' / ' + m.down_predictions;

            // Update confidence distribution chart
            updateConfidenceChart(m);
        }
    } catch (error) {
        console.error('Error loading performance metrics:', error);
    }
}

// Update confidence distribution chart
function updateConfidenceChart(metrics) {
    const ctx = document.getElementById('confidenceChart');

    if (confidenceChart) {
        confidenceChart.destroy();
    }

    confidenceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['High (>70%)', 'Medium (60-70%)', 'Low (<60%)'],
            datasets: [{
                data: [
                    metrics.high_confidence_count,
                    metrics.medium_confidence_count,
                    metrics.low_confidence_count
                ],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': ' + value + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// Load prediction history
async function loadPredictionHistory() {
    try {
        const response = await fetch('/api/prediction_history');
        const data = await response.json();

        if (data.success && data.history) {
            updatePredictionHistoryChart(data.history);
        }
    } catch (error) {
        console.error('Error loading prediction history:', error);
    }
}

// Update prediction history chart - Monthly aggregated with enhanced visualization
function updatePredictionHistoryChart(history) {
    const ctx = document.getElementById('predictionHistoryChart');

    if (predictionHistoryChart) {
        predictionHistoryChart.destroy();
    }

    // Format month labels (e.g., "2025-01" -> "Jan 2025")
    const monthLabels = history.months.map(m => {
        const [year, month] = m.split('-');
        const date = new Date(year, month - 1);
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    });

    // Convert confidence to percentage
    const confidences = history.avg_confidence.map(c => (c * 100).toFixed(1));

    // Calculate DOWN predictions
    const downCounts = history.total_predictions.map((total, i) => total - history.up_count[i]);

    predictionHistoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthLabels,
            datasets: [
                {
                    label: 'UP Predictions',
                    data: history.up_count,
                    backgroundColor: 'rgba(16, 185, 129, 0.85)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                },
                {
                    label: 'DOWN Predictions',
                    data: downCounts,
                    backgroundColor: 'rgba(239, 68, 68, 0.85)',
                    borderColor: 'rgba(239, 68, 68, 1)',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                },
                {
                    label: 'Avg Confidence',
                    data: confidences,
                    type: 'line',
                    borderColor: 'rgba(99, 102, 241, 1)',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    fill: false,
                    tension: 0.4,
                    yAxisID: 'y-confidence'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 12,
                            family: 'Inter',
                            weight: '500'
                        },
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(99, 102, 241, 0.5)',
                    borderWidth: 1,
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold',
                        family: 'Inter'
                    },
                    bodyFont: {
                        size: 13,
                        family: 'Inter'
                    },
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            return '📊 ' + context[0].label;
                        },
                        label: function(context) {
                            const index = context.dataIndex;
                            const datasetLabel = context.dataset.label;
                            const value = context.parsed.y;

                            if (datasetLabel === 'Avg Confidence') {
                                return '🎯 ' + datasetLabel + ': ' + value + '%';
                            } else if (datasetLabel === 'UP Predictions') {
                                const pct = history.up_percentage[index].toFixed(1);
                                return '📈 ' + datasetLabel + ': ' + value + ' (' + pct + '%)';
                            } else {
                                const pct = (100 - history.up_percentage[index]).toFixed(1);
                                return '📉 ' + datasetLabel + ': ' + value + ' (' + pct + '%)';
                            }
                        },
                        footer: function(context) {
                            const index = context[0].dataIndex;
                            return '\n📝 Total: ' + history.total_predictions[index] + ' predictions';
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11,
                            family: 'Inter',
                            weight: '500'
                        },
                        color: '#6b7280'
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.06)',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            size: 11,
                            family: 'Inter'
                        },
                        color: '#6b7280'
                    },
                    title: {
                        display: true,
                        text: 'Number of Predictions',
                        font: {
                            size: 12,
                            family: 'Inter',
                            weight: '600'
                        },
                        color: '#374151'
                    }
                },
                'y-confidence': {
                    type: 'linear',
                    position: 'right',
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        },
                        font: {
                            size: 11,
                            family: 'Inter'
                        },
                        color: '#6366f1'
                    },
                    title: {
                        display: true,
                        text: 'Confidence Level',
                        font: {
                            size: 12,
                            family: 'Inter',
                            weight: '600'
                        },
                        color: '#6366f1'
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Load sentiment data
async function loadSentimentData() {
    try {
        const response = await fetch('/api/sentiment_data');
        const data = await response.json();

        if (data.success && data.sentiment) {
            updateSentimentChart(data.sentiment);
        }
    } catch (error) {
        console.error('Error loading sentiment data:', error);
    }
}

// Update sentiment chart
function updateSentimentChart(sentiment) {
    const ctx = document.getElementById('sentimentChart');

    if (sentimentChart) {
        sentimentChart.destroy();
    }

    // Format dates
    const dates = sentiment.dates.map(d => {
        const date = new Date(d);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    sentimentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Sentiment Score',
                data: sentiment.sentiment,
                borderColor: 'rgba(79, 70, 229, 1)',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.y;
                            let sentiment = 'Neutral';
                            if (value > 0.1) sentiment = 'Positive';
                            if (value < -0.1) sentiment = 'Negative';
                            return 'Score: ' + value.toFixed(3) + ' (' + sentiment + ')';
                        }
                    }
                }
            },
            scales: {
                y: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Load recent predictions table with accuracy
async function loadRecentPredictionsTable() {
    try {
        // Try to load predictions with accuracy first
        const accResponse = await fetch('/api/predictions_with_accuracy');
        const accData = await accResponse.json();

        if (accData.success && accData.predictions) {
            updatePredictionsTableWithAccuracy(accData.predictions);
            return;
        }

        // Fallback to regular predictions
        const response = await fetch('/api/recent_predictions_table');
        const data = await response.json();

        if (data.success && data.predictions) {
            updatePredictionsTable(data.predictions);
        }
    } catch (error) {
        console.error('Error loading predictions table:', error);
    }
}

// Update predictions table
function updatePredictionsTable(predictions) {
    const tbody = document.getElementById('predictions-tbody');

    if (predictions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">No predictions yet</td>
            </tr>
        `;
        return;
    }

    let html = '';
    predictions.forEach(pred => {
        const date = new Date(pred.date).toLocaleString();
        const confidence = (pred.confidence * 100).toFixed(1);
        const probUp = (pred.prob_up * 100).toFixed(1);
        const probDown = (pred.prob_down * 100).toFixed(1);

        const directionClass = pred.direction === 'UP' ? 'up' : 'down';
        const directionIcon = pred.direction === 'UP' ?
            '<i class="fas fa-arrow-up me-1"></i>' :
            '<i class="fas fa-arrow-down me-1"></i>';

        // Signal strength bars
        let signalBars = '<div class="signal-strength">';
        const confidenceLevel = pred.confidence >= 0.70 ? 'high' :
                               pred.confidence >= 0.60 ? 'medium' : 'low';

        for (let i = 0; i < 5; i++) {
            const isActive = i < Math.ceil(pred.confidence * 5);
            signalBars += `<div class="signal-bar ${isActive ? 'active ' + confidenceLevel : ''}"></div>`;
        }
        signalBars += '</div>';

        html += `
            <tr>
                <td><small>${date}</small></td>
                <td>
                    <span class="direction-badge ${directionClass}">
                        ${directionIcon}${pred.direction}
                    </span>
                </td>
                <td><strong>${confidence}%</strong></td>
                <td>${probUp}%</td>
                <td>${probDown}%</td>
                <td>${signalBars}</td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

// Update predictions table with accuracy (RIGHT/WRONG indicators)
function updatePredictionsTableWithAccuracy(predictions) {
    const tbody = document.getElementById('predictions-tbody');

    if (predictions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">No predictions yet</td>
            </tr>
        `;
        return;
    }

    let html = '';
    let pendingCount = 0;  // Track pending predictions (1st = tomorrow, 2nd = today)

    predictions.forEach((pred, index) => {
        const date = new Date(pred.date).toLocaleString('en-US', { month: 'short', day: 'numeric' });
        const confidence = (pred.confidence * 100).toFixed(1);

        const predClass = pred.predicted === 'UP' ? 'up' : 'down';
        const predIcon = pred.predicted === 'UP' ? '<i class="fas fa-arrow-up me-1"></i>' : '<i class="fas fa-arrow-down me-1"></i>';

        // Check if this is a PENDING prediction (for next day)
        if (pred.is_pending) {
            pendingCount++;

            // PENDING PREDICTION - Special styling for next day's prediction
            const predictedDate = new Date(pred.date);
            const formattedDate = predictedDate.toLocaleDateString('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });

            // Calculate predicted movement percentage
            const predictedMovement = pred.predicted_movement || 0;
            const movementClass = predictedMovement >= 0 ? 'text-success' : 'text-danger';
            const movementSign = predictedMovement >= 0 ? '+' : '';
            const movementDisplay = `${movementSign}${predictedMovement.toFixed(2)}%`;

            // Determine badge text (1st pending = tomorrow, 2nd pending = today)
            const badgeText = pendingCount === 1 ? 'FOR TOMORROW' : 'FOR TODAY';
            const badgeIcon = pendingCount === 1 ? 'fa-calendar-plus' : 'fa-calendar-day';

            html += `
                <tr class="pending-prediction-row">
                    <td>
                        <div class="fw-bold text-primary" style="font-size: 0.95rem;">${formattedDate}</div>
                        <span class="badge bg-primary bg-opacity-10 text-primary" style="font-size: 0.7rem;">
                            <i class="fas ${badgeIcon} me-1"></i>${badgeText}
                        </span>
                    </td>
                    <td>
                        <span class="direction-badge ${predClass} pulse-animation">
                            ${predIcon}${pred.predicted}
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-warning text-dark">
                            <i class="fas fa-hourglass-half me-1"></i>PENDING
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-secondary">
                            <i class="fas fa-minus me-1"></i>AWAITING
                        </span>
                    </td>
                    <td><strong class="text-primary">${confidence}%</strong></td>
                    <td class="${movementClass} fw-bold" style="font-size: 1.1rem;">
                        ${movementDisplay}
                    </td>
                </tr>
            `;
        } else {
            // COMPLETED PREDICTION with actual results
            const actualClass = pred.actual === 'UP' ? 'up' : 'down';
            const actualIcon = pred.actual === 'UP' ? '<i class="fas fa-arrow-up me-1"></i>' : '<i class="fas fa-arrow-down me-1"></i>';

            // Result badge (RIGHT/WRONG)
            const resultBadge = pred.is_correct ?
                '<span class="badge bg-success"><i class="fas fa-check me-1"></i>RIGHT</span>' :
                '<span class="badge bg-danger"><i class="fas fa-times me-1"></i>WRONG</span>';

            // Actual return
            const returnValue = pred.actual_return.toFixed(2);
            const returnClass = pred.actual_return >= 0 ? 'text-success' : 'text-danger';
            const returnSign = pred.actual_return >= 0 ? '+' : '';

            html += `
                <tr>
                    <td><small>${date}</small></td>
                    <td>
                        <span class="direction-badge ${predClass}">
                            ${predIcon}${pred.predicted}
                        </span>
                    </td>
                    <td>
                        <span class="direction-badge ${actualClass}">
                            ${actualIcon}${pred.actual}
                        </span>
                    </td>
                    <td>${resultBadge}</td>
                    <td><strong>${confidence}%</strong></td>
                    <td class="${returnClass}"><strong>${returnSign}${returnValue}%</strong></td>
                </tr>
            `;
        }
    });

    tbody.innerHTML = html;
}

// Load market status
async function loadMarketStatus() {
    // Show loading state
    const loadingDiv = document.getElementById('market-loading');
    const contentDiv = document.getElementById('market-content');
    const errorDiv = document.getElementById('market-error');

    if (loadingDiv) loadingDiv.style.display = 'block';
    if (contentDiv) contentDiv.style.display = 'none';
    if (errorDiv) errorDiv.style.display = 'none';

    try {
        const response = await fetch('/api/market_status');
        const data = await response.json();

        if (data.success && data.market) {
            const m = data.market;

            // Format price with thousand separators
            const formattedPrice = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(m.current_price);

            document.getElementById('current-price').textContent = formattedPrice;

            // Format date - show "Today" if it's today's date
            const marketDate = new Date(m.date);
            const today = new Date();
            const isToday = marketDate.toDateString() === today.toDateString();
            const dateText = isToday ? 'Today' : marketDate.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
            document.getElementById('market-date').textContent = dateText;

            // Format change percentage
            const changeElement = document.getElementById('price-change');
            const changePct = Math.abs(m.change_pct).toFixed(2);
            const changeClass = m.change >= 0 ? 'bg-success' : 'bg-danger';
            const changeIcon = m.change >= 0 ? '<i class="fas fa-arrow-up me-1"></i>' : '<i class="fas fa-arrow-down me-1"></i>';
            const changeSign = m.change >= 0 ? '+' : '-';

            changeElement.innerHTML = `
                <span class="badge ${changeClass}">
                    ${changeIcon}${changeSign}${changePct}%
                </span>
            `;

            // Add animated effect to price on update
            const priceElement = document.getElementById('current-price');
            priceElement.classList.add('price-update-animation');
            setTimeout(() => {
                priceElement.classList.remove('price-update-animation');
            }, 600);

            // Show content, hide loading
            if (loadingDiv) loadingDiv.style.display = 'none';
            if (contentDiv) contentDiv.style.display = 'flex';
            if (errorDiv) errorDiv.style.display = 'none';

        } else {
            throw new Error(data.error || 'Failed to load market data');
        }
    } catch (error) {
        console.error('Error loading market status:', error);

        // Show error state
        if (loadingDiv) loadingDiv.style.display = 'none';
        if (contentDiv) contentDiv.style.display = 'none';
        if (errorDiv) {
            errorDiv.style.display = 'block';
            const errorTextElement = document.getElementById('market-error-text');
            if (errorTextElement) {
                errorTextElement.textContent = error.message || 'Failed to load market data. Please try again.';
            }
        }
    }
}

// Run prediction
async function runPrediction() {
    const btn = document.getElementById('predict-btn');
    const originalText = btn.innerHTML;

    // Show loading state
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Predicting...';

    try {
        const response = await fetch('/api/run_prediction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            // Show success message
            btn.innerHTML = '<i class="fas fa-check me-2"></i>Success!';
            btn.className = 'btn btn-success btn-lg me-2';

            // Reload all data
            setTimeout(async () => {
                await loadAllData();
                btn.innerHTML = originalText;
                btn.className = 'btn btn-primary btn-lg me-2';
                btn.disabled = false;
            }, 2000);
        } else {
            // Show error
            alert('Error: ' + (data.error || 'Failed to generate prediction'));
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    } catch (error) {
        console.error('Error running prediction:', error);
        alert('Error running prediction. Check console for details.');
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Export PDF Report
function exportPDF() {
    // Open PDF export endpoint in new tab (will trigger download)
    window.open('/api/export_pdf', '_blank');
}

// Load Feature Importance
async function loadFeatureImportance() {
    try {
        const response = await fetch('/api/feature_importance');
        const data = await response.json();

        if (data.success && data.data) {
            const features = data.data.features;
            const importance = data.data.importance;

            // Create chart
            const ctx = document.getElementById('featureImportanceChart');
            if (ctx) {
                // Destroy existing chart
                if (featureImportanceChart) {
                    featureImportanceChart.destroy();
                }

                featureImportanceChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: features,
                        datasets: [{
                            label: 'Importance Score',
                            data: importance,
                            backgroundColor: 'rgba(255, 193, 7, 0.7)',
                            borderColor: 'rgba(255, 193, 7, 1)',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return 'Importance: ' + context.parsed.x.toFixed(4);
                                    }
                                }
                            }
                        },
                        scales: {
                            x: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Importance Score'
                                }
                            }
                        }
                    }
                });
            }
        }
    } catch (error) {
        console.error('Error loading feature importance:', error);
    }
}

// Load Trading Simulation
async function loadTradingSimulation() {
    // Add loading state
    const metricBoxes = document.querySelectorAll('.metric-box');
    metricBoxes.forEach(box => box.classList.add('loading'));

    try {
        const response = await fetch('/api/trading_simulation');
        const data = await response.json();

        if (data.success && data.simulation) {
            const sim = data.simulation;

            // Remove loading state
            metricBoxes.forEach(box => box.classList.remove('loading'));

            // Update metrics with animations
            updateMetricWithAnimation('sim-initial-capital', '$' + sim.initial_capital.toLocaleString());
            updateMetricWithAnimation('sim-final-capital', '$' + sim.final_capital.toFixed(0).toLocaleString());

            const returnClass = sim.total_return >= 0 ? 'text-success' : 'text-danger';
            const returnSign = sim.total_return >= 0 ? '+' : '';
            const returnElement = document.getElementById('sim-total-return');
            updateMetricWithAnimation('sim-total-return', returnSign + sim.total_return.toFixed(2) + '%');
            returnElement.className = 'metric-value h5 fw-bold mb-0 ' + returnClass;

            updateMetricWithAnimation('sim-win-rate', sim.win_rate.toFixed(1) + '%');

            // Performance comparison
            updateMetricWithAnimation('sim-model-return', (sim.total_return >= 0 ? '+' : '') + sim.total_return.toFixed(2) + '%');
            updateMetricWithAnimation('sim-buyhold-return', (sim.buy_hold_return >= 0 ? '+' : '') + sim.buy_hold_return.toFixed(2) + '%');

            const outperformClass = sim.outperformance >= 0 ? 'text-success' : 'text-danger';
            const outperformElement = document.getElementById('sim-outperformance');
            updateMetricWithAnimation('sim-outperformance', (sim.outperformance >= 0 ? '+' : '') + sim.outperformance.toFixed(2) + 'pp');
            outperformElement.className = 'fw-bold ' + outperformClass;

            // Capital growth chart
            const ctx = document.getElementById('capitalGrowthChart');
            if (ctx) {
                // Destroy existing chart
                if (capitalGrowthChart) {
                    capitalGrowthChart.destroy();
                }

                // Enhanced chart configuration
                capitalGrowthChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: sim.dates,
                        datasets: [{
                            label: 'Capital Growth',
                            data: sim.capital_history,
                            borderColor: sim.total_return >= 0 ? 'rgba(16, 185, 129, 1)' : 'rgba(239, 68, 68, 1)',
                            backgroundColor: sim.total_return >= 0 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4,
                            pointRadius: 0,
                            pointHoverRadius: 6,
                            pointHoverBackgroundColor: sim.total_return >= 0 ? 'rgba(16, 185, 129, 1)' : 'rgba(239, 68, 68, 1)',
                            pointHoverBorderColor: '#fff',
                            pointHoverBorderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        interaction: {
                            mode: 'index',
                            intersect: false
                        },
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                enabled: true,
                                backgroundColor: 'rgba(0, 0, 0, 0.9)',
                                titleColor: '#fff',
                                bodyColor: '#fff',
                                borderColor: sim.total_return >= 0 ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)',
                                borderWidth: 2,
                                padding: 12,
                                displayColors: false,
                                callbacks: {
                                    title: function(context) {
                                        return '📅 ' + context[0].label;
                                    },
                                    label: function(context) {
                                        const capital = context.parsed.y;
                                        const initialCapital = sim.initial_capital;
                                        const gainLoss = capital - initialCapital;
                                        const gainLossPct = ((gainLoss / initialCapital) * 100).toFixed(2);
                                        const sign = gainLoss >= 0 ? '+' : '';
                                        return [
                                            '💰 Capital: $' + capital.toFixed(0).toLocaleString(),
                                            '📊 P&L: ' + sign + '$' + gainLoss.toFixed(0).toLocaleString() + ' (' + sign + gainLossPct + '%)'
                                        ];
                                    }
                                }
                            }
                        },
                        scales: {
                            x: {
                                display: false,
                                grid: {
                                    display: false
                                }
                            },
                            y: {
                                beginAtZero: false,
                                grid: {
                                    color: 'rgba(0, 0, 0, 0.05)',
                                    drawBorder: false
                                },
                                ticks: {
                                    callback: function(value) {
                                        return '$' + value.toFixed(0).toLocaleString();
                                    },
                                    font: {
                                        size: 11,
                                        family: 'Inter'
                                    },
                                    color: '#6b7280'
                                },
                                title: {
                                    display: true,
                                    text: 'Capital ($)',
                                    font: {
                                        size: 12,
                                        family: 'Inter',
                                        weight: '600'
                                    },
                                    color: '#374151'
                                }
                            }
                        },
                        animation: {
                            duration: 1000,
                            easing: 'easeInOutQuart'
                        }
                    }
                });
            }

            console.log('Trading simulation loaded successfully');
        } else {
            throw new Error(data.message || 'Failed to load trading simulation data');
        }
    } catch (error) {
        console.error('Error loading trading simulation:', error);

        // Remove loading state
        metricBoxes.forEach(box => box.classList.remove('loading'));

        // Show error state (optional - could add error UI here)
        document.getElementById('sim-final-capital').textContent = 'Error';
        document.getElementById('sim-total-return').textContent = 'N/A';
        document.getElementById('sim-win-rate').textContent = 'N/A';
    }
}

// Helper function to animate metric updates
function updateMetricWithAnimation(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.transition = 'all 0.3s ease';
        element.style.transform = 'scale(1.1)';
        element.textContent = value;

        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 300);
    }
}

// Load Rolling Accuracy
async function loadRollingAccuracy() {
    try {
        const response = await fetch('/api/rolling_accuracy');
        const data = await response.json();

        if (data.success && data.accuracy) {
            const acc = data.accuracy;

            // Update overall accuracy
            document.getElementById('rolling-overall-accuracy').textContent = acc.overall_accuracy.toFixed(1) + '%';

            // Update 7-day rolling
            if (acc.rolling_7d && acc.rolling_7d.current > 0) {
                document.getElementById('rolling-7d-value').textContent = acc.rolling_7d.current.toFixed(1) + '%';
                document.getElementById('rolling-7d-bar').style.width = acc.rolling_7d.current + '%';
            } else {
                document.getElementById('rolling-7d-value').textContent = 'N/A';
                document.getElementById('rolling-7d-bar').style.width = '0%';
            }

            // Update 30-day rolling
            if (acc.rolling_30d && acc.rolling_30d.current > 0) {
                document.getElementById('rolling-30d-value').textContent = acc.rolling_30d.current.toFixed(1) + '%';
                document.getElementById('rolling-30d-bar').style.width = acc.rolling_30d.current + '%';
            } else {
                document.getElementById('rolling-30d-value').textContent = 'N/A';
                document.getElementById('rolling-30d-bar').style.width = '0%';
            }

            // Update 90-day rolling
            if (acc.rolling_90d && acc.rolling_90d.current > 0) {
                document.getElementById('rolling-90d-value').textContent = acc.rolling_90d.current.toFixed(1) + '%';
                document.getElementById('rolling-90d-bar').style.width = acc.rolling_90d.current + '%';
            } else {
                document.getElementById('rolling-90d-value').textContent = 'N/A';
                document.getElementById('rolling-90d-bar').style.width = '0%';
            }
        }
    } catch (error) {
        console.error('Error loading rolling accuracy:', error);
    }
}

// Load Economic Indicators
async function loadEconomicIndicators() {
    // Show loading state
    const loadingDiv = document.getElementById('indicators-loading');
    const contentDiv = document.getElementById('indicators-content');
    const errorDiv = document.getElementById('indicators-error');

    if (loadingDiv) loadingDiv.style.display = 'block';
    if (contentDiv) contentDiv.style.display = 'none';
    if (errorDiv) errorDiv.style.display = 'none';

    try {
        const response = await fetch('/api/economic_indicators');
        const data = await response.json();

        if (data.success && data.indicators) {
            const ind = data.indicators;

            // Helper function to format change indicator
            function formatChange(change, value) {
                const icon = change > 0 ? 'fa-arrow-up' : change < 0 ? 'fa-arrow-down' : 'fa-minus';
                const colorClass = change > 0 ? 'text-success' : change < 0 ? 'text-danger' : 'text-muted';
                const sign = change > 0 ? '+' : '';
                const displayChange = Math.abs(change).toFixed(2);
                return `<i class="fas ${icon} ${colorClass}"></i> <span class="${colorClass}">${sign}${displayChange}</span>`;
            }

            // Helper function to add pulse animation
            function addPulseAnimation(elementId) {
                const element = document.getElementById(elementId);
                if (element) {
                    element.classList.add('indicator-update-pulse');
                    setTimeout(() => {
                        element.classList.remove('indicator-update-pulse');
                    }, 600);
                }
            }

            // Fed Funds Rate
            const fedRate = ind.fed_funds_rate.value.toFixed(2) + '%';
            document.getElementById('ind-fed-rate').textContent = fedRate;
            document.getElementById('ind-fed-change').innerHTML = formatChange(ind.fed_funds_rate.change, ind.fed_funds_rate.value);
            addPulseAnimation('ind-fed-rate');

            // Unemployment
            const unemployment = ind.unemployment_rate.value.toFixed(2) + '%';
            document.getElementById('ind-unemployment').textContent = unemployment;
            document.getElementById('ind-unemployment-change').innerHTML = formatChange(ind.unemployment_rate.change, ind.unemployment_rate.value);
            addPulseAnimation('ind-unemployment');

            // CPI
            const cpi = ind.cpi.value.toFixed(2);
            document.getElementById('ind-cpi').textContent = cpi;
            document.getElementById('ind-cpi-change').innerHTML = formatChange(ind.cpi.change, ind.cpi.value);
            addPulseAnimation('ind-cpi');

            // VIX
            const vix = ind.vix.value.toFixed(2);
            document.getElementById('ind-vix').textContent = vix;
            document.getElementById('ind-vix-change').innerHTML = formatChange(ind.vix.change, ind.vix.value);
            addPulseAnimation('ind-vix');

            // 10Y Treasury
            const treasury = ind.treasury_10y.value.toFixed(2) + '%';
            document.getElementById('ind-treasury').textContent = treasury;
            document.getElementById('ind-treasury-change').innerHTML = formatChange(ind.treasury_10y.change, ind.treasury_10y.value);
            addPulseAnimation('ind-treasury');

            // Yield Curve
            const yieldCurve = ind.yield_curve.value.toFixed(2);
            document.getElementById('ind-yield').textContent = yieldCurve;
            document.getElementById('ind-yield-change').innerHTML = formatChange(ind.yield_curve.change, ind.yield_curve.value);
            addPulseAnimation('ind-yield');

            // Initialize Bootstrap tooltips
            const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            tooltipTriggerList.forEach(tooltipTriggerEl => {
                new bootstrap.Tooltip(tooltipTriggerEl);
            });

            // Show content, hide loading
            if (loadingDiv) loadingDiv.style.display = 'none';
            if (contentDiv) contentDiv.style.display = 'flex';
            if (errorDiv) errorDiv.style.display = 'none';

        } else {
            throw new Error(data.message || 'Failed to load indicators');
        }
    } catch (error) {
        console.error('Error loading economic indicators:', error);

        // Show error state
        if (loadingDiv) loadingDiv.style.display = 'none';
        if (contentDiv) contentDiv.style.display = 'none';
        if (errorDiv) {
            errorDiv.style.display = 'block';
            const errorTextElement = document.getElementById('indicators-error-text');
            if (errorTextElement) {
                errorTextElement.textContent = error.message || 'Failed to load economic indicators. Please try again.';
            }
        }
    }
}

// Load Technical Indicators Chart
async function loadTechnicalIndicators() {
    try {
        const response = await fetch('/api/technical_indicators');
        const data = await response.json();

        if (data.success && data.data) {
            const techData = data.data;

            const ctx = document.getElementById('technicalChart');
            if (ctx) {
                // Destroy existing chart
                if (technicalChart) {
                    technicalChart.destroy();
                }

                technicalChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: techData.dates,
                        datasets: [
                            {
                                label: 'S&P 500 Close',
                                data: techData.close,
                                borderColor: 'rgba(75, 192, 192, 1)',
                                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                                borderWidth: 2,
                                fill: true,
                                tension: 0.3,
                                yAxisID: 'y'
                            },
                            {
                                label: 'SMA 20',
                                data: techData.sma_20,
                                borderColor: 'rgba(255, 159, 64, 1)',
                                borderWidth: 1.5,
                                fill: false,
                                tension: 0.3,
                                yAxisID: 'y'
                            },
                            {
                                label: 'SMA 50',
                                data: techData.sma_50,
                                borderColor: 'rgba(153, 102, 255, 1)',
                                borderWidth: 1.5,
                                fill: false,
                                tension: 0.3,
                                yAxisID: 'y'
                            },
                            {
                                label: 'BB Upper',
                                data: techData.bb_upper,
                                borderColor: 'rgba(220, 53, 69, 0.5)',
                                borderWidth: 1,
                                borderDash: [5, 5],
                                fill: false,
                                yAxisID: 'y'
                            },
                            {
                                label: 'BB Lower',
                                data: techData.bb_lower,
                                borderColor: 'rgba(220, 53, 69, 0.5)',
                                borderWidth: 1,
                                borderDash: [5, 5],
                                fill: false,
                                yAxisID: 'y'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        interaction: {
                            mode: 'index',
                            intersect: false
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top'
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return context.dataset.label + ': $' + context.parsed.y.toFixed(2);
                                    }
                                }
                            }
                        },
                        scales: {
                            x: {
                                display: true,
                                ticks: {
                                    maxTicksLimit: 10
                                }
                            },
                            y: {
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {
                                    display: true,
                                    text: 'Price ($)'
                                },
                                ticks: {
                                    callback: function(value) {
                                        return '$' + value.toFixed(0);
                                    }
                                }
                            }
                        }
                    }
                });
            }
        }
    } catch (error) {
        console.error('Error loading technical indicators:', error);
    }
}

// Load Recent News
async function loadRecentNews() {
    try {
        const response = await fetch('/api/recent_news');
        const data = await response.json();

        const newsFeed = document.getElementById('news-feed');
        if (!newsFeed) return;

        if (data.success && data.news && data.news.length > 0) {
            let html = '';

            data.news.forEach(item => {
                html += `
                    <div class="news-item p-3 mb-2 border-start border-${item.sentiment_class} border-3 bg-light rounded">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge bg-${item.sentiment_class}">${item.sentiment_label}</span>
                            <small class="text-muted">${item.date}</small>
                        </div>
                        <div class="fw-semibold small mb-1">${item.headline}</div>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">Sentiment Score: ${item.sentiment_score.toFixed(3)}</small>
                            <small class="text-muted"><i class="fas fa-newspaper me-1"></i>${item.news_count} articles</small>
                        </div>
                    </div>
                `;
            });

            newsFeed.innerHTML = html;
        } else {
            newsFeed.innerHTML = '<div class="text-center text-muted py-4">No news data available</div>';
        }
    } catch (error) {
        console.error('Error loading recent news:', error);
        const newsFeed = document.getElementById('news-feed');
        if (newsFeed) {
            newsFeed.innerHTML = '<div class="text-center text-danger py-4">Error loading news</div>';
        }
    }
}

// Load Confusion Matrix
async function loadConfusionMatrix() {
    try {
        const response = await fetch('/api/confusion_matrix');
        const data = await response.json();

        if (data.success && data.matrix) {
            const m = data.matrix;

            // Update confusion matrix cells
            document.getElementById('cm-tp').textContent = m.true_positives;
            document.getElementById('cm-fp').textContent = m.false_positives;
            document.getElementById('cm-fn').textContent = m.false_negatives;
            document.getElementById('cm-tn').textContent = m.true_negatives;

            // Update metrics
            document.getElementById('cm-precision').textContent = m.precision.toFixed(1) + '%';
            document.getElementById('cm-recall').textContent = m.recall.toFixed(1) + '%';
            document.getElementById('cm-f1').textContent = m.f1_score.toFixed(1) + '%';
            document.getElementById('cm-accuracy').textContent = m.accuracy.toFixed(1) + '%';
        }
    } catch (error) {
        console.error('Error loading confusion matrix:', error);
    }
}

// Load Risk Metrics
async function loadRiskMetrics() {
    try {
        const response = await fetch('/api/risk_metrics');
        const data = await response.json();

        if (data.success && data.metrics) {
            const m = data.metrics;

            // Update risk metrics
            document.getElementById('risk-drawdown').textContent = m.max_drawdown.toFixed(2) + '%';
            document.getElementById('risk-sharpe').textContent = m.sharpe_ratio.toFixed(2);
            document.getElementById('risk-win-streak').textContent = m.max_win_streak;
            document.getElementById('risk-loss-streak').textContent = m.max_loss_streak;

            // Current streak
            const streakType = m.current_streak_type === 'win' ? 'Wins' : 'Losses';
            const streakClass = m.current_streak_type === 'win' ? 'text-success' : 'text-danger';
            document.getElementById('risk-current-streak').textContent = m.current_streak_count + ' ' + streakType;
            document.getElementById('risk-current-streak').className = 'h4 fw-bold mb-0 ' + streakClass;

            // Average returns
            document.getElementById('risk-avg-win').textContent = '+' + m.avg_win_return.toFixed(2) + '%';
            document.getElementById('risk-avg-loss').textContent = m.avg_loss_return.toFixed(2) + '%';
        }
    } catch (error) {
        console.error('Error loading risk metrics:', error);
    }
}

// Load Best & Worst Predictions
async function loadBestWorstPredictions() {
    try {
        const response = await fetch('/api/best_worst_predictions');
        const data = await response.json();

        if (data.success) {
            // Best predictions
            const bestList = document.getElementById('best-predictions-list');
            if (bestList && data.best && data.best.length > 0) {
                let html = '';
                data.best.forEach((pred, index) => {
                    const returnSign = pred.actual_return >= 0 ? '+' : '';
                    html += `
                        <div class="prediction-item p-3 mb-2 bg-success bg-opacity-10 rounded border-start border-success border-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="badge bg-success">#${index + 1} Best</span>
                                <small class="text-muted">${pred.date}</small>
                            </div>
                            <div class="row g-2">
                                <div class="col-6">
                                    <small class="text-muted">Predicted:</small>
                                    <div class="fw-bold text-success">${pred.predicted}</div>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Actual:</small>
                                    <div class="fw-bold">${pred.actual}</div>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Confidence:</small>
                                    <div class="fw-bold">${(pred.confidence * 100).toFixed(1)}%</div>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Return:</small>
                                    <div class="fw-bold text-success">${returnSign}${pred.actual_return.toFixed(2)}%</div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                bestList.innerHTML = html;
            } else if (bestList) {
                bestList.innerHTML = '<div class="text-center text-muted py-4">No data available</div>';
            }

            // Worst predictions
            const worstList = document.getElementById('worst-predictions-list');
            if (worstList && data.worst && data.worst.length > 0) {
                let html = '';
                data.worst.forEach((pred, index) => {
                    const returnSign = pred.actual_return >= 0 ? '+' : '';
                    html += `
                        <div class="prediction-item p-3 mb-2 bg-danger bg-opacity-10 rounded border-start border-danger border-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="badge bg-danger">#${index + 1} Worst</span>
                                <small class="text-muted">${pred.date}</small>
                            </div>
                            <div class="row g-2">
                                <div class="col-6">
                                    <small class="text-muted">Predicted:</small>
                                    <div class="fw-bold text-danger">${pred.predicted}</div>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Actual:</small>
                                    <div class="fw-bold">${pred.actual}</div>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Confidence:</small>
                                    <div class="fw-bold">${(pred.confidence * 100).toFixed(1)}%</div>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Return:</small>
                                    <div class="fw-bold">${returnSign}${pred.actual_return.toFixed(2)}%</div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                worstList.innerHTML = html;
            } else if (worstList) {
                worstList.innerHTML = '<div class="text-center text-muted py-4">No data available</div>';
            }
        }
    } catch (error) {
        console.error('Error loading best/worst predictions:', error);
    }
}

// Load AI Explanation
async function loadAIExplanation() {
    try {
        const response = await fetch('/api/ai_explanation');
        const data = await response.json();

        const contentDiv = document.getElementById('ai-explanation-content');
        if (!contentDiv) return;

        if (data.success && data.features && data.features.length > 0) {
            let html = '<div class="explanation-features">';

            data.features.forEach((feature, index) => {
                const absContribution = Math.abs(feature.contribution);
                const maxContribution = Math.abs(data.features[0].contribution); // First is largest
                const barWidth = (absContribution / maxContribution) * 100;

                const isBullish = feature.direction === 'bullish';
                const barColor = isBullish ? 'success' : 'danger';
                const icon = isBullish ? 'fa-arrow-up' : 'fa-arrow-down';
                const textClass = isBullish ? 'text-success' : 'text-danger';

                html += `
                    <div class="mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <div class="d-flex align-items-center">
                                <span class="badge bg-${barColor} me-2">${index + 1}</span>
                                <span class="small fw-semibold">${feature.feature}</span>
                            </div>
                            <span class="${textClass} small fw-bold">
                                <i class="fas ${icon} me-1"></i>
                                ${isBullish ? 'Bullish' : 'Bearish'}
                            </span>
                        </div>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-${barColor}"
                                 role="progressbar"
                                 style="width: ${barWidth}%"
                                 aria-valuenow="${barWidth}"
                                 aria-valuemin="0"
                                 aria-valuemax="100">
                                <small>${feature.importance.toFixed(4)}</small>
                            </div>
                        </div>
                        <div class="small text-muted mt-1">
                            Value: ${feature.value.toFixed(4)} | Impact: ${feature.contribution.toFixed(6)}
                        </div>
                    </div>
                `;
            });

            html += '</div>';

            // Add prediction summary
            html += `
                <div class="alert alert-${data.prediction === 'UP' ? 'success' : 'danger'} mt-3 mb-0">
                    <i class="fas fa-${data.prediction === 'UP' ? 'arrow-up' : 'arrow-down'} me-2"></i>
                    <strong>Overall Prediction: ${data.prediction}</strong>
                    <div class="small mt-1">
                        These are the top 10 features driving the model's ${data.prediction} prediction
                    </div>
                </div>
            `;

            contentDiv.innerHTML = html;
        } else {
            contentDiv.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    ${data.message || 'No explanation data available'}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading AI explanation:', error);
        const contentDiv = document.getElementById('ai-explanation-content');
        if (contentDiv) {
            contentDiv.innerHTML = `
                <div class="text-center text-danger py-4">
                    <i class="fas fa-times-circle me-2"></i>
                    Error loading explanation
                </div>
            `;
        }
    }
}

// Load Candlestick Chart
async function loadCandlestickChart(days = 90) {
    const chartElement = document.querySelector("#candlestickChart");
    const loadingDiv = document.getElementById('candlestick-loading');
    const errorDiv = document.getElementById('candlestick-error');

    // Safety check - ensure element exists
    if (!chartElement) {
        console.error('Chart element not found');
        return;
    }

    try {
        const response = await fetch(`/api/candlestick_data?days=${days}`);
        const data = await response.json();

        if (data.success && data.candlestick && data.candlestick.length > 0) {
            // Convert candlestick data to line data (use closing prices)
            const lineData = data.candlestick.map(candle => ({
                x: candle.x,
                y: candle.y[3]  // y[3] is the closing price in candlestick format
            }));

            // Calculate dynamic height based on screen size
            const chartHeight = window.innerWidth < 768 ? 350 : window.innerWidth < 992 ? 400 : 450;

            const options = {
                series: [{
                    name: 'S&P 500 Close',
                    data: lineData
                }],
                chart: {
                    type: 'line',
                    height: chartHeight,
                    toolbar: {
                        show: true,
                        tools: {
                            download: true,
                            selection: true,
                            zoom: true,
                            zoomin: true,
                            zoomout: true,
                            pan: true,
                            reset: true
                        },
                        autoSelected: 'zoom'
                    },
                    animations: {
                        enabled: true,
                        speed: 800,
                        animateGradually: {
                            enabled: true,
                            delay: 150
                        }
                    },
                    zoom: {
                        enabled: true,
                        type: 'x',
                        autoScaleYaxis: true
                    }
                },
                colors: ['#667eea'],
                stroke: {
                    width: 3,
                    curve: 'smooth'
                },
                fill: {
                    type: 'gradient',
                    gradient: {
                        shade: 'light',
                        type: 'vertical',
                        shadeIntensity: 0.5,
                        gradientToColors: ['#764ba2'],
                        inverseColors: false,
                        opacityFrom: 0.7,
                        opacityTo: 0.1,
                        stops: [0, 100]
                    }
                },
                markers: {
                    size: 0,
                    hover: {
                        size: 7,
                        sizeOffset: 3
                    }
                },
                title: {
                    text: `S&P 500 Price Movement (Last ${days} Days)`,
                    align: 'left',
                    style: {
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#6c757d'
                    }
                },
                xaxis: {
                    type: 'datetime',
                    labels: {
                        datetimeUTC: false,
                        style: {
                            fontSize: '11px'
                        }
                    }
                },
                yaxis: {
                    tooltip: {
                        enabled: true
                    },
                    labels: {
                        formatter: function(value) {
                            return '$' + value.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                        },
                        style: {
                            fontSize: '11px'
                        }
                    }
                },
                grid: {
                    borderColor: '#e0e0e0',
                    strokeDashArray: 4,
                    xaxis: {
                        lines: {
                            show: true
                        }
                    },
                    yaxis: {
                        lines: {
                            show: true
                        }
                    }
                },
                tooltip: {
                    enabled: true,
                    theme: 'light',
                    x: {
                        format: 'MMM dd, yyyy'
                    },
                    y: {
                        formatter: function(value) {
                            return '$' + value.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                        }
                    },
                    marker: {
                        show: true
                    }
                },
                responsive: [{
                    breakpoint: 768,
                    options: {
                        chart: {
                            height: 350
                        },
                        title: {
                            style: {
                                fontSize: '12px'
                            }
                        }
                    }
                }]
            };

            // Destroy existing chart
            if (candlestickChart) {
                try {
                    candlestickChart.destroy();
                } catch (e) {
                    console.warn('Error destroying chart:', e);
                }
            }

            // Render new chart
            candlestickChart = new ApexCharts(chartElement, options);

            // Handle render promise
            candlestickChart.render().then(() => {
                // Hide loading after successful render
                if (loadingDiv) loadingDiv.style.display = 'none';
                console.log(`Line chart loaded: ${days} days`);
            }).catch(err => {
                console.error('Chart render error:', err);
                if (loadingDiv) loadingDiv.style.display = 'none';
                if (errorDiv) errorDiv.style.display = 'block';
            });

        } else {
            throw new Error('No data available');
        }
    } catch (error) {
        console.error('Error loading chart:', error);
        if (loadingDiv) loadingDiv.style.display = 'none';
        if (errorDiv) errorDiv.style.display = 'block';
    }
}

// Update candlestick period
function updateCandlestickPeriod(days) {
    currentCandlestickPeriod = days;

    // Update button states
    const buttons = document.querySelectorAll('.period-selector button');
    buttons.forEach(btn => {
        btn.classList.remove('active');
        const btnPeriod = parseInt(btn.getAttribute('data-period'));
        if (btnPeriod === days) {
            btn.classList.add('active');
        }
    });

    // Reload chart with new period
    loadCandlestickChart(days);
}

// Load Economic Calendar
async function loadEconomicCalendar() {
    try {
        const response = await fetch('/api/economic_calendar');
        const data = await response.json();

        const calendarDiv = document.getElementById('economic-calendar');
        if (!calendarDiv) return;

        if (data.success && data.events && data.events.length > 0) {
            let html = '';

            data.events.forEach(event => {
                // Determine border color based on impact
                const borderClass = event.impact_class;

                html += `
                    <div class="event-item p-3 mb-2 border-start border-3 border-${borderClass} bg-light rounded">
                        <div class="d-flex justify-content-between align-items-start mb-1">
                            <strong class="small">${event.title}</strong>
                            <span class="badge bg-${borderClass}">${event.impact} Impact</span>
                        </div>
                        <div class="small text-muted">${event.date} - ${event.time}</div>
                        <div class="small mt-1">${event.description}</div>
                    </div>
                `;
            });

            calendarDiv.innerHTML = html;
        } else {
            calendarDiv.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-calendar-times me-2"></i>
                    No upcoming events
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading economic calendar:', error);
        const calendarDiv = document.getElementById('economic-calendar');
        if (calendarDiv) {
            calendarDiv.innerHTML = `
                <div class="text-center text-danger py-4">
                    <i class="fas fa-times-circle me-2"></i>
                    Error loading calendar
                </div>
            `;
        }
    }
}
