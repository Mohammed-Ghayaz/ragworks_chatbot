from qdrant_client import models, AsyncQdrantClient
import os
from dotenv import load_dotenv
from ..core.config import EMBEDDING_DIM, TOP_K, MAX_TOP_K
from typing import List

load_dotenv()

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

qdrant_client = AsyncQdrantClient(
    url=qdrant_url, 
    api_key=qdrant_api_key,
)

async def create_collection(conversation_id: str) -> None:
    collection_name = f"conversation_{conversation_id}__emb_v1"

    try:
        await qdrant_client.get_collection(collection_name)
        return

    except Exception:
        await qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIM,
                distance=models.Distance.COSINE
            )
        )

async def upsert_documents(conversation_id: str, embeddings: List[List[float]], payload: List[dict], ids: List[str]):
    collection_name = f"conversation_{conversation_id}__emb_v1"

    await qdrant_client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=idx,
                vector=embedding,
                payload=doc
            )

            for idx, embedding, doc in zip(ids, embeddings, payload)
        ]
    )

async def similarity_search(conversation_id: str, query_embedding: List[float], top_k: int = TOP_K):
    collection_name = f"conversation_{conversation_id}__emb_v1"
    top_k = min(top_k, MAX_TOP_K)

    hits = await qdrant_client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=top_k,
    ).points

    return [
        {
            "payload": hit.payload,
            "score": hit.score
        }

        for hit in hits
    ]