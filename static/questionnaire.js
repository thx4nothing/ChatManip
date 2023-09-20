import {getLanguage, getSessionIdFromUrl, getTranslation} from "./common.js";

document.addEventListener("DOMContentLoaded", async function () {
    const form = document.getElementById("rosas-form");
    const translations = await getTranslation(await getLanguage("questionnaire"), "questionnaire");

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

        async function getNextSession() {
            const response = await fetch(`/questionnaire/${session_id}/has_next`)
            const data = await response.json();
            console.log(data)
            if (data.has_next) {
                window.alert(translations.next_session_info)
            }
            window.location.href = `/chat/${session_id}/next`;
        }

        if (response.ok) {
            console.log("Form data submitted successfully!");
            const response = await fetch(`/questionnaire/${session_id}/show_discussion`);
            if (response.ok) {
                const data = await response.json();
                const show_discussion = data.show_discussion_section;
                if (show_discussion) {
                    window.location.href = `/questionnaire/${session_id}/after`;
                } else {
                    await getNextSession();
                }
            } else {
                await getNextSession();
            }

        } else {
            console.error("Error submitting form data.");
        }
    });


});