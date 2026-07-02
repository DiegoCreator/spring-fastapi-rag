import { apiRequest, URL } from "./api.js";
import { chatMessages, chatForm, userInput, chatListContainer } from "./dom.js";
import { setCurrentSessionId } from "./state.js";
import {
  appendMessage,
  getActiveChatId,
  render,
  toggleMenu,
  createActionsMenu,
} from "./ui.js";

export let currentSessionId = null;

export async function deleteChat(id) {
  const activeId = getActiveChatId();
  const response = await apiRequest(`${URL}/chat/session/${id}`, {
    method: "DELETE",
  });

  await loadChatList();

  if (activeId === id) {
    history.pushState({}, "", "/");
    render();
  }
}

export async function renameChatTitle(id, newTitle) {
  const activeId = getActiveChatId();
  const response = await apiRequest(
    `${URL}/chat/session/${id}?title=${encodeURIComponent(newTitle)}`,
    {
      method: "PUT",
    },
  );

  await loadChatList();
}

export async function getChatList() {
  const response = await apiRequest(`${URL}/chat/sessions`);
  return response.json();
}

export async function loadChatHistory(session_id) {
  setCurrentSessionId(session_id);

  chatMessages.innerHTML = "";

  const response = await apiRequest(
    `${URL}/chat/session/${session_id}/history`,
  );

  const historyMessages = await response.json();

  historyMessages.forEach((msg) => {
    const messageClass = msg.role === "user" ? "user-message" : "ai-message";
    appendMessage(msg.content, messageClass);
  });
}

export async function loadChatList() {
  try {
    const chatList = await getChatList();

    chatListContainer.innerHTML = chatList
      .map(
        (chat) => `
      <div class="chat-item" data-session-id="${chat.session_id}">
        <span class="chatTitle" title="${chat.title}">${chat.title}</span>
        
        ${createActionsMenu(chat.session_id)}

      </div>
    `,
      )
      .join("");
  } catch (error) {
    console.error("failed to load documents:", error);
    chatListContainer.innerHTML = `<pError loading documents.</p>`;
  }
}

export function initializeChatForm() {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const messageText = userInput.value.trim();
    if (!messageText) return;

    appendMessage(messageText, "user-message");
    userInput.value = "";

    const loadingMessageId = appendMessage("Thinking...", "ai-message loading");

    let chatId = getActiveChatId();

    try {
      if (!chatId) {
        console.log("No active session. Creating a new chat session...");

        const response = await apiRequest(`${URL}/chat/session`, {
          method: "POST",
        });

        const sessionData = await response.json();

        chatId = sessionData.session_id;

        setCurrentSessionId(sessionData.session_id);

        await loadChatList();

        history.pushState({}, "", `?Chat=${chatId}`);
      }

      const response = await apiRequest(`${URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: messageText,
          session_id: chatId,
        }),
      });

      const loadingElem = document.getElementById(loadingMessageId);
      if (loadingElem) {
        loadingElem.textContent = await response.text();
        loadingElem.className = "message ai-message";
      }

      setTimeout(async () => {
        await loadChatList();
      }, 5000);
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
}

export function handleChatListClick() {
  chatListContainer.addEventListener("click", async (e) => {
    const dotsMenuBtn = e.target.closest(".dots-menu-btn");
    if (dotsMenuBtn) {
      const chatItem = dotsMenuBtn.closest(".chat-item");
      toggleMenu(e, chatItem.dataset.sessionId);
      return;
    }

    const deleteBtn = e.target.closest(".delete-btn");
    if (deleteBtn) {
      const chatItem = deleteBtn.closest(".chat-item");
      deleteChat(chatItem.dataset.sessionId);
      return;
    }

    const renameBtn = e.target.closest(".rename-btn");
    if (renameBtn) {
      const chatItem = renameBtn.closest(".chat-item");

      const newTitle = prompt("Write a new chat name (max 50 characters): ");

      if (newTitle !== null) {
        const trimmedTitle = newTitle.trim();
        if (trimmedTitle === "") {
          alert("The chat name cannot be blank!");
        } else if (trimmedTitle.length > 50) {
          alert(`The name is too long! (you writed ${trimmedTitle.length}).`);
        } else {
          renameChatTitle(chatItem.dataset.sessionId, newTitle.trim());
        }
      }
      return;
    }

    const chatItem = e.target.closest(".chat-item");

    if (chatItem) {
      if (chatItem && !e.target.closest(".dropdown-menu")) {
        navigateToChat(chatItem.dataset.sessionId);
      }
    }
  });
}

export function navigateToChat(session_id) {
  history.pushState({}, "", `?Chat=${session_id}`);
  render();
}
