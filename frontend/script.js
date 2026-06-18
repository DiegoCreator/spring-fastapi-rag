const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const uploadLabel = document.getElementById("uploadLabel");
const uploadInput = document.getElementById("uploadInput");
const statusDiv = document.getElementById("status");
const chatListContainer = document.getElementById("chatList");
const documentListContainer = document.getElementById("documentList");

let currentSessionId = null;

let messageCounter = 0;

const CHAT_BASE_URL = "http://localhost:8080/api";
const DOC_BASE_URL = "http://localhost:8000";

function getActiveChatId() {
  return new URLSearchParams(window.location.search).get("Chat");
}

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

      const response = await apiRequest(`${CHAT_BASE_URL}/chat/session`, {
        method: "POST",
      });

      const sessionData = await response.json();

      chatId = sessionData.session_id;
      currentSessionId = sessionData.session_id;

      history.pushState({}, "", `?Chat=${chatId}`);
      await loadChatList();
    }

    const response = await apiRequest(`${CHAT_BASE_URL}/ask`, {
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

async function loadChatHistory(session_id) {
  currentSessionId = session_id;

  chatMessages.innerHTML = "";

  const response = await apiRequest(
    `${CHAT_BASE_URL}/chat/session/${session_id}/history`,
  );

  const historyMessages = await response.json();

  historyMessages.forEach((msg) => {
    const messageClass = msg.role === "user" ? "user-message" : "ai-message";
    appendMessage(msg.content, messageClass);
  });
}

async function loadChatList() {
  const chatList = await getChatList();

  chatListContainer.innerHTML = chatList
    .map(
      (chat) => `
      <div class="chat-item" data-session-id="${chat.session_id}">
        <span class="chatTitle">${chat.title}</span>
        <button class="delete-btn" onclick="event.stopPropagation(); deleteChat('${chat.session_id}')">
          Delete
        </button>
      </div>
    `,
    )
    .join("");
}

async function deleteChat(id) {
  const response = await apiRequest(`${DOC_BASE_URL}/chat/session/${id}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  });

  await loadChatList();

  const activeId = getActiveChatId();

  if (activeId === id) {
    history.pushState({}, "", "/");
    render();
  }

  return response.json();
}

async function getChatList() {
  const response = await apiRequest(`${CHAT_BASE_URL}/chat/sessions`);
  return response.json();
}

uploadInput.addEventListener("change", async () => {
  if (uploadInput.files.length === 0) {
    return;
  }

  const file = uploadInput.files[0];

  try {
    const result = await uploadFile(file);
    console.log("Server response:", result);
  } catch (error) {
    console.log(`Upload failed: ${error.message}`);
  }
});

async function loadDocuments() {
  const documents = await getDocuments();

  documentListContainer.innerHTML = documents
    .map(
      (doc) => `
      <div>
        ${doc.filename}
        <button class="delete-btn" onclick="deleteDocument('${doc.id}')">
          Delete
        </button>
      </div>
    `,
    )
    .join("");
}

async function deleteDocument(id) {
  const response = await apiRequest(`${DOC_BASE_URL}/documents/${id}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  });

  loadDocuments();

  return response.text();
}

async function uploadFile(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await apiRequest(`${DOC_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  await loadDocuments();

  return response.text();
}

async function getDocuments() {
  const response = await apiRequest(`${DOC_BASE_URL}/documents`);
  return response.json();
}

async function render() {
  const chatId = getActiveChatId();

  if (!chatId) {
    currentSessionId = null;
    chatMessages.innerHTML = "";
    return;
  }

  currentSessionId = chatId;
  await loadChatHistory(chatId);
}

function navigateToChat(session_id) {
  history.pushState({}, "", `?Chat=${session_id}`);
  render();
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`${response.status}: ${error}`);
  }

  return response;
}

chatListContainer.addEventListener("click", (e) => {
  const chatItem = e.target.closest(".chat-item");
  if (!chatItem) return;

  navigateToChat(chatItem.dataset.sessionId);
});

window.addEventListener("popstate", () => {
  render();
});

window.addEventListener("DOMContentLoaded", () => {
  render();
  loadChatList();
  loadDocuments();
});
