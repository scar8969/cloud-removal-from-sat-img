// app.js - Core logic for Cloud Removal Showcase

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const btnExample = document.getElementById('btnExample');
    const exampleSelect = document.getElementById('exampleSelect');
    const btnProcess = document.getElementById('btnProcess');
    const loading = document.getElementById('loading');
    const resultsPanel = document.getElementById('resultsPanel');
    const imgInput = document.getElementById('imgInput');
    const imgOutput = document.getElementById('imgOutput');
    const metricPsnr = document.getElementById('metricPsnr');
    const metricSsim = document.getElementById('metricSsim');
    const metricTime = document.getElementById('metricTime');
    const psnrBar = document.getElementById('psnrBar');
    const ssimBar = document.getElementById('ssimBar');
    const btnDownload = document.getElementById('btnDownload');
    const btnDownloadComp = document.getElementById('btnDownloadComp');

    let currentImage = null;
    let currentResult = null;

    // Load examples into select
    fetch('/api/examples')
        .then(r => r.json())
        .then(data => {
            if (data.examples) {
                data.examples.forEach(ex => {
                    const opt = document.createElement('option');
                    opt.value = ex.id;
                    opt.textContent = `Example ${ex.id}`;
                    exampleSelect.appendChild(opt);
                });
            }
        });

    // Upload zone click
    uploadZone.addEventListener('click', () => fileInput.click());

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFile(file);
    });

    function handleFile(file) {
        currentImage = file;
        btnProcess.disabled = false;
        uploadZone.querySelector('.upload-text').textContent = file.name;
        uploadZone.querySelector('.upload-subtext').textContent = `${(file.size / 1024).toFixed(1)} KB`;
    }

    // Example button
    btnExample.addEventListener('click', () => {
        exampleSelect.focus();
    });

    exampleSelect.addEventListener('change', () => {
        if (exampleSelect.value) {
            currentImage = null;
            btnProcess.disabled = false;
        }
    });

    // Process button
    btnProcess.addEventListener('click', async () => {
        if (!currentImage && !exampleSelect.value) return;

        loading.classList.add('active');
        resultsPanel.style.display = 'none';

        const formData = new FormData();
        if (currentImage) {
            formData.append('image', currentImage);
        } else {
            // Load example image
            const exId = exampleSelect.value;
            const resp = await fetch(`/api/examples`);
            const data = await resp.json();
            const ex = data.examples.find(e => e.id === exId);
            if (ex) {
                const imgResp = await fetch(ex.cloudy_url);
                const blob = await imgResp.blob();
                formData.append('image', blob, 'example.png');
            }
        }

        try {
            const resp = await fetch('/api/infer', {
                method: 'POST',
                body: formData
            });
            const data = await resp.json();

            if (data.success) {
                displayResults(data);
            } else {
                alert('Error: ' + data.error);
            }
        } catch (err) {
            alert('Error: ' + err.message);
        } finally {
            loading.classList.remove('active');
        }
    });

    function displayResults(data) {
        currentResult = data;
        resultsPanel.style.display = 'block';

        // Set images
        imgInput.src = data.input_image;
        imgOutput.src = data.cleaned_image;

        // Set metrics
        metricPsnr.textContent = data.metrics.psnr.toFixed(2) + ' dB';
        metricSsim.textContent = data.metrics.ssim.toFixed(4);
        metricTime.textContent = data.metrics.processing_time_ms.toFixed(1) + 'ms';

        // Set metric bars
        const psnrPercent = Math.min(100, (data.metrics.psnr / 30) * 100);
        psnrBar.style.width = psnrPercent + '%';
        psnrBar.style.background = psnrPercent > 80 ? 'var(--success)' :
                                  psnrPercent > 60 ? 'var(--warning)' : 'var(--accent)';

        const ssimPercent = data.metrics.ssim * 100;
        ssimBar.style.width = ssimPercent + '%';
        ssimBar.style.background = ssimPercent > 80 ? 'var(--success)' :
                                  ssimPercent > 60 ? 'var(--warning)' : 'var(--accent)';

        // Initialize slider
        if (window.initSlider) window.initSlider();
    }

    // Download buttons
    btnDownload.addEventListener('click', () => {
        if (currentResult) {
            downloadBase64(currentResult.cleaned_image, 'cleaned.png');
        }
    });

    btnDownloadComp.addEventListener('click', () => {
        if (currentResult) {
            downloadBase64(currentResult.comparison_image, 'comparison.png');
        }
    });

    function downloadBase64(b64, filename) {
        const link = document.createElement('a');
        link.href = b64;
        link.download = filename;
        link.click();
    }

    // Navbar scroll effect
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Smooth scroll for CTA
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});
