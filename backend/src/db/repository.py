from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Message, MessageRole, Conversation
from uuid import UUID

async def fetch_history(db: AsyncSession, conversation_id: str, limit: int = 5):
    try:
        conversation_uuid = UUID(conversation_id)

        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_uuid)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)

        messages = result.scalars().all()

        # We queried newest → oldest, so reverse to oldest → newest
        return list(reversed(messages))

    except Exception:
        raise


async def insert_message(db: AsyncSession, conversation_id: str, message: str, role: str):
    message_role = {
        "human": MessageRole.HUMAN,
        "ai": MessageRole.AI,
        "system": MessageRole.SYSTEM
    }.get(role, MessageRole.HUMAN)

    try:
        new_message = Message(conversation_id=UUID(conversation_id), role=message_role, content=message)
        db.add(new_message)
        await db.commit()
        await db.refresh(new_message)

    except Exception as e:
        await db.rollback()
        raise

async def create_conversation(db: AsyncSession, user_id: str):
    try:
        new_conversation = Conversation(user_id=UUID(user_id))
        db.add(new_conversation)
        await db.commit()
        await db.refresh(new_conversation)

        return new_conversation.conversation_id
    
    except Exception:
        await db.rollback()
        raise