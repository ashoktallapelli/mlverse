from app.embedding.embedder import embed_text
from config.settings import VECTOR_DB
import os

FAISS_INDEX_PATH = "data/faiss/index.bin"
CHUNKS_PATH = "data/faiss/chunks.npy"
CHROMA_PATH = "data/chroma"

if VECTOR_DB == "chroma":
    import chromadb
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection("notes")
else:
    import faiss
    import numpy as np


def load_index():
    if VECTOR_DB == "chroma":
        return collection
    if os.path.exists(FAISS_INDEX_PATH):
        return faiss.read_index(FAISS_INDEX_PATH)
    raise RuntimeError("FAISS index not found.")


def load_chunks():
    if VECTOR_DB == "chroma":
        # chroma stores documents internally
        # returning just the documents list for compatibility
        res = collection.get()
        return res.get("documents", [])
    if os.path.exists(CHUNKS_PATH):
        return np.load(CHUNKS_PATH, allow_pickle=True).tolist()
    raise RuntimeError("Chunk store not found.")


def retrieve_relevant_chunks(query, top_k=5):
    if VECTOR_DB == "chroma":
        query_embedding = embed_text([query])[0].tolist()
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        docs = results.get("documents", [[]])
        return docs[0] if docs else []

    index = load_index()
    chunks = load_chunks()
    query_embedding = embed_text([query])  # shape: (1, 384)
    D, I = index.search(np.array(query_embedding), top_k)
    return [chunks[i] for i in I[0] if i < len(chunks)]
