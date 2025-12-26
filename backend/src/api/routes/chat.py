from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...schemas.message import Message
from ...services.rag_service import summarize_history, stream_answer, build_retrieval_query
from ...services.embedding_service import embed_query
from ...vectorstore.qdrant_client import similarity_search
from ...db.models import MessageRole
from ...db.repository import insert_message, fetch_history, get_conversation_by_id
from ...db.session import get_db
from ...utils.auth_dependency import decode_and_get_user

router = APIRouter()

@router.websocket("/chat")
async def chat_with_rag(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    try:
        await websocket.accept()
        token = websocket.query_params.get("token")
        user = await decode_and_get_user(db, token)

        if not user:
            await websocket.close(code=4401)
            return

        while True:
            try:
                data = await websocket.receive_json()

                conversation_id, query = data.get("conversation_id"), data.get("message")

                if not conversation_id or not query:
                    await websocket.send_text("conversation_id and message are required.")
                    continue

                conversation = await get_conversation_by_id(db, conversation_id)
                if conversation.user_id != user.user_id:
                    await websocket.send_text("Unauthorized user")
                    await websocket.close(code=4401)
                    return

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

            except Exception as e:
                import traceback
                print("CHAT ERROR:", e)
                traceback.print_exc()
                await websocket.send_text("Something went wrong, try again.")

    except WebSocketDisconnect:
        pass 
