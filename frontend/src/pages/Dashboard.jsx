import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getConversations } from "../api/chat";
import Hero from "../components/Hero";
import Spinner from "../components/Spinner";

export default function Dashboard() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [convs, setConvs] = useState([]);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const res = await getConversations(token);
      const data = await res.json();
      setConvs(data);
      setLoading(false);
    }

    load();
  }, [token]);

  return (
    <div>
      <Hero
        title="RAGWorks — Chat with your documents"
        subtitle="Go to the conversations"
      >
        <div className="flex gap-2">
          <button
            onClick={() => navigate("/chat")}
            className="bg-white/30 text-white px-4 py-2 rounded font-semibold"
          >
            Go to conversations
          </button>
        </div>
      </Hero>

      <section className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded shadow md:col-span-3">
          <h3 className="font-semibold mb-3">Recent Conversations</h3> 

          {loading && <Spinner />}

          {!loading && convs.length === 0 && (
            <p className="text-sm text-slate-600">No conversations yet — open the chat and upload documents there to start a conversation.</p>
          )}

          <div className="space-y-2">
            {convs.slice(0, 8).map((c) => (
              <div key={c.conversation_id} className="flex items-center justify-between p-3 border rounded hover:bg-gray-50">
                <div>
                  <div className="font-medium">Conversation</div>
                  <div className="text-xs text-slate-500">{c.created_at || ''}</div>
                </div>
                <div className="flex gap-2">
                  <button className="px-3 py-1 bg-indigo-600 text-white rounded" onClick={() => navigate(`/chat?c=${c.conversation_id}`)}>Open</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
