# src/api/routes/conversations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import get_db
from ...utils.auth_dependency import get_current_user
from ...db.models import Conversation, MessageRole
from sqlalchemy import select
from ...db.repository import fetch_history, get_conversation_by_id

router = APIRouter()

@router.get("/conversations")
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user.user_id)
        .order_by(Conversation.created_at.desc())
    )

    result = await db.execute(stmt)
    conversations = result.scalars().all()

    return [
        {
            "conversation_id": str(c.conversation_id),
            "created_at": c.created_at
        }
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    # verify conversation exists and belongs to user
    convo = await get_conversation_by_id(db, conversation_id)
    if not convo or convo.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msgs = await fetch_history(db=db, conversation_id=conversation_id, limit=limit)

    # convert to serializable objects
    message_role = {
        MessageRole.HUMAN: "human",
        MessageRole.AI: "ai",
        MessageRole.SYSTEM: "system"
    }

    return [
        {
            "role": message_role.get(m.role, "human"),
            "content": m.content,
            "created_at": m.created_at
        }
        for m in msgs
    ]
