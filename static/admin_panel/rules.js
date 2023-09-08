import {getToken} from "./admin_panel.js";

export function initializeRulesSection() {
    function populateRulesTable(rules) {
        const rulesTable = document.getElementById("rulesTable");
        while (rulesTable.rows.length > 1) {
            rulesTable.deleteRow(1);
        }

        rules.forEach(rule => {
            const row = rulesTable.insertRow();
            row.insertCell().textContent = rule.name;
            row.insertCell().textContent = rule.description;
        });
    }

    function getRules() {
        fetch(`/admin/rules/?token=${getToken()}`)
            .then(response => response.json())
            .then(data => {
                console.log("Rules:", data);
                populateRulesTable(data);
            })
            .catch(error => {
                console.error("Error fetching rules:", error);
            });
    }

    getRules();
}