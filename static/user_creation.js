import {getLanguage, getTranslation} from "./common.js";

document.addEventListener("DOMContentLoaded", function () {
    initializeUserCreation().then()
    initializeLanguage()
});

async function initializeLanguage() {
    const languageDropdown = document.getElementById("languageSelect");
    const currentPath = window.location.pathname;
    const parts = currentPath.split("/");
    const language = await getLanguage()
    const privacyPolicyFrame = document.getElementById('privacyPolicyFrame');

    if (language === "en" || language === "de") {
        languageDropdown.value = language;
        privacyPolicyFrame.src = `/chatmanip/static/privacy_policy_${language}.html`;
    }

    languageDropdown.addEventListener("change", function () {
        const selectedLanguage = languageDropdown.value;
        const inviteCodeInput = document.getElementById("invite_code");
        const inviteCodeValue = inviteCodeInput.value;
        window.location.href = `/${selectedLanguage}?invitecode=${encodeURIComponent(inviteCodeValue)}`;

    });
}

async function initializeUserCreation() {
    const privacyPolicyLink = document.getElementById('privacyPolicyLink');
    const privacyPolicyModal = document.getElementById('privacyPolicyModal');
    const agreeButton = document.getElementById('agreeButton');
    const disagreeButton = document.getElementById('disagreeButton');
    const dataCollectionCheckbox = document.getElementById('dataCollectionCheckbox');
    const queryParams = new URLSearchParams(window.location.search);
    const translations = await getTranslation(await getLanguage(), "user_creation");

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
            alert(translations.privacy_alert);
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

        fetch("/chatmanip/create_user", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userInfo)
        })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    alert(translations.invalid_invite_code_error);
                    return false;
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


