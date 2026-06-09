const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const uploadLabel = document.getElementById("uploadLabel");
const uplodInput = document.getElementById("uploadInput");
const statusDiv = document.getElementById("status");
const chatListContainer = document.getElementById("chatList");
const documentListContainer = document.getElementById("documentList");

let currentSessionId = null;
let chatHistory = [];

let messageCounter = 0;

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const BACKEND_URL = "http://localhost:8080/api/ask";

  const messageText = userInput.value.trim();
  if (!messageText) return;

  appendMessage(messageText, "user-message");

  userInput.value = "";

  const loadingMessageId = appendMessage("Thinking...", "ai-message loading");

  try {
    if (currentSessionId === null) {
      console.log("No active session. Creating a new chat session...");

      const sessionResponse = await fetch(
        "http://localhost:8080/api/chat/session",
        {
          method: "POST",
        },
      );

      if (!sessionResponse.ok) {
        throw new Error(`Failed to create session: ${sessionResponse.status}`);
      }

      const sessionData = await sessionResponse.json();

      console.log(sessionData);

      currentSessionId = sessionData.session_id;
    }

    const response = await fetch(BACKEND_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: messageText,
        session_id: currentSessionId,
      }),
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

uplodInput.addEventListener("change", async () => {
  if (uplodInput.files.length === 0) {
    statusDiv.textContent = "Please select a file first.";
    return;
  }

  const file = uplodInput.files[0];
  statusDiv.textContent = "Uploading";

  try {
    const result = await uploadFile(file);
    statusDiv.textContent = `Success! File ID: ${result.file_id}`;
    console.log("Server response:", result);
  } catch (error) {
    statusDiv.textContent = `Upload failed: ${error.message}`;
  }
});

async function uploadFile(file) {
  const formData = new FormData();

  formData.append("file", file);

  try {
    const response = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Upload failed with status ${response.status}: ${errorText}`,
      );
    }

    const data = await response.text();
    return data;
  } catch (error) {
    console.error("Error uploading file: ", error);
  }
}

async function getDocuments() {
  try {
    const response = await fetch("http://localhost:8000/documents", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Upload failed with status ${response.status}: ${errorText}`,
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error uploading file: ", error);
  }
}

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
  try {
    const response = await fetch(`http://localhost:8000/documents/${id}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Upload failed with status ${response.status}: ${errorText}`,
      );
    }

    const data = await response.json();

    await loadDocuments();

    return data;
  } catch (error) {
    console.error("Error deleting file: ", error);
  }
}

async function deleteChat(id) {
  try {
    const response = await fetch(`http://localhost:8000/chat/session/${id}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Upload failed with status ${response.status}: ${errorText}`,
      );
    }

    const data = await response.json();

    await loadDocuments();

    return data;
  } catch (error) {
    console.error("Error deleting chat: ", error);
  }
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

async function loadChatHistory(session_id) {
  currentSessionId = session_id;

  chatMessages.innerHTML = "";

  statusDiv.textContent = "Loading chat history...";

  try {
    const response = await fetch(
      `http://localhost:8080/api/chat/session/${session_id}/history`,
      {
        method: "GET",
      },
    );

    if (!response.ok) throw new Error("Could not load history");

    const historyMessages = await response.json();

    historyMessages.forEach((msg) => {
      const messageClass = msg.role === "user" ? "user-message" : "ai-message";
      appendMessage(msg.content, messageClass);
    });

    statusDiv.textContent = "History loaded.";
  } catch (error) {
    console.error("Error loading history:", error);
    statusDiv.textContent = "Failed to load history.";
  }
}

async function getChatList() {
  try {
    const response = await fetch(`http://localhost:8080/api/chat/sessions`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Upload failed with status ${response.status}: ${errorText}`,
      );
    }

    const data = await response.json();

    return data;
  } catch (error) {
    console.error("Error loading chats:", error);
    statusDiv.textContent = "Failed to load chats.";
  }
}

async function loadChatList() {
  const chatList = await getChatList();

  chatListContainer.innerHTML = chatList
    .map(
      (chat) => `
      <div class="chat-item" data-session-id="${chat.session_id}">
        <span class="chatTitle">${chat.title}</span>
        <button class="delete-btn" onclick="deleteChat('${chat.session_id}')">
          Delete
        </button>
      </div>
    `,
    )
    .join("");
}

chatListContainer.addEventListener("click", (e) => {
  const chatItem = e.target.closest(".chat-item");

  if (!chatItem) return;

  const session_id = chatItem.dataset.sessionId;

  history.pushState({}, "", `?Chat=${session_id}`);

  loadChatHistory(session_id);
});

window.addEventListener("DOMContentLoaded", () => {
  const parts = window.location.pathname.split("/");
  const params = new URLSearchParams(window.location.search);
  const session_id = params.get("Chat");

  if (session_id) {
    loadChatHistory(session_id);
  }
});

loadChatList();
loadDocuments();
