async function handleSubmit(event) {
    event.preventDefault();
    const epicno = document.getElementById('epicno').value;
    const phone = document.getElementById('phone').value;

    const response = await fetch('/voter-login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ epicno, phone })
    });

    const data = await response.json();

    if (data.success) {
        document.querySelector('form.info').style.display = 'none';
        document.getElementById('otpSection').style.display = 'block';
    } else {
        alert(data.message);
        window.location.reload();
    }
}

function phoneEmailListener(userObj) {
    var user_json_url = userObj.user_json_url;
    fetch('/virtual_election/verify_otp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_json_url })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // console.log("success");
            sessionStorage.setItem('userDetails', JSON.stringify(data.user));
            window.location.href = data.redirectUrl;
        } else {
            alert(data.message);
            window.location.href = data.redirectUrl;
        }
    })
    .catch(err => {
        console.error(err);
        alert('An error occurred. Please try again.');
        window.location.href = "/";
    });
}

document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent the default link action
        // Perform logout
        fetch('/logout', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = this.href; // Navigate to the link after logging out
                } else {
                    alert('Failed to log out');
                }
            })
            .catch(error => console.error('Error:', error));
    });
  });