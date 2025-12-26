import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { validateToken } from "../utils/auth";

export default function Upload() {
  const navigate = useNavigate();
  const [ready, setReady] = useState(false);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");

    validateToken(token).then(valid => {
      if (!valid) navigate("/login");
      else setReady(true);
    });
  }, []);

  async function handleUpload(e) {
    e.preventDefault();

    const token = localStorage.getItem("token");

    const form = new FormData();
    files.forEach(f => form.append("uploaded_files", f));

    setLoading(true);

    const res = await fetch("http://localhost:8000/upload", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: form
    });

    const data = await res.json();
    setLoading(false);

    if (res.ok) navigate(`/chat/${data.conversation_id}`);
    else alert("Upload failed");
  }

  if (!ready) return null;

  return (
    <div className="max-w-lg mx-auto mt-20 bg-white shadow p-6 rounded-xl">
      <h2 className="text-2xl font-semibold mb-4 text-center">
        Upload Documents
      </h2>

      <form onSubmit={handleUpload} className="space-y-4">
        <input
          type="file"
          multiple
          onChange={e => setFiles(Array.from(e.target.files))}
        />

        <button disabled={loading}
          className="w-full bg-black text-white py-2 rounded-lg">
          {loading ? "Processing..." : "Start Chat"}
        </button>
      </form>
    </div>
  );
}
