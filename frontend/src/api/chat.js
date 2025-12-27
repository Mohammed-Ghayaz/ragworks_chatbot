import { API_BASE } from "../config";

const API = API_BASE || process.env.REACT_APP_BACKEND_URL || process.env.BACKEND_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000');

async function handleResponse(res) {
  const json = await res.json().catch(() => null);
  if (!res.ok) throw new Error(json?.detail || `HTTP ${res.status}`);
  return json;
}

export async function getConversations(token) {
  try {
    const res = await fetch(`${API}/conversations`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return await handleResponse(res);
  } catch (err) {
    throw new Error(`Network error: ${err.message}`);
  }
}

export async function getConversationMessages(conversationId, token, limit = 100) {
  try {
    const res = await fetch(`${API}/conversations/${conversationId}/messages?limit=${limit}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return await handleResponse(res);
  } catch (err) {
    throw new Error(`Network error: ${err.message}`);
  }
}
