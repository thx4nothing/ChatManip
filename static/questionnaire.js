import {getSessionIdFromUrl} from "./common.js";

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("rosas-form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(form);
        const data = {};

        for (const [key, value] of formData.entries()) {
            data[key] = value;
            console.log(key, value)
        }
        console.log(data)
        const session_id = getSessionIdFromUrl("questionnaire");
        const response = await fetch(`/questionnaire/${session_id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            console.log("Form data submitted successfully!");
            window.location.href = `/chat/${session_id}/next`; // Redirect to the next page
        } else {
            console.error("Error submitting form data.");
        }
    });
});

