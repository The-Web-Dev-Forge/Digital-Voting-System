/**
 * Clean Google Translate Integration for VOTE4ALL Homepage
 * No widgets, no banners, just seamless translation
 */

// Initialize Google Translate when page loads
function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'en',
        includedLanguages: 'en,hi,bn,te,mr,ta,gu,kn,ml,pa,or,as,ur',
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false,
        multilanguagePage: true,
        gaTrack: false,
        gaId: null
    }, 'google_translate_element');
    
    // Immediately hide all Google Translate UI
    hideAllGoogleTranslateUI();
    
    // Set up the language selector
    setupLanguageSelector();
    
    // Keep hiding UI elements
    setInterval(hideAllGoogleTranslateUI, 300);
}

// Aggressively hide all Google Translate UI elements
function hideAllGoogleTranslateUI() {
    // List of all possible Google Translate UI elements
    const selectors = [
        '.goog-te-banner-frame',
        '.goog-te-banner-frame.skiptranslate',
        '.goog-te-gadget',
        '.goog-te-gadget-simple',
        '.goog-logo-link',
        '.goog-te-balloon-frame',
        '.goog-te-menu-frame',
        '.goog-te-ftab',
        '.goog-te-menu2',
        '.goog-te-spinner-pos',
        '.goog-te-spinner',
        'iframe.goog-te-banner-frame',
        'iframe.skiptranslate',
        '.skiptranslate',
        '#goog-gt-tt',
        '.goog-te-menu-value',
        '.goog-te-menu2-item',
        '.goog-te-menu2-colpad'
    ];
    
    selectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.style.display = 'none';
            element.style.visibility = 'hidden';
            element.style.opacity = '0';
            element.style.height = '0';
            element.style.width = '0';
            element.style.margin = '0';
            element.style.padding = '0';
            element.style.position = 'absolute';
            element.style.top = '-9999px';
            element.style.left = '-9999px';
            element.style.zIndex = '-9999';
            
            // Also hide parent if it's a Google Translate container
            if (element.parentNode && element.parentNode.className && 
                element.parentNode.className.includes('goog-te')) {
                element.parentNode.style.display = 'none';
            }
        });
    });
    
    // Force body to stay at top (remove Google Translate's top offset)
    document.body.style.top = '0';
    document.body.style.position = 'static';
    document.body.style.marginTop = '0';
    document.documentElement.style.marginTop = '0';
}

// Set up the language selector functionality
function setupLanguageSelector() {
    const selector = document.getElementById('language-selector');
    if (selector) {
        // Set current language
        const currentLang = getCurrentLanguage();
        selector.value = currentLang;
        
        // Add change event listener
        selector.addEventListener('change', function() {
            const selectedLang = this.value;
            changeLanguage(selectedLang);
            
            // Update selector appearance based on language
            updateSelectorAppearance(selectedLang);
        });
        
        // Apply saved language preference
        const savedLang = localStorage.getItem('vote4all_language');
        if (savedLang && savedLang !== 'en') {
            setTimeout(() => {
                selector.value = savedLang;
                changeLanguage(savedLang);
                updateSelectorAppearance(savedLang);
            }, 1000);
        }
    }
}

// Update selector appearance to show current language state
function updateSelectorAppearance(langCode) {
    const selector = document.getElementById('language-selector');
    if (selector) {
        if (langCode === 'en') {
            selector.style.borderColor = '#004d99';
            selector.style.backgroundColor = '#fff';
        } else {
            selector.style.borderColor = '#ff6600';
            selector.style.backgroundColor = '#fff8f0';
        }
    }
}

// Change language function
function changeLanguage(langCode) {
    if (langCode === 'en') {
        // Reset to English using multiple methods
        resetToEnglish();
    } else {
        // Translate to selected language
        const gtCombo = document.querySelector('.goog-te-combo');
        if (gtCombo) {
            gtCombo.value = langCode;
            gtCombo.dispatchEvent(new Event('change'));
        } else {
            // Fallback method
            window.location.hash = `#googtrans(en|${langCode})`;
        }
    }
    
    // Save language preference
    localStorage.setItem('vote4all_language', langCode);
    
    // Hide UI elements after translation
    setTimeout(hideAllGoogleTranslateUI, 100);
    setTimeout(hideAllGoogleTranslateUI, 500);
    setTimeout(hideAllGoogleTranslateUI, 1000);
}

// Reset to English function with multiple methods
function resetToEnglish() {
    // Method 1: Clear Google Translate combo
    const gtCombo = document.querySelector('.goog-te-combo');
    if (gtCombo) {
        gtCombo.value = '';
        gtCombo.dispatchEvent(new Event('change'));
    }
    
    // Method 2: Clear URL hash
    if (window.location.hash.includes('googtrans')) {
        window.location.hash = '';
        history.replaceState(null, null, window.location.pathname + window.location.search);
    }
    
    // Method 3: Clear Google Translate cookie
    document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=' + window.location.hostname;
    document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    
    // Method 4: Try to click on English in the Google Translate menu (if accessible)
    setTimeout(() => {
        try {
            const gtFrame = document.querySelector('iframe.goog-te-menu-frame');
            if (gtFrame && gtFrame.contentDocument) {
                const englishItem = gtFrame.contentDocument.querySelector('.goog-te-menu2-item span.text');
                if (englishItem && englishItem.textContent.includes('English')) {
                    englishItem.click();
                }
            }
        } catch (e) {
            // Ignore cross-origin errors
        }
    }, 100);
    
    // Method 5: Force page reload if translation persists
    setTimeout(() => {
        if (document.documentElement.lang !== 'en' && document.documentElement.className.includes('translated')) {
            window.location.reload();
        }
    }, 2000);
}

// Get current language
function getCurrentLanguage() {
    // Check URL hash
    const hashLang = window.location.hash.match(/#googtrans\(en\|([a-z-]+)\)/);
    if (hashLang) {
        return hashLang[1];
    }
    
    // Check localStorage
    const savedLang = localStorage.getItem('vote4all_language');
    if (savedLang) {
        return savedLang;
    }
    
    // Check Google Translate combo
    const gtCombo = document.querySelector('.goog-te-combo');
    if (gtCombo && gtCombo.value) {
        return gtCombo.value;
    }
    
    return 'en';
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Hide elements immediately
    hideAllGoogleTranslateUI();
    
    // Wait for Google Translate to load
    setTimeout(() => {
        if (typeof google !== 'undefined' && google.translate) {
            setupLanguageSelector();
        }
    }, 1500);
});

// Additional event listeners to keep UI hidden
window.addEventListener('load', function() {
    setTimeout(hideAllGoogleTranslateUI, 500);
    setTimeout(hideAllGoogleTranslateUI, 1500);
    setTimeout(hideAllGoogleTranslateUI, 3000);
});

window.addEventListener('focus', hideAllGoogleTranslateUI);
window.addEventListener('resize', hideAllGoogleTranslateUI);

// Handle Google Translate callback
window.googleTranslateCallback = googleTranslateElementInit;
