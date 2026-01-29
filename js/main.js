// Current language (default English)
let currentLanguage = 'EN';

// Translation function
function t(key) {
    return translations[currentLanguage][key] || key;
}

// Update all elements with data-i18n attribute
function updateTranslations() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);

        // Update text content for most elements
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            // For form inputs, update placeholder if it exists
            if (element.placeholder) {
                element.placeholder = translation;
            }
        } else if (element.tagName === 'OPTION') {
            element.textContent = translation;
        } else {
            element.textContent = translation;
        }
    });

    // Update image alt attributes with data-i18n-alt
    const imagesWithAlt = document.querySelectorAll('[data-i18n-alt]');
    imagesWithAlt.forEach(img => {
        const key = img.getAttribute('data-i18n-alt');
        const translation = t(key);
        img.alt = translation;
    });
}

// Change language
function changeLanguage(lang) {
    currentLanguage = lang;
    
    // Update language button styles
    document.getElementById('lang-en').className = lang === 'EN' 
        ? 'text-sm px-2 py-1 rounded transition-colors bg-orange-500 text-white'
        : 'text-sm px-2 py-1 rounded transition-colors hover:text-orange-400';
    
    document.getElementById('lang-tc').className = lang === '繁' 
        ? 'text-sm px-2 py-1 rounded transition-colors bg-orange-500 text-white'
        : 'text-sm px-2 py-1 rounded transition-colors hover:text-orange-400';
    
    document.getElementById('lang-sc').className = lang === '简' 
        ? 'text-sm px-2 py-1 rounded transition-colors bg-orange-500 text-white'
        : 'text-sm px-2 py-1 rounded transition-colors hover:text-orange-400';
    
    // Update all translations on the page
    updateTranslations();
}

// Smooth scroll to section
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Toggle mobile menu
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = document.getElementById('menu-icon');
    const closeIcon = document.getElementById('close-icon');
    
    if (mobileMenu.classList.contains('hidden')) {
        mobileMenu.classList.remove('hidden');
        menuIcon.classList.add('hidden');
        closeIcon.classList.remove('hidden');
    } else {
        mobileMenu.classList.add('hidden');
        menuIcon.classList.remove('hidden');
        closeIcon.classList.add('hidden');
    }
}

// Handle contact form submission
function handleFormSubmit(event) {
    event.preventDefault();

    // EmailJS configuration
    const serviceID = 'default_service';
    const templateID = 'template_czus2pw';

    // Show loading state
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Sending...';

    // Send email using EmailJS
    emailjs.sendForm(serviceID, templateID, event.target)
        .then(() => {
            // Show success message
            alert(t('contact.form.success') || 'Message sent successfully!');
            // Reset form
            event.target.reset();
        })
        .catch((error) => {
            console.error('Email send error:', error);
            alert('Sorry, there was an error sending your message. Please try again or contact us directly at info@sunfly.com.hk');
        })
        .finally(() => {
            // Restore button state
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize translations first (critical for page display)
    updateTranslations();

    // Initialize EmailJS if available
    if (typeof emailjs !== 'undefined') {
        emailjs.init('7OufI5CIU1Q7BV8Cr');
    }

    // Set up form submission handler
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', handleFormSubmit);
    }

    // Add smooth scrolling to the page
    document.documentElement.classList.add('smooth-scroll');
    document.documentElement.style.scrollBehavior = 'smooth';
});

// Handle window resize to close mobile menu if screen gets larger
window.addEventListener('resize', function() {
    if (window.innerWidth >= 768) { // md breakpoint
        const mobileMenu = document.getElementById('mobile-menu');
        const menuIcon = document.getElementById('menu-icon');
        const closeIcon = document.getElementById('close-icon');
        
        if (!mobileMenu.classList.contains('hidden')) {
            mobileMenu.classList.add('hidden');
            menuIcon.classList.remove('hidden');
            closeIcon.classList.add('hidden');
        }
    }
});