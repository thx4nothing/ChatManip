import {initializeTasksSection} from "./tasks.js";
import {initializeRulesSection} from "./rules.js";
import {initializeInviteCodeSection} from "./invite_codes.js";
import {initializeUserManagementSection} from "./users.js";
import {initializePersonaSection} from "./personas.js";
import {initializeHistorysSection} from "./history.js";

document.addEventListener("DOMContentLoaded", function () {
    initializePersonaSection();
    initializeUserManagementSection();
    initializeInviteCodeSection();
    initializeRulesSection();
    initializeTasksSection();
    initializeHistorysSection();
    initializeLanguage();
});

export function getToken() {
    const urlSearchParams = new URLSearchParams(window.location.search);
    return urlSearchParams.get("token")
}

function initializeLanguage() {
    const languageDropdown = document.getElementById("languageSelect");
    const language = getLanguage()
    if (language === "en" || language === "de") {
        languageDropdown.value = language;
    }

    languageDropdown.addEventListener("change", function () {
        const selectedLanguage = languageDropdown.value;
        console.log(selectedLanguage)
        window.location.href = `/admin/${selectedLanguage}/?token=${getToken()}`;
    });
}

export function getLanguage() {
    const currentPath = window.location.pathname;
    const parts = currentPath.split("/");
    return parts.length >= 3 ? parts[2] : "en"
}

export async function getTranslation(language) {
    const translationEndpoint = `/admin/translations/${language}`;

    try {
        const response = await fetch(translationEndpoint);
        return await response.json();
    } catch (error) {
        console.error("Error fetching translation data:", error);
        return null;
    }
}
