# LLM config (e.g., API keys)
LLM_PROVIDER = "local"

from agno.models.ollama import Ollama

import os

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

llm = Ollama(id="llama3.2",
             host=OLLAMA_URL)
