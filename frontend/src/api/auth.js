import { API_BASE } from "../config";

async function handleResponse(res) {
  const json = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(json?.detail || `HTTP ${res.status}`);
  }
  return json;
}

export async function loginUser(email, password) {
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    return await handleResponse(res);
  } catch (err) {
    throw new Error(`Network error: ${err.message}`);
  }
}

export async function registerUser(name, email, password) {
  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });
    return await handleResponse(res);
  } catch (err) {
    throw new Error(`Network error: ${err.message}`);
  }
}
