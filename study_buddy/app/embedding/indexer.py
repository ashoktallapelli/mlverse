import faiss
import numpy as np
import os

FAISS_INDEX_PATH = "data/faiss/index.bin"

dimension = 384  # depends on embedding model
index = faiss.IndexFlatL2(dimension)


def index_text_chunks(chunks, embeddings):
    index.add(np.array(embeddings))
    save_index()


def save_index():
    faiss.write_index(index, FAISS_INDEX_PATH)


def load_index():
    global index
    if os.path.exists(FAISS_INDEX_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
