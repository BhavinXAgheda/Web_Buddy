import csv
import faiss
import numpy as np
import os
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

CHUNKS_FILE = "/tmp/chunks.csv"
INDEX_FILE  = "/tmp/faiss.index"
OUTPUT_CSV  = "/tmp/output.csv"

index = None
chunks = []

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


def load_index():
    global index, chunks
    if os.path.exists(INDEX_FILE) and os.path.exists(CHUNKS_FILE):
        index = faiss.read_index(INDEX_FILE)
        with open(CHUNKS_FILE, "r") as f:
            chunks = list(csv.DictReader(f))


# Step 1 — chunk output.csv → chunks.csv
@app.get("/chunk")
def chunk_data():
    with open(OUTPUT_CSV, "r") as infile, open(CHUNKS_FILE, "w", newline="") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=["chunk_id", "url", "title", "chunk_text"])
        writer.writeheader()
        chunk_id = 0
        for row in reader:
            for chunk in splitter.split_text(row["paragraphs"]):
                writer.writerow({
                    "chunk_id": chunk_id,
                    "url": row["url"],
                    "title": row["title"],
                    "chunk_text": chunk
                })
                chunk_id += 1
    return {"status": "done", "chunks": chunk_id}


# Step 2 — embed chunks.csv → faiss.index
@app.get("/embed")
def embed_data():
    global index, chunks
    with open(CHUNKS_FILE, "r") as f:
        chunks = list(csv.DictReader(f))

    texts = [row["chunk_text"] for row in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    faiss.write_index(index, INDEX_FILE)

    return {"status": "done", "vectors": index.ntotal}


# Step 3 — query the index
@app.post("/search")
def search(request: QueryRequest):
    if index is None:
        load_index()
    if index is None:
        return {"error": "index not found, run /embed first"}

    embedding = model.encode([request.query])
    distances, indices = index.search(np.array(embedding), request.top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        chunk = chunks[idx]
        results.append({
            "rank": i + 1,
            "url": chunk["url"],
            "title": chunk["title"],
            "text": chunk["chunk_text"][:300],
            "score": float(distances[0][i])
        })

    return {"query": request.query, "results": results}


# Load index on startup
load_index()