import {initializeTasksSection} from "./tasks.js";
import {initializeRulesSection} from "./rules.js";
import {initializeInviteCodeSection} from "./invite_codes.js";
import {initializeUserManagementSection} from "./users.js";
import {initializePersonaSection} from "./personas.js";
import {initializeHistorysSection} from "./history.js";
import {getLanguage} from "../common.js";

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

async function initializeLanguage() {
    const languageDropdown = document.getElementById("languageSelect");
    const language = await getLanguage()
    if (language === "en" || language === "de") {
        languageDropdown.value = language;
    }

    languageDropdown.addEventListener("change", function () {
        const selectedLanguage = languageDropdown.value;
        window.location.href = `/chatmanip/admin/${selectedLanguage}?token=${getToken()}`;
    });
}

