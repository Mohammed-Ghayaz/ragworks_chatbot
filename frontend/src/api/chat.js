const API = "http://localhost:8000";

export async function getConversations(token) {
  return fetch(`${API}/conversations`, {
    headers: { Authorization: `Bearer ${token}` }
  });
}
