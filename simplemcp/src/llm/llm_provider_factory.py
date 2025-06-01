from mcp import ClientSession

from llm.claude_provider import ClaudeProvider
from llm.llm_provider import LLMProvider
from llm.ollama_provider import OllamaProvider
from llm.openai_provider import OpenAIProvider


class LLMProviderFactory:
    """Factory class to create LLM providers"""

    @staticmethod
    def create_provider(provider_type: str, session: ClientSession, **kwargs) -> LLMProvider:
        """Create an LLM provider of the specified type"""
        if provider_type.lower() == "claude":
            return ClaudeProvider(session, model=kwargs.get('model', 'claude-3-5-sonnet-20241022'))
        elif provider_type.lower() == "ollama":
            return OllamaProvider(
                session,
                model=kwargs.get('model', 'llama3.2'),
                host=kwargs.get('host', 'http://localhost:11434')
            )
        elif provider_type.lower() == "openai":
            return OpenAIProvider(
                session,
                model=kwargs.get('model', 'gpt-4o'),
                api_key=kwargs.get('api_key')
            )
        else:
            raise ValueError(f"Unknown provider type: {provider_type}. Supported: claude, ollama, openai")
