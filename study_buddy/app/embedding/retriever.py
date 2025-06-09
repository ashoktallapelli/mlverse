from app.embedding.embedder import embed_text
from config.settings import VECTOR_DB
import os
import numpy as np
from functools import lru_cache

FAISS_INDEX_PATH = "data/faiss/index.bin"
CHUNKS_PATH = "data/faiss/chunks.npy"
CHROMA_PATH = "data/chroma"

if VECTOR_DB == "chroma":
    import chromadb

    _chroma_collection = None
    def get_chroma_collection():
        global _chroma_collection
        if _chroma_collection is None:
            chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
            _chroma_collection = chroma_client.get_or_create_collection("notes")
        return _chroma_collection
else:
    import faiss


@lru_cache()
def load_index():
    if VECTOR_DB == "chroma":
        return get_chroma_collection()
    if os.path.exists(FAISS_INDEX_PATH):
        return faiss.read_index(FAISS_INDEX_PATH)
    raise RuntimeError("FAISS index not found.")


@lru_cache()
def load_chunks():
    if VECTOR_DB == "chroma":
        return get_chroma_collection().get().get("documents", [])
    if os.path.exists(CHUNKS_PATH):
        return np.load(CHUNKS_PATH, allow_pickle=True).tolist()
    raise RuntimeError("Chunk store not found.")


def retrieve_relevant_chunks(query, top_k=5):
    query_embedding = embed_text([query])[0]

    if VECTOR_DB == "chroma":
        collection = get_chroma_collection()
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        docs = results.get("documents", [[]])
        return docs[0] if docs and docs[0] else []

    index = load_index()
    chunks = load_chunks()
    D, I = index.search(np.array([query_embedding]), top_k)
    return [chunks[i] for i in I[0] if i < len(chunks)]
