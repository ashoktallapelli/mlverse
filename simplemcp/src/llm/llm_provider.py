from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from mcp import ClientSession


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, session: ClientSession):
        self.session: Optional[ClientSession] = session

    @abstractmethod
    async def ask(self, query: str) -> str:
        """Process a query using the LLM and available tools"""
        pass

    async def get_formatted_tools(self) -> List[Dict[str, Any]]:
        """Get tools formatted for the specific LLM provider"""
        response = await self.session.list_tools()
        return self.format_tools(response.tools)

    @abstractmethod
    def format_tools(self, tools) -> List[Dict[str, Any]]:
        """Format MCP tools for the specific LLM's expected format"""
        pass

    def extract_result_content(self, result) -> str:
        """Extract content from MCP tool result"""
        if hasattr(result, 'content'):
            if isinstance(result.content, list):
                result_text = ""
                for item in result.content:
                    if hasattr(item, 'text'):
                        result_text += item.text
                    else:
                        result_text += str(item)
                return result_text
            else:
                return str(result.content)
        return str(result)
