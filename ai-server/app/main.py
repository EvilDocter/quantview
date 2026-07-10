"""
QuantView — AI Model Server FastAPI Application

Inference and embedding services running inside HuggingFace Space.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import torch
from sentence_transformers import SentenceTransformer

app = FastAPI(
    title="QuantView AI Model Server",
    description="Provides embeddings and local LLM inference services",
    version="0.1.0"
)

# Load Embedding Model (BGE-large-en-v1.5)
# Using CPU by default since it runs on free-tier Spaces.
print("Loading BGE Embedding model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5", device=device)
print(f"BGE Embedding model loaded successfully on {device}!")

# ── Pydantic Request/Response Schema ───────────────────────────

class EmbeddingRequest(BaseModel):
    texts: List[str]

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]

class CompletionRequest(BaseModel):
    prompt: str
    model: Optional[str] = "qwen2.5:3b"
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 512

class CompletionResponse(BaseModel):
    text: str

# ── Endpoints ──────────────────────────────────────────────────

@app.post("/embeddings", response_model=EmbeddingResponse)
async def generate_embeddings(request: EmbeddingRequest):
    try:
        embeddings = embedding_model.encode(request.texts, show_progress_bar=False)
        return EmbeddingResponse(embeddings=embeddings.tolist())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/completion", response_model=CompletionResponse)
async def generate_completion(request: CompletionRequest):
    """
    Stubs LLM completion. In production, this proxies to a local Ollama instance
    or runs inference locally on the Hugging Face Space using transformers.
    """
    # For now, return a placeholder response.
    # When deployed, we load Qwen 2.5 using transformers/llama.cpp.
    stub_response = f"[STUB] AI response to: {request.prompt[:100]}..."
    return CompletionResponse(text=stub_response)

@app.get("/health")
async def health():
    return {"status": "healthy", "device": device}
