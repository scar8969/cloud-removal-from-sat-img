// slider.js - Comparison slider logic

function initSlider() {
    const sliders = document.querySelectorAll('.comparison-slider');

    sliders.forEach(slider => {
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

        // Mouse events
        slider.addEventListener('mousedown', (e) => {
            isDragging = true;
            updateSlider(e.clientX);
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                e.preventDefault();
                updateSlider(e.clientX);
            }
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });

        // Touch events
        slider.addEventListener('touchstart', (e) => {
            isDragging = true;
            updateSlider(e.touches[0].clientX);
        });

        document.addEventListener('touchmove', (e) => {
            if (isDragging) {
                e.preventDefault();
                updateSlider(e.touches[0].clientX);
            }
        });

        document.addEventListener('touchend', () => {
            isDragging = false;
        });

        // Initialize at 50%
        updateSlider(slider.getBoundingClientRect().left + slider.getBoundingClientRect().width / 2);
    });
}

// Export for use in app.js
window.initSlider = initSlider;

// Auto-init on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    initSlider();
});
