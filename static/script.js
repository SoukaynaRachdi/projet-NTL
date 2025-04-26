// Fonction pour ajouter un message dans le chatbox
function addMessage(message, sender) {
    const chatbox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.className = sender;
    messageElement.innerHTML = message; // Permet d'afficher du HTML (images, liens, etc.)
    chatbox.appendChild(messageElement);
    chatbox.scrollTop = chatbox.scrollHeight; // Scroll automatique en bas
}

function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() !== '') {
        const chatBox = document.getElementById('chat-box');

        const userMessage = document.createElement('div');
        userMessage.classList.add('user-message');
        userMessage.textContent = userInput;
        chatBox.appendChild(userMessage);

        fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: userInput
            })
        })
        .then(response => response.json())
        .then(data => {
            const botMessage = document.createElement('div');
            botMessage.classList.add('bot-message');

            botMessage.innerHTML = data.response; // <= changer ici

            chatBox.appendChild(botMessage);
            chatBox.scrollTop = chatBox.scrollHeight;
            document.getElementById('user-input').value = '';
        })
        .catch(error => {
            console.error("Erreur:", error);
        });
    }
} 
