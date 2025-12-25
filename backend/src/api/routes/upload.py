from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
from ...db.repository import create_conversation
from ...db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ...services.ingestion_service import ingest_documents
from ...utils.auth_dependency import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_documents(db: AsyncSession = Depends(get_db), uploaded_files: List[UploadFile] = File(...), user = Depends(get_current_user)):
    try:
        files = []

        if not uploaded_files or len(uploaded_files) == 0:
            raise HTTPException(status_code=400, detail="Upload documents")

        for file in uploaded_files:
            content = await file.read()
            text = content.decode("utf-8")
            if len(text.strip()) == 0:
                continue

            files.append({"filename": file.filename, "text": text})

        conversation_id = await create_conversation(db=db, user_id="8e5af5a4-96ad-4eb0-9e4e-f019bd2c9c18")

        await ingest_documents(conversation_id=conversation_id, files=files)

        return {
            "conversation_id": str(conversation_id)
        }
    
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")