import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleLogin(e) {
    e.preventDefault();

    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.ok) {
      login(data.access_token);
      window.location.href = "/";
    } else {
      alert(data.detail || "Login failed");
    }
  }

  return (
    <div className="max-w-md mx-auto mt-16 bg-white shadow p-6 rounded-xl">
      <h2 className="text-2xl font-semibold mb-4 text-center">Login</h2>

      <form onSubmit={handleLogin} className="space-y-4">
        <input className="w-full border p-2 rounded"
          type="email"
          placeholder="Email"
          onChange={e => setEmail(e.target.value)}
        />

        <input className="w-full border p-2 rounded"
          type="password"
          placeholder="Password"
          onChange={e => setPassword(e.target.value)}
        />

        <button className="w-full bg-black text-white py-2 rounded-lg">
          Login
        </button>
      </form>
    </div>
  );
}
