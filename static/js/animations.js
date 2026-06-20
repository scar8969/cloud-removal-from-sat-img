// animations.js - Scroll-reveal and other animations

document.addEventListener('DOMContentLoaded', () => {
    // Scroll reveal animation
    const revealElements = document.querySelectorAll('.section, .feature-card, .gallery-card, .about-card, .arch-block');

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    revealElements.forEach(el => {
        el.classList.add('reveal');
        revealObserver.observe(el);
    });

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = anchor.getAttribute('href');
            const target = document.querySelector(targetId);
            if (target) {
                const navHeight = document.getElementById('navbar').offsetHeight;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navHeight;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Navbar background on scroll
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Add stagger animation to gallery cards
    const galleryCards = document.querySelectorAll('.gallery-card');
    galleryCards.forEach((card, index) => {
        card.style.transitionDelay = `${index * 0.1}s`;
    });

    // Add stagger animation to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.style.transitionDelay = `${index * 0.15}s`;
    });

    // Parallax effect on hero clouds (subtle)
    const heroClouds = document.getElementById('heroClouds');
    if (heroClouds) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            heroClouds.style.transform = `translateY(${scrolled * 0.5}px)`;
        });
    }

    // Counter animation for stats
    const stats = document.querySelectorAll('.stat-value');
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    stats.forEach(stat => counterObserver.observe(stat));

    function animateCounter(element) {
        const text = element.textContent;
        const hasComma = text.includes(',');
        const numMatch = text.replace(/,/g, '').match(/\d+/);
        if (!numMatch) return;

        const target = parseInt(numMatch[0]);
        const duration = 1000;
        const startTime = Date.now();

        function update() {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease out cubic
            const current = Math.floor(target * eased);

            if (hasComma) {
                element.textContent = current.toLocaleString() + text.replace(/[\d,]/g, '');
            } else {
                element.textContent = current + text.replace(/\d/g, '');
            }

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.textContent = text; // Reset to original
            }
        }
        update();
    }
});
