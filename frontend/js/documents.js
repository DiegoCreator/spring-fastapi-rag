import { apiRequest, URL } from "./api.js";
import { uploadInput, documentListContainer } from "./dom.js";

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
      <div>
        ${escapeHTML(doc.filename)}
       <button class="delete-btn" data-id="${doc.id}">
          Delete
        </button>
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
    const btn = e.target.closest(".delete-btn");
    if (!btn) return;

    const id = btn.dataset.id;
    try {
      deleteDocument(id);
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
