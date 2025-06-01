import asyncio
from contextlib import AsyncExitStack
from typing import Optional

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from llm.llm_provider_factory import LLMProviderFactory

load_dotenv()  # load environment variable from .env


class MCPClient:
    def __init__(self, provider="ollama", model="llama3.2"):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.provider = provider
        self.model = model

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"

        # Connect to server
        server_params = StdioServerParameters(command=command, args=[server_script_path], env=None)
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def ask_question(self, question):
        """Ask a question and get response"""
        provider = LLMProviderFactory.create_provider(provider_type=self.provider, session=self.session,
                                                      model=self.model)
        return await provider.ask(question)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\n🧑 YOU: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.ask_question(query)
                print("\n🤖 BOT:: " + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    # Simple argument parsing
    if len(sys.argv) < 2:
        print("Usage: python client.py server.py [--provider provider_name] [--model model_name]")
        print("Example: python client.py server.py --provider ollama --model llama3.2")
        return

    server_file = sys.argv[1]

    # Get model name if specified
    provider = "ollama"  # default
    if "--provider" in sys.argv:
        try:
            provider_index = sys.argv.index("--provider") + 1
            if provider_index < len(sys.argv):
                provider = sys.argv[provider_index]
        except:
            pass

    # Get model name if specified
    model = "llama3.2"  # default
    if "--model" in sys.argv:
        try:
            model_index = sys.argv.index("--model") + 1
            if model_index < len(sys.argv):
                model = sys.argv[model_index]
        except:
            pass

    # Create and run client
    client = MCPClient(provider=provider, model=model)

    try:
        await client.connect_to_server(server_file)
        await client.chat_loop()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
