document.addEventListener("DOMContentLoaded", function () {
    const proceedButton = document.getElementById("proceedButton");
    const warningModal = document.getElementById("warningModal");
    const confirmationCheckbox = document.getElementById("confirmationCheckbox");
    const confirmButton = document.getElementById("confirmButton");
    const closeButton = document.getElementById("closeButton");


    proceedButton.addEventListener("click", function () {
        warningModal.classList.add('is-visible');
    });

    confirmButton.addEventListener("click", function () {
        if (confirmationCheckbox.checked) {
            const session_id = getSessionIdFromUrl();
            window.location.href = `/chat/${session_id}/next`;
        } else {
            alert("Please confirm that you have submitted the questionnaire.");
        }
    });
    closeButton.addEventListener("click", function () {
        warningModal.classList.remove('is-visible');
    });
});

function getSessionIdFromUrl() {
    const path = window.location.pathname;
    const parts = path.split('/');
    const sessionIdIndex = parts.indexOf('chat'); // Find the index of 'session' in the path
    if (sessionIdIndex !== -1 && sessionIdIndex < parts.length - 1) {
        // If 'session' is found and the session_id is present in the next part of the path
        return parts[sessionIdIndex + 1]; // Return the session_id
    }
    return null; // If session_id is not found, return null
}