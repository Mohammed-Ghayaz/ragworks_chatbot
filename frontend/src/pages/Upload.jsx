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

    try {
      const data = await uploadDocuments(files, token);
      if (data && data.conversation_id) {
        navigate(`/chat?c=${data.conversation_id}`);
      } else {
        alert('Upload succeeded but no conversation id returned');
      }
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Upload failed: " + (err.message || "unknown error"));
    } finally {
      setLoading(false);
    }
  }

  function onDrop(e) {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer?.files || []).filter(Boolean);
    setFiles((prev) => [...prev, ...dropped]);
  }

  function onFileInputChange(e) {
    const selected = Array.from(e.target.files || []).filter(Boolean);
    setFiles((prev) => [...prev, ...selected]);
    // clear input value so same file can be chosen again
    e.target.value = null;
  }

  function removeFile(index) {
    setFiles((prev) => prev.filter((_, i) => i !== index));
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
            <input className="hidden" type="file" multiple onChange={onFileInputChange} />
          </label>
        </div>

        {files.length > 0 && (
          <div className="mt-4">
            <h4 className="font-semibold">Files to upload</h4>
            <ul className="mt-2 space-y-1">
              {files.map((f, i) => (
                <li key={`${f.name}-${f.size}-${i}`} className="flex items-center justify-between p-2 border rounded">
                  <div className="flex-1 text-sm truncate">{f.name}</div>
                  <div className="flex items-center gap-3">
                    <div className="text-xs text-slate-500">{Math.round((f.size||0)/1024)} KB</div>
                    <button type="button" className="text-rose-600 text-xs" onClick={() => removeFile(i)}>Remove</button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-4 flex gap-3">
          <button type="button" className="bg-indigo-600 text-white px-4 py-2 rounded" onClick={submit} disabled={loading}>
            {loading ? 'Uploading…' : 'Upload & Start Chat'}
          </button>
          <button type="button" className="px-4 py-2 border rounded" onClick={() => setFiles([])}>Clear</button>
        </div>
      </div>
    </div>
  );
}
