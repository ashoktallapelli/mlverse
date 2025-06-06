# LLM config (e.g., API keys)
LLM_PROVIDER = "local"

from agno.models.ollama import Ollama

llm = Ollama(id="llama3.2")
