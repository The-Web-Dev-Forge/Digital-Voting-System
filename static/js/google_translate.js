/**
 * Google Translate Integration for VOTE4ALL
 * Provides multi-language support for the voting application
 */

// Google Translate configuration
function googleTranslateElementInit() {
    new google.translate.TranslateElement(
        {
            pageLanguage: 'en',
            includedLanguages: 'en,hi,bn,te,mr,ta,gu,kn,ml,pa,or,as,ur,fr,es,de,ja,ko,zh,ar,ru',
            layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
            autoDisplay: false,
            multilanguagePage: true,
            gaTrack: false,
            gaId: null
        },
        'google_translate_element'
    );
    
    // Hide Google Translate UI immediately after initialization
    hideGoogleTranslateUI();
    
    // Initialize custom selector after Google Translate loads
    setTimeout(() => {
        initializeLanguageSelector();
        hideGoogleTranslateUI();
    }, 1000);
    
    // Keep hiding the UI elements periodically
    setInterval(hideGoogleTranslateUI, 500);
}

// Language mapping for display
const languageMap = {
    'en': 'English',
    'hi': 'हिन्दी',
    'bn': 'বাংলা',
    'te': 'తెలుగు',
    'mr': 'मराठी',
    'ta': 'தமிழ்',
    'gu': 'ગુજરાતી',
    'kn': 'ಕನ್ನಡ',
    'ml': 'മലയാളം',
    'pa': 'ਪੰਜਾਬੀ',
    'or': 'ଓଡ଼ିଆ',
    'as': 'অসমীয়া',
    'ur': 'اردو',
    'fr': 'Français',
    'es': 'Español',
    'de': 'Deutsch',
    'ja': '日本語',
    'ko': '한국어',
    'zh': '中文',
    'ar': 'العربية',
    'ru': 'Русский'
};

// Create custom language selector
function createLanguageSelector() {
    const selector = document.createElement('select');
    selector.id = 'language-selector';
    selector.className = 'language-dropdown';
    selector.setAttribute('aria-label', 'Select Language');
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = 'en';
    defaultOption.textContent = 'English';
    selector.appendChild(defaultOption);
    
    // Add language options
    Object.entries(languageMap).forEach(([code, name]) => {
        if (code !== 'en') {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = name;
            selector.appendChild(option);
        }
    });
    
    // Add change event listener
    selector.addEventListener('change', function() {
        const selectedLang = this.value;
        changeLanguage(selectedLang);
        setLanguagePreference(selectedLang);
    });
    
    return selector;
}

// Get current language from Google Translate or localStorage
function getCurrentLanguage() {
    // Check URL fragment for Google Translate language
    const urlLang = window.location.hash.match(/#googtrans\(en\|([a-z-]+)\)/);
    if (urlLang) {
        return urlLang[1];
    }
    
    // Check localStorage
    const storedLang = localStorage.getItem('preferred_language');
    if (storedLang) {
        return storedLang;
    }
    
    // Check if Google Translate combo exists
    const gtCombo = document.querySelector('.goog-te-combo');
    if (gtCombo && gtCombo.value !== '') {
        return gtCombo.value;
    }
    
    return 'en';
}

// Hide Google Translate UI elements
function hideGoogleTranslateUI() {
    // Hide all Google Translate UI elements
    const elementsToHide = [
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
        'iframe.skiptranslate'
    ];
    
    elementsToHide.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.style.display = 'none';
            element.style.visibility = 'hidden';
            element.style.opacity = '0';
            element.style.height = '0';
            element.style.margin = '0';
            element.style.padding = '0';
            if (element.parentNode) {
                element.parentNode.style.display = 'none';
            }
        });
    });
    
    // Force body to stay at top
    document.body.style.top = '0';
    document.body.style.position = 'static';
    
    // Remove any margin/padding from html and body that Google Translate might add
    document.documentElement.style.marginTop = '0';
    document.body.style.marginTop = '0';
}

// Change language using Google Translate
function changeLanguage(langCode) {
    if (langCode === 'en') {
        // Reset to English
        window.location.hash = '';
        
        // Clear Google Translate selection
        const gtCombo = document.querySelector('.goog-te-combo');
        if (gtCombo) {
            gtCombo.value = '';
            gtCombo.dispatchEvent(new Event('change'));
        }
    } else {
        // Set specific language
        const gtCombo = document.querySelector('.goog-te-combo');
        if (gtCombo) {
            gtCombo.value = langCode;
            gtCombo.dispatchEvent(new Event('change'));
        } else {
            // Fallback: use URL hash method
            window.location.hash = `#googtrans(en|${langCode})`;
        }
    }
    
    // Hide Google Translate UI after language change
    setTimeout(() => {
        hideGoogleTranslateUI();
    }, 100);
    
    // Store preference
    localStorage.setItem('preferred_language', langCode);
    
    // Update UI
    updateLanguageDisplay(langCode);
}

// Update language display
function updateLanguageDisplay(langCode) {
    const selector = document.querySelector('#language-selector');
    if (selector) {
        selector.value = langCode;
    }
    
    // Update any language indicators
    const indicators = document.querySelectorAll('.current-language');
    indicators.forEach(indicator => {
        indicator.textContent = languageMap[langCode] || languageMap['en'];
    });
}

// Set language preference on server
function setLanguagePreference(langCode) {
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     document.querySelector('meta[name="csrf-token"]')?.content;
    
    fetch('/api/set-language/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            language_code: langCode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Language preference saved:', langCode);
        }
    })
    .catch(error => {
        console.error('Error saving language preference:', error);
    });
}

// Initialize language selector
function initializeLanguageSelector() {
    const langContainer = document.querySelector('.lang-selector-container');
    if (!langContainer) return;
    
    // Remove loading indicator
    const loadingElement = langContainer.querySelector('.translate-loading');
    if (loadingElement) {
        loadingElement.remove();
    }
    
    // Create and add selector
    const selector = createLanguageSelector();
    langContainer.appendChild(selector);
    
    // Apply saved language preference
    const savedLang = getCurrentLanguage();
    if (savedLang && savedLang !== 'en') {
        setTimeout(() => {
            changeLanguage(savedLang);
        }, 500);
    }
    
    updateLanguageDisplay(savedLang);
}

// Handle page load
document.addEventListener('DOMContentLoaded', function() {
    // Add custom styles immediately
    addTranslateStyles();
    
    // Start hiding Google Translate UI immediately
    hideGoogleTranslateUI();
    
    // Wait for Google Translate to initialize
    setTimeout(() => {
        if (typeof google !== 'undefined' && google.translate) {
            initializeLanguageSelector();
            hideGoogleTranslateUI();
        } else {
            // Fallback initialization
            setTimeout(() => {
                initializeLanguageSelector();
                hideGoogleTranslateUI();
            }, 2000);
        }
    }, 1500);
    
    // Continuously hide Google Translate UI
    setInterval(hideGoogleTranslateUI, 200);
});

// Add custom styles
function addTranslateStyles() {
    if (document.querySelector('#vote-translate-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'vote-translate-styles';
    style.textContent = `
        /* Hide ALL Google Translate UI elements */
        .goog-te-banner-frame,
        .goog-te-banner-frame.skiptranslate,
        .goog-te-gadget,
        .goog-te-gadget-simple,
        .goog-logo-link,
        .goog-te-balloon-frame,
        .goog-te-menu-frame,
        .goog-te-ftab,
        .goog-te-menu2,
        .goog-te-spinner-pos,
        .goog-te-spinner {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Force body to stay at top - no Google Translate offset */
        body {
            top: 0 !important;
            position: static !important;
        }
        
        /* Hide the translate element container */
        #google_translate_element {
            display: none !important;
        }
        
        /* Hide Google branding and links */
        .goog-logo-link,
        .goog-te-gadget .goog-te-gadget-simple a,
        .goog-te-menu-value span:first-child {
            display: none !important;
        }
        
        /* Loading states */
        .translate-loading {
            color: #ace8fe;
            font-size: 12px;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Language selector improvements */
        .language-dropdown {
            transition: all 0.3s ease;
        }
        
        .language-dropdown:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* RTL support for Arabic and Urdu */
        html:lang(ar), html:lang(ur) {
            direction: rtl;
        }
        
        html:lang(ar) .navbar,
        html:lang(ur) .navbar {
            flex-direction: row-reverse;
        }
    `;
    document.head.appendChild(style);
}

// Monitor Google Translate changes and hide UI
function monitorGoogleTranslate() {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                // Hide any newly added Google Translate elements
                hideGoogleTranslateUI();
                
                // Check if Google Translate combo changed
                const gtCombo = document.querySelector('.goog-te-combo');
                if (gtCombo) {
                    const currentLang = gtCombo.value || 'en';
                    updateLanguageDisplay(currentLang);
                }
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Also hide UI elements periodically
    setInterval(hideGoogleTranslateUI, 1000);
}

// Initialize monitoring
setTimeout(monitorGoogleTranslate, 2000);

// Public API
window.VoteTranslate = {
    changeLanguage,
    getCurrentLanguage,
    updateLanguageDisplay,
    languageMap,
    setLanguagePreference
};

// Handle Google Translate callback
window.googleTranslateCallback = googleTranslateElementInit;
