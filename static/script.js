function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() !== '') {
        const chatBox = document.getElementById('chat-box');
        
        // Ajouter le message de l'utilisateur
        const userMessage = document.createElement('div');
        userMessage.classList.add('user-message');
        userMessage.textContent = userInput;
        chatBox.appendChild(userMessage);
        
        // Ajouter la réponse du bot avec une image
        const botMessage = document.createElement('div');
        botMessage.classList.add('bot-message');
        
        let botResponse = "";
        let imageUrl = "";
        
        if (userInput.toLowerCase().includes("marrakech")) {
            botResponse = "Marrakech est une ville incontournable du Maroc, célèbre pour ses souks, sa place Jamaâ El Fna et ses magnifiques jardins.";
            imageUrl = "https://i.pinimg.com/736x/26/78/f0/2678f009553d87e400708f69a9568858.jpg"; // Assure-toi de mettre le bon chemin de l'image dans le dossier static
        } else if (userInput.toLowerCase().includes("casablanca")) {
            botResponse = "Casablanca est une ville moderne avec une magnifique côte et la célèbre mosquée Hassan II.";
            imageUrl = "https://i.pinimg.com/736x/ed/a0/19/eda01999bf63e3e8634d8681cd1a4e9e.jpg"; // Assure-toi de mettre le bon chemin de l'image
        } else if (userInput.toLowerCase() === "bonjour") {
            botResponse = "Bonjour ! Comment puis-je vous aider aujourd'hui ?";
            imageUrl = "https://i.pinimg.com/736x/c0/05/83/c00583b8b9b3aa2e0e986966c1711ea6.jpg"; // Image de bienvenue
        } else {
            botResponse = "Je suis désolé, je n'ai pas d'informations sur ce sujet pour le moment.";
            imageUrl = "/static/images/sorry.jpg"; // Image d'excuse
        }
        
        // Créer un message du bot avec une image
        const imgElement = document.createElement('img');
        imgElement.src = imageUrl;
        imgElement.alt = "Image de " + userInput;

        const textElement = document.createElement('p');
        textElement.textContent = botResponse;
        
        botMessage.appendChild(imgElement);
        botMessage.appendChild(textElement);
        
        chatBox.appendChild(botMessage);
        
        // Faire défiler vers le bas
        chatBox.scrollTop = chatBox.scrollHeight;
        
        // Réinitialiser le champ de saisie
        document.getElementById('user-input').value = '';
    }
}
