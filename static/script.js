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

let currentUtterance = null;
let isSpeaking = false;
let availableVoices = [];

// Chargement des voix au début
window.speechSynthesis.onvoiceschanged = () => {
    availableVoices = speechSynthesis.getVoices();
};

// Fonction pour détecter la langue du texte (simplement)
function detectLanguage(text) {
    const arabicRegex = /[\u0600-\u06FF]/;
    const frenchRegex = /[éèêàùâçîôëï]/i;
    const englishRegex = /^[a-zA-Z0-9.,!?'"()\s]+$/;

    if (arabicRegex.test(text)) return 'ar';
    if (frenchRegex.test(text)) return 'fr';
    if (englishRegex.test(text)) return 'en';

    return 'fr'; // Par défaut, on suppose le français
}

// Fonction pour lire le message avec la bonne langue
function playAudio() {
    const chatBox = document.getElementById('chat-box');
    const lastBotMessage = chatBox.querySelector('.bot-message:last-child');

    if (!lastBotMessage) {
        console.log("Aucun message du bot à lire.");
        return;
    }

    const message = lastBotMessage.innerText;
    const audioButton = document.getElementById('audioButton');

    if (isSpeaking) {
        speechSynthesis.cancel();
        isSpeaking = false;
        audioButton.textContent = "🔊";
        return;
    }

    const lang = detectLanguage(message);
    const selectedVoice = availableVoices.find(v => v.lang.startsWith(lang));

    if (!selectedVoice) {
        console.log("Aucune voix trouvée pour la langue :", lang);
        return;
    }

    currentUtterance = new SpeechSynthesisUtterance(message);
    currentUtterance.lang = selectedVoice.lang;
    currentUtterance.voice = selectedVoice;

    speechSynthesis.speak(currentUtterance);
    isSpeaking = true;
    audioButton.textContent = "⏹️";

    currentUtterance.onend = () => {
        isSpeaking = false;
        audioButton.textContent = "🔊";
    };
}

document.getElementById('audioButton').addEventListener('click', playAudio);
