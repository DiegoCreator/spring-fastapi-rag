import {
  loadChatList,
  initializeChatForm,
  handleChatListClick,
} from "./chat.js";
import {
  loadDocuments,
  initializeDocumentUpload,
  handleDocumentDeleteClick,
} from "./documents.js";
import { render, appendMessage } from "./ui.js";

window.addEventListener("DOMContentLoaded", async () => {
  initializeChatForm();
  initializeDocumentUpload();
  handleChatListClick();
  handleDocumentDeleteClick();

  await render();
  await loadChatList();
  await loadDocuments();
});

window.addEventListener("popstate", render);
