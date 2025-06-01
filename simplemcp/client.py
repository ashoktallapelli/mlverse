import asyncio
from contextlib import AsyncExitStack
from typing import Optional

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from claude_provider import ClaudeProvider
from ollama_provider import OllamaProvider

load_dotenv()  # load environment variable from .env


class MCPClient:
    def __init__(self, use_ollama=False, ollama_model="llama3.2"):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.use_ollama = use_ollama
        self.ollama_model = ollama_model

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
        if self.use_ollama:
            ollama_provider = OllamaProvider(session=self.session, ollama_model=self.ollama_model)
            return await ollama_provider.ask_ollama(question)
        else:
            claude_provider = ClaudeProvider(session=self.session)
            return await claude_provider.ask_claude(question)

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
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient(use_ollama=True, ollama_model="llama3.2")
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
