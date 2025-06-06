import faiss
import numpy as np
import os

FAISS_INDEX_PATH = "data/faiss/index.bin"
CHUNKS_PATH = "data/faiss/chunks.npy"

dimension = 384  # depends on embedding model
index = faiss.IndexFlatL2(dimension)
all_chunks = []

def index_text_chunks(chunks, embeddings):
    global all_chunks
    index.add(np.array(embeddings))
    all_chunks.extend(chunks)
    save_index()


def save_index():
    faiss.write_index(index, FAISS_INDEX_PATH)
    np.save(CHUNKS_PATH, np.array(all_chunks))


def load_index():
    global index
    if os.path.exists(FAISS_INDEX_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
