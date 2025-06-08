import os
import uuid
import numpy as np
from config.settings import VECTOR_DB

FAISS_INDEX_PATH = "data/faiss/index.bin"
CHUNKS_PATH = "data/faiss/chunks.npy"
CHROMA_PATH = "data/chroma"

if VECTOR_DB == "chroma":
    import chromadb
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection("notes")
else:
    import faiss
    dimension = 384  # depends on embedding model
    index = faiss.IndexFlatL2(dimension)
    all_chunks = []


def index_text_chunks(chunks, embeddings):
    """Index text chunks and embeddings into the selected vector store."""
    if VECTOR_DB == "chroma":
        ids = [str(uuid.uuid4()) for _ in chunks]
        # chroma expects python lists, not numpy arrays
        collection.add(documents=chunks, embeddings=[e.tolist() for e in embeddings], ids=ids)
    else:
        global all_chunks
        index.add(np.array(embeddings))
        all_chunks.extend(chunks)
        save_index()


def save_index():
    if VECTOR_DB == "chroma":
        # chroma persistent client saves automatically
        return
    faiss.write_index(index, FAISS_INDEX_PATH)
    np.save(CHUNKS_PATH, np.array(all_chunks))


def load_index():
    if VECTOR_DB == "chroma":
        return collection
    global index
    if os.path.exists(FAISS_INDEX_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
    return index
