from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from .session import Base
from datetime import datetime, timezone
from enum import Enum
import uuid

class MessageRole(str, Enum):
    SYSTEM = "system"
    HUMAN = "human"
    AI = "ai"

class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Conversation(Base):
    __tablename__  = "conversations"
    
    conversation_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Message(Base):
    __tablename__  = "messages"
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    role = Column(SQLAlchemyEnum(MessageRole), nullable=False, default=MessageRole.HUMAN)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    