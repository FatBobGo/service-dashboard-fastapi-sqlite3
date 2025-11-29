let chart;

async function fetchData(cardScheme = 'All', rejectCode = 'All') {
    const url = new URL('/api/transactions', window.location.origin);
    if (cardScheme !== 'All') {
        url.searchParams.append('card_scheme', cardScheme);
    }
    if (rejectCode !== 'All') {
        url.searchParams.append('reject_code', rejectCode);
    }

    const response = await fetch(url);
    const data = await response.json();
    return data;
}

async function fetchStats() {
    const response = await fetch('/api/stats');
    const stats = await response.json();

    document.getElementById('visaTotal').textContent = stats.visa.total;
    document.getElementById('visaApproved').textContent = stats.visa.approved;
    document.getElementById('mastercardTotal').textContent = stats.mastercard.total;
    document.getElementById('mastercardApproved').textContent = stats.mastercard.approved;
}

async function populateRejectCodes() {
    const response = await fetch('/api/reject_codes');
    const codes = await response.json();
    const select = document.getElementById('rejectCode');

    codes.forEach(item => {
        const option = document.createElement('option');
        option.value = item.code;
        option.textContent = `${item.code} - ${item.description}`;
        select.appendChild(option);
    });
}

function initChart(data) {
    const ctx = document.getElementById('transactionChart').getContext('2d');

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Transaction Count',
                data: data,
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                }
            },
            plugins: {
                zoom: {
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x',
                    },
                    pan: {
                        enabled: true,
                        mode: 'x',
                    }
                }
            }
        }
    });
}

async function updateChart() {
    const cardScheme = document.getElementById('cardScheme').value;
    const rejectCode = document.getElementById('rejectCode').value;
    const data = await fetchData(cardScheme, rejectCode);

    chart.data.datasets[0].data = data;
    chart.update();

    // Also update stats when chart updates (though stats are global, not filtered by time in this simple version)
    fetchStats();
}

document.addEventListener('DOMContentLoaded', async () => {
    await populateRejectCodes();
    const data = await fetchData();
    initChart(data);
    fetchStats();

    document.getElementById('cardScheme').addEventListener('change', updateChart);
    document.getElementById('rejectCode').addEventListener('change', updateChart);

    document.getElementById('resetZoom').addEventListener('click', () => {
        chart.resetZoom();
    });

    // Auto-refresh every 10 seconds
    setInterval(updateChart, 10000);
});
