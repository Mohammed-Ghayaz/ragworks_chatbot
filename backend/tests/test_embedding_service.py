import importlib
import os
import types

import pytest

# Ensure GEMINI_API_KEY is set for module import
os.environ.setdefault("GEMINI_API_KEY", "test")

# Import module after env var is set
import backend.src.services.embedding_service as svc


class DummyEmbedding:
    def __init__(self, values):
        self.values = values


class DummyResponse:
    def __init__(self, embeddings):
        self.embeddings = embeddings


@pytest.fixture(autouse=True)
def patch_client(monkeypatch):
    def fake_embed_content(model, contents, config):
        # Return predictable vectors: length equals len(content)
        embeddings = [DummyEmbedding([float(len(c)) for _ in range(1)]) for c in contents]
        return DummyResponse(embeddings)

    monkeypatch.setattr(svc.embedding_client.models, "embed_content", fake_embed_content)
    yield


@pytest.mark.asyncio
async def test_embed_query():
    vec = await svc.embed_query("hello")
    assert isinstance(vec, list)
    assert vec == [5.0]


@pytest.mark.asyncio
async def test_embed_documents():
    docs = ["a", "bb", "ccc"]
    res = await svc.embed_documents(docs)
    assert res == [[1.0], [2.0], [3.0]]
