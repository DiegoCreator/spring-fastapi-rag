let currentSessionId = null;

export function setCurrentSessionId(id) {
  currentSessionId = id;
}

export function getCurrentSessionId() {
  return currentSessionId;
}
