// document.getElementById('signup-form').addEventListener('submit', handleSubmit);

function handleSubmit(event) {
    event.preventDefault();
    
    const form = document.getElementById('signup-form');
    const formData = new FormData(form);
    const jsonData = {};

    formData.forEach((value, key) => {
        jsonData[key] = value;
    });

    fetch('/Digilocker-login/Sign-up', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        window.location.reload();
        if (data.redirectUrl) {
            window.location.href = data.redirectUrl;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

$(document).ready(function(){
    function addOptions(select, start, end) {
        for (var i = start; i <= end; i++) {
            var option = $("<option>").val(i).text(i);
            select.append(option);
        }
    }

    var daysSelect = $("#dob-day");
    addOptions(daysSelect, 1, 31);

    var monthsSelect = $("#dob-month");
    var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    for (var i = 0; i < months.length; i++) {
        var option = $("<option>").val(i + 1).text(months[i]);
        monthsSelect.append(option);
    }

    var yearsSelect = $("#dob-year");
    var currentYear = new Date().getFullYear();
    addOptions(yearsSelect, currentYear - 100, currentYear);
});

document.addEventListener("DOMContentLoaded", function() {
    var mobileInput = document.getElementById("mobile");
    
    mobileInput.addEventListener("input", function() {
        var mobileNumber = this.value.trim(); 
        
        mobileNumber = mobileNumber.replace(/\D/g, "");
        
        if (/^\d{10}$/.test(mobileNumber)) {
            this.setCustomValidity(""); 
        } else {
            this.setCustomValidity("Mobile number must be 10 digits long");
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    var aadhaarInput = document.getElementById("Aadhaar");
    
    aadhaarInput.addEventListener("input", function() {
        var aadhaarNumber = this.value.trim(); 
        
        aadhaarNumber = aadhaarNumber.replace(/\D/g, "");
        
        if (/^\d{12}$/.test(aadhaarNumber)) {
            this.setCustomValidity(""); 
        } else {
            this.setCustomValidity("Aadhaar number must be 12 digits long");
        }
    });
});

// document.addEventListener("DOMContentLoaded", function() {
//     var aadhaarInput = document.getElementById("pin");
    
//     aadhaarInput.addEventListener("input", function() {
//         var aadhaarNumber = this.value.trim(); 
        
//         aadhaarNumber = aadhaarNumber.replace(/\D/g, "");
        
//         if (/^\d{6}$/.test(aadhaarNumber)) {
//             this.setCustomValidity(""); 
//         } else {
//             this.setCustomValidity("pin number must be 6 digits long");
//         }
//     });
// });
