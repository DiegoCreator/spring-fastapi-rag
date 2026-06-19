import { chatMessages } from "./dom.js";
import { setCurrentSessionId } from "./state.js";
import { loadChatHistory } from "./chat.js";
let messageCounter = 0;

export function getActiveChatId() {
  return new URLSearchParams(window.location.search).get("Chat");
}

export async function render() {
  const chatId = getActiveChatId();

  if (!chatId) {
    setCurrentSessionId(null);
    chatMessages.innerHTML = "";

    appendMessage("Hello! How can I help you today?", "ai-message");
    return;
  }

  setCurrentSessionId(chatId);
  await loadChatHistory(chatId);
}

export function appendMessage(text, className) {
  const messageDiv = document.createElement("div");
  const uniqueId = `msg-${Date.now()}-${messageCounter++}`;

  messageDiv.id = uniqueId;
  messageDiv.className = `message ${className}`;
  messageDiv.textContent = text;

  chatMessages.appendChild(messageDiv);

  chatMessages.scrollTop = chatMessages.scrollHeight;

  return uniqueId;
}
