document.addEventListener("DOMContentLoaded", function () {
    initializePersonaSection();
    initializeUserManagementSection();
    initializeInviteCodeSection();
    initializeRulesSection();
});

function getToken() {
    const urlSearchParams = new URLSearchParams(window.location.search);
    return urlSearchParams.get("token")
}

function initializePersonaSection() {
    const personaDropdown = document.getElementById("personaDropdown");
    const createNewBtn = document.getElementById("createNewBtn");
    const editSelectedBtn = document.getElementById("editSelectedBtn");
    const deleteSelectedBtn = document.getElementById("deleteSelectedBtn");
    const personaForm = document.getElementById("personaForm");
    const personaName = document.getElementById("personaName");
    const savePersonaBtn = document.getElementById("savePersonaBtn");
    const addLanguageBtn = document.getElementById("addLanguageBtn");
    const languageInputs = document.getElementById("languageInputs");

    function populatePersonaDetails(persona) {
        const personaNameSpan = document.getElementById("personaNameD");
        const personaDetailsContainer = document.getElementById("personaDetails");

        personaNameSpan.textContent = persona.name;

        while (personaDetailsContainer.children.length > 2) {
            personaDetailsContainer.removeChild(personaDetailsContainer.lastChild);
        }
        console.log(persona)
        for (const language in persona.system_instruction) {
            const languageDiv = document.createElement("div");
            languageDiv.classList.add("language-row");

            const languageName = document.createElement("p");
            languageName.textContent = "Language: " + language;
            languageDiv.appendChild(languageName);

            const systemInstruction = document.createElement("p");
            systemInstruction.textContent = `System Instruction: ${persona.system_instruction[language] || ""}`;
            languageDiv.appendChild(systemInstruction);

            const instructionBefore = document.createElement("p");
            instructionBefore.textContent = `Instruction Before: ${persona.before_instruction[language] || ""}`;
            languageDiv.appendChild(instructionBefore);

            const instructionAfter = document.createElement("p");
            instructionAfter.textContent = `Instruction After: ${persona.after_instruction[language] || ""}`;
            languageDiv.appendChild(instructionAfter);

            personaDetailsContainer.appendChild(languageDiv);
        }
    }


    function populatePersonaDropdown() {
        fetch(`/admin/personas?token=${getToken()}`)
            .then(response => response.json())
            .then(personas => {
                personaDropdown.innerHTML = "";
                personas.forEach(persona => {
                    const option = document.createElement("option");
                    option.value = persona.persona_id;
                    option.textContent = persona.name;
                    personaDropdown.appendChild(option);
                });
                handlePersonaDropdownChange();
            })
            .catch(error => {
                console.error("Error fetching personas:", error);
            });
    }

    function handleCreateNewClick() {
        personaDropdown.selectedIndex = -1;
        personaForm.classList.remove("hidden");
        personaName.value = "";

        // Clear existing language rows
        const languageContainer = document.getElementById("languageInputs");
        languageContainer.innerHTML = '';

        // Create a single row for the language
        const row = document.createElement("div");
        row.classList.add("language-input-row");

        const languageInput = document.createElement("input");
        languageInput.type = "text";
        languageInput.classList.add("language-name");
        languageInput.placeholder = "english or german";

        const systemInstructionInput = document.createElement("input");
        systemInstructionInput.type = "text";
        systemInstructionInput.classList.add("system-instruction");
        systemInstructionInput.placeholder = "System Instruction";

        const instructionBeforeInput = document.createElement("input");
        instructionBeforeInput.type = "text";
        instructionBeforeInput.classList.add("instruction-before");
        instructionBeforeInput.placeholder = "Instruction before User Message";

        const instructionAfterInput = document.createElement("input");
        instructionAfterInput.type = "text";
        instructionAfterInput.classList.add("instruction-after");
        instructionAfterInput.placeholder = "Instruction after User Message";

        row.appendChild(languageInput);
        row.appendChild(systemInstructionInput);
        row.appendChild(instructionBeforeInput);
        row.appendChild(instructionAfterInput);

        languageContainer.appendChild(row);
    }

    function handleEditSelectedClick() {
        const selectedPersonaId = personaDropdown.value;
        if (selectedPersonaId) {
            fetch(`/admin/personas/${selectedPersonaId}?token=${getToken()}`)
                .then(response => response.json())
                .then(persona => {
                    personaName.value = persona.name;
                    const availableLanguages = Object.keys(persona.system_instruction);
                    const languageContainer = document.getElementById("languageInputs");
                    languageContainer.innerHTML = '';
                    availableLanguages.forEach(language => {
                        const row = document.createElement("div");
                        row.classList.add("language-input-row");

                        const languageInput = document.createElement("input");
                        languageInput.type = "text";
                        languageInput.classList.add("language-name");
                        languageInput.placeholder = "english or german";
                        languageInput.value = language;

                        const systemInstructionInput = document.createElement("input");
                        systemInstructionInput.type = "text";
                        systemInstructionInput.classList.add("system-instruction");
                        systemInstructionInput.placeholder = "System Instruction";
                        systemInstructionInput.value = persona.system_instruction[language] || "";

                        const instructionBeforeInput = document.createElement("input");
                        instructionBeforeInput.type = "text";
                        instructionBeforeInput.classList.add("instruction-before");
                        instructionBeforeInput.placeholder = "Instruction before User Message";
                        instructionBeforeInput.value = persona.before_instruction[language] || "";

                        const instructionAfterInput = document.createElement("input");
                        instructionAfterInput.type = "text";
                        instructionAfterInput.classList.add("instruction-after");
                        instructionAfterInput.placeholder = "Instruction after User Message";
                        instructionAfterInput.value = persona.after_instruction[language] || "";

                        row.appendChild(languageInput);
                        row.appendChild(systemInstructionInput);
                        row.appendChild(instructionBeforeInput);
                        row.appendChild(instructionAfterInput);

                        languageContainer.appendChild(row);
                    });

                    personaForm.classList.remove("hidden");
                })
                .catch(error => {
                    console.error("Error fetching selected persona:", error);
                });
        }
    }

    function handleDeleteSelectedClick() {
        const selectedPersonaId = personaDropdown.value;
        if (selectedPersonaId) {
            fetch(`/admin/personas/${selectedPersonaId}?token=${getToken()}`, {
                method: "DELETE"
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                    populatePersonaDropdown();
                    personaForm.classList.add("hidden");
                })
                .catch(error => {
                    console.error("Error deleting persona:", error);
                });
        }
    }

    function handleSavePersonaClick() {
        const selectedPersonaId = personaDropdown.value;
        const personaData = {
            name: personaName.value,
            system_instruction: {},
            before_instruction: {},
            after_instruction: {}
        };

        const languageRows = document.querySelectorAll(".language-input-row");
        languageRows.forEach(row => {
            const language = row.querySelector(".language-name").value;
            const systemInstruction = row.querySelector(".system-instruction").value;
            const instructionBefore = row.querySelector(".instruction-before").value;
            const instructionAfter = row.querySelector(".instruction-after").value;

            personaData.system_instruction[language] = systemInstruction;
            personaData.before_instruction[language] = instructionBefore;
            personaData.after_instruction[language] = instructionAfter;
        });

        const fetchOptions = {
            method: selectedPersonaId ? "PUT" : "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(personaData)
        };

        const url = selectedPersonaId ? `/admin/personas/${selectedPersonaId}?token=${getToken()}` : `/admin/personas?token=${getToken()}`;

        fetch(url, fetchOptions)
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                populatePersonaDropdown();
                personaForm.classList.add("hidden");
            })
            .catch(error => {
                console.error(selectedPersonaId ? "Error updating persona:" : "Error creating persona:", error);
            });
    }

    function handlePersonaDropdownChange() {
        const selectedPersonaId = personaDropdown.value;
        const isPersonaSelected = selectedPersonaId !== "-1"; // Check if a valid persona is selected
        editSelectedBtn.disabled = !isPersonaSelected; // Enable/disable "Edit Selected" button
        deleteSelectedBtn.disabled = !isPersonaSelected; // Enable/disable "Delete Selected" button
        if (selectedPersonaId) {
            fetch(`/admin/personas/${selectedPersonaId}?token=${getToken()}`)
                .then(response => response.json())
                .then(persona => {
                    populatePersonaDetails(persona);
                    personaForm.classList.add("hidden");
                })
                .catch(error => {
                    console.error("Error fetching selected persona:", error);
                });
        }
    }

    function exportPersonaDatabase() {
        fetch(`/admin/personas/export?token=${getToken()}`, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                const beautifiedJson = JSON.stringify(data, null, 2);
                const blob = new Blob([beautifiedJson], {type: 'application/json'});
                const url = URL.createObjectURL(blob);

                const a = document.createElement('a');
                a.href = url;
                a.download = 'personas_export.json';
                a.click();

                URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Error exporting persona database:', error);
            });
    }

    function importPersonaDatabase(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch(`/admin/personas/import?token=${getToken()}`, {
            method: 'POST',
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                console.log('Import successful:', data);
                populatePersonaDropdown();
            })
            .catch(error => {
                console.error('Error importing persona database:', error);
            });
    }

    function handleAddLanguageClick() {
        const newRow = document.createElement("div");
        newRow.classList.add("language-input-row");

        const languageNameInput = document.createElement("input");
        languageNameInput.type = "text";
        languageNameInput.classList.add("language-name");
        languageNameInput.placeholder = "english or german";

        const systemInstructionInput = document.createElement("input");
        systemInstructionInput.type = "text";
        systemInstructionInput.classList.add("system-instruction");
        systemInstructionInput.placeholder = "System Instruction";

        const instructionBeforeInput = document.createElement("input");
        instructionBeforeInput.type = "text";
        instructionBeforeInput.classList.add("instruction-before");
        instructionBeforeInput.placeholder = "Instruction before User Message";

        const instructionAfterInput = document.createElement("input");
        instructionAfterInput.type = "text";
        instructionAfterInput.classList.add("instruction-after");
        instructionAfterInput.placeholder = "Instruction after User Message";

        newRow.appendChild(languageNameInput);
        newRow.appendChild(systemInstructionInput);
        newRow.appendChild(instructionBeforeInput);
        newRow.appendChild(instructionAfterInput);

        languageInputs.appendChild(newRow);
    }

    addLanguageBtn.addEventListener("click", handleAddLanguageClick);
    createNewBtn.addEventListener("click", handleCreateNewClick);
    editSelectedBtn.addEventListener("click", handleEditSelectedClick);
    deleteSelectedBtn.addEventListener("click", handleDeleteSelectedClick);
    savePersonaBtn.addEventListener("click", handleSavePersonaClick);
    personaDropdown.addEventListener("change", handlePersonaDropdownChange);

    document.getElementById('exportPersonaBtn').addEventListener('click', exportPersonaDatabase);

    document.getElementById('importPersonaBtn').addEventListener('click', () => {
        const importPersonaInput = document.getElementById('importPersonaInput');
        importPersonaInput.click();
    });

    document.getElementById('importPersonaInput').addEventListener('change', event => {
        const file = event.target.files[0];
        if (file) {
            importPersonaDatabase(file);
        }
    });

    populatePersonaDropdown();
}

function initializeUserManagementSection() {

    function populateUserTable() {
        const userTableDiv = document.getElementById("userTable");

        while (userTableDiv.rows.length > 1) {
            userTableDiv.deleteRow(1);
        }

        fetch(`/admin/users?token=${getToken()}`)
            .then(response => response.json())
            .then(users => {
                users.forEach(user => {
                    const row = userTableDiv.insertRow();
                    row.insertCell().textContent = user.age;
                    row.insertCell().textContent = user.gender;
                    row.insertCell().textContent = user.occupation;
                    row.insertCell().textContent = user.location;
                    row.insertCell().textContent = user.language;
                    row.insertCell().textContent = user.user_id;
                    row.insertCell().textContent = user.api_prompt_tokens;
                    row.insertCell().textContent = user.api_completion_tokens;
                    row.insertCell().textContent = user.api_total_tokens;

                    const deleteBtn = document.createElement("button");
                    deleteBtn.textContent = "Delete";
                    deleteBtn.addEventListener("click", () => deleteUser(user.user_id));
                    row.insertCell().appendChild(deleteBtn);
                });
            })
            .catch(error => {
                console.error("Error fetching users:", error);
            });
    }


    // Button to handle user deletion
    function deleteUser(userId) {
        fetch(`/admin/users/delete/${userId}?token=${getToken()}`, {
            method: "DELETE"
        })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                populateUserTable(); // Refresh the user list after deletion
            })
            .catch(error => {
                console.error("Error deleting user:", error);
            });
    }

    // Call the functions when the page loads
    populateUserTable();
}

function initializeInviteCodeSection() {
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
            const rulesCell = row.insertCell();
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

            // Create textbox for Rules
            const rulesTextbox = document.createElement("input");
            rulesTextbox.type = "text";
            rulesTextbox.placeholder = "Enter a comma separated list of rules";
            rulesTextbox.value = inviteCode.rules ? inviteCode.rules : "";
            rulesCell.appendChild(rulesTextbox);

            // Create save button
            if (!inviteCode.used) {
                const saveBtn = document.createElement("button");
                saveBtn.textContent = "Save";
                saveBtn.addEventListener("click", () => {
                    const rules = rulesTextbox.value.trim();
                    let personaDropdownValue = parseInt(personaDropdown.value)
                    let persona_id = isNaN(personaDropdownValue) ? -1 : personaDropdownValue
                    updateInviteCode(inviteCode.invite_code, persona_id, rules);
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
        fetch(`/admin/invite_codes/${inviteCode}/?token=${getToken()}`, {
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

    function updateInviteCode(inviteCode, persona_id, rules) {
        const queryParams = new URLSearchParams({
            persona_id: parseInt(persona_id), rules: rules
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

function initializeRulesSection() {
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
        fetch(`/admin/rules?token=${getToken()}`)
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