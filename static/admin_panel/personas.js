import {getToken} from "./admin_panel.js";

export function initializePersonaSection() {
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

            const firstMessage = document.createElement("p");
            firstMessage.textContent = `First Message: ${persona.first_message[language] || ""}`;
            languageDiv.appendChild(firstMessage);

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

    function addNewLanguageRow() {
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

        const firstMessageInput = document.createElement("input");
        firstMessageInput.type = "text";
        firstMessageInput.classList.add("first-message");
        firstMessageInput.placeholder = "First Message";

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
        newRow.appendChild(firstMessageInput);
        newRow.appendChild(instructionBeforeInput);
        newRow.appendChild(instructionAfterInput);

        languageInputs.appendChild(newRow);
    }

    function handleCreateNewClick() {
        personaDropdown.selectedIndex = -1;
        personaForm.classList.remove("hidden");
        personaName.value = "";

        // Clear existing language rows
        languageInputs.innerHTML = '';
        addNewLanguageRow();
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

                        const firstMessageInput = document.createElement("input");
                        firstMessageInput.type = "text";
                        firstMessageInput.classList.add("first-message");
                        firstMessageInput.placeholder = "First Message";
                        firstMessageInput.value = persona.first_message[language] || "";

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
            first_message: {},
            before_instruction: {},
            after_instruction: {}
        };

        const languageRows = document.querySelectorAll(".language-input-row");
        languageRows.forEach(row => {
            const language = row.querySelector(".language-name").value;
            const systemInstruction = row.querySelector(".system-instruction").value;
            const firstMessage = row.querySelector(".first-message").value;
            const instructionBefore = row.querySelector(".instruction-before").value;
            const instructionAfter = row.querySelector(".instruction-after").value;

            personaData.system_instruction[language] = systemInstruction;
            personaData.first_message[language] = firstMessage;
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

    addLanguageBtn.addEventListener("click", addNewLanguageRow);
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