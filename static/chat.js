import {getLanguage, getSessionIdFromUrl, getTranslation} from "./common.js";

document.addEventListener("DOMContentLoaded", function () {
    initializeChat()
});

async function initializeChat() {
    const chatMessages = document.getElementById("chat-messages");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const taskButton = document.getElementById("task-button");
    const doneButton = document.getElementById('done-button');
    const timerDisplay = document.getElementById('timer-display');
    const messageCounter = document.getElementById('message-counter');
    const overlay = document.getElementById("loadingOverlay");
    const charCount = document.getElementById("charCount");
    const translations = await getTranslation(await getLanguage("chat"), "chat");

    function sendMessage() {
        const message = userInput.value.trim();
        if (message !== "") {
            userInput.disabled = true;
            displayMessage("user", message);
            userInput.value = "";
            charCount.textContent = "200";

            // Send message to the server for processing
            // console.log(message);
            sendToServer(message);
        }
    }

    function displayMessage(sender, message) {
        const messageElement = document.createElement("div");
        if (sender === "system") return
        messageElement.classList.add("message");
        messageElement.classList.add(sender === "user" ? "user-message" : "bot-message");
        messageElement.innerHTML = (sender === "user" ? "<strong>You:</strong> " : "<strong>ChatBot:</strong> ") + DOMPurify.sanitize(marked.parse(message));

        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function sendToServer(message) {
        const session_id = getSessionIdFromUrl("chat");
        // Make an HTTP request to the server
        fetch(`/chat/${session_id}`, {
            method: "POST", headers: {
                "Content-Type": "application/json"
            }, body: JSON.stringify({content: message})
        })
            .then(response => response.json())
            .then(data => {
                const response = data.response;
                displayMessage("assistant", response);
                userInput.disabled = false;
            })
            .catch(error => {
                console.error("Error:", error);
                userInput.disabled = false;
            });
    }


    async function endSession() {
        const session_id = getSessionIdFromUrl("chat");
        userInput.disabled = true;
        sendButton.disabled = true;
        doneButton.disabled = true;
        timerDisplay.textContent = translations.chat_session_ended;
        overlay.style.display = "flex";

        try {
            const response = await fetch(`/chat/${session_id}/session_end`);

            if (response.ok) {
                console.log("API call successful");
                window.location.href = `/questionnaire/${session_id}/before`;
            } else {
                console.error("API call failed");
            }
        } catch (error) {
            console.error("An error occurred:", error);
        }
    }

    function checkSessionEnd() {
        const session_id = getSessionIdFromUrl("chat");

        fetch(`/chat/${session_id}/check_done`)
            .then(response => response.json())
            .then(data => {
                if (data.session_end) {
                    return endSession();
                } else {
                    // Update timer display
                    const timeLeft = data.time_left;
                    const minutes = Math.floor(timeLeft / 60);
                    const seconds = Math.floor(timeLeft % 60);
                    timerDisplay.textContent = translations.time_remaining + `: ${minutes}:${seconds.toString().padStart(2, '0')}`;

                    const available_tokens = data.available_tokens;
                    if (available_tokens <= 0) {
                        displayMessage("assistant", translations.rate_limit_reached);
                    }
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
    }


    function loadChatHistory() {
        const session_id = getSessionIdFromUrl("chat")
        let first_time = true;
        // Make an HTTP request to the server
        fetch(`/chat/${session_id}/history`, {})
            .then(response => response.json())
            .then(history => {
                history.forEach(chat => {
                    const response = chat.content;
                    const sender = chat.role;
                    displayMessage(sender, response);
                    if (sender !== "system") {
                        first_time = false;
                    }
                });
                if (first_time) {
                    //request_greeting();
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
        return first_time;
    }

    function showTaskModal() {
        const modal = document.getElementById('taskModal');
        const session_id = getSessionIdFromUrl("chat")

        fetch(`/chat/${session_id}/task`)
            .then(response => response.text())
            .then(data => {
                data = data.replace(/^"(.*)"$/, '$1');
                const modalContent = document.querySelector('#taskModal .modal-body');
                const paragraph = document.createElement('p');
                paragraph.innerText = data;
                modalContent.appendChild(paragraph);
            });

        modal.classList.add('is-visible');

        const closeButton = document.getElementById('modalCloseButton');
        closeButton.addEventListener('click', function () {
            modal.classList.remove('is-visible');
        });
    }

    function showEndChatModal() {
        const modal = document.getElementById('endChatModal');
        const session_id = getSessionIdFromUrl("chat")

        fetch(`/chat/${session_id}/check_done`)
            .then(response => response.json())
            .then(data => {
                const modalContent = document.querySelector('#endChatModal .modal-body');
                modalContent.innerHTML = '';
                if (!data.session_end && data.available_tokens > 0) {
                    const warningMessage = document.createElement('p');
                    warningMessage.textContent = translations.end_chat_warning;
                    modalContent.appendChild(warningMessage);

                    modal.classList.add('is-visible');

                    const endChatButton = document.getElementById('endChatModalConfirmButton');
                    endChatButton.classList.add('is-visible');
                    endChatButton.addEventListener('click', function () {
                        modal.classList.remove('is-visible');
                        if (data.can_end_session) {
                            endSession();
                        } else {
                            endChatButton.classList.remove('is-visible')
                        }
                    });
                    if (!data.can_end_session) {
                        endChatButton.classList.remove('is-visible')
                    }
                    const closeButton = document.getElementById('endChatModalCancelButton');
                    closeButton.addEventListener('click', function () {
                        modal.classList.remove('is-visible');
                    });
                } else if (data.session_end) {
                    endSession();
                }
            });

    }

    // Event listeners
    sendButton.addEventListener("click", sendMessage);
    taskButton.addEventListener("click", showTaskModal)
    doneButton.addEventListener("click", showEndChatModal);
    userInput.addEventListener("keyup", function (event) {
        if (event.code === 'Enter') {
            sendMessage();
        }
    });
    userInput.addEventListener("input", function (event) {
        const currentLength = userInput.value.length;
        const maxLimit = 200;
        const remaining = maxLimit - currentLength;
        charCount.textContent = remaining.toString();

        if (currentLength > maxLimit) {
            userInput.value = userInput.value.slice(0, maxLimit);
        }
    });

    //Startup functions
    loadChatHistory();
    showTaskModal();
    setInterval(checkSessionEnd, 1000);
}
