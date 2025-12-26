from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
import time
import logging
from .embedding_service import embed_documents
import uuid
from ..vectorstore.qdrant_client import create_collection, upsert_documents

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40
)

ingestion_logger = logging.getLogger("ragworks.ingestion")

def chunk_text(text: str) -> List[str]:
    return text_splitter.split_text(text)


def generate_vector_ids(conversation_id: str, filename: str, n: int):
    ids = []
    for i in range(n):
        key = f"{conversation_id}:{filename}:{i}"
        uid = uuid.uuid5(uuid.NAMESPACE_DNS, key)
        ids.append(str(uid))
    return ids


async def ingest_documents(conversation_id: str, files: List[dict]):
    payload = []
    embeddings = []
    vector_ids = []
    
    ingestion_logger.info("Ingestion started")

    start = time.perf_counter()
    await create_collection(conversation_id)

    embeddings_start = time.perf_counter()
    for file in files:
        text, filename = file["text"], file["filename"]
        chunks = chunk_text(text)
        file_embeddings = await embed_documents(chunks)
        vector_id = generate_vector_ids(conversation_id, filename, len(chunks))
        
        for i in range(len(chunks)):
            vector_ids.append(vector_id[i])
            embeddings.append(file_embeddings[i])
            payload.append({
                "text": chunks[i],
                "filename": filename,
                "chunk_index": i
            })

    embedding_completion_time = time.perf_counter()
    ingestion_logger.info(f"Embeddings generated in {(embedding_completion_time - embeddings_start) * 1000} ms")

    upsert_start = time.perf_counter()
    await upsert_documents(conversation_id, embeddings, payload, vector_ids)
    upsert_completion_time = time.perf_counter()
    ingestion_logger.info(f"Documents upserted in {(upsert_completion_time - upsert_start) * 1000} ms")

    end = time.perf_counter()

    ingestion_logger.info(f"Ingestion completed in {(end - start) * 1000} ms")
