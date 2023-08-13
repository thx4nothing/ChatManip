document.addEventListener("DOMContentLoaded", function () {
    initializeUserCreation()
});


function initializeUserCreation() {
    const privacyPolicyLink = document.getElementById('privacyPolicyLink');
    const privacyPolicyModal = document.getElementById('privacyPolicyModal');
    const agreeButton = document.getElementById('agreeButton');
    const disagreeButton = document.getElementById('disagreeButton');
    const dataCollectionCheckbox = document.getElementById('dataCollectionCheckbox');

    function handleUserSubmit(event) {
        event.preventDefault(); // Prevent form submission

        if (!document.getElementById('dataCollectionCheckbox').checked) {
            alert("Please agree to the data collection terms.");
            return false;
        }

        var age = document.getElementById("age").value;
        var gender = document.getElementById("gender").value;
        var occupation = document.getElementById("occupation").value;
        var location = document.getElementById("location").value;
        var language = document.querySelector('input[name="language"]:checked').value;
        var invite_code = document.getElementById("invite_code").value;

        var userInfo = {
            age: age,
            gender: gender,
            occupation: occupation,
            location: location,
            language: language,
            invite_code: invite_code
        };

        fetch("/create_user", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userInfo)
        })
            .then(response => {
                if (response.redirected) {
                    // Get the redirect URL from the response headers
                    const redirectUrl = response.url;

                    // Manually redirect the user to the new URL
                    window.location.href = redirectUrl;
                }
            })
            .catch(error => {
                console.error("Error creating user:", error);
            });

        // Reset the form
        document.getElementById("userForm").reset();
    }

    privacyPolicyLink.addEventListener('click', function () {
        privacyPolicyModal.classList.add('is-visible');
    });

    agreeButton.addEventListener('click', function () {
        dataCollectionCheckbox.checked = true;
        privacyPolicyModal.classList.remove('is-visible');
    });

    disagreeButton.addEventListener('click', function () {
        dataCollectionCheckbox.checked = false;
        privacyPolicyModal.classList.remove('is-visible');
    });

    document.getElementById("userForm").addEventListener("submit", handleUserSubmit);
}


