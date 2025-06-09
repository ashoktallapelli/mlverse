import os
from functools import lru_cache
from agno.models.ollama import Ollama

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL_ID", "llama3.2")

if not OLLAMA_URL.startswith("http"):
    raise ValueError(f"Invalid OLLAMA_BASE_URL: {OLLAMA_URL}")


@lru_cache()
def get_llm():
    return Ollama(id=OLLAMA_MODEL, host=OLLAMA_URL)
