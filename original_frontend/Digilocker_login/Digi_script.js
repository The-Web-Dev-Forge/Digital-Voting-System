function showForm(formId) {
    document.getElementById('mobile').style.display = 'none';
    document.getElementById('username').style.display = 'none';
    document.getElementById('aadhaar').style.display = 'none';

    document.getElementById('tab-mobile').classList.remove('active');
    document.getElementById('tab-username').classList.remove('active');
    document.getElementById('tab-aadhaar').classList.remove('active');

    document.getElementById(formId).style.display = 'block';

    document.getElementById('tab-' + formId).classList.add('active');
}

function validateMobile(mobile) {
    const mobileRegex = /^\d{10}$/;
    return mobileRegex.test(mobile);
}

function validateUsername(username) {
    const usernameRegex = /^[A-Za-z\s]+$/;
    return usernameRegex.test(username);
}

function validateAadhaar(aadhaar) {
    const aadhaarRegex = /^\d{12}$/;
    return aadhaarRegex.test(aadhaar);
}

function validatePin(pin) {
    const pinRegex = /^\d{6}$/;
    return pinRegex.test(pin);
}

function handleSubmit(event) {
    event.preventDefault();
    const activeTab = document.querySelector('.tab.active');
    let formData;
    let isValid = true;
    const submitButton = document.querySelector('.signin-button');

    if (activeTab.id === 'tab-mobile') {
        const mobile = document.querySelector('input[name="mobile"]').value;
        const pin = document.querySelector('input[name="mobile-pin"]').value;
        if (!validateMobile(mobile)) {
            alert('Invalid mobile format. It should be a 10 digit number.');
            isValid = false;
        } else if (!validatePin(pin)) {
            alert('Invalid PIN format. It should be a 6 digit number.');
            isValid = false;
        } else {
            formData = { type: 'Mobile', mobile, pin };
        }
    } else if (activeTab.id === 'tab-username') {
        const username = document.querySelector('input[name="username"]').value;
        const pin = document.querySelector('input[name="username-pin"]').value;
        if (!validateUsername(username)) {
            alert('Invalid username format. It should be alphanumeric.');
            isValid = false;
        } else if (!validatePin(pin)) {
            alert('Invalid PIN format. It should be a 6 digit number.');
            isValid = false;
        } else {
            formData = { type: 'Username', username, pin };
        }
    } else if (activeTab.id === 'tab-aadhaar') {
        const aadhaar = document.querySelector('input[name="aadhaar"]').value;
        const pin = document.querySelector('input[name="aadhaar-pin"]').value;
        if (!validateAadhaar(aadhaar)) {
            alert('Invalid Aadhaar format. It should be a 12 digit number.');
            isValid = false;
        } else if (!validatePin(pin)) {
            alert('Invalid PIN format. It should be a 6 digit number.');
            isValid = false;
        } else {
            formData = { type: 'Aadhaar', aadhaar, pin };
        }
    }

    if (isValid) {
        // console.log('Form Data:', formData);
        submitButton.innerText = 'Logging in...';
        submitButton.disabled = true;
        fetch('/Digilocker-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            window.location.reload();
            if (data.redirectUrl) {
                sessionStorage.setItem('userDetails', JSON.stringify(data.user));
                window.location.href = data.redirectUrl;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
        
    }
}

document.getElementById('mobile').style.display = 'block';
