// JavaScript code for chat functionality

document.addEventListener("DOMContentLoaded", function () {

    function loadChatHistory() {
        const session_id = getSessionIdFromUrl()
        // Make an HTTP request to the server
        fetch(`/session/${session_id}/history`, {})
            .then(response => response.json())
            .then(history => {
                history.forEach(chat => {
                    const response = chat.content;
                    const sender = chat.role;
                    displayMessage(sender, response);
                });
            })
            .catch(error => {
                console.error("Error:", error);
            });
    }

    loadChatHistory();
});

// Get DOM elements
const chatMessages = document.getElementById("chat-messages");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

// Event listener for send button
sendButton.addEventListener("click", sendMessage);

// Event listener for Enter key press
userInput.addEventListener("keyup", function (event) {
    if (event.keyCode === 13) {
        sendMessage();
    }
});

// Function to send a message
function sendMessage() {
    const message = userInput.value.trim();
    if (message !== "") {
        displayMessage("user", message);
        userInput.value = "";

        // Send message to the server for processing
        // console.log(message);
        sendToServer(message);
    }
}

// Function to display a message in the chat
function displayMessage(sender, message) {
    const messageElement = document.createElement("div");
    if (sender === "system") return
    messageElement.classList.add("message");
    messageElement.classList.add(sender === "user" ? "user-message" : "bot-message");
    messageElement.innerHTML = (sender === "user" ? "<strong>You:</strong> " : "<strong>ChatGPT:</strong> ") + DOMPurify.sanitize(marked.parse(message));

    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to send the message to the server for processing
function sendToServer(message) {
    const session_id = getSessionIdFromUrl()
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
        })
        .catch(error => {
            console.error("Error:", error);
        });
}

function getSessionIdFromUrl() {
    const path = window.location.pathname;
    const parts = path.split('/');
    const sessionIdIndex = parts.indexOf('session'); // Find the index of 'session' in the path
    if (sessionIdIndex !== -1 && sessionIdIndex < parts.length - 1) {
        // If 'session' is found and the session_id is present in the next part of the path
        return parts[sessionIdIndex + 1]; // Return the session_id
    }
    return null; // If session_id is not found, return null
}
