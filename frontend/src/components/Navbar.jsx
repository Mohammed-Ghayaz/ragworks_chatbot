import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { token, logout } = useAuth();

  return (
    <nav className="bg-black text-white px-6 py-3 flex justify-between">
      <Link to="/" className="font-bold text-xl">
        RAGWorks
      </Link>

      <div className="space-x-4">
        {token ? (
          <>
            <Link to="/upload">Upload</Link>
            <button onClick={logout} className="underline">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}
