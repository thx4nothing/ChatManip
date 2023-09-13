import {getToken} from "./admin_panel.js";

export function initializeHistorysSection() {
    const historyDropdown = document.getElementById("historyDropdown");
    const createNewHistoryBtn = document.getElementById("createNewHistoryBtn");
    const editSelectedHistoryBtn = document.getElementById("editSelectedHistoryBtn");
    const deleteSelectedHistoryBtn = document.getElementById("deleteSelectedHistoryBtn");
    const historyForm = document.getElementById("historyForm");
    const historyName = document.getElementById("historyName");
    const saveHistoryBtn = document.getElementById("saveHistoryBtn");
    const addHistoryLanguageBtn = document.getElementById("addHistoryLanguageBtn");
    const historyLanguageInputs = document.getElementById("historyLanguageInputs");

    function populateHistoryDetails(history) {
        const historyDetailsContainer = document.getElementById("historyDetails");
        historyDetailsContainer.innerHTML = "<h3>History Details</h3>"; // Clear existing content
        console.log(history)
        for (const language in history.history) {
            const languageDiv = document.createElement("div");
            languageDiv.classList.add("history-language-row");

            const languageName = document.createElement("p");
            languageName.textContent = "Language: " + language;
            languageDiv.appendChild(languageName);

            const conversation = history.history[language];
            conversation.forEach(message => {
                const messageDiv = document.createElement("div");
                const role = message.role === "user" ? "User" : "Assistant";
                messageDiv.textContent = `${role}: ${message.content}`;
                languageDiv.appendChild(messageDiv);
            });

            historyDetailsContainer.appendChild(languageDiv);
        }
    }


    function populateHistoryDropdown() {
        fetch(`/admin/history?token=${getToken()}`)
            .then(response => response.json())
            .then(histories => {
                historyDropdown.innerHTML = "";
                histories.forEach(history => {
                    const option = document.createElement("option");
                    option.value = history.history_id;
                    option.textContent = history.name;
                    historyDropdown.appendChild(option);
                });
                handleHistoryDropdownChange();
            })
            .catch(error => {
                console.error("Error fetching histories:", error);
            });
    }

    function handleCreateNewHistoryClick() {
        historyDropdown.selectedIndex = -1;
        historyForm.classList.remove("hidden");
        historyName.value = "";
        historyLanguageInputs.innerHTML = "";

        handleAddHistoryLanguageClick();
    }


    function handleEditSelectedHistoryClick() {
        const selectedHistoryId = historyDropdown.value;
        if (selectedHistoryId) {
            fetch(`/admin/history/${selectedHistoryId}?token=${getToken()}`)
                .then(response => response.json())
                .then(history => {
                    historyName.value = history.name;

                    const historyLanguageInputs = document.getElementById("historyLanguageInputs");
                    historyLanguageInputs.innerHTML = ''; // Clear existing content

                    for (const language in history.history) {
                        const row = document.createElement("div");
                        row.classList.add("history-language-input-row");

                        const languageInput = document.createElement("input");
                        languageInput.type = "text";
                        languageInput.classList.add("history-language-name");
                        languageInput.placeholder = "Language";
                        languageInput.value = language;
                        row.appendChild(languageInput);

                        console.log(history.history[language])

                        const conversationsContainer = document.createElement("div");
                        conversationsContainer.classList.add("conversations-container");
                        history.history[language].forEach((conversation, index) => {
                            if (index % 2 === 0) {
                                const conversationContainer = document.createElement("div");
                                conversationContainer.classList.add("conversation-container");

                                const userMessageInput = document.createElement("input");
                                userMessageInput.type = "text";
                                userMessageInput.classList.add("history-user-message");
                                userMessageInput.placeholder = "User message";
                                userMessageInput.value = conversation.content;
                                conversationContainer.appendChild(userMessageInput);

                                const assistantConversation = history.history[language][index + 1];
                                const botResponseInput = document.createElement("input");
                                botResponseInput.type = "text";
                                botResponseInput.classList.add("history-bot-response");
                                botResponseInput.placeholder = "Bot Response";
                                botResponseInput.value = assistantConversation.content;
                                conversationContainer.appendChild(botResponseInput);

                                conversationsContainer.appendChild(conversationContainer);
                            }
                        });

                        const addConversationBtn = document.createElement("button");
                        addConversationBtn.classList.add("add-conversation-btn", "pure-button");
                        addConversationBtn.textContent = "Add Conversation";
                        addConversationBtn.addEventListener("click", handleAddConversationClick);

                        row.appendChild(conversationsContainer)
                        row.appendChild(addConversationBtn);

                        historyLanguageInputs.appendChild(row);
                    }

                    historyForm.classList.remove("hidden");
                })
                .catch(error => {
                    console.error("Error fetching selected history:", error);
                });
        }
    }


    function handleDeleteSelectedHistoryClick() {
        const selectedHistoryId = historyDropdown.value;
        if (selectedHistoryId) {
            fetch(`/admin/history/${selectedHistoryId}?token=${getToken()}`, {
                method: "DELETE"
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                    populateHistoryDropdown();
                    historyForm.classList.add("hidden");
                })
                .catch(error => {
                    console.error("Error deleting history:", error);
                });
        }
    }

    function handleSaveHistoryClick() {
        const selectedHistoryId = historyDropdown.value;
        const historyData = {
            name: historyName.value,
            history: {}
        };


        const languageRows = document.querySelectorAll(".history-language-input-row");
        languageRows.forEach(row => {
            const language = row.querySelector(".history-language-name").value;

            const messages = [];

            const conversationContainers = row.querySelectorAll(".conversation-container");
            conversationContainers.forEach(conversationContainer => {
                const userMessage = conversationContainer.querySelector(".history-user-message").value;
                const botResponse = conversationContainer.querySelector(".history-bot-response").value;

                messages.push({
                    role: "user",
                    content: userMessage
                });

                messages.push({
                    role: "assistant",
                    content: botResponse
                });
            });

            historyData.history[language] = messages
        });
        console.log(historyData)
        const fetchOptions = {
            method: selectedHistoryId ? "PUT" : "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(historyData)
        };

        const url = selectedHistoryId ? `/admin/history/${selectedHistoryId}?token=${getToken()}` : `/admin/history?token=${getToken()}`;

        fetch(url, fetchOptions)
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                populateHistoryDropdown();
                historyForm.classList.add("hidden");
            })
            .catch(error => {
                console.error(selectedHistoryId ? "Error updating history:" : "Error creating history:", error);
            });
    }


    function handleAddHistoryLanguageClick() {
        const languageRow = document.createElement("div");
        languageRow.classList.add("history-language-input-row");

        const languageInput = document.createElement("input");
        languageInput.type = "text";
        languageInput.classList.add("history-language-name");
        languageInput.placeholder = "Language";

        const conversationsContainer = document.createElement("div");
        conversationsContainer.classList.add("conversations-container");

        const addConversationBtn = document.createElement("button");
        addConversationBtn.classList.add("add-conversation-btn", "pure-button");
        addConversationBtn.textContent = "Add Conversation";
        addConversationBtn.addEventListener("click", handleAddConversationClick);

        languageRow.appendChild(languageInput);
        languageRow.appendChild(conversationsContainer);
        languageRow.appendChild(addConversationBtn);

        const conversationContainer = createConversationInputs();
        languageRow.querySelector(".conversations-container").appendChild(conversationContainer);

        historyLanguageInputs.appendChild(languageRow);
    }


    function handleHistoryDropdownChange() {
        const selectedHistoryId = historyDropdown.value;
        const isHistorySelected = selectedHistoryId !== "-1"; // Check if a valid history is selected
        editSelectedHistoryBtn.disabled = !isHistorySelected; // Enable/disable "Edit Selected" button
        deleteSelectedHistoryBtn.disabled = !isHistorySelected; // Enable/disable "Delete Selected" button
        if (selectedHistoryId) {
            fetch(`/admin/history/${selectedHistoryId}?token=${getToken()}`)
                .then(response => response.json())
                .then(history => {
                    populateHistoryDetails(history);
                })
                .catch(error => {
                    console.error("Error fetching selected history:", error);
                });
        }
    }

    function exportHistoryDatabase() {
        fetch(`/admin/history/export?token=${getToken()}`, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                const beautifiedJson = JSON.stringify(data, null, 2);
                const blob = new Blob([beautifiedJson], {type: 'application/json'});
                const url = URL.createObjectURL(blob);

                const a = document.createElement('a');
                a.href = url;
                a.download = 'histories_export.json';
                a.click();

                URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Error exporting history database:', error);
            });
    }

    function importHistoryDatabase(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch(`/admin/history/import?token=${getToken()}`, {
            method: 'POST',
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                console.log('Import successful:', data);
                populateHistoryDropdown();
            })
            .catch(error => {
                console.error('Error importing history database:', error);
            });
    }

    function createConversationInputs() {
        const conversationContainer = document.createElement("div");
        conversationContainer.classList.add("conversation-container");

        const userMessageInput = document.createElement("input");
        userMessageInput.type = "text";
        userMessageInput.classList.add("history-user-message");
        userMessageInput.placeholder = "User message";

        const botResponseInput = document.createElement("input");
        botResponseInput.type = "text";
        botResponseInput.classList.add("history-bot-response");
        botResponseInput.placeholder = "Bot Response";

        conversationContainer.appendChild(userMessageInput);
        conversationContainer.appendChild(botResponseInput);

        return conversationContainer;
    }

    function handleAddConversationClick(e) {
        const languageRow = e.target.closest(".history-language-input-row");
        const conversationContainer = createConversationInputs();
        languageRow.querySelector(".conversations-container").appendChild(conversationContainer);
    }


    addHistoryLanguageBtn.addEventListener("click", handleAddHistoryLanguageClick);
    createNewHistoryBtn.addEventListener("click", handleCreateNewHistoryClick);
    editSelectedHistoryBtn.addEventListener("click", handleEditSelectedHistoryClick);
    deleteSelectedHistoryBtn.addEventListener("click", handleDeleteSelectedHistoryClick);
    saveHistoryBtn.addEventListener("click", handleSaveHistoryClick);
    historyDropdown.addEventListener("change", handleHistoryDropdownChange);

    document.getElementById('exportHistoryBtn').addEventListener('click', exportHistoryDatabase);

    document.getElementById('importHistoryBtn').addEventListener('click', () => {
        const importHistoryInput = document.getElementById('importHistoryInput');
        importHistoryInput.click();
    });

    document.getElementById('importHistoryInput').addEventListener('change', event => {
        const file = event.target.files[0];
        if (file) {
            importHistoryDatabase(file);
        }
    });

    populateHistoryDropdown();
}