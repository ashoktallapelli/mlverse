import asyncio
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.mcp import MCPTools
from textwrap import dedent

from dotenv import load_dotenv

load_dotenv()

async def run_atlassian_agent():
    # Point at your locally-running MCP server:
    async with MCPTools(
        url="http://localhost:9000/mcp",
        transport="streamable-http",
        timeout_seconds=30
    ) as mcp_tools:

        agent = Agent(
            name="Atlassian Helper",
            model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
            tools=[mcp_tools],
            instructions=dedent("""
                You can search and manipulate Jira issues and Confluence pages.
            """),
            markdown=True,
            add_state_in_messages=True,
            show_tool_calls=True,
        )

        # Ask it something!
        await agent.aprint_response(
            "Find all the pages in Confluence that mention.",
            stream=True
        )

# async def chat_loop():
#     """Interactive chat loop"""
#     print("Commands: 'quit' (exit)")
#
#     while True:
#         try:
#             query = input("\n🧑 YOU: ").strip()
#
#             if query.lower() == 'quit':
#                 break
#             elif not query:
#                 continue
#
#             print(f"\n🤖 BOT:")
#             agent.print_response(query, stream=True)
#
#         except KeyboardInterrupt:
#             print("\nExiting...")
#             break
#         except Exception as e:
#             print(f"\nError: {e}")
#
#
# if __name__ == "__main__":
#     asyncio.run(chat_loop())

if __name__ == "__main__":
    asyncio.run(run_atlassian_agent())
