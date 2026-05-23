const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");

let messageCounter = 0;

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = userInput.value.trim();
  if (!query) return;

  const BACKEND_URL = "http://localhost:8080/api/ask";

  const messageText = userInput.value.trim();
  if (!messageText) return;

  appendMessage(messageText, "user-message");

  userInput.value = "";

  const loadingMessageId = appendMessage("Thinking...", "ai-message loading");

  try {
    const response = await fetch(BACKEND_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: messageText }),
    });

    if (!response.ok && response.status !== 200) {
      throw new Error(`Server responded with status: ${response.status}`);
    }

    const data = await response.text();

    const loadingElem = document.getElementById(loadingMessageId);
    if (loadingElem) {
      loadingElem.textContent = data;
      loadingElem.className = "message ai-message";
    }
  } catch (error) {
    console.error("Error connecting to backend:", error);

    const loadingElem = document.getElementById(loadingMessageId);
    if (loadingElem) {
      loadingElem.textContent =
        "Something went wrong connecting to the server.";
      loadingElem.classList.add("error-message");
    }
  }
});

function appendMessage(text, className) {
  const messageDiv = document.createElement("div");
  const uniqueId = `msg-${Date.now()}-${messageCounter++}`;

  messageDiv.id = uniqueId;
  messageDiv.className = `message ${className}`;
  messageDiv.textContent = text;

  chatMessages.appendChild(messageDiv);

  chatMessages.scrollTop = chatMessages.scrollHeight;

  return uniqueId;
}
