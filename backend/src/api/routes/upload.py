from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
from ...db.repository import create_conversation
from ...db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ...services.ingestion_service import ingest_documents
from ...utils.auth_dependency import get_current_user
import logging
import io
from PyPDF2 import PdfReader

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
            data = await file.read()

            # Handle PDFs by extracting text from pages
            text = ""
            try:
                if file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
                    reader = PdfReader(io.BytesIO(data))
                    pages = []
                    for page in reader.pages:
                        page_text = page.extract_text() or ""
                        pages.append(page_text)
                    text = "\n\n".join(pages)
                else:
                    # Try decoding as utf-8, fall back to ignoring errors
                    text = data.decode("utf-8", errors="ignore")
            except Exception as e:
                upload_logger.warning("Failed to parse %s: %s", file.filename, e)
                text = data.decode("utf-8", errors="ignore")

            upload_logger.info("Read file %s (len=%d)", file.filename, len(text))

            if len(text.strip()) == 0:
                # Skip empty files
                continue

            files.append({"filename": file.filename, "text": text})

        if not files:
            raise HTTPException(status_code=400, detail="No valid text content found in uploaded files")

        conversation_id = await create_conversation(db=db, user_id=str(user.user_id))

        await ingest_documents(conversation_id=conversation_id, files=files)

        filenames = [f["filename"] for f in files]
        return {
            "conversation_id": str(conversation_id),
            "filenames": filenames
        }
    
    except HTTPException:
        raise
    except Exception:
        upload_logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail="Internal Server Error")