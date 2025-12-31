// Voter Login JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const methodTabs = document.querySelectorAll('.method-tab');
    const loginMethods = document.querySelectorAll('.login-method');
    const sendOtpBtns = document.querySelectorAll('.send-otp-btn');
    const otpSection = document.getElementById('otpSection');
    const otpInputs = document.querySelectorAll('.otp-digit');
    const verifyOtpBtn = document.getElementById('verifyOtpBtn');
    const resendOtpBtn = document.getElementById('resendOtpBtn');
    const loadingModal = document.getElementById('loadingModal');
    const messageModal = document.getElementById('messageModal');
    const modalMessage = document.getElementById('modalMessage');
    const closeModal = document.querySelector('.close');
    const displayPhone = document.getElementById('displayPhone');
    const otpCountdown = document.getElementById('otpCountdown');
    
    let currentMethod = 'name-phone';
    let currentPhoneNumber = '';
    let otpTimer = null;
    let otpTimeLeft = 120; // 2 minutes

    // Initialize
    initializeFormValidation();
    setupEventListeners();

    function setupEventListeners() {
        // Method tab switching
        methodTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const method = this.dataset.method;
                switchMethod(method);
            });
        });

        // Send OTP button clicks
        sendOtpBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const formId = this.dataset.form;
                sendOTP(formId);
            });
        });

        // OTP input handling
        otpInputs.forEach((input, index) => {
            input.addEventListener('input', function() {
                handleOTPInput(this, index);
            });

            input.addEventListener('keydown', function(e) {
                handleOTPKeydown(this, e, index);
            });

            input.addEventListener('paste', function(e) {
                handleOTPPaste(e);
            });
        });

        // Verify OTP button
        verifyOtpBtn.addEventListener('click', function() {
            verifyOTP();
        });

        // Resend OTP button
        resendOtpBtn.addEventListener('click', function() {
            resendOTP();
        });

        // Close modal
        if (closeModal) {
            closeModal.addEventListener('click', function() {
                messageModal.style.display = 'none';
            });
        }

        // Close modal when clicking outside
        window.addEventListener('click', function(e) {
            if (e.target === messageModal) {
                messageModal.style.display = 'none';
            }
        });
    }

    function switchMethod(method) {
        // Update active tab
        methodTabs.forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.method === method) {
                tab.classList.add('active');
            }
        });

        // Update active method
        loginMethods.forEach(methodDiv => {
            methodDiv.classList.remove('active');
            if (methodDiv.id === method + '-method') {
                methodDiv.classList.add('active');
            }
        });

        currentMethod = method;
        hideOTPSection();
    }

    function initializeFormValidation() {
        // Aadhaar number validation
        const aadhaarInput = document.getElementById('aadhaar_input');
        if (aadhaarInput) {
            aadhaarInput.addEventListener('input', function() {
                this.value = this.value.replace(/\D/g, '').substring(0, 12);
            });
        }

        // Phone number validation for all forms
        const phoneInputs = document.querySelectorAll('input[type="tel"]');
        phoneInputs.forEach(input => {
            input.addEventListener('input', function() {
                this.value = this.value.replace(/\D/g, '').substring(0, 10);
            });
        });

        // Voter ID validation
        const voterIdInput = document.getElementById('voter_id_input');
        if (voterIdInput) {
            voterIdInput.addEventListener('input', function() {
                this.value = this.value.toUpperCase().substring(0, 20);
            });
        }
    }

    function sendOTP(formId) {
        const form = document.getElementById(formId);
        const formData = new FormData(form);
        
        // Validate form based on current method
        if (!validateCurrentForm()) {
            return;
        }

        // Get phone number and prepare data
        let phoneInput, requestData;
        switch (currentMethod) {
            case 'name-phone':
                phoneInput = document.getElementById('phone_name');
                requestData = {
                    method: 'name-phone',
                    phone: phoneInput.value,
                    name_input: document.getElementById('name_input').value
                };
                break;
            case 'aadhaar-phone':
                phoneInput = document.getElementById('phone_aadhaar');
                requestData = {
                    method: 'aadhaar-phone',
                    phone: phoneInput.value,
                    aadhaar_input: document.getElementById('aadhaar_input').value
                };
                break;
            case 'voter-phone':
                phoneInput = document.getElementById('phone_voter');
                requestData = {
                    method: 'voter-phone',
                    phone: phoneInput.value,
                    voter_id_input: document.getElementById('voter_id_input').value
                };
                break;
        }

        currentPhoneNumber = phoneInput.value;

        // Disable send OTP button
        const sendBtn = form.querySelector('.send-otp-btn');
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending OTP...';

        // Show loading modal
        loadingModal.style.display = 'block';

        // Send OTP request
        fetch('/login-send-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            loadingModal.style.display = 'none';
            
            if (data.success) {
                showMessage('success', data.message);
                showOTPSection();
                
                // For development - log the OTP
                if (data.otp) {
                    console.log(`Development OTP: ${data.otp}`);
                }
            } else {
                showMessage('error', data.error);
            }
            
            // Reset send OTP button
            sendBtn.disabled = false;
            sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send OTP';
        })
        .catch(error => {
            console.error('Error:', error);
            loadingModal.style.display = 'none';
            showMessage('error', 'Failed to send OTP. Please try again.');
            
            // Reset send OTP button
            sendBtn.disabled = false;
            sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send OTP';
        });
    }

    function validateCurrentForm() {
        let isValid = true;
        let errorMessage = '';

        switch (currentMethod) {
            case 'name-phone':
                const nameInput = document.getElementById('name_input');
                const phoneNameInput = document.getElementById('phone_name');
                
                if (!nameInput.value.trim()) {
                    errorMessage = 'Please enter your full name or username';
                    isValid = false;
                } else if (!phoneNameInput.value || phoneNameInput.value.length !== 10) {
                    errorMessage = 'Please enter a valid 10-digit phone number';
                    isValid = false;
                }
                break;

            case 'aadhaar-phone':
                const aadhaarInput = document.getElementById('aadhaar_input');
                const phoneAadhaarInput = document.getElementById('phone_aadhaar');
                
                if (!aadhaarInput.value || aadhaarInput.value.length !== 12) {
                    errorMessage = 'Please enter a valid 12-digit Aadhaar number';
                    isValid = false;
                } else if (!phoneAadhaarInput.value || phoneAadhaarInput.value.length !== 10) {
                    errorMessage = 'Please enter a valid 10-digit phone number';
                    isValid = false;
                }
                break;

            case 'voter-phone':
                const voterIdInput = document.getElementById('voter_id_input');
                const phoneVoterInput = document.getElementById('phone_voter');
                
                if (!voterIdInput.value.trim()) {
                    errorMessage = 'Please enter your Voter ID EPIC number';
                    isValid = false;
                } else if (!phoneVoterInput.value || phoneVoterInput.value.length !== 10) {
                    errorMessage = 'Please enter a valid 10-digit phone number';
                    isValid = false;
                }
                break;
        }

        if (!isValid) {
            showMessage('error', errorMessage);
        }

        return isValid;
    }

    function showOTPSection() {
        otpSection.style.display = 'block';
        displayPhone.textContent = `+91-${currentPhoneNumber.substring(0, 2)}XXX-XX${currentPhoneNumber.substring(8)}`;
        clearOTPInputs();
        otpInputs[0].focus();
        startOTPTimer();
        
        // Scroll to OTP section
        otpSection.scrollIntoView({ behavior: 'smooth' });
    }

    function hideOTPSection() {
        otpSection.style.display = 'none';
        clearOTPTimer();
        clearOTPInputs();
    }

    function handleOTPInput(input, index) {
        // Only allow digits
        input.value = input.value.replace(/\D/g, '');

        // Move to next input if current is filled
        if (input.value && index < otpInputs.length - 1) {
            otpInputs[index + 1].focus();
        }

        // Update visual state
        if (input.value) {
            input.classList.add('filled');
            input.classList.remove('error');
        } else {
            input.classList.remove('filled');
        }

        // Check if all inputs are filled
        checkOTPComplete();
    }

    function handleOTPKeydown(input, e, index) {
        // Handle backspace
        if (e.key === 'Backspace' && !input.value && index > 0) {
            otpInputs[index - 1].focus();
            otpInputs[index - 1].value = '';
            otpInputs[index - 1].classList.remove('filled');
            checkOTPComplete();
        }
        
        // Handle arrow keys
        if (e.key === 'ArrowLeft' && index > 0) {
            otpInputs[index - 1].focus();
        } else if (e.key === 'ArrowRight' && index < otpInputs.length - 1) {
            otpInputs[index + 1].focus();
        }
    }

    function handleOTPPaste(e) {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text').replace(/\D/g, '');
        
        if (pastedData.length === 6) {
            for (let i = 0; i < 6; i++) {
                otpInputs[i].value = pastedData[i];
                otpInputs[i].classList.add('filled');
            }
            checkOTPComplete();
        }
    }

    function checkOTPComplete() {
        const otp = Array.from(otpInputs).map(input => input.value).join('');
        verifyOtpBtn.disabled = otp.length !== 6;
    }

    function clearOTPInputs() {
        otpInputs.forEach(input => {
            input.value = '';
            input.classList.remove('filled', 'error');
        });
        verifyOtpBtn.disabled = true;
    }

    function addOTPErrorState() {
        otpInputs.forEach(input => {
            input.classList.add('error');
        });
    }

    function verifyOTP() {
        const otp = Array.from(otpInputs).map(input => input.value).join('');
        
        if (otp.length !== 6) {
            showMessage('error', 'Please enter a complete 6-digit OTP');
            return;
        }

        // Disable verify button
        verifyOtpBtn.disabled = true;
        verifyOtpBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';

        // Show loading modal
        loadingModal.style.display = 'block';

        // Verify OTP request
        fetch('/login-verify-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                otp: otp
            })
        })
        .then(response => response.json())
        .then(data => {
            loadingModal.style.display = 'none';
            
            if (data.success) {
                showMessage('success', data.message);
                
                // Redirect to voter info page after a short delay
                setTimeout(() => {
                    window.location.href = '/voter-info/';
                }, 1500);
            } else {
                showMessage('error', data.error);
                addOTPErrorState();
                clearOTPInputs();
                
                // Reset verify button
                verifyOtpBtn.disabled = false;
                verifyOtpBtn.innerHTML = '<i class="fas fa-check-circle"></i> Verify & Login';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingModal.style.display = 'none';
            showMessage('error', 'Failed to verify OTP. Please try again.');
            addOTPErrorState();
            clearOTPInputs();
            
            // Reset verify button
            verifyOtpBtn.disabled = false;
            verifyOtpBtn.innerHTML = '<i class="fas fa-check-circle"></i> Verify & Login';
        });
    }

    function resendOTP() {
        // Disable resend button
        resendOtpBtn.disabled = true;
        resendOtpBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

        // Simulate resending OTP
        setTimeout(() => {
            showMessage('success', `OTP resent successfully to +91-${currentPhoneNumber}`);
            
            // Reset timer
            clearOTPTimer();
            otpTimeLeft = 120;
            startOTPTimer();
            
            // Clear OTP inputs
            clearOTPInputs();
            otpInputs[0].focus();
            
            // Reset resend button
            resendOtpBtn.disabled = false;
            resendOtpBtn.innerHTML = '<i class="fas fa-redo"></i> Resend OTP';
            
            // For development - log a new sample OTP
            const sampleOTP = Math.floor(100000 + Math.random() * 900000);
            console.log(`Development OTP (resent): ${sampleOTP}`);
            
        }, 1500);
    }

    function startOTPTimer() {
        otpTimer = setInterval(() => {
            const minutes = Math.floor(otpTimeLeft / 60);
            const seconds = otpTimeLeft % 60;
            
            otpCountdown.textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            if (otpTimeLeft <= 0) {
                clearOTPTimer();
                otpCountdown.textContent = '00:00';
                otpCountdown.style.color = '#e74c3c';
                showMessage('warning', 'OTP has expired. Please request a new one.');
                
                // Disable verify button and enable resend
                verifyOtpBtn.disabled = true;
                resendOtpBtn.disabled = false;
            }
            
            otpTimeLeft--;
        }, 1000);
    }

    function clearOTPTimer() {
        if (otpTimer) {
            clearInterval(otpTimer);
            otpTimer = null;
        }
    }

    function showMessage(type, message) {
        const icon = type === 'success' ? 'fas fa-check-circle' : 
                    type === 'error' ? 'fas fa-exclamation-circle' : 
                    'fas fa-exclamation-triangle';
        
        const color = type === 'success' ? '#27ae60' : 
                     type === 'error' ? '#e74c3c' : 
                     '#f39c12';

        modalMessage.innerHTML = `
            <div style="color: ${color}; margin-bottom: 15px;">
                <i class="${icon}" style="font-size: 3em;"></i>
            </div>
            <p style="font-size: 1.2em; color: #2c3e50; margin: 0;">${message}</p>
        `;
        
        messageModal.style.display = 'block';
        
        // Auto close success messages
        if (type === 'success') {
            setTimeout(() => {
                messageModal.style.display = 'none';
            }, 3000);
        }
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});
