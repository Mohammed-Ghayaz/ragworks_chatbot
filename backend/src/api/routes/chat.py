from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...schemas.message import Message
from ...services.rag_service import summarize_history, stream_answer, build_retrieval_query
from ...services.embedding_service import embed_query
from ...vectorstore.qdrant_client import similarity_search
from ...db.models import MessageRole
from ...db.repository import insert_message, fetch_history
from ...db.session import get_db

router = APIRouter()

@router.websocket("/chat")
async def chat_with_rag(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    try:
        await websocket.accept()
        while True:
            try:
                data = await websocket.receive_json()

                conversation_id, query = data.get("conversation_id"), data.get("message")

                if not conversation_id or not query:
                    await websocket.send_text("conversation_id and message are required.")
                    continue

                chat_history = await fetch_history(db=db, conversation_id=conversation_id)

                message_role = {
                    MessageRole.HUMAN: "human",
                    MessageRole.AI: "ai",
                    MessageRole.SYSTEM: "system"
                }
                chat_history = [Message(role=message_role.get(message.role, "human"), content=message.content) for message in chat_history]

                history_summary = await summarize_history(chat_history) if chat_history else ""
                retrieval_query = build_retrieval_query(history_summary, query)
                query_embedding = await embed_query(retrieval_query)
                context = await similarity_search(conversation_id, query_embedding)

                assistant_reply = ""
                async for chunk in stream_answer(history_summary, context, query):
                    assistant_reply += chunk
                    await websocket.send_text(chunk)

                await insert_message(db, conversation_id, query, "human")
                await insert_message(db, conversation_id, assistant_reply, "ai")

            except Exception:
                await websocket.send_text("Something went wrong, try again.")

    except WebSocketDisconnect:
        pass 
