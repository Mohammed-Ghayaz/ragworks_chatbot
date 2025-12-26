import { useEffect, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { getConversations } from "../api/chat";
import Spinner from "../components/Spinner";

export default function Chat() {

  const { token } = useAuth();
  const wsRef = useRef(null);

  const [list,setList] = useState([]);
  const [current,setCurrent] = useState(localStorage.getItem("conv") || null);
  const [messages,setMessages] = useState([]);
  const [input,setInput] = useState("");
  const [loading,setLoading] = useState(false);
  const [connecting,setConnecting] = useState(false);

  // ---------------- Load Conversations ----------------
  useEffect(()=>{
    async function load(){
      setLoading(true);
      const res = await getConversations(token);
      const data = await res.json();
      setList(data);
      setLoading(false);
    }
    load();
  },[token]);

  // ---------------- Connect WebSocket ----------------
  function connect(convId){

    if(!token) return;

    if(wsRef.current){
      wsRef.current.close();
      wsRef.current = null;
    }

    setConnecting(true);

    const ws = new WebSocket(
      `ws://localhost:8000/chat?token=${token}`
    );

    wsRef.current = ws;

    ws.onopen = () => {
      setMessages([]);
      setCurrent(convId);
      localStorage.setItem("conv", convId);
      setConnecting(false);
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
    <div className="flex h-screen">

      {/* ---------------- Sidebar ---------------- */}
      <aside className="w-72 border-r p-4 space-y-2 bg-gray-100">
        <h2 className="font-semibold">Conversations</h2>

        {loading && <Spinner/>}

        {list.map(c => (
          <button
            key={c.conversation_id}
            className={`block w-full text-left px-3 py-2 rounded
            ${current===c.conversation_id?"bg-black text-white":"hover:bg-gray-200"}`}
            onClick={() => connect(c.conversation_id)}
          >
            Chat
          </button>
        ))}
      </aside>

      {/* ---------------- Chat Window ---------------- */}
      <main className="flex-1 flex flex-col">

        <div className="flex-1 p-6 space-y-3 overflow-y-auto">
          {messages.map((m,i)=>(
            <div key={i}
              className={`max-w-lg p-3 rounded-xl
              ${m.role==="human"?"bg-blue-100 ml-auto":"bg-gray-200"}`}>
              {m.content}
            </div>
          ))}
        </div>

        {/* ---------------- Input ---------------- */}
        <div className="p-4 border-t flex gap-2">
          <input
            className="flex-1 border p-2 rounded"
            value={input}
            onChange={e=>setInput(e.target.value)}
            disabled={connecting}
          />

          <button
            className="bg-black text-white px-4 rounded"
            onClick={send}
            disabled={connecting}
          >
            {connecting ? "Connecting..." : "Send"}
          </button>
        </div>

      </main>

    </div>
  );
}
