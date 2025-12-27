import { useEffect, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { getConversations, getConversationMessages } from "../api/chat";
import { uploadDocuments } from "../api/upload";
import Spinner from "../components/Spinner";
import { useLocation } from "react-router-dom";

export default function Chat() {

  const { token } = useAuth();
  const wsRef = useRef(null);
  const containerRef = useRef(null);
  const endRef = useRef(null);
  const location = useLocation();

  const [list,setList] = useState([]);
  const [current,setCurrent] = useState(localStorage.getItem("conv") || null);
  const [messages,setMessages] = useState([]);
  const [input,setInput] = useState("");
  const [loading,setLoading] = useState(false);
  const [connecting,setConnecting] = useState(false);

  // upload-specific state
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [showUpload, setShowUpload] = useState(true);

  // when current conversation changes, load any persisted uploaded filenames for it
  useEffect(()=>{
    if(current){
      const stored = localStorage.getItem(`uploaded_files_${current}`);
      if(stored){
        try { setUploadedFiles(JSON.parse(stored)); setShowUpload(false); } catch(e){ setUploadedFiles([]); setShowUpload(true); }
      } else {
        setUploadedFiles([]);
        setShowUpload(true);
      }
    } else {
      setUploadedFiles([]);
      setShowUpload(true);
    }
  },[current]);

  // ---------------- Load Conversations ----------------
  useEffect(()=>{
    async function load(){
      setLoading(true);
      const res = await getConversations(token);
      const data = await res.json();
      setList(data);
      setLoading(false);
    }
    if(token) load();
  },[token]);

  // ---------------- Auto-connect if query param present ----------------
  useEffect(()=>{
    const params = new URLSearchParams(location.search);
    const conv = params.get("c");
    if(conv && token){
      connect(conv);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[location.search, token]);

  // ---------------- Auto-connect on reload when a conversation is stored in localStorage ----------------
  useEffect(()=>{
    if(current && token){
      // only attempt to connect if there's not already an open socket
      if(!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN){
        connect(current);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[current, token]);

  // ---------------- Load messages when current conversation changes (persisted history)
  useEffect(()=>{
    if(!current || !token) return;

    (async () => {
      try {
        const res = await getConversationMessages(current, token);
        if(res && res.ok){
          const data = await res.json();
          setMessages(data.map(d => ({ role: d.role, content: d.content })));
        } else {
          setMessages([]);
        }
      } catch (e) {
        console.error('Failed to load conversation messages', e);
        setMessages([]);
      }
    })();

    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[current, token]);

  // ---------------- scroll to bottom on new messages ----------------
  useEffect(()=>{
    if(endRef.current) endRef.current.scrollIntoView({ behavior: "smooth" });
  },[messages]);

  // ---------------- Cleanup on unmount (close websocket when leaving chat page) ----------------
  useEffect(() => {
    return () => {
      if(wsRef.current){
        try {
          if(wsRef.current.readyState === WebSocket.OPEN){
            try { wsRef.current.send(JSON.stringify({ action: 'close' })); } catch(e){}
          }
          wsRef.current.close();
        } catch(e){}
        wsRef.current = null;
      }
    };
  }, []);

  // ---------------- Connect WebSocket ----------------
  function connect(convId){

    if(!token) return;

    if(wsRef.current){
      try { wsRef.current.close(); } catch(e){}
      wsRef.current = null;
    }

    setConnecting(true);

    const wsUrl = (window.location.hostname === 'localhost')
      ? `ws://localhost:8000/chat?token=${token}`
      : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/chat?token=${token}`;

    const ws = new WebSocket(wsUrl);

    wsRef.current = ws;

    ws.onopen = () => {
      // load persisted messages from server for this conversation
      setCurrent(convId);
      localStorage.setItem("conv", convId);
      setConnecting(false);

      (async () => {
        try {
          const res = await getConversationMessages(convId, token);
          if(res && res.ok){
            const data = await res.json();
            setMessages(data.map(d => ({ role: d.role, content: d.content })));
          } else {
            setMessages([]);
          }
        } catch (e) {
          console.error('Failed to load conversation messages', e);
          setMessages([]);
        }
      })();
    };

    ws.onclose = (e) => {
      setConnecting(false);
      console.log("WebSocket closed", e);
      wsRef.current = null;
    };

    ws.onmessage = e => {
      setMessages(prev => {
        const updated = [...prev];

        // ensure last item exists
        if(updated.length === 0 || updated[updated.length-1].role !== "ai"){
          updated.push({ role:"ai", content:e.data });
        } else {
          updated[updated.length-1].content += e.data;
        }

        return updated;
      });
    };

    ws.onclose = () => {
      setConnecting(false);
      console.log("WebSocket closed");
    };

    ws.onerror = () => {
      setConnecting(false);
      console.log("WebSocket error");
    };
  }

  // ---------------- New Chat ----------------
  function newChat(){
    // close websocket and clear current conversation so upload area can be used
    if(wsRef.current){
      try {
        if(wsRef.current.readyState === WebSocket.OPEN){
          try { wsRef.current.send(JSON.stringify({ action: 'close' })); } catch(e){}
        }
        wsRef.current.close();
      } catch(e){}
      wsRef.current = null;
    }
    setCurrent(null);
    localStorage.removeItem("conv");
    setMessages([]);
    // reset uploaded files UI
    setUploadedFiles([]);
    setShowUpload(true);
  }

  // ---------------- Upload handlers ----------------
  function onDrop(e){
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer?.files || []).filter(Boolean);
    setFiles(prev => [...prev, ...dropped]);
  }

  function onFileInputChange(e){
    const selected = Array.from(e.target.files || []).filter(Boolean);
    setFiles(prev => [...prev, ...selected]);
    e.target.value = null;
  }

  function removeFile(index){
    setFiles(prev => prev.filter((_,i) => i !== index));
  }

  async function uploadFiles(){
    if(files.length === 0) return alert("Please select files to upload");
    setUploading(true);

    try {
      const res = await uploadDocuments(files, token);
      const data = await res.json();
      // add to conversation list and connect immediately
      const newId = data.conversation_id;
      const filenames = data.filenames || files.map(f => f.name);
      // persist uploaded filenames for this conversation so we can display them when opened
      localStorage.setItem(`uploaded_files_${newId}`, JSON.stringify(filenames));
      setUploadedFiles(filenames);
      setShowUpload(false);
      setList(prev => [{ conversation_id: newId, created_at: new Date().toISOString() }, ...prev]);
      setFiles([]);
      connect(newId);
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Upload failed: " + (err.message || "unknown error"));
    } finally {
      setUploading(false);
    }
  }

  // ---------------- Send Message ----------------
  function send(){

    if(!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN){
      alert("Chat is not connected yet");
      return;
    }

    if(!current){
      alert("Please select a conversation");
      return;
    }

    const msg = input.trim();
    if(!msg) return;

    setMessages(prev => [
      ...prev,
      { role:"human", content:msg },
      { role:"ai", content:"" }
    ]);

    wsRef.current.send(JSON.stringify({
      conversation_id: current,
      message: msg
    }));

    setInput("");
  }

  return (
    <div className="flex h-screen bg-gray-50">

      {/* ---------------- Sidebar ---------------- */}
      <aside className="w-72 border-r p-4 space-y-2 bg-white">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Conversations</h2>
          <button className="text-sm text-indigo-600" onClick={newChat}>New</button>
        </div>

        {loading && <Spinner/>}

        {list.map((c, i) => (
          <button
            key={c.conversation_id}
            className={`block w-full text-left px-3 py-2 rounded mt-2
            ${current===c.conversation_id?"bg-black text-white":"hover:bg-gray-100"}`}
            onClick={() => connect(c.conversation_id)}
          >
            {`Chat #${list.length - i}`}
          </button>
        ))} 
      </aside>

      {/* ---------------- Chat Window ---------------- */}
      <main className="flex-1 flex flex-col">

        {/* ---------------- Upload area (top) ---------------- */}
        {showUpload ? (
          <div className="border-b bg-white">
            <div className="max-w-3xl mx-auto p-4">
              <div
                onDrop={onDrop}
                onDragOver={(e) => e.preventDefault()}
                className="border-dashed border-2 border-slate-200 rounded p-4 text-center text-slate-600"
              >
                <p className="text-sm">Drag & drop files here, or</p>
                <label className="inline-block mt-2 bg-indigo-600 text-white px-3 py-1 rounded cursor-pointer">
                  Select files
                  <input className="hidden" type="file" multiple onChange={onFileInputChange} />
                </label>
              </div>

              {files.length > 0 && (
                <div className="mt-3">
                  <h4 className="font-semibold text-sm">Files to upload</h4>
                  <ul className="mt-2 space-y-2">
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

                  <div className="mt-3 flex gap-3">
                    <button type="button" className="bg-indigo-600 text-white px-3 py-1 rounded" onClick={uploadFiles} disabled={uploading}>
                      {uploading ? 'Uploading…' : 'Upload & Start Chat'}
                    </button>
                    <button type="button" className="px-3 py-1 border rounded" onClick={() => setFiles([])} disabled={uploading}>Clear</button>
                  </div>
                </div>
              )}

              {!current && (
                <div className="mt-3 text-sm text-slate-500">Upload files to start a new conversation, or select one from the left.</div>
              )}
            </div>
          </div>
        ) : (
          <div className="border-b bg-white">
            <div className="max-w-3xl mx-auto p-4">
              {uploadedFiles && uploadedFiles.length > 0 && (
                <div>
                  <h4 className="font-semibold text-sm">Uploaded files</h4>
                  <ul className="mt-2 space-y-1">
                    {uploadedFiles.map((name,i)=>(
                      <li key={i} className="text-sm text-slate-700">{name}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={containerRef} className="flex-1 p-6 space-y-3 overflow-y-auto flex justify-center">
          <div className="w-full max-w-3xl">
            {messages.map((m,i)=>(
              <div key={i}
                className={`w-fit max-w-full p-3 rounded-xl my-2 ${m.role==="human"?"bg-black text-white ml-auto":"bg-gray-200"}`}>
                {m.content}
              </div>
            ))}
            <div ref={endRef} />
          </div>
        </div>

        {/* ---------------- Input ---------------- */}
        <div className="p-4 border-t bg-white">
          <div className="max-w-3xl mx-auto flex gap-2">
            <input
              className="flex-1 border p-2 rounded"
              value={input}
              onChange={e=>setInput(e.target.value)}
              disabled={!current || connecting || uploading}
              onKeyDown={(e) => { if(e.key === 'Enter') send(); }}
              placeholder={current ? "Type your message..." : "Upload files to enable chat"}
            />

            <button
              className="bg-black text-white px-4 rounded"
              onClick={send}
              disabled={!current || connecting || uploading}
            >
              {connecting ? "Connecting..." : "Send"}
            </button>
          </div>
        </div>

      </main>

    </div>
  );
}
