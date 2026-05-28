const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const uploadLabel = document.getElementById("uploadLabel");
const txtFile = document.getElementById("txt-file");
const statusDiv = document.getElementById("status");

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

txtFile.addEventListener("change", async () => {
  if (txtFile.files.lenght === 0) {
    statusDiv.textContent = "Please select a file first.";
    return;
  }

  const file = txtFile.files[0];
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
