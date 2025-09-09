import json
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from database import Conversation, get_db

def get_conversations_from_user(db: Session, user_id: int):
    convos = db.query(Conversation).filter(Conversation.user_id == user_id).all()

    return [
        {"id": conv.id, "messages": json.dumps(conv.messages)} for conv in convos
    ]

def save_conversation(db: Session, user_id: int, messages: List[Dict[str, str]], conversation_id: Optional[int] = None):
    json_msg = json.dumps(messages)

    if conversation_id:
        convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if convo.user_id == user_id:
            convo.messages = json_msg
            db.commit()
            return convo

        else:
            raise HTTPException(400, "Unauthorized user")

    else:
        new_convo = Conversation(user_id = user_id, messages = json_msg)
        db.add(new_convo)
        db.commit()
        db.refresh(new_convo)

        return new_convo

def get_conversation_by_id(db: Session, conversation_id: int):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()