document.addEventListener("DOMContentLoaded", function () {
    initializeChat()
});

function initializeChat() {
    const chatMessages = document.getElementById("chat-messages");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const doneButton = document.getElementById('done-button');
    const timerDisplay = document.getElementById('timer-display');
    const messageCounter = document.getElementById('message-counter');


    function sendMessage() {
        const message = userInput.value.trim();
        if (message !== "") {
            userInput.disabled = true;
            displayMessage("user", message);
            userInput.value = "";

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
        const session_id = getSessionIdFromUrl();
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

    function request_greeting() {
        const session_id = getSessionIdFromUrl()
        // Make an HTTP request to the server
        fetch(`/chat/${session_id}/greetings`)
            .then(response => response.json())
            .then(data => {
                const response = data.response;
                displayMessage("assistant", response);
            })
            .catch(error => {
                console.error("Error:", error);
            });
    }

    function getSessionIdFromUrl() {
        const path = window.location.pathname;
        const parts = path.split('/');
        const sessionIdIndex = parts.indexOf('chat'); // Find the index of 'session' in the path
        if (sessionIdIndex !== -1 && sessionIdIndex < parts.length - 1) {
            // If 'session' is found and the session_id is present in the next part of the path
            return parts[sessionIdIndex + 1]; // Return the session_id
        }
        return null; // If session_id is not found, return null
    }

    function endSession() {
        const session_id = getSessionIdFromUrl();
        userInput.disabled = true;
        sendButton.disabled = true;
        doneButton.disabled = true;
        timerDisplay.textContent = "Chat session ended.";
        window.location.href = `/chat/${session_id}/intermission`;
    }

    async function checkSessionEnd() {
        try {
            const session_id = getSessionIdFromUrl();
            const response = await fetch(`/chat/${session_id}/check_done`);
            const data = await response.json();
            if (data.session_end) {
                endSession();
            } else {
                // Update timer display
                const timeLeft = data.time_left;
                const minutes = Math.floor(timeLeft / 60);
                const seconds = Math.floor(timeLeft % 60);
                timerDisplay.textContent = `Time remaining: ${minutes}:${seconds.toString().padStart(2, '0')}`;

                // Update messages left display
                const messagesLeft = data.messages_left;
                messageCounter.textContent = `Messages left: ${messagesLeft}`;
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    function loadChatHistory() {
        const session_id = getSessionIdFromUrl()
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

    function showDisclaimerModal() {
        const modal = document.getElementById('disclaimerModal');
        const session_id = getSessionIdFromUrl()

        fetch(`/chat/${session_id}/disclaimer`)
            .then(response => response.text())
            .then(data => {
                const modalContent = document.querySelector('#disclaimerModal .modal-body');
                modalContent.innerHTML = "<p>" + data + "</p>";
            });

        modal.classList.add('is-visible');

        const closeButton = document.getElementById('modalCloseButton');
        closeButton.addEventListener('click', function () {
            modal.classList.remove('is-visible');
        });
    }

    function showEndChatModal() {
        const modal = document.getElementById('endChatModal');
        const session_id = getSessionIdFromUrl()

        fetch(`/chat/${session_id}/check_done`)
            .then(response => response.json())
            .then(data => {
                const modalContent = document.querySelector('#endChatModal .modal-body');
                modalContent.innerHTML = '';
                if (!data.session_end && data.messages_left > 0) {
                    const warningMessage = document.createElement('p');
                    warningMessage.textContent = `Warning: You still have ${data.messages_left} messages left to send.`;
                    modalContent.appendChild(warningMessage);

                    modal.classList.add('is-visible');

                    const endChatButton = document.getElementById('endChatModalConfirmButton');
                    endChatButton.addEventListener('click', function () {
                        modal.classList.remove('is-visible');
                        endSession();
                    });

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
    doneButton.addEventListener("click", showEndChatModal)
    userInput.addEventListener("keyup", function (event) {
        if (event.code === 'Enter') {
            sendMessage();
        }
    });

    //Startup functions
    loadChatHistory();
    showDisclaimerModal();
    setInterval(checkSessionEnd, 1000);
}
