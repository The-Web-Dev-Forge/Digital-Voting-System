// OTP Verification JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const otpInputs = document.querySelectorAll('.otp-digit');
    const verifyBtn = document.getElementById('verifyBtn');
    const resendBtn = document.getElementById('resendBtn');
    const loadingModal = document.getElementById('loadingModal');
    const messageModal = document.getElementById('messageModal');
    const modalMessage = document.getElementById('modalMessage');
    const closeModal = document.querySelector('.close');
    const countdownElement = document.getElementById('countdown');

    let countdown = 120; // 2 minutes in seconds
    let countdownInterval;
    let resendTimeout;

    // Initialize countdown
    startCountdown();

    // Auto-send OTP on page load
    sendOTP();

    // OTP input handling
    otpInputs.forEach((input, index) => {
        input.addEventListener('input', function() {
            // Only allow digits
            this.value = this.value.replace(/\D/g, '');

            // Move to next input
            if (this.value && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }

            // Update visual state
            if (this.value) {
                this.classList.add('filled');
                this.classList.remove('error');
            } else {
                this.classList.remove('filled');
            }

            // Check if all inputs are filled
            checkOTPComplete();
        });

        input.addEventListener('keydown', function(e) {
            // Handle backspace
            if (e.key === 'Backspace' && !this.value && index > 0) {
                otpInputs[index - 1].focus();
                otpInputs[index - 1].value = '';
                otpInputs[index - 1].classList.remove('filled');
            }

            // Handle Enter key
            if (e.key === 'Enter') {
                e.preventDefault();
                if (isOTPComplete()) {
                    verifyOTP();
                }
            }

            // Prevent non-numeric input
            if (!/[\d\b\t\r\n]/.test(e.key) && !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
            }
        });

        input.addEventListener('paste', function(e) {
            e.preventDefault();
            const pasteData = e.clipboardData.getData('text').replace(/\D/g, '');
            
            if (pasteData.length === 6) {
                // Fill all inputs with pasted OTP
                otpInputs.forEach((input, i) => {
                    if (i < pasteData.length) {
                        input.value = pasteData[i];
                        input.classList.add('filled');
                        input.classList.remove('error');
                    }
                });
                checkOTPComplete();
            }
        });

        input.addEventListener('focus', function() {
            this.select();
        });
    });

    // Check if OTP is complete
    function checkOTPComplete() {
        const isComplete = isOTPComplete();
        verifyBtn.disabled = !isComplete;
        
        if (isComplete) {
            verifyBtn.classList.add('ready');
        } else {
            verifyBtn.classList.remove('ready');
        }
    }

    function isOTPComplete() {
        return Array.from(otpInputs).every(input => input.value.length === 1);
    }

    // Get OTP value
    function getOTPValue() {
        return Array.from(otpInputs).map(input => input.value).join('');
    }

    // Verify OTP
    verifyBtn.addEventListener('click', verifyOTP);

    function verifyOTP() {
        if (!isOTPComplete()) {
            showMessage('error', 'Please enter the complete 6-digit OTP.');
            return;
        }

        const otp = getOTPValue();
        
        verifyBtn.disabled = true;
        verifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';
        loadingModal.style.display = 'block';

        fetch('/verify-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ otp: otp })
        })
        .then(response => response.json())
        .then(data => {
            loadingModal.style.display = 'none';
            
            if (data.success) {
                showMessage('success', data.message);
                clearInterval(countdownInterval);
                setTimeout(() => {
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    }
                }, 2000);
            } else {
                showMessage('error', data.error);
                clearOTPInputs();
                addErrorState();
                verifyBtn.disabled = false;
                verifyBtn.innerHTML = '<i class="fas fa-check-circle"></i> Verify OTP';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingModal.style.display = 'none';
            showMessage('error', 'Verification failed. Please check your connection and try again.');
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = '<i class="fas fa-check-circle"></i> Verify OTP';
        });
    }

    // Resend OTP
    resendBtn.addEventListener('click', function() {
        if (this.disabled) return;
        
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        
        sendOTP();
    });

    function sendOTP() {
        fetch('/send-otp-api/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('success', data.message);
                resetCountdown();
                clearOTPInputs();
                otpInputs[0].focus();
                
                // For development - show OTP in console
                if (data.otp) {
                    console.log('Development OTP:', data.otp);
                }
            } else {
                showMessage('error', data.error);
            }
            
            resendBtn.disabled = false;
            resendBtn.innerHTML = '<i class="fas fa-redo"></i> Resend OTP';
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('error', 'Failed to send OTP. Please try again.');
            resendBtn.disabled = false;
            resendBtn.innerHTML = '<i class="fas fa-redo"></i> Resend OTP';
        });
    }

    // Countdown timer
    function startCountdown() {
        countdownInterval = setInterval(() => {
            const minutes = Math.floor(countdown / 60);
            const seconds = countdown % 60;
            
            countdownElement.textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            if (countdown <= 0) {
                clearInterval(countdownInterval);
                countdownElement.textContent = '00:00';
                document.getElementById('timer').innerHTML = 
                    '<span style="color: #e74c3c;">OTP has expired. Please request a new one.</span>';
                resendBtn.disabled = false;
                disableOTPInputs();
            }
            
            countdown--;
        }, 1000);
        
        // Enable resend button after 30 seconds
        resendTimeout = setTimeout(() => {
            resendBtn.disabled = false;
        }, 30000);
    }

    function resetCountdown() {
        clearInterval(countdownInterval);
        clearTimeout(resendTimeout);
        countdown = 120;
        document.getElementById('timer').innerHTML = 'OTP expires in: <span id="countdown">02:00</span>';
        countdownElement = document.getElementById('countdown');
        resendBtn.disabled = true;
        enableOTPInputs();
        startCountdown();
    }

    // Clear OTP inputs
    function clearOTPInputs() {
        otpInputs.forEach(input => {
            input.value = '';
            input.classList.remove('filled', 'error');
        });
        checkOTPComplete();
    }

    // Add error state to inputs
    function addErrorState() {
        otpInputs.forEach(input => {
            input.classList.add('error');
        });
        
        setTimeout(() => {
            otpInputs.forEach(input => {
                input.classList.remove('error');
            });
        }, 1000);
    }

    // Disable/Enable OTP inputs
    function disableOTPInputs() {
        otpInputs.forEach(input => {
            input.disabled = true;
            input.style.opacity = '0.5';
        });
        verifyBtn.disabled = true;
    }

    function enableOTPInputs() {
        otpInputs.forEach(input => {
            input.disabled = false;
            input.style.opacity = '1';
        });
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

    // Get CSRF token
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Focus first input on page load
    otpInputs[0].focus();

    // Handle page visibility change
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            // Page became visible, focus first empty input
            const firstEmpty = Array.from(otpInputs).find(input => !input.value);
            if (firstEmpty) {
                firstEmpty.focus();
            }
        }
    });
});

// Add CSS for ready state
const style = document.createElement('style');
style.textContent = `
    .verify-btn.ready {
        background: linear-gradient(135deg, #27ae60, #229954) !important;
        box-shadow: 0 0 20px rgba(39, 174, 96, 0.4) !important;
        animation: readyPulse 2s ease-in-out infinite;
    }
    
    @keyframes readyPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
`;
document.head.appendChild(style);
