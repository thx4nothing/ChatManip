import {getToken} from "./admin_panel.js";

export function initializeInviteCodeSection() {
    const generateCodesBtn = document.getElementById("generateCodesBtn");
    const numCodesInput = document.getElementById("numCodes");
    const inviteCodesTable = document.getElementById("inviteCodesTable");

    function populateInviteCodesTable(inviteCodes) {
        while (inviteCodesTable.rows.length > 1) {
            inviteCodesTable.deleteRow(1);
        }

        inviteCodes.forEach(inviteCode => {
            const row = inviteCodesTable.insertRow();
            row.insertCell().textContent = inviteCode.invite_code;
            row.insertCell().textContent = inviteCode.user_id === -1 ? "Not used" : inviteCode.user_id;
            const personaCell = row.insertCell();
            const taskCell = row.insertCell();
            const historyCell = row.insertCell();
            const rulesCell = row.insertCell();
            const nextSessionIDCell = row.insertCell();
            const saveCell = row.insertCell();
            const deleteCell = row.insertCell();

            // Create dropdown for Persona
            const personaDropdown = document.createElement("select");
            fetch(`/admin/personas?token=${getToken()}`)
                .then(response => response.json())
                .then(personas => {
                    personas.forEach(persona => {
                        const option = document.createElement("option");
                        option.value = persona.persona_id;
                        option.textContent = persona.name;
                        personaDropdown.appendChild(option);
                    });
                    personaDropdown.value = inviteCode.persona_id || "";
                })
                .catch(error => {
                    console.error("Error fetching personas:", error);
                });
            personaCell.appendChild(personaDropdown);

            // Create dropdown for Tasks
            const taskDropdown = document.createElement("select");
            fetch(`/admin/tasks?token=${getToken()}`)
                .then(response => response.json())
                .then(tasks => {
                    tasks.forEach(task => {
                        const option = document.createElement("option");
                        option.value = task.task_id;
                        option.textContent = task.name;
                        taskDropdown.appendChild(option);
                    });
                    taskDropdown.value = inviteCode.task_id || "";
                })
                .catch(error => {
                    console.error("Error fetching tasks:", error);
                });
            taskCell.appendChild(taskDropdown);

            // Create dropdown for History
            const historyDropdown = document.createElement("select");
            fetch(`/admin/history?token=${getToken()}`)
                .then(response => response.json())
                .then(histories => {
                    histories.forEach(history => {
                        const option = document.createElement("option");
                        option.value = history.history_id;
                        option.textContent = history.name;
                        historyDropdown.appendChild(option);
                    });
                    historyDropdown.value = inviteCode.history_id || "";
                })
                .catch(error => {
                    console.error("Error fetching tasks:", error);
                });
            historyCell.appendChild(historyDropdown);

            // Create textbox for Rules
            const rulesTextbox = document.createElement("input");
            rulesTextbox.type = "text";
            rulesTextbox.placeholder = "Enter a comma separated list of rules";
            rulesTextbox.value = inviteCode.rules ? inviteCode.rules : "";
            rulesCell.appendChild(rulesTextbox);

            // Create dropdown for nextSessionID
            const nextSessionIDDropdown = document.createElement("select");
            fetch(`/admin/invite_codes?token=${getToken()}`)
                .then(response => response.json())
                .then(invite_codes => {
                    const option = document.createElement("option");
                    option.value = "none";
                    option.textContent = "none";
                    nextSessionIDDropdown.appendChild(option);
                    invite_codes.forEach(invite_code => {
                        if (invite_code.invite_code !== inviteCode.invite_code) {
                            const option = document.createElement("option");
                            option.value = invite_code.invite_code;
                            option.textContent = invite_code.invite_code;
                            nextSessionIDDropdown.appendChild(option);
                        }
                    });
                    nextSessionIDDropdown.value = inviteCode.next_session_id || "";
                })
                .catch(error => {
                    console.error("Error fetching nextSessionID:", error);
                });
            nextSessionIDCell.appendChild(nextSessionIDDropdown);

            // Create save button
            if (!inviteCode.used) {
                const saveBtn = document.createElement("button");
                saveBtn.textContent = "Save";
                saveBtn.addEventListener("click", () => {
                    const rules = rulesTextbox.value.trim();
                    let personaDropdownValue = parseInt(personaDropdown.value)
                    let persona_id = isNaN(personaDropdownValue) ? -1 : personaDropdownValue
                    let taskDropdownValue = parseInt(taskDropdown.value)
                    let historyDropdownValue = parseInt(historyDropdown.value)
                    let task_id = isNaN(taskDropdownValue) ? -1 : taskDropdownValue
                    let history_id = isNaN(historyDropdownValue) ? -1 : historyDropdownValue
                    let next_session_id = nextSessionIDDropdown.value
                    updateInviteCode(inviteCode.invite_code, persona_id, task_id, history_id, rules, next_session_id);
                });
                saveCell.appendChild(saveBtn);
            }

            // Create delete button
            if (!inviteCode.used) {
                const deleteBtn = document.createElement("button");
                deleteBtn.textContent = "Delete";
                deleteBtn.addEventListener("click", () => deleteInviteCode(inviteCode.invite_code));
                deleteCell.appendChild(deleteBtn);
            }
        });
    }

    function generateInviteCodes() {
        const numCodes = numCodesInput.value;
        fetch(`/admin/invite_codes?num_codes=${numCodes}&token=${getToken()}`, {
            method: "POST"
        })
            .then(response => response.json())
            .then(data => {
                console.log("Generated codes:", data);
                getInviteCodes();
            })
            .catch(error => {
                console.error("Error generating codes:", error);
            });
    }

    function deleteInviteCode(inviteCode) {
        fetch(`/admin/invite_codes/${inviteCode}?token=${getToken()}`, {
            method: "DELETE"
        })
            .then(response => response.json())
            .then(data => {
                console.log("Deleted code:", data);
                getInviteCodes();
            })
            .catch(error => {
                console.error("Error deleting code:", error);
            });
    }

    function getInviteCodes() {
        fetch(`/admin/invite_codes?token=${getToken()}`)
            .then(response => response.json())
            .then(data => {
                console.log("Invite codes:", data);
                populateInviteCodesTable(data);
            })
            .catch(error => {
                console.error("Error fetching invite codes:", error);
            });
    }

    function updateInviteCode(inviteCode, persona_id, task_id, history_id, rules, next_session_id) {
        const queryParams = new URLSearchParams({
            persona_id: parseInt(persona_id),
            task_id: parseInt(task_id),
            history_id: parseInt(history_id),
            rules: rules,
            next_session_id: next_session_id
        });
        fetch(`/admin/invite_codes/${inviteCode}?${queryParams}&token=${getToken()}`, {
            method: "PATCH", headers: {
                "Content-Type": "application/json"
            },
        })
            .then(response => response.json())
            .then(data => {
                console.log("Updated invite code:", data);
                getInviteCodes();
            })
            .catch(error => {
                console.error("Error updating invite code:", error);
            });
    }

    generateCodesBtn.addEventListener("click", generateInviteCodes);
    getInviteCodes();
}