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


        async function getNextSession() {
            const response = await fetch(`/chatmanip/questionnaire/${session_id}/has_next`)
            const data = await response.json();
            console.log(data)
            if (data.has_next) {
                window.alert(translations.next_session_info)
            }
            window.location.href = `/chatmanip/${session_id}/next`;
        }

        const session_id = getSessionIdFromUrl("questionnaire");
        const time = window.location.pathname.includes("before") ? "before" : "after";

        const response = await fetch(`/chatmanip/questionnaire/${session_id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });


        if (response.ok) {
            console.log("Form data submitted successfully!");
            if (time !== "after") {
                window.location.href = `/chatmanip/questionnaire/${session_id}/after`;
            } else {
                await getNextSession();
            }

        } else {
            console.error("Error submitting form data.");
        }
    });


});