function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value;
    if (!message) return;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<p><strong>Vous:</strong> ${message}</p>`;

    fetch("/chat", {
        method: "POST",
        body: JSON.stringify({ message }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => response.json())
      .then(data => {
          chatBox.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
          chatBox.scrollTop = chatBox.scrollHeight;
      });

    input.value = "";
}
