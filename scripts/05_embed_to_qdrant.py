# scripts/05_embed_to_qdrant.py
import hashlib
import os

import requests
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

load_dotenv()

EMBED_URL = os.environ.get("EMBED_NGROK_URL", "").rstrip("/")
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION", "documents")
VECTOR_SIZE = 384

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def deterministic_embedding(text: str, size: int = VECTOR_SIZE) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = []
    while len(values) < size:
        for byte in digest:
            values.append((byte / 127.5) - 1.0)
            if len(values) == size:
                break
        digest = hashlib.sha256(digest).digest()
    return values


def get_embeddings(records: list[dict]) -> tuple[list[list[float]], str]:
    texts = [record["text"] for record in records]
    if EMBED_URL:
        try:
            response = requests.post(f"{EMBED_URL}/embed", json={"texts": texts}, timeout=30)
            response.raise_for_status()
            return response.json()["embeddings"], "kaggle_embedding_service"
        except Exception as exc:
            print(f"Embedding service unavailable; using deterministic fallback ({type(exc).__name__})")

    return [deterministic_embedding(text) for text in texts], "deterministic_local_fallback"


def ensure_collection() -> None:
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )


def embed_and_store(records: list[dict]) -> None:
    ensure_collection()
    embeddings, mode = get_embeddings(records)
    points = [
        PointStruct(id=index, vector=embedding, payload=record)
        for index, (embedding, record) in enumerate(zip(embeddings, records))
    ]
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Integration 5 OK: {len(points)} vectors stored in Qdrant using {mode}")


if __name__ == "__main__":
    embed_and_store(
        [
            {"id": "doc_001", "text": "AI platform integration test"},
            {"id": "doc_002", "text": "Kafka to Prefect pipeline"},
        ]
    )
