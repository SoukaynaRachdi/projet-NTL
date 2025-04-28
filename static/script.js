// Fonction pour ajouter un message dans la chatbox
function addMessage(message, sender) {
    const chatbox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.className = sender;
    messageElement.innerHTML = message; // Permet d'afficher du HTML
    chatbox.appendChild(messageElement);
    chatbox.scrollTop = chatbox.scrollHeight; // Scroll automatique en bas
    checkScrollButtonVisibility(); // Vérifie si on doit afficher ↓
}

// Fonction pour envoyer un message
function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() !== '') {
        const chatBox = document.getElementById('chat-box');

        // Ajouter le message de l'utilisateur
        const userMessage = document.createElement('div');
        userMessage.classList.add('user-message');
        userMessage.textContent = userInput;
        chatBox.appendChild(userMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
        document.getElementById('user-input').value = '';

        checkScrollButtonVisibility(); // Vérifie après l'ajout

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
            botMessage.innerHTML = data.response; // Affiche la réponse
            chatBox.appendChild(botMessage);
            chatBox.scrollTop = chatBox.scrollHeight;
            checkScrollButtonVisibility(); // Vérifie après la réponse
        })
        .catch(error => {
            console.error("Erreur:", error);
        });
    }
}

// Envoyer avec la touche "Entrée"
document.getElementById('user-input').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});

// Gestion du bouton ↓
const scrollButton = document.getElementById('scroll-button');
const chatBox = document.getElementById('chat-box');

// Fonction pour afficher/cacher le bouton ↓
function checkScrollButtonVisibility() {
    if (chatBox.scrollTop + chatBox.clientHeight < chatBox.scrollHeight - 100) {
        scrollButton.style.display = 'flex'; // Montre le bouton
    } else {
        scrollButton.style.display = 'none'; // Cache le bouton
    }
}

// Quand on scrolle dans la chatbox
chatBox.addEventListener('scroll', checkScrollButtonVisibility);

// Vérifie au chargement de la page
window.addEventListener('load', checkScrollButtonVisibility);

// Quand on clique sur le bouton ↓
scrollButton.addEventListener('click', function () {
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' }); 
});

document.getElementById('map-button').addEventListener('click', function() {
    // Exemple simple : ouvrir Google Maps
    window.open('https://www.google.com/maps', '_blank');
});

