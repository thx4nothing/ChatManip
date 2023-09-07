import {getSessionIdFromUrl} from "./common.js";

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("rosas-form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            data[key] = value;
        });
        console.log(data)

        const session_id = getSessionIdFromUrl("questionnaire");
        const time = window.location.pathname.includes("before") ? "before" : "after";

        const response = await fetch(`/questionnaire/${session_id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            console.log("Form data submitted successfully!");
            const response = await fetch(`/questionnaire/${session_id}/show_discussion`);
            if (response.ok) {
                const data = await response.json();
                const show_discussion = data.show_discussion_section;
                if (show_discussion) {
                    window.location.href = `/questionnaire/${session_id}/after`; // Redirect to the 2nd page
                } else {
                    window.location.href = `/chat/${session_id}/next`; // Redirect to the next page
                }
            } else {
                window.location.href = `/chat/${session_id}/next`;
            }

        } else {
            console.error("Error submitting form data.");
        }
    });
});