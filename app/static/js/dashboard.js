let chart;

async function fetchData(cardScheme = 'All') {
    const url = new URL('/api/transactions', window.location.origin);
    if (cardScheme !== 'All') {
        url.searchParams.append('card_scheme', cardScheme);
    }
    
    const response = await fetch(url);
    const data = await response.json();
    return data;
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
    const data = await fetchData(cardScheme);
    
    chart.data.datasets[0].data = data;
    chart.update();
}

document.addEventListener('DOMContentLoaded', async () => {
    const data = await fetchData();
    initChart(data);
    
    document.getElementById('cardScheme').addEventListener('change', updateChart);
    
    document.getElementById('resetZoom').addEventListener('click', () => {
        chart.resetZoom();
    });

    // Auto-refresh every 10 seconds
    setInterval(updateChart, 10000);
});
