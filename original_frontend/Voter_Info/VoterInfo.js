document.addEventListener('DOMContentLoaded', () => {
  // Handle form submission
  document.getElementById('captchaForm').addEventListener('submit', (e) => {
      e.preventDefault();

      const formData = new FormData(e.target);
      const data = Object.fromEntries(formData.entries());
    //   console.log(data);
      const userDetails = JSON.parse(sessionStorage.getItem('userDetails'));
      const loginType = userDetails.loginType;
      console.log(loginType);
      let endpoint = '';
      if (loginType == 'Digilocker') {
        endpoint = '/Digilocker_login/Voter_Info/VoterInfo.html';
      }
      if (loginType === 'voter') {
          endpoint = '/virtual_election/Voter_Info/VoterInfo.html';
      }

      fetch('/Voter_Info', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
      })
      .then(response => response.json())
      .then(result => {
          if (result.hasVoted == 1) {
              alert(result.message);
              logout();
              window.location.href = "/";
          } else if (result.hasVoted == 0) {
              alert(result.message);
              sessionStorage.setItem('userDetails', JSON.stringify(data.user));
              // Conditional redirect based on login type
              // if (loginType === 'Digilocker') {
              //     window.location.href = "/Digilocker_login/Vote/vote.html";
              // } else if (loginType === 'voter') {
              //     window.location.href = "/virtual_election/Vote/vote.html";
              // }
              window.location.href = result.redirectUrl;
          } else {
              // alert(result.message);
              alert("Failed reCAPTCHA verification or another issue occurred");
              window.location.href = '/';
          }
      })
      .catch(err => {
          console.error("Error:", err);
          alert("Something went wrong, please try again later.");
      });
  });

  // Fetch and display user details if logged in
  const userDetails = JSON.parse(sessionStorage.getItem('userDetails'));
  if (!userDetails) {
      alert("You are not logged in.");
      window.location.href = "/";
  } else {
      document.getElementById('voter-id').textContent = userDetails.voter_id;
      document.getElementById('constituency').textContent = userDetails.constituency;
      document.getElementById('aadhaar').textContent = userDetails.aadhaar;
      document.getElementById('dob').textContent = userDetails.dob;
      document.getElementById('full-name').textContent = userDetails.name_of_voter;
      document.getElementById('father-name').textContent = userDetails.name_of_father_of_voter;
      document.getElementById('gender').textContent = userDetails.gender;
      document.getElementById('address').textContent = userDetails.address;
  }
});

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

function logout() {
  fetch('/logout', {
    method: 'POST',
  }).then(response => {
    if (response.ok) {
      // alert("hi");
      console.log('Logged out successfully');
    } else {
      console.error('Logout failed');
    }
  }).catch(error => {
    console.error('Error logging out:', error);
  });
}

window.addEventListener('beforeunload', function(e) {
  alert("refresh");
  navigator.sendBeacon('/logout', JSON.stringify({ user: JSON.parse(sessionStorage.getItem('userDetails')) }));
  window.location.href = "/";
});