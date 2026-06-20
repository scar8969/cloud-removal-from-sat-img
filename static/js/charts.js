// charts.js - Training metrics charts

document.addEventListener('DOMContentLoaded', () => {
    // Load metrics and render charts
    fetch('/api/metrics')
        .then(r => r.json())
        .then(data => {
            if (data.history) {
                renderCharts(data.history);
            }
        })
        .catch(err => console.log('No training metrics available yet'));

    function renderCharts(history) {
        const epochs = history.map((_, i) => i + 1);

        // Loss chart
        const lossCtx = document.getElementById('lossChart');
        if (lossCtx) {
            new Chart(lossCtx, {
                type: 'line',
                data: {
                    labels: epochs,
                    datasets: [
                        {
                            label: 'Training Loss',
                            data: history.map(h => h.train),
                            borderColor: '#00b4d8',
                            backgroundColor: 'rgba(0, 180, 216, 0.1)',
                            tension: 0.3,
                        },
                        {
                            label: 'Validation Loss',
                            data: history.map(h => h.val),
                            borderColor: '#ff6b6b',
                            backgroundColor: 'rgba(255, 107, 107, 0.1)',
                            tension: 0.3,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Loss over Epochs', color: '#ffffff' }
                    },
                    scales: {
                        y: { ticks: { color: '#8892b0' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                        x: { ticks: { color: '#8892b0' }, grid: { color: 'rgba(255,255,255,0.1)' } }
                    }
                }
            });
        }

        // PSNR chart
        const psnrCtx = document.getElementById('psnrChart');
        if (psnrCtx) {
            new Chart(psnrCtx, {
                type: 'line',
                data: {
                    labels: epochs,
                    datasets: [{
                        label: 'PSNR (dB)',
                        data: history.map(h => h.val_psnr),
                        borderColor: '#4ecdc4',
                        backgroundColor: 'rgba(78, 205, 196, 0.1)',
                        tension: 0.3,
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Validation PSNR', color: '#ffffff' }
                    },
                    scales: {
                        y: { ticks: { color: '#8892b0' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                        x: { ticks: { color: '#8892b0' }, grid: { color: 'rgba(255,255,255,0.1)' } }
                    }
                }
            });
        }

        // SSIM chart
        const ssimCtx = document.getElementById('ssimChart');
        if (ssimCtx) {
            new Chart(ssimCtx, {
                type: 'line',
                data: {
                    labels: epochs,
                    datasets: [{
                        label: 'SSIM',
                        data: history.map(h => h.val_ssim),
                        borderColor: '#ffe66d',
                        backgroundColor: 'rgba(255, 230, 109, 0.1)',
                        tension: 0.3,
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Validation SSIM', color: '#ffffff' }
                    },
                    scales: {
                        y: { ticks: { color: '#8892b0' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                        x: { ticks: { color: '#8892b0' }, grid: { color: 'rgba(255,255,255,0.1)' } }
                    }
                }
            });
        }
    }
});
