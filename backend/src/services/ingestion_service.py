from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from .embedding_service import embed_documents
from ..vectorstore.qdrant_client import create_collection, upsert_documents

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40
)

def chunk_text(text: str) -> List[str]:
    return text_splitter.split_text(text)

def generate_vector_ids(conversation_id: str, filename: str, n: int):
    vector_ids = [f"{conversation_id}__{filename}__chunk_{i}" for i in range(n)]
    return vector_ids

async def ingest_documents(conversation_id: str, files: List[dict]):
    payload = []
    embeddings = []
    vector_ids = []
    
    await create_collection(conversation_id)

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

    await upsert_documents(conversation_id, embeddings, payload, vector_ids)



