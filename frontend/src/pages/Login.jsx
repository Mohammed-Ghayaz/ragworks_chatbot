import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { loginUser } from "../api/auth";
import Spinner from "../components/Spinner";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function submit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await loginUser(email, password);
      const data = await res.json();

      if (res.ok) {
        login(data.access_token);
        navigate("/", { replace: true });
      } else {
        alert(data.detail || "Login failed");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto mt-16 p-6 bg-white shadow rounded">
      <h2 className="text-2xl font-semibold mb-4 text-slate-800">Welcome back</h2>

      {loading && <Spinner />}

      <form onSubmit={submit} className="space-y-4">
        <input className="w-full border p-2 rounded" placeholder="Email" onChange={e => setEmail(e.target.value)} />
        <input type="password" className="w-full border p-2 rounded" placeholder="Password" onChange={e => setPassword(e.target.value)} />
        <button className="bg-black text-white w-full py-2 rounded">
          Login
        </button>
      </form>
    </div>
  );
}
