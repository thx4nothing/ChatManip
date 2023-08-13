import {initializeTasksSection} from "./tasks.js";
import {initializeRulesSection} from "./rules.js";
import {initializeInviteCodeSection} from "./invite_codes.js";
import {initializeUserManagementSection} from "./users.js";
import {initializePersonaSection} from "./personas.js";

document.addEventListener("DOMContentLoaded", function () {
    initializePersonaSection();
    initializeUserManagementSection();
    initializeInviteCodeSection();
    initializeRulesSection();
    initializeTasksSection();
});

export function getToken() {
    const urlSearchParams = new URLSearchParams(window.location.search);
    return urlSearchParams.get("token")
}