import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { token, logout } = useAuth();

  return (
    <nav className="px-6 py-3 border-b flex justify-between items-center bg-white/80 backdrop-blur sticky top-0 z-20">
      <Link to="/" className="font-semibold text-lg text-slate-800">RAGWorks</Link>

      <div className="space-x-3">
        {!token && (
          <>
            <Link className="text-slate-600 hover:text-slate-800" to="/login">Login</Link>
            <Link className="text-slate-600 hover:text-slate-800" to="/register">Register</Link>
          </>
        )}

        {token && (
          <>
            <Link className="text-slate-600 hover:text-slate-800" to="/chat">Chat</Link>
            <button
              className="ml-2 px-3 py-1 bg-rose-600 text-white rounded"
              onClick={() => logout()}
            >
              Logout
            </button>
          </>
        )} 
      </div>
    </nav>
  );
}
