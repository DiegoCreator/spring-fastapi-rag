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

export function toggleMenu(event, session_id) {
  event.stopPropagation();

  document.querySelectorAll(".dropdown-menu").forEach((menu) => {
    if (menu.id !== `dropdown-${session_id}`) {
      menu.classList.remove("show");
    }
  });
  const currentMenu = document.getElementById(`dropdown-${session_id}`);
  if (currentMenu) {
    currentMenu.classList.toggle("show");
  }
}

export function createActionsMenu(id, { showRename = true } = {}) {
  return `
    <div class="menu-container">
      <button class="dots-menu-btn">⋮</button>

      <div id="dropdown-${id}" class="dropdown-menu">
        ${showRename ? `<button class="rename-btn">Rename</button>` : ""}
        <button class="delete-btn">Delete</button>
      </div>
    </div>
  `;
}

export function closeAllMenus() {
  document.querySelectorAll(".dropdown-menu").forEach((menu) => {
    menu.classList.remove("show");
  });
}
