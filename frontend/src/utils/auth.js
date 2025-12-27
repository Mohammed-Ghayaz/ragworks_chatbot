import { API_BASE } from "../config";

export async function validateToken(token) {
  if (!token) return false;

  try {
    const API = API_BASE || process.env.REACT_APP_BACKEND_URL || process.env.BACKEND_URL || "http://localhost:8000";
    const res = await fetch(`${API}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    return res.ok;
  } catch {
    return false;
  }
}
