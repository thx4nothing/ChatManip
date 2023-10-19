import {getToken} from "./admin_panel.js";

export function initializeTasksSection() {
    const taskDropdown = document.getElementById("taskDropdown");
    const createNewTaskBtn = document.getElementById("createNewTaskBtn");
    const editSelectedTaskBtn = document.getElementById("editSelectedTaskBtn");
    const deleteSelectedTaskBtn = document.getElementById("deleteSelectedTaskBtn");
    const taskForm = document.getElementById("taskForm");
    const taskName = document.getElementById("taskName");
    const taskShowDiscussionCheckbox = document.getElementById("taskShowDiscussionCheckbox");
    const saveTaskBtn = document.getElementById("saveTaskBtn");
    const addTaskLanguageBtn = document.getElementById("addTaskLanguageBtn");
    const taskLanguageInputs = document.getElementById("taskLanguageInputs");

    function populateTaskDetails(task) {
        const taskNameSpan = document.getElementById("taskNameD");
        const taskDetailsContainer = document.getElementById("taskDetails");

        taskNameSpan.textContent = task.name;

        while (taskDetailsContainer.children.length > 2) {
            taskDetailsContainer.removeChild(taskDetailsContainer.lastChild);
        }

        for (const language in task.task_instruction) {
            const languageDiv = document.createElement("div");
            languageDiv.classList.add("task-language-row");

            const languageName = document.createElement("p");
            languageName.textContent = "Language: " + language;
            languageDiv.appendChild(languageName);

            const taskInstruction = document.createElement("p");
            taskInstruction.textContent = `Task Instruction: ${task.task_instruction[language] || ""}`;
            languageDiv.appendChild(taskInstruction);

            const taskDiscussion = document.createElement("p");
            taskDiscussion.textContent = `Show Discussion questions: ${task.show_discussion_section}`;
            languageDiv.appendChild(taskDiscussion);

            taskDetailsContainer.appendChild(languageDiv);
        }
    }


    function populateTaskDropdown() {
        fetch(`/chatmanip/admin/tasks?token=${getToken()}`)
            .then(response => response.json())
            .then(tasks => {
                taskDropdown.innerHTML = "";
                tasks.forEach(task => {
                    const option = document.createElement("option");
                    option.value = task.task_id;
                    option.textContent = task.name;
                    taskDropdown.appendChild(option);
                });
                handleTaskDropdownChange();
            })
            .catch(error => {
                console.error("Error fetching tasks:", error);
            });
    }

    function handleCreateNewTaskClick() {
        taskDropdown.selectedIndex = -1;
        taskForm.classList.remove("hidden");
        taskName.value = "";
        taskShowDiscussionCheckbox.checked = false

        const languageContainer = document.getElementById("taskLanguageInputs");
        languageContainer.innerHTML = '';

        const row = document.createElement("div");
        row.classList.add("task-language-input-row");

        const languageInput = document.createElement("input");
        languageInput.type = "text";
        languageInput.classList.add("task-language-name");
        languageInput.placeholder = "Language";

        const taskInstructionInput = document.createElement("input");
        taskInstructionInput.type = "text";
        taskInstructionInput.classList.add("task-instruction");
        taskInstructionInput.placeholder = "Task Instruction";

        row.appendChild(languageInput);
        row.appendChild(taskInstructionInput);

        languageContainer.appendChild(row);
    }

    function handleEditSelectedTaskClick() {
        const selectedTaskId = taskDropdown.value;
        if (selectedTaskId) {
            fetch(`/chatmanip/admin/tasks/${selectedTaskId}?token=${getToken()}`)
                .then(response => response.json())
                .then(task => {
                    taskName.value = task.name;
                    taskShowDiscussionCheckbox.checked = task.show_discussion_section
                    const availableLanguages = Object.keys(task.task_instruction);
                    const languageContainer = document.getElementById("taskLanguageInputs");
                    languageContainer.innerHTML = '';
                    availableLanguages.forEach(language => {
                        const row = document.createElement("div");
                        row.classList.add("task-language-input-row");

                        const languageInput = document.createElement("input");
                        languageInput.type = "text";
                        languageInput.classList.add("task-language-name");
                        languageInput.placeholder = "Language";
                        languageInput.value = language;

                        const taskInstructionInput = document.createElement("input");
                        taskInstructionInput.type = "text";
                        taskInstructionInput.classList.add("task-instruction");
                        taskInstructionInput.placeholder = "Task Instruction";
                        taskInstructionInput.value = task.task_instruction[language] || "";

                        row.appendChild(languageInput);
                        row.appendChild(taskInstructionInput);

                        languageContainer.appendChild(row);
                    });

                    taskForm.classList.remove("hidden");
                })
                .catch(error => {
                    console.error("Error fetching selected task:", error);
                });
        }
    }

    function handleDeleteSelectedTaskClick() {
        const selectedTaskId = taskDropdown.value;
        if (selectedTaskId) {
            fetch(`/chatmanip/admin/tasks/${selectedTaskId}?token=${getToken()}`, {
                method: "DELETE"
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                    populateTaskDropdown();
                    taskForm.classList.add("hidden");
                })
                .catch(error => {
                    console.error("Error deleting task:", error);
                });
        }
    }

    function handleSaveTaskClick() {
        const selectedTaskId = taskDropdown.value;
        const taskData = {
            name: taskName.value,
            show_discussion_section: taskShowDiscussionCheckbox.checked,
            task_instruction: {}
        };

        const languageRows = document.querySelectorAll(".task-language-input-row");
        languageRows.forEach(row => {
            const language = row.querySelector(".task-language-name").value;
            const taskInstruction = row.querySelector(".task-instruction").value;

            taskData.task_instruction[language] = taskInstruction;
        });

        const fetchOptions = {
            method: selectedTaskId ? "PUT" : "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(taskData)
        };

        const url = selectedTaskId ? `/chatmanip/admin/tasks/${selectedTaskId}?token=${getToken()}` : `/chatmanip/admin/tasks?token=${getToken()}`;

        fetch(url, fetchOptions)
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                populateTaskDropdown();
                taskForm.classList.add("hidden");
            })
            .catch(error => {
                console.error(selectedTaskId ? "Error updating task:" : "Error creating task:", error);
            });
    }

    function handleAddTaskLanguageClick() {
        const newRow = document.createElement("div");
        newRow.classList.add("task-language-input-row");

        const languageNameInput = document.createElement("input");
        languageNameInput.type = "text";
        languageNameInput.classList.add("task-language-name");
        languageNameInput.placeholder = "Language";

        const taskInstructionInput = document.createElement("input");
        taskInstructionInput.type = "text";
        taskInstructionInput.classList.add("task-instruction");
        taskInstructionInput.placeholder = "Task Instruction";

        newRow.appendChild(languageNameInput);
        newRow.appendChild(taskInstructionInput);

        taskLanguageInputs.appendChild(newRow);
    }

    function handleTaskDropdownChange() {
        const selectedTaskId = taskDropdown.value;
        const isTaskSelected = selectedTaskId !== "-1"; // Check if a valid task is selected
        editSelectedTaskBtn.disabled = !isTaskSelected; // Enable/disable "Edit Selected" button
        deleteSelectedTaskBtn.disabled = !isTaskSelected; // Enable/disable "Delete Selected" button
        if (selectedTaskId) {
            fetch(`/chatmanip/admin/tasks/${selectedTaskId}?token=${getToken()}`)
                .then(response => response.json())
                .then(task => {
                    populateTaskDetails(task);
                })
                .catch(error => {
                    console.error("Error fetching selected task:", error);
                });
        }
    }

    function exportTaskDatabase() {
        fetch(`/chatmanip/admin/tasks/export?token=${getToken()}`, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                const beautifiedJson = JSON.stringify(data, null, 2);
                const blob = new Blob([beautifiedJson], {type: 'application/json'});
                const url = URL.createObjectURL(blob);

                const a = document.createElement('a');
                a.href = url;
                a.download = 'tasks_export.json';
                a.click();

                URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Error exporting task database:', error);
            });
    }

    function importTaskDatabase(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch(`/chatmanip/admin/tasks/import?token=${getToken()}`, {
            method: 'POST',
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                console.log('Import successful:', data);
                populateTaskDropdown();
            })
            .catch(error => {
                console.error('Error importing task database:', error);
            });
    }


    addTaskLanguageBtn.addEventListener("click", handleAddTaskLanguageClick);
    createNewTaskBtn.addEventListener("click", handleCreateNewTaskClick);
    editSelectedTaskBtn.addEventListener("click", handleEditSelectedTaskClick);
    deleteSelectedTaskBtn.addEventListener("click", handleDeleteSelectedTaskClick);
    saveTaskBtn.addEventListener("click", handleSaveTaskClick);
    taskDropdown.addEventListener("change", handleTaskDropdownChange);

    document.getElementById('exportTaskBtn').addEventListener('click', exportTaskDatabase);

    document.getElementById('importTaskBtn').addEventListener('click', () => {
        const importTaskInput = document.getElementById('importTaskInput');
        importTaskInput.click();
    });

    document.getElementById('importTaskInput').addEventListener('change', event => {
        const file = event.target.files[0];
        if (file) {
            importTaskDatabase(file);
        }
    });

    populateTaskDropdown();
}