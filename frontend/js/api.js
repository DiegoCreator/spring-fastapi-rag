export const URL = "http://localhost:8080/api";

export async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`${response.status}: ${error}`);
  }

  return response;
}
