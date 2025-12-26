import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { token, setToken } = useAuth();

  return (
    <nav className="px-6 py-3 border-b flex justify-between bg-white">
      <Link to="/" className="font-semibold text-lg">RAGWorks</Link>

      <div className="space-x-3">
        {!token && <>
          <Link to="/login">Login</Link>
          <Link to="/register">Register</Link>
        </>}

        {token && <>
          <Link to="/">Upload</Link>
          <Link to="/chat">Chat</Link>
          <button onClick={() => setToken(null)}>Logout</button>
        </>}
      </div>
    </nav>
  );
}
