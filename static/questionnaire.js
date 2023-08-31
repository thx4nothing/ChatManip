import {getSessionIdFromUrl} from "./common.js";

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("rosas-form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(form);
        const data = {};
        let allRangeInputsValid = true

        formData.forEach((value, key) => {
            data[key] = value;

            const inputElement = form.querySelector(`input[name="${key}"]`);
            if (inputElement && inputElement.type === "range" && parseInt(value) <= 0) {
                allRangeInputsValid = false;
            }
            console.log(key, value)
        });
        console.log(data)

        if (!allRangeInputsValid) {
            alert("All range inputs must have values greater than 0.");
            return; // Stop form submission
        }

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

    const rangeInputs = document.querySelectorAll('input[type="range"]');

    rangeInputs.forEach(input => {
        input.addEventListener('input', function () {
            const value = parseInt(this.value);
            const minValue = 1;
            const maxValue = parseInt(this.max);

            // Restrict the value to the range of 1 to 5
            if (value < 1) {
                this.value = minValue;
            } else if (value > 5) {
                this.value = maxValue;
            }

            this.nextElementSibling.textContent = this.value;
        });
    });
});