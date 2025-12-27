# 🧠 RAGWorks Chatbot

Live Demo: [https://ragworks-chatbot.vercel.app](https://ragworks-chatbot.vercel.app)

A Retrieval-Augmented Generation (RAG) chatbot with secure authentication, document uploads, vector search, and streaming AI responses.

RAGWorks lets users upload documents, embed text into a vector database, and chat with an AI assistant that answers questions using the uploaded content as context.

---

## ✨ Features

- ✅ **User authentication** (Register, Login, Logout)
- ✅ **JWT-protected routes & protected WebSocket**
- ✅ **Document upload & ingestion** (multiple files)
- ✅ **Vector store** (Qdrant / Chroma)
- ✅ **Streaming AI responses** via WebSockets
- ✅ **Persistent conversations** with history
- ✅ **Conversation sidebar** for quick navigation
- ✅ **Production-ready** (deployment notes included)

---

## 🧰 Tech Stack

**Frontend**
- React (CRA/Vite)
- Tailwind CSS
- Context API for auth
- WebSockets for streaming

**Backend**
- FastAPI
- Async SQLAlchemy + asyncpg
- JWT authentication
- Google GenAI (embeddings & LLM)
- Qdrant (or Chroma) for vectors

**Database & Hosting**
- PostgreSQL (Neon)
- Backend: Render
- Frontend: Vercel

---

## Application workflow

1. **Authenticate** — Client calls `/auth/register` or `/auth/login`; server returns a JWT which the client stores (Context/localStorage) and includes in Authorization headers and WebSocket tokens.
2. **Upload & Ingest** — User uploads files (`/upload`) → server extracts text, chunks documents, computes embeddings (batch) and stores vectors with metadata in the vector DB (Qdrant). Ingestion can run as asynchronous/background jobs.
3. **Embedding & Indexing** — Embeddings are generated using the configured embedding provider (Google GenAI), then upserted into the vector store with references to source files and conversation IDs.
4. **Querying / Retrieval** — When a user asks a question, the client sends the query; server embeds the query and performs a top‑k similarity search on the vector store to fetch relevant text snippets.
5. **Response Generation (RAG)** — Retrieved snippets are assembled into a prompt/context for the LLM; the LLM generates an answer which is streamed back to the client (WebSocket streaming at `/chat?token=...`).
6. **Persistence & UI updates** — Streaming tokens are appended in the UI, final messages are saved to the `messages` table, and the conversation list is updated with the latest timestamp.

**Notes:**
- REST endpoints: `/auth`, `/upload`, `/conversations`, `/conversations/:id/messages`.
- WebSocket endpoint for streaming chat: `/chat?token=<jwt>`.
- In production, restrict CORS and secure secrets (JWT, embedding keys).

---

## 📁 Project Structure

```
ragworks_chatbot/
├── backend/
│   ├── main.py
│   ├── src/
│   │   ├── api/         # routes
│   │   ├── db/          # models & session
│   │   ├── services/    # ingestion, embeddings, rag logic
│   │   ├── utils/       # auth, helpers
│   │   └── vectorstore/ # Qdrant client or other
│   └── requirements.txt
└── frontend/
    ├── src/             # React app
    ├── public/
    └── package.json
```

---

## 🔧 Environment Variables

### Backend (.env)

| Name | Example | Description |
|---|---|---|
| DATABASE_URL | `postgresql+asyncpg://user:pass@host:port/db` | PostgreSQL connection string |
| JWT_SECRET | `your_jwt_secret` | JWT signing secret |
| JWT_EXPIRE_MINUTES | `60` | Token expiry (minutes) |
| GOOGLE_API_KEY | `sk-...` | Google GenAI API key |
| QDRANT_URL | `https://...` | Qdrant HTTP API URL |

### Frontend (.env)

> Create React App requires env vars prefixed with `REACT_APP_` for them to be available in the browser.

- `REACT_APP_BACKEND_URL` or `REACT_APP_API_BASE` — e.g. `https://your-backend-url.onrender.com`

---

## 🧪 Run Locally

### Backend (development)

**Windows (PowerShell):**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**macOS / Linux:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

### Frontend (development)

```bash
cd frontend
npm install
npm start
```

- UI: `http://localhost:3000`

> If you change env variables, restart the dev server so CRA/Vite picks them up.

---

## 🗂 Database (core tables overview)

- **users**: `user_id (uuid)`, `name`, `email`, `password_hash`
- **conversations**: `conversation_id (uuid)`, `user_id`, `created_at`
- **messages**: `message_id`, `conversation_id`, `role` (`user`/`ai`), `content`, `created_at`
- **vector store**: stored in Qdrant or configured vector database

---

## 🔐 Security

- JWT-based authentication
- Password hashing (bcrypt / argon2)
- CORS configured; restrict origins in production
- WebSocket endpoints protected by token

---

## 🌍 Deployment

**Backend (Render)**
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port 10000`

**Frontend (Vercel)**
- Build: `npm run build`
- Deploy path: `build/` or Vercel auto-detect

---

## 🛠 Roadmap

- Support more file types (PDF, images, Office docs)
- Role-based admin panel
- Collaborative spaces & chat tagging
- Fine-tuned long-term memory

---

## 🤝 Contributing

Contributions are welcome! Please open issues or submit pull requests. Include tests and a brief description of changes.

---

## 🧪 Tests

Run backend tests (if added):
```bash
pytest
```

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 👤 Author

**Mohammed Ghayaz**

[LinkedIn | Mohammed Ghayaz](https://www.linkedin.com/in/mohammed-ghayaz/)

[GitHub | Mohammed Ghayaz](https://github.com/Mohammed-Ghayaz)
