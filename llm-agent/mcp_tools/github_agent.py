import asyncio

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools


async def run_agent(message: str) -> None:
    async with MCPTools(command=f"uvx mcp-server-git") as mcp_tools:
        # Setup and run the agent
        agent = Agent(model=OpenAIChat(id="gpt-4o"), tools=[mcp_tools])
        await agent.aprint_response("What is the license for this project?", stream=True)


# Example usage
if __name__ == "__main__":
    # Basic example - exploring project license
    asyncio.run(run_agent("What is the license for this project?"))