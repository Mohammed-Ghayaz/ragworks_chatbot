import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { token, logout } = useAuth();

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-5xl mx-auto px-4 py-3 flex justify-between items-center">
        <Link to="/" className="text-xl font-semibold">
          RagWorks 🤖
        </Link>

        <div className="space-x-4">
          {!token ? (
            <>
              <Link to="/login" className="text-gray-600 hover:text-black">
                Login
              </Link>
              <Link
                to="/register"
                className="bg-black text-white px-3 py-1 rounded-lg"
              >
                Sign Up
              </Link>
            </>
          ) : (
            <button
              onClick={logout}
              className="bg-red-500 text-white px-3 py-1 rounded-lg"
            >
              Logout
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
