import asyncio

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools, MultiMCPTools

# Try different endpoints to see which one works
server_url_stream = "http://localhost:8000/stream"
server_url_message = "http://localhost:8000/message"
server_url_mcp = "http://localhost:8000/mcp"  # If you add the new endpoint


async def run_agent_with_message_endpoint(message: str) -> None:
    """Try using the /message endpoint instead of /stream"""
    try:
        async with MCPTools(transport="streamable-http", url=server_url_message) as mcp_tools:
            agent = Agent(
                model=Ollama(id="llama3.2"),
                tools=[mcp_tools],
                markdown=True,
            )
            await agent.aprint_response(message=message, stream=True, markdown=True)
    except Exception as e:
        print(f"Error with message endpoint: {e}")


async def run_agent_with_stream(message: str) -> None:
    """Original approach with stream endpoint"""
    try:
        async with MCPTools(transport="streamable-http", url=server_url_stream) as mcp_tools:
            agent = Agent(
                model=Ollama(id="llama3.2"),
                tools=[mcp_tools],
                markdown=True,
            )
            await agent.aprint_response(message=message, stream=True, markdown=True)
    except Exception as e:
        print(f"Error with stream endpoint: {e}")


async def run_agent_with_mcp_endpoint(message: str) -> None:
    """Try with the new /mcp endpoint"""
    try:
        async with MCPTools(transport="streamable-http", url=server_url_mcp) as mcp_tools:
            agent = Agent(
                model=Ollama(id="llama3.2"),
                tools=[mcp_tools],
                markdown=True,
            )
            await agent.aprint_response(message=message, stream=True, markdown=True)
    except Exception as e:
        print(f"Error with mcp endpoint: {e}")


if __name__ == "__main__":
    message = "List all the users"

    print("Trying message endpoint...")
    asyncio.run(run_agent_with_message_endpoint(message))

    print("\nTrying stream endpoint...")
    asyncio.run(run_agent_with_stream(message))

    print("\nTrying MCP endpoint...")
    asyncio.run(run_agent_with_mcp_endpoint(message))