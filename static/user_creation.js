document.addEventListener("DOMContentLoaded", function () {
    initializeUserCreation()
    initializeLanguage()
});

function initializeLanguage() {
    const languageDropdown = document.getElementById("languageSelect");
    const currentPath = window.location.pathname;
    const parts = currentPath.split("/");
    const language = parts.length >= 2 ? parts[1] : "en";
    const privacyPolicyFrame = document.getElementById('privacyPolicyFrame');

    if (language === "en" || language === "de") {
        languageDropdown.value = language;
        privacyPolicyFrame.src = `/static/privacy_policy_${language}.html`;
    }

    languageDropdown.addEventListener("change", function () {
        const selectedLanguage = languageDropdown.value;
        console.log(selectedLanguage)
        window.location.href = `/${selectedLanguage}`;
    });
}

function initializeUserCreation() {
    const privacyPolicyLink = document.getElementById('privacyPolicyLink');
    const privacyPolicyModal = document.getElementById('privacyPolicyModal');
    const agreeButton = document.getElementById('agreeButton');
    const disagreeButton = document.getElementById('disagreeButton');
    const dataCollectionCheckbox = document.getElementById('dataCollectionCheckbox');
    const queryParams = new URLSearchParams(window.location.search);

    if (queryParams.has('invitecode')) {
        const inviteCodeValue = queryParams.get('invitecode');
        const invite_code = document.getElementById("invite_code");
        if (invite_code) {
            invite_code.value = inviteCodeValue;
        }
    }

    function handleUserSubmit(event) {
        event.preventDefault(); // Prevent form submission

        if (!document.getElementById('dataCollectionCheckbox').checked) {
            alert("Please agree to the data collection terms.");
            return false;
        }

        const age = document.getElementById("age").value;
        const gender = document.getElementById("gender").value;
        const occupation = document.getElementById("occupation").value;
        const location = document.getElementById("location").value;
        const language = document.querySelector('input[name="language"]:checked').value;
        const invite_code = document.getElementById("invite_code").value;

        const userInfo = {
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
                    window.location.href = response.url;
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


