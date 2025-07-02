import os
from functools import lru_cache

import torch
from agno.embedder.sentence_transformer import SentenceTransformerEmbedder
from sentence_transformers import SentenceTransformer
from agno.models.ollama import Ollama
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL_ID", "llama3.2")

GROQ_MODEL = os.getenv("GROQ_MODEL_ID", "llama3.2")

if not OLLAMA_URL.startswith("http"):
    raise ValueError(f"Invalid OLLAMA_BASE_URL: {OLLAMA_URL}")


def get_ollama():
    return Ollama(id=OLLAMA_MODEL, host=OLLAMA_URL)


def get_groq():
    return Groq(id=GROQ_MODEL)


@lru_cache()
def get_llm():
    if LLM_PROVIDER == "ollama":
        return get_ollama()
    elif LLM_PROVIDER == "groq":
        return get_groq()
    else:
        raise ValueError(f"Invalid LLM_PROVIDER: {LLM_PROVIDER}")


def get_embedding_model():
    # 1. Detect MPS (Apple GPU) or fall back to CPU
    device = "mps" if torch.backends.mps.is_available() else "cpu"

    # 2. Create the SBERT model on the chosen device
    st_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)  # :contentReference[oaicite:0]{index=0}

    # 3. Inject that client into the AGNO embedder
    embedder = SentenceTransformerEmbedder(
        id="sentence-transformers/all-MiniLM-L6-v2",
        sentence_transformer_client=st_model
    )
    return embedder

