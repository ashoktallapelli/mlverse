# app/embedding/retriever.py

import faiss
import numpy as np
import os
from app.embedding.embedder import embed_text

FAISS_INDEX_PATH = "data/faiss/index.bin"
CHUNKS_PATH = "data/faiss/chunks.npy"

def load_index():
    if os.path.exists(FAISS_INDEX_PATH):
        return faiss.read_index(FAISS_INDEX_PATH)
    raise RuntimeError("FAISS index not found.")

def load_chunks():
    if os.path.exists(CHUNKS_PATH):
        return np.load(CHUNKS_PATH, allow_pickle=True).tolist()
    raise RuntimeError("Chunk store not found.")

def retrieve_relevant_chunks(query, top_k=5):
    index = load_index()
    chunks = load_chunks()

    query_embedding = embed_text([query])  # shape: (1, 384)
    D, I = index.search(np.array(query_embedding), top_k)

    return [chunks[i] for i in I[0] if i < len(chunks)]
