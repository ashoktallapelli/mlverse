from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools
from dotenv import load_dotenv

load_dotenv()


async def run_agent(message: str) -> str:
    """Run the retail banking agent with the given message."""
    print(f"Starting agent with message: {message}")

    file_path = str(Path(__file__).parent.parent.parent.parent)
    print(f"File path: {file_path}")

    try:
        print("Connecting to MCP server...")
        async with MCPTools(transport="streamable-http", url="http://127.0.0.1:8000/mcp/") as mcp_tools:
            print("MCP connection established")

            agent = Agent(
                name="Study buddy",
                model=Ollama(id="llama3.2"),
                tools=[mcp_tools],
                instructions=dedent("""\
                    You are a AI study assistant. Use the tools to access the file system.
                    - Use headings to organize your responses
                    - Be concise and focus on relevant information\
                """),
                markdown=True,
                show_tool_calls=True,
            )
            print("Agent created")

            # Run the agent
            print("Running agent...")
            print("=" * 50)
            response = await agent.arun(message, stream=False)
            print("=" * 50)
            print("Agent finished")
            return response.content

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {e}"


# if __name__ == "__main__":
#     # Basic example - exploring project license
#     async def main():
#         response = await run_agent("List all the accounts")
#         print(response)
#
#
#     asyncio.run(main())


async def answer_with_context(question, context_chunks):
    context = "\n".join(context_chunks)
    prompt = f"""You are a helpful study assistant. Use the following notes to answer the question.
    Context: {context}
    Question: {question}
    Answer:"""

    response = await run_agent(prompt)
    return response
