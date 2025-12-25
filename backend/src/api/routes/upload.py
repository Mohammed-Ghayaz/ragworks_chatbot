from fastapi import APIRouter, UploadFile, File, Depends
from typing import List
from ...db.repository import create_conversation
from ...db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/upload")
async def upload_documents(db: AsyncSession = Depends(get_db), files: List[UploadFile] = File(...)):
    for file in files:
        print(file.filename)

    conversation_id = await create_conversation(db=db, user_id="8e5af5a4-96ad-4eb0-9e4e-f019bd2c9c18")

    return {
        "conversation_id": conversation_id
    }