// User Registration JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingModal = document.getElementById('loadingModal');
    const messageModal = document.getElementById('messageModal');
    const modalMessage = document.getElementById('modalMessage');
    const closeModal = document.querySelector('.close');

    // Form validation patterns
    const patterns = {
        aadhaar: /^\d{12}$/,
        phone: /^\d{10}$/,
        voterID: /^[A-Z]{3}\d{7}$/i
    };

    // File upload handling
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileText = this.parentElement.querySelector('.file-upload-text');
            if (this.files.length > 0) {
                fileText.textContent = this.files[0].name;
                fileText.style.color = '#27ae60';
            } else {
                fileText.textContent = 'Choose file';
                fileText.style.color = '#3498db';
            }
        });
    });

    // Real-time validation
    const aadhaarInput = document.getElementById('aadhaar_number');
    const phoneInput = document.getElementById('phone_number');
    const voterIdInput = document.getElementById('voter_id_epic');

    // Aadhaar validation
    aadhaarInput.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '').substring(0, 12);
        validateField(this, patterns.aadhaar, 'Aadhaar number must be 12 digits');
    });

    // Phone validation
    phoneInput.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '').substring(0, 10);
        validateField(this, patterns.phone, 'Phone number must be 10 digits');
    });

    // Voter ID validation
    voterIdInput.addEventListener('input', function() {
        this.value = this.value.toUpperCase().substring(0, 10);
        // More flexible voter ID validation
        const isValid = this.value.length >= 6 && this.value.length <= 20;
        if (isValid) {
            this.classList.remove('error');
            this.classList.add('valid');
        } else {
            this.classList.remove('valid');
            this.classList.add('error');
        }
    });

    // Generic field validation
    function validateField(field, pattern, message) {
        const isValid = pattern.test(field.value);
        const errorElement = field.parentElement.querySelector('.error-message');
        
        if (field.value && !isValid) {
            field.classList.add('error');
            field.classList.remove('valid');
            if (!errorElement) {
                const error = document.createElement('small');
                error.className = 'error-message';
                error.style.color = '#e74c3c';
                error.textContent = message;
                field.parentElement.appendChild(error);
            }
        } else if (field.value && isValid) {
            field.classList.remove('error');
            field.classList.add('valid');
            if (errorElement) {
                errorElement.remove();
            }
        } else {
            field.classList.remove('error', 'valid');
            if (errorElement) {
                errorElement.remove();
            }
        }
    }

    // Date of birth validation (must be 18+ years old)
    const dobInput = document.getElementById('date_of_birth');
    dobInput.addEventListener('change', function() {
        const dob = new Date(this.value);
        const today = new Date();
        const age = today.getFullYear() - dob.getFullYear();
        const monthDiff = today.getMonth() - dob.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
            age--;
        }
        
        if (age < 18) {
            this.classList.add('error');
            showMessage('error', 'You must be at least 18 years old to register.');
        } else {
            this.classList.remove('error');
            this.classList.add('valid');
        }
    });

    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registering...';
        loadingModal.style.display = 'block';

        const formData = new FormData(form);

        fetch('/register-submit/', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            loadingModal.style.display = 'none';
            if (data.success) {
                showMessage('success', data.message);
                setTimeout(() => {
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    }
                }, 2000);
            } else {
                // Show backend error message (may include missing field names)
                showMessage('error', data.message || 'Registration failed. Please fill all required fields.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-user-plus"></i> Register';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingModal.style.display = 'none';
            showMessage('error', 'Registration failed. Please check your connection and try again.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-user-plus"></i> Register';
        });
    });

    // Form validation
    function validateForm() {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        let firstErrorField = null;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('error');
                if (!firstErrorField) firstErrorField = field;
                isValid = false;
            } else {
                field.classList.remove('error');
            }
        });

        // Check file uploads
        const fileInputs = form.querySelectorAll('input[type="file"][required]');
        fileInputs.forEach(input => {
            if (!input.files.length) {
                input.classList.add('error');
                if (!firstErrorField) firstErrorField = input;
                isValid = false;
            } else {
                // Check file size (2MB limit)
                const file = input.files[0];
                if (file.size > 2 * 1024 * 1024) {
                    input.classList.add('error');
                    showMessage('error', `File ${file.name} is too large. Maximum size is 2MB.`);
                    if (!firstErrorField) firstErrorField = input;
                    isValid = false;
                } else {
                    input.classList.remove('error');
                }
            }
        });

        // Check terms checkbox
        const termsCheckbox = document.getElementById('terms');
        if (!termsCheckbox.checked) {
            showMessage('error', 'Please accept the terms and conditions to continue.');
            isValid = false;
        }

        if (!isValid) {
            showMessage('error', 'Please fill in all required fields correctly.');
            if (firstErrorField) {
                firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstErrorField.focus();
            }
        }

        return isValid;
    }

    // Show message modal
    function showMessage(type, message) {
        const iconClass = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
        const iconColor = type === 'success' ? '#27ae60' : '#e74c3c';
        
        modalMessage.innerHTML = `
            <div style="color: ${iconColor}; font-size: 3em; margin-bottom: 15px;">
                <i class="${iconClass}"></i>
            </div>
            <h3 style="color: ${iconColor}; margin-bottom: 15px;">
                ${type === 'success' ? 'Success!' : 'Error!'}
            </h3>
            <p style="color: #2c3e50; font-size: 1.1em; line-height: 1.5;">
                ${message}
            </p>
        `;
        
        messageModal.style.display = 'block';
    }

    // Close modal
    closeModal.addEventListener('click', function() {
        messageModal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === messageModal) {
            messageModal.style.display = 'none';
        }
    });

    // Auto-format inputs
    const inputs = form.querySelectorAll('input[type="text"], input[type="tel"]');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            this.value = this.value.trim();
        });
    });

    // Username availability check (debounced)
    const usernameInput = document.getElementById('username');
    let usernameTimeout;
    
    usernameInput.addEventListener('input', function() {
        clearTimeout(usernameTimeout);
        const username = this.value.trim();
        
        if (username.length >= 3) {
            usernameTimeout = setTimeout(() => {
                checkUsernameAvailability(username);
            }, 500);
        }
    });

    function checkUsernameAvailability(username) {
        // This would typically make an API call to check username availability
        // For now, we'll just validate the format
        const usernamePattern = /^[a-zA-Z0-9_]{3,20}$/;
        const input = document.getElementById('username');
        
        if (usernamePattern.test(username)) {
            input.classList.remove('error');
            input.classList.add('valid');
        } else {
            input.classList.remove('valid');
            input.classList.add('error');
        }
    }

    // Auto-advance focus for better UX
    const textInputs = form.querySelectorAll('input[type="text"], input[type="tel"], input[type="email"]');
    textInputs.forEach((input, index) => {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const nextInput = textInputs[index + 1];
                if (nextInput) {
                    nextInput.focus();
                }
            }
        });
    });
});

// Add CSS classes for validation
const style = document.createElement('style');
style.textContent = `
    .form-group input.valid,
    .form-group select.valid {
        border-color: #27ae60 !important;
        background-color: #f8fff9 !important;
    }
    
    .form-group input.error,
    .form-group select.error {
        border-color: #e74c3c !important;
        background-color: #fdf2f2 !important;
    }
    
    .error-message {
        display: block !important;
        margin-top: 5px !important;
    }
`;
document.head.appendChild(style);
