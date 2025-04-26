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
        
        // Ajouter le message de l'utilisateur
        const userMessage = document.createElement('div');
        userMessage.classList.add('user-message');
        userMessage.textContent = userInput;
        chatBox.appendChild(userMessage);
        
        // Envoyer la requête à l'API Flask
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
            
            const textElement = document.createElement('p');
            textElement.textContent = data.response;
            
            botMessage.appendChild(textElement);
            chatBox.appendChild(botMessage);
            
            // Faire défiler vers le bas
            chatBox.scrollTop = chatBox.scrollHeight;
            
            // Réinitialiser le champ de saisie
            document.getElementById('user-input').value = '';
        })
        .catch(error => {
            console.error("Erreur:", error);
        });
    }
}

