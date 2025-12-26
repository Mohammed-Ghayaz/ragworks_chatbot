import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { login } = useAuth();
  const [form, setForm] = useState({ name: "", email: "", password: "" });

  async function handleRegister(e) {
    e.preventDefault();

    const res = await fetch("http://localhost:8000/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });

    const data = await res.json();

    if (res.ok) {
      login(data.access_token);
      window.location.href = "/";
    } else {
      alert(data.detail || "Registration failed");
    }
  }

  return (
    <div className="max-w-md mx-auto mt-16 bg-white shadow p-6 rounded-xl">
      <h2 className="text-2xl font-semibold mb-4 text-center">Register</h2>

      <form onSubmit={handleRegister} className="space-y-4">
        <input className="w-full border p-2 rounded"
          placeholder="Name"
          onChange={e => setForm({ ...form, name: e.target.value })}
        />

        <input className="w-full border p-2 rounded"
          type="email"
          placeholder="Email"
          onChange={e => setForm({ ...form, email: e.target.value })}
        />

        <input className="w-full border p-2 rounded"
          type="password"
          placeholder="Password"
          onChange={e => setForm({ ...form, password: e.target.value })}
        />

        <button className="w-full bg-black text-white py-2 rounded-lg">
          Register
        </button>
      </form>
    </div>
  );
}
