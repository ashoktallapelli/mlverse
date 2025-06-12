import os
from functools import lru_cache

from agno.embedder.sentence_transformer import SentenceTransformerEmbedder
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
    embedder = SentenceTransformerEmbedder(
        id="sentence-transformers/all-MiniLM-L6-v2",  # Fast and good quality
        # model="all-mpnet-base-v2",  # Higher quality but slower
        # model="multi-qa-mpnet-base-dot-v1",  # Good for Q&A
    )
    return embedder
