# src/api/routes/conversations.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import get_db
from ...utils.auth_dependency import get_current_user
from ...db.models import Conversation
from sqlalchemy import select

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
