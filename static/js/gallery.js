// gallery.js - Gallery logic

document.addEventListener('DOMContentLoaded', () => {
    const galleryGrid = document.getElementById('galleryGrid');
    if (!galleryGrid) return;

    // Load examples
    fetch('/api/examples')
        .then(r => r.json())
        .then(data => {
            if (data.examples) {
                renderGallery(data.examples);
            }
        });

    function renderGallery(examples) {
        galleryGrid.innerHTML = '';
        examples.forEach(ex => {
            const card = document.createElement('div');
            card.className = 'gallery-card';
            card.innerHTML = `
                <div class="comparison-slider" id="slider-${ex.id}">
                    <div class="comparison-before">
                        <img src="${ex.cloudy_url}" alt="Cloudy ${ex.id}">
                        <div class="comparison-label">Cloudy</div>
                    </div>
                    <div class="comparison-after">
                        <img src="${ex.cleaned_url}" alt="Cleaned ${ex.id}">
                        <div class="comparison-label">Cleaned</div>
                    </div>
                    <div class="comparison-handle">⟷</div>
                </div>
                <div class="gallery-info">
                    <h4>Example ${ex.id}</h4>
                    <div class="gallery-metrics">
                        <span>PSNR: ${ex.metrics ? ex.metrics.psnr.toFixed(2) : '--'} dB</span>
                        <span>SSIM: ${ex.metrics ? ex.metrics.ssim.toFixed(4) : '--'}</span>
                    </div>
                </div>
            `;
            galleryGrid.appendChild(card);

            // Initialize slider for this card
            setTimeout(() => {
                const slider = card.querySelector('.comparison-slider');
                if (slider) initSliderForElement(slider);
            }, 100);
        });
    }

    function initSliderForElement(slider) {
        const after = slider.querySelector('.comparison-after');
        const handle = slider.querySelector('.comparison-handle');
        if (!after || !handle) return;

        let isDragging = false;

        function updateSlider(x) {
            const rect = slider.getBoundingClientRect();
            let pos = (x - rect.left) / rect.width;
            pos = Math.max(0, Math.min(1, pos));

            after.style.width = (pos * 100) + '%';
            handle.style.left = (pos * 100) + '%';
        }

        slider.addEventListener('mousedown', (e) => {
            isDragging = true;
            updateSlider(e.clientX);
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) updateSlider(e.clientX);
        });

        document.addEventListener('mouseup', () => { isDragging = false; });

        slider.addEventListener('touchstart', (e) => {
            isDragging = true;
            updateSlider(e.touches[0].clientX);
        });

        document.addEventListener('touchmove', (e) => {
            if (isDragging) updateSlider(e.touches[0].clientX);
        });

        document.addEventListener('touchend', () => { isDragging = false; });

        updateSlider(slider.getBoundingClientRect().left + slider.getBoundingClientRect().width / 2);
    }
});
