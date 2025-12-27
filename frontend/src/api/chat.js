const API = "http://localhost:8000";

export async function getConversations(token) {
  return fetch(`${API}/conversations`, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export async function getConversationMessages(conversationId, token, limit = 100) {
  return fetch(`${API}/conversations/${conversationId}/messages?limit=${limit}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
}
