import { apiRequest, URL } from "./api.js";
import { uploadInput, documentListContainer } from "./dom.js";
import { createActionsMenu, toggleMenu } from "./ui.js";

export async function getDocuments() {
  const response = await apiRequest(`${URL}/documents`);
  return response.json();
}

export async function loadDocuments() {
  try {
    const documents = await getDocuments();

    documentListContainer.innerHTML = documents
      .map(
        (doc) => `
      <div class="doc-item" data-id="${doc.id}">
        <span class=docTitle title="${doc.filename}">${escapeHTML(doc.filename)}</span>
        ${createActionsMenu(doc.id, { showRename: false })}
      </div>
    `,
      )
      .join("");
  } catch (error) {
    console.error("failed to load documents:", error);
    documentListContainer.innerHTML = `<pError loading documents.</p>`;
  }
}

export function handleDocumentDeleteClick() {
  documentListContainer.addEventListener("click", (e) => {
    const dotsMenuBtn = e.target.closest(".dots-menu-btn");
    if (dotsMenuBtn) {
      const docItem = dotsMenuBtn.closest(".doc-item");

      toggleMenu(e, docItem.dataset.id);
      return;
    }

    const btn = e.target.closest(".delete-btn");
    if (!btn) return;

    const docItem = btn.closest(".doc-item");
    try {
      deleteDocument(docItem.dataset.id);
    } catch (error) {
      console.error(`Deletion failed: ${error.message}`);
      alert("Could not delete document.");
    }
  });
}

export async function uploadFile(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(`${URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`${response.status}: ${error}`);
  }

  await loadDocuments();
  return response.text();
}

export async function deleteDocument(id) {
  const response = await apiRequest(`${URL}/documents/${id}`, {
    method: "DELETE",
  });

  loadDocuments();

  return response.text();
}

export function initializeDocumentUpload() {
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
      alert("File upload failed.");
    }
  });
}

function escapeHTML(str) {
  return str.replace(
    /[&<>'"]/g,
    (tag) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[
        tag
      ] || tag,
  );
}
