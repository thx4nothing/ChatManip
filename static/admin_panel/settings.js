import {getToken} from "./admin_panel.js";

document.addEventListener("DOMContentLoaded", () => {
    fetchSettings();

    const saveSettingsBtn = document.getElementById("saveSettingsBtn");
    saveSettingsBtn.addEventListener("click", saveSettings);
});

function fetchSettings() {
    fetch(`/admin/settings/model?token=${getToken()}`)
        .then(response => response.json())
        .then(data => {
            const modelSelect = document.getElementById("modelSelect");
            console.log(data)
            modelSelect.value = data;
        })
        .catch(error => console.error("Error fetching model settings:", error));

    fetch(`/admin/settings/temperature?token=${getToken()}`)
        .then(response => response.json())
        .then(data => {
            const temperatureInput = document.getElementById("temperatureInput");
            temperatureInput.value = data;
        })
        .catch(error => console.error("Error fetching temperature settings:", error));
}

function saveSettings() {
    const modelSelect = document.getElementById("modelSelect");
    const selectedModel = modelSelect.value;

    const temperatureInput = document.getElementById("temperatureInput");
    const selectedTemperature = parseFloat(temperatureInput.value);

    fetch(`/admin/settings/model?token=${getToken()}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({model: selectedModel}),
    })
        .catch(error => console.error("Error saving model settings:", error));

    fetch(`/admin/settings/temperature?token=${getToken()}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({temperature: selectedTemperature}),
    })
        .catch(error => console.error("Error saving temperature settings:", error));
}
