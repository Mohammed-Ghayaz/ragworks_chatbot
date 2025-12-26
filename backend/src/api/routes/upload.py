from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
from ...db.repository import create_conversation
from ...db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ...services.ingestion_service import ingest_documents
from ...utils.auth_dependency import get_current_user
import logging

upload_logger = logging.getLogger("ragworks.upload")

router = APIRouter()

@router.post("/upload")
async def upload_documents(db: AsyncSession = Depends(get_db), uploaded_files: List[UploadFile] = File(...), user = Depends(get_current_user)):
    try:
        upload_logger.info("Start")
        files = []

        if not uploaded_files or len(uploaded_files) == 0:
            raise HTTPException(status_code=400, detail="Upload documents")

        for file in uploaded_files:
            content = await file.read()
            text = content.decode("utf-8")
            upload_logger.info(len(text))
            if len(text.strip()) == 0:
                continue

            files.append({"filename": file.filename, "text": text})

        conversation_id = await create_conversation(db=db, user_id=str(user.user_id))

        await ingest_documents(conversation_id=conversation_id, files=files)

        return {
            "conversation_id": str(conversation_id)
        }
    
    except Exception:
        upload_logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail="Internal Server Error")