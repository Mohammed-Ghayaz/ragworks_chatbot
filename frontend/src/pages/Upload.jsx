import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadDocuments } from "../api/upload";
import { useAuth } from "../context/AuthContext";
import Spinner from "../components/Spinner";

export default function Upload() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  async function submit() {
    if (files.length === 0) return alert("Please select files to upload");
    setLoading(true);
    const res = await uploadDocuments(files, token);
    const data = await res.json();
    setLoading(false);

    navigate(`/chat?c=${data.conversation_id}`);
  }

  function onDrop(e) {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...dropped]);
  }

  return (
    <div className="max-w-3xl mx-auto mt-12">
      <div className="bg-white shadow p-6 rounded">
        <h2 className="text-xl font-semibold mb-4">Upload Documents</h2>

        {loading && <Spinner />}

        <div
          onDrop={onDrop}
          onDragOver={(e) => e.preventDefault()}
          className="border-dashed border-2 border-slate-200 rounded p-6 text-center text-slate-600"
        >
          <p>Drag & drop files here, or</p>
          <label className="inline-block mt-3 bg-indigo-600 text-white px-4 py-2 rounded cursor-pointer">
            Select files
            <input className="hidden" type="file" multiple onChange={(e) => setFiles([...files, ...e.target.files])} />
          </label>
        </div>

        {files.length > 0 && (
          <div className="mt-4">
            <h4 className="font-semibold">Files to upload</h4>
            <ul className="mt-2 space-y-1">
              {files.map((f, i) => (
                <li key={i} className="flex items-center justify-between p-2 border rounded">
                  <div className="text-sm">{f.name}</div>
                  <div className="text-xs text-slate-500">{Math.round((f.size||0)/1024)} KB</div>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-4 flex gap-3">
          <button className="bg-indigo-600 text-white px-4 py-2 rounded" onClick={submit}>
            {loading ? 'Uploading…' : 'Upload & Start Chat'}
          </button>
          <button className="px-4 py-2 border rounded" onClick={() => setFiles([])}>Clear</button>
        </div>
      </div>
    </div>
  );
}
