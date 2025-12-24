from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ...schemas.message import Message
from ...services.rag_service import summarize_history, stream_answer, build_retrieval_query
from ...services.embedding_service import embed_query
from ...vectorstore.qdrant_client import similarity_search

router = APIRouter()

@router.websocket("/chat")
async def chat_with_rag(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_json()
            
            conversation_id, query = data["conversation_id"], data["message"]
            # human_message = Message(role="human", content=query)
            history_summary = query
            retrieval_query = build_retrieval_query(history_summary, query)
            query_embedding = await embed_query(retrieval_query)
            context = await similarity_search(conversation_id, query_embedding)

            async for chunk in stream_answer(history_summary, context, query):
                await websocket.send_text(chunk)

    except WebSocketDisconnect:
        pass
