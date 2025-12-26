import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { loginUser } from "../api/auth";
import Spinner from "../components/Spinner";

export default function Login() {
  const { setToken } = useAuth();
  const [loading, setLoading] = useState(false);
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");

  async function submit(e){
    e.preventDefault();
    setLoading(true);

    const res = await loginUser(email,password);
    const data = await res.json();

    setLoading(false);

    if(res.ok){
      setToken(data.access_token);
      window.location.href="/";
    } else alert(data.detail);
  }

  return (
    <div className="max-w-md mx-auto mt-16 p-6 bg-white shadow rounded">
      <h2 className="text-xl font-semibold mb-4">Login</h2>

      {loading && <Spinner/>}

      <form onSubmit={submit} className="space-y-4">
        <input className="w-full border p-2" placeholder="Email" onChange={e=>setEmail(e.target.value)}/>
        <input type="password" className="w-full border p-2" placeholder="Password" onChange={e=>setPassword(e.target.value)}/>
        <button className="bg-black text-white w-full py-2 rounded">
          Login
        </button>
      </form>
    </div>
  );
}
