import { useEffect, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { getConversations } from "../api/chat";
import Spinner from "../components/Spinner";

export default function Chat(){
  const { token } = useAuth();
  const wsRef = useRef(null);

  const [list,setList]=useState([]);
  const [current,setCurrent]=useState(localStorage.getItem("conv")||null);
  const [messages,setMessages]=useState([]);
  const [input,setInput]=useState("");
  const [loading,setLoading]=useState(false);

  useEffect(()=>{
    async function load(){
      setLoading(true);
      const res = await getConversations(token);
      const data = await res.json();
      setList(data);
      setLoading(false);
    }
    load();
  },[]);

  function connect(conv){
    if(wsRef.current) wsRef.current.close();

    wsRef.current = new WebSocket(
      `ws://localhost:8000/chat?token=${token}`
    );

    wsRef.current.onopen = () => {
      setMessages([]);
      setCurrent(conv);
      localStorage.setItem("conv",conv);
    };

    wsRef.current.onmessage = e => {
      setMessages(prev=>{
        const m=[...prev];
        m[m.length-1].content+=e.data;
        return m;
      });
    };
  }

  function send(){
    setMessages(prev=>[
      ...prev,
      {role:"human",content:input},
      {role:"ai",content:""}
    ]);

    wsRef.current.send(JSON.stringify({
      conversation_id: current,
      message: input
    }));

    setInput("");
  }

  return (
    <div className="flex h-screen">

      <aside className="w-72 border-r p-4 space-y-2 bg-gray-100">
        <h2 className="font-semibold">Conversations</h2>

        {loading && <Spinner/>}

        {list.map(c=>(
          <button
            key={c.conversation_id}
            className={`block w-full text-left px-3 py-2 rounded
            ${current===c.conversation_id?"bg-black text-white":"hover:bg-gray-200"}`}
            onClick={()=>connect(c.conversation_id)}>
            Chat
          </button>
        ))}
      </aside>

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

        <div className="p-4 border-t flex gap-2">
          <input className="flex-1 border p-2 rounded"
            value={input}
            onChange={e=>setInput(e.target.value)}/>
          <button className="bg-black text-white px-4 rounded" onClick={send}>
            Send
          </button>
        </div>
      </main>

    </div>
  );
}
