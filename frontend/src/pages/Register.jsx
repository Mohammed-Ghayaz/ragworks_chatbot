import { useState } from "react";
import { registerUser } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import Spinner from "../components/Spinner";

export default function Register() {
  const { setToken } = useAuth();
  const [loading,setLoading]=useState(false);
  const [name,setName]=useState("");
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");

  async function submit(e){
    e.preventDefault();
    setLoading(true);

    const res = await registerUser(name,email,password);
    const data = await res.json();

    setLoading(false);

    if(res.ok){
      setToken(data.access_token);
      window.location.href="/";
    } else alert(data.detail);
  }

  return (
    <div className="max-w-md mx-auto mt-16 p-6 bg-white shadow rounded">
      <h2 className="text-xl font-semibold mb-4">Register</h2>

      {loading && <Spinner/>}

      <form onSubmit={submit} className="space-y-4">
        <input className="w-full border p-2" placeholder="Name" onChange={e=>setName(e.target.value)}/>
        <input className="w-full border p-2" placeholder="Email" onChange={e=>setEmail(e.target.value)}/>
        <input type="password" className="w-full border p-2" placeholder="Password" onChange={e=>setPassword(e.target.value)}/>
        <button className="bg-black text-white w-full py-2 rounded">
          Register
        </button>
      </form>
    </div>
  );
}
