import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { validateToken } from "../utils/auth";

export default function Chat() {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const ws = useRef(null);

  const [ready, setReady] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");

    validateToken(token).then(valid => {
      if (!valid) navigate("/login");
      else setReady(true);
    });
  }, []);

  useEffect(() => {
    if (!ready) return;

    const token = localStorage.getItem("token");

    ws.current = new WebSocket(
      `ws://localhost:8000/chat?token=${token}`
    );

    ws.current.onmessage = e => {
      setMessages(prev => {
        const last = prev[prev.length - 1];

        if (last?.role === "assistant") {
          return [
            ...prev.slice(0, -1),
            { ...last, content: last.content + e.data }
          ];
        }

        return [...prev, { role: "assistant", content: e.data }];
      });
    };

    ws.current.onclose = () => navigate("/login");

    return () => ws.current?.close();

  }, [ready]);

  function sendMessage(e) {
    e.preventDefault();

    ws.current.send(
      JSON.stringify({
        conversation_id: conversationId,
        message: input
      })
    );

    setMessages(prev => [
      ...prev,
      { role: "user", content: input },
      { role: "assistant", content: "" }
    ]);

    setInput("");
  }

  return (
    <div className="max-w-3xl mx-auto mt-10 space-y-4">

      <div className="border rounded-xl p-4 h-[70vh] overflow-y-auto bg-white shadow">
        {messages.map((m, i) => (
          <div key={i} className={`my-2 ${m.role === "user" ? "text-right" : ""}`}>
            <span className={`inline-block px-3 py-2 rounded-xl 
              ${m.role === "user" ? "bg-black text-white" : "bg-gray-200"}
            `}>
              {m.content}
            </span>
          </div>
        ))}
      </div>

      <form onSubmit={sendMessage} className="flex gap-2">
        <input className="flex-1 border rounded-lg px-3 py-2"
          value={input}
          onChange={e => setInput(e.target.value)}
        />
        <button className="bg-black text-white px-4 rounded-lg">
          Send
        </button>
      </form>
    </div>
  );
}
