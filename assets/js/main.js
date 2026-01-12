// Local Pro Connect JS - Inspired by Angi.com

// Search functionality
async function handleSearch(event) {
    event.preventDefault();
    const serviceInput = document.getElementById('serviceInput').value.trim();
    const locationInput = document.getElementById('locationInput').value.trim();
    const searchBtn = document.getElementById('searchBtn');
    const searchBtnText = document.getElementById('searchBtnText');
    const searchResults = document.getElementById('searchResults');
    const searchError = document.getElementById('searchError');

    if (!serviceInput || !locationInput) {
        searchError.textContent = 'Please enter both service and location';
        searchError.style.display = 'block';
        return;
    }

    searchBtn.disabled = true;
    searchBtnText.innerHTML = '<span class="loading-spinner"></span>Searching...';
    searchError.style.display = 'none';
    searchResults.innerHTML = '';

    try {
        // BACKEND: Replace with actual API endpoint
        // const response = await fetch('/api/search', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({ service: serviceInput, location: locationInput })
        // });
        // const data = await response.json();

        setTimeout(() => {
            const mockResults = `
                <div class="row g-3">
                    <div class="col-md-6">
                        <div style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <h5 style="color: var(--primary-cobalt);">John's Plumbing Services</h5>
                            <p style="margin: 0.5rem 0; color: #666;">
                                <i class="fas fa-star" style="color: var(--alert-yellow);"></i>
                                4.8 (125 reviews)
                            </p>
                            <p style="color: #999; font-size: 0.9rem;">Licensed • Insured • 15+ years experience</p>
                            <button class="search-btn" style="margin-top: 1rem; width: 100%; font-size: 0.9rem;">
                                View Details
                            </button>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <h5 style="color: var(--primary-cobalt);">Pro Plumbing Co</h5>
                            <p style="margin: 0.5rem 0; color: #666;">
                                <i class="fas fa-star" style="color: var(--alert-yellow);"></i>
                                4.6 (98 reviews)
                            </p>
                            <p style="color: #999; font-size: 0.9rem;">Licensed • Insured • 24/7 Available</p>
                            <button class="search-btn" style="margin-top: 1rem; width: 100%; font-size: 0.9rem;">
                                View Details
                            </button>
                        </div>
                    </div>
                </div>
            `;
            searchResults.innerHTML = mockResults;
            searchBtn.disabled = false;
            searchBtnText.textContent = 'Search';
        }, 1000);

    } catch (error) {
        searchError.textContent = 'Error searching professionals. Please try again.';
        searchError.style.display = 'block';
        searchBtn.disabled = false;
        searchBtnText.textContent = 'Search';
    }
}

// Registration form validation and submission
function handleRegistration(event) {
    event.preventDefault();
    const nameInput = document.getElementById('nameInput');
    const emailInput = document.getElementById('emailInput');
    const agreeCheckbox = document.getElementById('agreeCheckbox');
    const registerBtn = document.getElementById('registerBtn');
    const registerBtnText = document.getElementById('registerBtnText');
    const successMessage = document.getElementById('successMessage');
    const registrationError = document.getElementById('registrationError');
    let isValid = true;
    successMessage.classList.remove('show');
    registrationError.style.display = 'none';
    const nameFormGroup = nameInput.closest('.form-group');
    if (nameInput.value.trim().length < 2) {
        nameFormGroup.classList.add('error');
        isValid = false;
    } else {
        nameFormGroup.classList.remove('error');
    }
    const emailFormGroup = emailInput.closest('.form-group');
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailInput.value.trim())) {
        emailFormGroup.classList.add('error');
        isValid = false;
    } else {
        emailFormGroup.classList.remove('error');
    }
    if (!agreeCheckbox.checked) {
        registrationError.textContent = 'Please agree to the Terms of Service and Privacy Policy';
        registrationError.style.display = 'block';
        isValid = false;
    }
    if (!isValid) {
        return;
    }
    registerBtn.disabled = true;
    registerBtnText.innerHTML = '<span class="loading-spinner"></span>Creating Account...';
    const formData = {
        name: nameInput.value.trim(),
        email: emailInput.value.trim(),
        agreeToTerms: agreeCheckbox.checked
    };
    setTimeout(() => {
        successMessage.classList.add('show');
        document.getElementById('registrationForm').reset();
        document.getElementById('agreeCheckbox').closest('.form-check').classList.remove('error');
        successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
        registerBtn.disabled = false;
        registerBtnText.textContent = 'Create My Account';
    }, 1500);
}

document.getElementById('nameInput').addEventListener('input', function() {
    if (this.value.trim().length >= 2) {
        this.closest('.form-group').classList.remove('error');
    }
});
document.getElementById('emailInput').addEventListener('input', function() {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailRegex.test(this.value.trim())) {
        this.closest('.form-group').classList.remove('error');
    }
});
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#' && document.querySelector(href)) {
            e.preventDefault();
            document.querySelector(href).scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ========================================
// SCROLL ANIMATIONS
// ========================================

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animated');
            // Optionally unobserve after animation
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all elements with animate-on-scroll class
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(el => observer.observe(el));
});

// ========================================
// NAVBAR SCROLL EFFECT
// ========================================

let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    // Add shadow on scroll
    if (currentScroll > 10) {
        navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
    } else {
        navbar.style.boxShadow = 'none';
    }
    
    lastScroll = currentScroll;
});

// ========================================
// SMOOTH COUNTER ANIMATION (for statistics)
// ========================================

function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = Math.round(target);
            clearInterval(timer);
        } else {
            element.textContent = Math.round(start);
        }
    }, 16);
}

// ========================================
// PARALLAX EFFECT FOR HERO SECTION
// ========================================

window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroSection = document.querySelector('.hero-section');
    
    if (heroSection && scrolled < window.innerHeight) {
        heroSection.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});

// ========================================
// CARD TILT EFFECT (Optional subtle 3D effect)
// ========================================

document.querySelectorAll('.service-card, .feature-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px) scale(1.02)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = '';
    });
});
