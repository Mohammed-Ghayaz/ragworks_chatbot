import { useState } from "react";
import { uploadDocuments } from "../api/upload";
import { useAuth } from "../context/AuthContext";
import Spinner from "../components/Spinner";

export default function Upload(){
  const { token } = useAuth();
  const [files,setFiles]=useState([]);
  const [loading,setLoading]=useState(false);

  async function submit(){
    setLoading(true);
    const res = await uploadDocuments(files,token);
    const data = await res.json();
    setLoading(false);

    window.location.href="/chat?c="+data.conversation_id;
  }

  return (
    <div className="max-w-lg mx-auto mt-12 bg-white shadow p-6 rounded">
      <h2 className="text-xl font-semibold mb-4">Upload Documents</h2>

      {loading && <Spinner/>}

      <input type="file" multiple onChange={e=>setFiles([...e.target.files])}/>
      <button className="bg-black text-white px-4 py-2 rounded mt-4"
        onClick={submit}>
        Upload & Start Chat
      </button>
    </div>
  );
}
