// JavaScript code for chat functionality

// Get DOM elements
const chatMessages = document.getElementById("chat-messages");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

// Event listener for send button
sendButton.addEventListener("click", sendMessage);

// Event listener for Enter key press
userInput.addEventListener("keyup", function(event) {
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
    messageElement.classList.add("message");
    messageElement.classList.add(sender === "user" ? "user-message" : "bot-message");
    messageElement.textContent = (sender === "user" ? "You: " : "ChatGPT: ") + message;

    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to send the message to the server for processing
function sendToServer(message) {
    // Make an HTTP request to the server
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ content: message })
    })
    .then(response => response.json())
    .then(data => {
        const response = data.response;
        displayMessage("bot", response);
    })
    .catch(error => {
        console.error("Error:", error);
    });
}
