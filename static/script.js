// Fonction pour ajouter un message dans la chatbox
function addMessage(message, sender) {
    const chatbox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.className = sender;
    messageElement.innerHTML = message; // Permet d'afficher du HTML

    // Ajouter le message en une seule fois
    chatbox.appendChild(messageElement);

    // Scroll automatique en bas
    chatbox.scrollTop = chatbox.scrollHeight; 

    // Vérifie si on doit afficher ↓
    checkScrollButtonVisibility();
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

        // Vérification du message de l'utilisateur
        let botResponse = "";
        const greetings = {
            'fr': ["bonjour", "salut", "salut !", "bonjour !"],
            'ar': ["مرحبا", "السلام عليكم", "اهلا"],
            'en': ["hi", "hello", "hey", "good morning", "good evening"]
        };

        // Fonction pour vérifier la langue du message
        function detectLanguage(input) {
            const arabicPattern = /[\u0600-\u06FF]/;
            const englishPattern = /[a-zA-Z]/;

            if (arabicPattern.test(input)) {
                return 'ar'; // Langue arabe
            } else if (englishPattern.test(input)) {
                return 'en'; // Langue anglaise
            }
            return 'fr'; // Langue par défaut : français
        }

        const userLanguage = detectLanguage(userInput);

        // Vérification des salutations selon la langue détectée
        if (userLanguage === 'fr' && greetings['fr'].some(greeting => userInput.toLowerCase().includes(greeting))) {
            botResponse = "Bonjour ! Comment puis-je vous aider aujourd'hui ?";
        } else if (userLanguage === 'ar' && greetings['ar'].some(greeting => userInput.includes(greeting))) {
            botResponse = "مرحباً! كيف يمكنني مساعدتك اليوم؟";
        } else if (userLanguage === 'en' && greetings['en'].some(greeting => userInput.toLowerCase().includes(greeting))) {
            botResponse = "Hello! How can I help you today?";
        } else {
            // Si ce n'est pas une salutation, on traite la ville ou la demande
            const cityNames = ["marrakech", "casablanca", "rabat", "fes", "tanger"];
            const cityMatch = cityNames.find(city => userInput.toLowerCase().includes(city));
            
            if (cityMatch) {
                // Vérification si l'utilisateur veut en savoir plus sur les monuments
                if (userInput.toLowerCase().includes("monuments")) {
                    botResponse = `Les monuments de ${cityMatch} incluent des sites comme la Médina de Fès, la mosquée Karaouiyne, et bien plus. Que voulez-vous savoir précisément à propos des monuments ?`;
                } else {
                    botResponse = `Je peux vous donner des informations sur ${cityMatch}. Que voulez-vous savoir à propos de cette ville ?`;
                }
            } else {
                // Envoyer la requête à l'API Flask pour obtenir la réponse du bot
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
                    botResponse = data.response; // Réponse du bot
                    displayBotMessage(botResponse); // Affichage de la réponse
                })
                .catch(error => {
                    console.error("Erreur:", error);
                    botResponse = "Désolé, il semble que quelque chose ne va pas. Pouvez-vous reformuler votre question ?";
                    displayBotMessage(botResponse);
                });
            }
        }

        // Si la réponse a été définie au préalable (pour les saluts ou villes)
        if (botResponse) {
            displayBotMessage(botResponse);
        }
    }
}

// Fonction pour afficher le message du bot
function displayBotMessage(botMessage) {
    const chatBox = document.getElementById('chat-box');
    const botMessageElement = document.createElement('div');
    botMessageElement.classList.add('bot-message');
    botMessageElement.innerHTML = botMessage; // Affiche la réponse
    chatBox.appendChild(botMessageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    checkScrollButtonVisibility(); // Vérifie après la réponse
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
