let userDetailsString = {}

document.addEventListener('DOMContentLoaded', (event) => {
    userDetailsString = sessionStorage.getItem('userDetails');
    // console.log(userDetailsString);
    if (!userDetailsString) {
        alert("You are not logged in.");
        window.location.href = "/";
        return; 
    }

    setTimeout(() => {
        alert("You have been on this page for 5 minutes. Redirecting to homepage.");
        logout();
        window.location.href = "/";
    }, 300000);
});

function selectCandidate(button) {
    const rows = document.querySelectorAll('.candidates-table tbody tr');
    rows.forEach(row => {
        row.querySelector('.radio').style.backgroundColor = 'white';
        row.querySelector('.radio').removeAttribute('data-selected');
    });
    const row = button.parentNode.parentNode;
    const radio = row.querySelector('.radio');
    radio.style.backgroundColor = 'red';
    radio.setAttribute('data-selected', 'true');
}

// const userDetails = JSON.parse(sessionStorage.getItem('userDetails'));
// alert(userDetails);
// if (!userDetails) {
//     alert("You are not logged in.");
//     window.location.href = "/";
// }

function submitVote(event) {
    event.preventDefault();
    const selectedCandidateElement = document.querySelector('.radio[data-selected="true"]');
    if (!selectedCandidateElement) {
        alert('Please select a candidate before proceeding.');
        return;
    }
    
    const selectedCandidate = selectedCandidateElement.getAttribute('data-candidate');
    const selectedparty = selectedCandidateElement.getAttribute('data-party');
    console.log(selectedparty);
    const jsonData = {};
    jsonData['candidate']=selectedCandidate;
    jsonData['party']=selectedparty;
    const confirmation = confirm(`Are you sure you want to vote for ${selectedCandidate}?`);

    if (confirmation) {
        document.getElementById('proceedButton').disabled = true;
        alert('Your vote has been submitted successfully!');

        // userDetailsString = JSON.parse(sessionStorage.getItem('userDetails'));
        // const loginType = userDetailsString.loginType;
        // console.log(userDetailsString);
        // let endpoint = '';
        // if (loginType == 'Digilocker') {
        //     endpoint = '/Digilocker_login/Voter_Info/VoterInfo.html';
        // }
        // if (loginType === 'voter') {
        //     endpoint = '/virtual_election/Voter_Info/VoterInfo.html';
        // }

        fetch('/vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data.message);
            logout();
            window.location.href = "/";
        })
        .catch(err => {
            console.log(err);
            alert("An error occurred. Please try again.");
            document.getElementById('proceedButton').disabled = false;
        });
    }
    
};

document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault(); 
        fetch('/logout', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Leaving!");
                    window.location.href = this.href; 
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
        console.log('Logged out successfully');
    } else {
        console.error('Logout failed');
    }
    }).catch(error => {
    console.error('Error logging out:', error);
    });
}

window.addEventListener('beforeunload', function(e) {
    // if (faceMonitorWindow) {
    //     faceMonitorWindow.close();
    // }
    navigator.sendBeacon('/logout', JSON.stringify({ user: JSON.parse(sessionStorage.getItem('userDetails')) }));
});