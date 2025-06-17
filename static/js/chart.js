// Chart.js initialization for results visualization

document.addEventListener('DOMContentLoaded', function() {
    const chartElements = document.querySelectorAll('canvas');
    
    if (chartElements.length > 0 && typeof Chart !== 'undefined') {
        chartElements.forEach(chartElement => {
            const chartType = chartElement.id.replace('Chart', '').toLowerCase();
            const chartData = JSON.parse(chartElement.dataset.chart || '{}');
            
            new Chart(chartElement, {
                type: chartType,
                data: chartData,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }
                }
            });
        });
    }
});