document.addEventListener("DOMContentLoaded", function () {
    initializePersonaSection();
    initializeUserManagementSection();
    initializeInviteCodeSection();
});

function initializePersonaSection() {
    const personaDropdown = document.getElementById("personaDropdown");
    const createNewBtn = document.getElementById("createNewBtn");
    const editSelectedBtn = document.getElementById("editSelectedBtn");
    const deleteSelectedBtn = document.getElementById("deleteSelectedBtn");
    const personaForm = document.getElementById("personaForm");
    const savePersonaBtn = document.getElementById("savePersonaBtn");

    function populatePersonaDetails(persona) {
        const personaNameSpan = document.getElementById("personaNameD");
        const personaSystemInstructionSpan = document.getElementById("personaSystemInstruction");
        const personaInstructionBeforeSpan = document.getElementById("personaInstructionBefore");
        const personaInstructionAfterSpan = document.getElementById("personaInstructionAfter");

        personaNameSpan.textContent = persona.name;
        personaSystemInstructionSpan.textContent = persona.system_instruction;
        personaInstructionBeforeSpan.textContent = persona.before_instruction;
        personaInstructionAfterSpan.textContent = persona.after_instruction;
    }

    function populatePersonaDropdown() {
        fetch("/admin/personas/")
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
        systemInstruction.value = "";
        instructionBefore.value = "";
        instructionAfter.value = "";
    }

    function handleEditSelectedClick() {
        const selectedPersonaId = personaDropdown.value;
        if (selectedPersonaId) {
            fetch(`/admin/personas/${selectedPersonaId}/`)
                .then(response => response.json())
                .then(persona => {
                    personaName.value = persona.name;
                    systemInstruction.value = persona.system_instruction;
                    instructionBefore.value = persona.before_instruction;
                    instructionAfter.value = persona.after_instruction;
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
            fetch(`/admin/personas/${selectedPersonaId}/`, {
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
            system_instruction: systemInstruction.value,
            before_instruction: instructionBefore.value,
            after_instruction: instructionAfter.value
        };

        if (selectedPersonaId) {
            fetch(`/admin/personas/${selectedPersonaId}/`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(personaData)
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                    populatePersonaDropdown();
                    personaForm.classList.add("hidden");
                })
                .catch(error => {
                    console.error("Error updating persona:", error);
                });
        } else {
            fetch("/admin/personas/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(personaData)
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                    populatePersonaDropdown();
                    personaForm.classList.add("hidden");
                })
                .catch(error => {
                    console.error("Error creating persona:", error);
                });
        }
    }

    function handlePersonaDropdownChange() {
        const selectedPersonaId = personaDropdown.value;
        const isPersonaSelected = selectedPersonaId !== "-1"; // Check if a valid persona is selected
        editSelectedBtn.disabled = !isPersonaSelected; // Enable/disable "Edit Selected" button
        deleteSelectedBtn.disabled = !isPersonaSelected; // Enable/disable "Delete Selected" button
        if (selectedPersonaId) {
            fetch(`/admin/personas/${selectedPersonaId}/`)
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

    createNewBtn.addEventListener("click", handleCreateNewClick);
    editSelectedBtn.addEventListener("click", handleEditSelectedClick);
    deleteSelectedBtn.addEventListener("click", handleDeleteSelectedClick);
    savePersonaBtn.addEventListener("click", handleSavePersonaClick);
    personaDropdown.addEventListener("change", handlePersonaDropdownChange);


    populatePersonaDropdown();
}

function initializeUserManagementSection() {

    function populateUserTable() {
        const userTableDiv = document.getElementById("userTable");

        while (userTableDiv.rows.length > 1) {
            userTableDiv.deleteRow(1);
        }
        fetch("/admin/users/")
            .then(response => response.json())
            .then(users => {
                users.forEach(user => {
                    const row = userTableDiv.insertRow();
                    row.insertCell().textContent = user.first_name;
                    row.insertCell().textContent = user.last_name;
                    row.insertCell().textContent = user.user_id;
                    row.insertCell().textContent = user.api_calls;

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
        fetch(`/admin/users/delete/${userId}/`, {
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
            row.insertCell().textContent = inviteCode.used ? "Yes" : "No";
            if (!inviteCode.used) {
                const deleteBtn = document.createElement("button");
                deleteBtn.textContent = "Delete";
                deleteBtn.addEventListener("click", () => deleteInviteCode(inviteCode.invite_code));
                row.insertCell().appendChild(deleteBtn);
            } else {
                row.insertCell();
            }
        });
    }

    function generateInviteCodes() {
        const numCodes = numCodesInput.value;
        fetch(`/admin/invite_codes/?num_codes=${numCodes}`, {
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
        fetch(`/admin/invite_codes/${inviteCode}`, {
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
        fetch("/admin/invite_codes/")
            .then(response => response.json())
            .then(data => {
                console.log("Invite codes:", data);
                populateInviteCodesTable(data);
            })
            .catch(error => {
                console.error("Error fetching invite codes:", error);
            });
    }

    generateCodesBtn.addEventListener("click", generateInviteCodes);
    getInviteCodes();
}