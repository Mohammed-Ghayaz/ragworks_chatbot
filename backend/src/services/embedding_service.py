from dotenv import load_dotenv
import os
import asyncio
import logging
from google import genai
from google.genai import types
from typing import List
from ..core.config import EMBEDDING_MODEL, EMBEDDING_DIM, EMBEDDING_BATCH_SIZE


load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

logger = logging.getLogger(__name__)

if GEMINI_API_KEY:
    embedding_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    # Running without a GEMINI API key (local/dev). Use a deterministic fallback
    # embedding generator so ingestion and local testing can proceed.
    embedding_client = None
    logger.warning("GEMINI_API_KEY is not set; using local deterministic embedding fallback")


def _embed_sync(contents: List[str]) -> List[List[float]]:
    """Synchronous helper that calls the GenAI embed_content API and normalizes the response.

    Returns a list of vectors (each vector is a list of floats).
    """
    if not isinstance(contents, list):
        raise TypeError("contents must be a list of strings")

    if embedding_client is None:
        # Deterministic fallback: create simple vector based on sha256 digest of text
        import hashlib
        embeddings = []
        for c in contents:
            digest = hashlib.sha256(c.encode("utf-8")).digest()
            # Create EMBEDDING_DIM floats by repeating digest bytes and normalizing
            vec = [float(digest[i % len(digest)]) / 255.0 for i in range(EMBEDDING_DIM)]
            embeddings.append(vec)
        return embeddings

    response = embedding_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=contents,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
    )

    embeddings: List[List[float]] = []
    for emb in response.embeddings:
        # Support objects with `.values`, `.embedding`, or dict-like responses
        values = getattr(emb, "values", None)
        if values is None:
            values = getattr(emb, "embedding", None)
        if values is None and isinstance(emb, dict):
            values = emb.get("values") or emb.get("embedding") or emb.get("vector")

        if values is None:
            logger.error("Unexpected embedding object format: %s", type(emb))
            raise RuntimeError("unexpected embedding response format")

        embeddings.append(list(values))

    return embeddings


async def embed_documents(documents: List[str]) -> List[List[float]]:
    """Embed a list of documents in batches and return a list of vectors."""
    if not documents:
        return []

    for d in documents:
        if not isinstance(d, str):
            raise TypeError("each document must be a string")

    async def embed_batch(batch: List[str]) -> List[List[float]]:
        return await asyncio.to_thread(_embed_sync, batch)

    tasks = [
        embed_batch(documents[i:i + EMBEDDING_BATCH_SIZE])
        for i in range(0, len(documents), EMBEDDING_BATCH_SIZE)
    ]

    results = await asyncio.gather(*tasks)
    embeddings = [vec for batch in results for vec in batch]
    return embeddings


async def embed_query(text: str) -> List[float]:
    """Embed a single query string and return a single vector (list of floats)."""
    if not text or not isinstance(text, str):
        raise ValueError("text must be a non-empty string")

    vectors = await asyncio.to_thread(_embed_sync, [text])
    return vectors[0]

