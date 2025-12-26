export async function validateToken(token) {
  if (!token) return false;

  try {
    const res = await fetch("http://localhost:8000/auth/me", {
      headers: { Authorization: `Bearer ${token}` }
    });

    return res.ok;
  } catch {
    return false;
  }
}
