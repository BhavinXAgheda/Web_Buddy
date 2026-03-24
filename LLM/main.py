import csv
import os
import faiss
import httpx
import mcp
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from fastmcp import FastMCP



# Config
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gpt-oss:120b-cloud"

CHUNKS_FILE = "/tmp/chunks.csv"
INDEX_FILE  = "/tmp/faiss.index"

TOP_K = 10

# Load model + index once at startup
embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = None
chunks = []

def load_index():
    global index, chunks
    if os.path.exists(INDEX_FILE) and os.path.exists(CHUNKS_FILE):
        index = faiss.read_index(INDEX_FILE)
        with open(CHUNKS_FILE, "r") as f:
            chunks = list(csv.DictReader(f))

class AskRequest(BaseModel):
    query: str
    top_k: int = TOP_K


def retrieve_context(query: str, top_k: int):

    global index, chunks

    if index is None:
        load_index()

    if index is None:
        raise Exception("Index not found. Run pipeline first.")

    embedding = embedder.encode([query])
    distances, indices = index.search(np.array(embedding), top_k)

    results = []
    for idx in indices[0]:
        chunk = chunks[idx]
        results.append({
            "url": chunk["url"],
            "title": chunk["title"],
            "text": chunk["chunk_text"]
        })

    return results

def ask_ollama(query: str, context: str) -> str:
    prompt = f"""You are an AI assistant that must ONLY use the information provided in the given context.

STRICT RULES:
1. Do NOT use any external knowledge or assumptions.
3. Every answer must be fully grounded in the given context.

FORMAT RULES:
- Always start with a short heading (### Heading)
- Use bullet points for key facts
- Keep each bullet concise and clear
- End with a one-line summary prefixed with **Summary:**

Context:
{context}

Question: {query}
Answer:"""

    response = httpx.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
        timeout=120.0
    )
    return response.json()["response"]


def ask(request: AskRequest):
    # Step 1 — retrieve top chunks
    results = retrieve_context(request.query, request.top_k)

    # Step 2 — build context string
    context = "\n\n".join([
        f"Source: {r['url']}\n{r['text']}" for r in results
    ])

    # Step 3 — ask ollama
    answer = ask_ollama(request.query, context)

    return {
        "query":   request.query,
        "answer":  answer,
        # "sources": [{"url": r["url"], "title": r["title"]} for r in results]
    }

