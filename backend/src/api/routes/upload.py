from fastapi import APIRouter, UploadFile, File
from typing import List

router = APIRouter()

@router.post("/upload")
def upload_documents(files: List[UploadFile] = File(...)):
    for file in files:
        print(file.filename)

    return {
        "conversation_id": "UUID"
    }