from dotenv import load_dotenv
import os
import asyncio
from google import genai
from google.genai import types
from typing import List
from ..core.config import EMBEDDING_MODEL, EMBEDDING_DIM, EMBEDDING_BATCH_SIZE


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

embedding_client = genai.Client(api_key=GEMINI_API_KEY)

async def embed_documents(documents: List[str]) -> List[List[float]]:
    async def embed_batch(batch):
        batch_embeddings = await asyncio.to_thread(
            embedding_client.models.embed_content,
            model=EMBEDDING_MODEL,
            content=batch,
            config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
        )

        return [emb.values for emb in batch_embeddings.embeddings]
    tasks = [
        embed_batch(documents[i:i+EMBEDDING_BATCH_SIZE])
        for i in range(0, len(documents), EMBEDDING_BATCH_SIZE)
    ]

    results = await asyncio.gather(*tasks)

    embeddings = [embedding_obj for batch in results for embedding_obj in batch]
    return embeddings

async def embed_query(text: str) -> List[float]:
    response = await asyncio.to_thread(
        embedding_client.models.embed_content,
        model=EMBEDDING_MODEL,
        content=text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIM
        ),
    )
    return response.embedding.values
