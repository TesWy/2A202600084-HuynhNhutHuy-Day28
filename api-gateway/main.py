# api-gateway/main.py
import os
import time

import httpx
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field

app = FastAPI(title="AI Platform API Gateway")
Instrumentator().instrument(app).expose(app)

VLLM_URL = os.environ.get("VLLM_URL", "").rstrip("/")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333").rstrip("/")
MODEL_ID = os.environ.get("MODEL_ID", "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4")


class ChatRequest(BaseModel):
    query: str
    embedding: list[float] = Field(default_factory=lambda: [0.0] * 384)


def fallback_answer(query: str) -> str:
    return (
        "Fallback response: platform engineering connects ingestion, orchestration, "
        "feature and vector stores, model serving, and observability into one "
        f"reliable AI delivery path. Query received: {query}"
    )


async def search_context(embedding: list[float]) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(
                f"{QDRANT_URL}/collections/documents/points/search",
                json={"vector": embedding, "limit": 3},
            )
            response.raise_for_status()
            return response.json().get("result", [])
    except Exception:
        return []


async def generate_answer(prompt: str, query: str) -> tuple[str, str, str]:
    if not VLLM_URL:
        return fallback_answer(query), "fallback-local", "fallback_missing_vllm_url"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{VLLM_URL}/v1/chat/completions",
                json={
                    "model": MODEL_ID,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"], result.get("model", MODEL_ID), "vllm"
    except Exception as exc:
        return fallback_answer(query), "fallback-local", f"fallback_vllm_error:{type(exc).__name__}"


@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    start = time.time()
    context = await search_context(request.embedding)
    prompt = f"Context: {context}\n\nQuery: {request.query}"
    answer, model, mode = await generate_answer(prompt, request.query)
    latency = (time.time() - start) * 1000

    return {
        "answer": answer,
        "latency_ms": round(latency, 2),
        "model": model,
        "mode": mode,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mode": "vllm" if VLLM_URL else "fallback_missing_vllm_url",
        "qdrant_url": QDRANT_URL,
    }
