let currentSlide = 0;
const slides = document.querySelectorAll('.carousel-slide');
let autoSlideInterval = null;

function showSlide(idx) {
    const activeElement = document.activeElement;
    let focusType = null;
    if (activeElement && activeElement.classList.contains('carousel-masaje-btn')) {
        focusType = 'btn';
    } else if (activeElement && activeElement.classList.contains('carousel-autoplay-checkbox')) {
        focusType = 'checkbox';
    }

    slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === idx);

        const btn = slide.querySelector('.carousel-masaje-btn');
        const checkbox = slide.querySelector('.carousel-autoplay-checkbox');
        if (btn) btn.tabIndex = (i === idx) ? 0 : -1;
        if (checkbox) checkbox.tabIndex = (i === idx) ? 0 : -1;
    });

    const activeSlide = slides[idx];
    if (focusType === 'btn') {
        const btn = activeSlide.querySelector('.carousel-masaje-btn');
        if (btn) btn.focus();
    } else if (focusType === 'checkbox') {
        const checkbox = activeSlide.querySelector('.carousel-autoplay-checkbox');
        if (checkbox) checkbox.focus();
    }
}

function moveCarousel(dir) {
    currentSlide = (currentSlide + dir + slides.length) % slides.length;
    showSlide(currentSlide);
    resetAutoSlide();
}

function autoSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
}

function resetAutoSlide() {
    clearInterval(autoSlideInterval);
    autoSlideInterval = setInterval(autoSlide, 10000); 
}

document.addEventListener('DOMContentLoaded', () => {
    showSlide(currentSlide);
    autoSlideInterval = setInterval(autoSlide, 10000); 

    document.querySelectorAll('.carousel-caption button').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.name;
            window.location.href = `/masaje/?tipo=${id}`;
        });
    });

    const pauseCheckbox = document.getElementById('pause-autoplay');
    pauseCheckbox.addEventListener('change', function() {
        if (this.checked) {
            clearInterval(autoSlideInterval);
        } else {
            resetAutoSlide();
        }
    });
});