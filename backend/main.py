import json
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile, BackgroundTasks
from database import Conversation, User, get_db, SessionLocal
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from conversation import get_conversations_from_user, save_conversation, get_conversation_by_id
from auth import UserRegistration, UserLogin, Token
from ingestion import ingest_data
from user import register_user, login_user, get_current_user
from rag_conversation_chain import get_rag_chain
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    chat_history: List[Dict[str, str]] = []
    conversation_id: Optional[int] = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def save_conversation_task(db: Session, user_id: int, messages: List[Dict[str, Any]], conversation_id: int):
    save_conversation(db=db, user_id=user_id, messages=messages, conversation_id=conversation_id)
    db.close()

@app.post("/register", response_model=Token)
async def register(user: UserRegistration, db: Session = Depends(get_db)):
    return register_user(user, db)

@app.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(user, db)

@app.post("/chat")
@app.post("/chat")
async def chat_with_rag(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        conversation = get_conversation_by_id(db, request.conversation_id)
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Conversation not found or does not belong to user")

        rag_chain = get_rag_chain(current_user.id, conversation.id)
        
        full_response_content = ""

        async def generate_stream():
            nonlocal full_response_content
            async for event in rag_chain.astream_events({
                'input': request.query,
                'chat_history': request.chat_history
            }, version="v1"):
                kind = event["event"]
                if kind == "on_chat_model_stream" and "chunk" in event["data"]:
                    content = event["data"]["chunk"].content
                    if content:
                        full_response_content += content
                        # Split by spaces to send word by word
                        words = full_response_content.split()
                        for word in words[len(full_response_content.split()):]:
                            yield word + " "
                        yield content + " "  # fallback, send chunk as is

        def save_conversation():
            full_chat_history = request.chat_history + [
                {"role": "user", "content": request.query},
                {"role": "assistant", "content": full_response_content},
            ]
            save_conversation_task(db, current_user.id, full_chat_history, conversation.id)

        background_tasks.add_task(save_conversation)

        headers = {
            "X-Conversation-ID": str(conversation.id)
        }

        return StreamingResponse(generate_stream(), media_type="text/event-stream", headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file uploaded. Supports only pdf files.")

    # Create a new conversation record for this file upload
    new_conversation = Conversation(
        user_id=current_user.id,
        messages=json.dumps([{"role": "user", "content": f"Document uploaded: {file.filename}"}]),
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)

    # Use the new conversation ID to create the collection
    collection_name = f"user_{current_user.id}_docs"
    file_location = f"temp_docs/{new_conversation.id}_{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    try:
        ingest_data(file_location, current_user.id, new_conversation.id, file.filename)
    except Exception as e:
        os.remove(file_location)
        db.delete(new_conversation)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    
    os.remove(file_location)
    return {"message": "File processed and ingested.", "conversation_id": new_conversation.id}


@app.get("/conversations")
async def get_user_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        conversations = get_conversations_from_user(db, current_user.id)
        return conversations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )


@app.get("/")
def greet():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, port=8000)