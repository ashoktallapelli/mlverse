import asyncio
import json
import sys
from contextlib import AsyncExitStack
from typing import Optional, Dict, List
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from llm.llm_provider_factory import LLMProviderFactory

load_dotenv()


class MultiSessionWrapper:
    """Wrapper that combines multiple MCP sessions into one interface"""

    def __init__(self, servers: Dict[str, ClientSession]):
        self.servers = servers
        self._cached_tools = None

    async def list_tools(self):
        """List tools from all connected servers"""
        if self._cached_tools is not None:
            return self._cached_tools

        all_tools = []
        for name, session in self.servers.items():
            try:
                response = await session.list_tools()
                tools = response.tools
                # Add server name to tool metadata for tracking
                for tool in tools:
                    tool._server_name = name
                all_tools.extend(tools)
            except Exception as e:
                print(f"Warning: Could not get tools from {name}: {e}")

        # Create a response-like object
        class ToolsResponse:
            def __init__(self, tools):
                self.tools = tools

        self._cached_tools = ToolsResponse(all_tools)
        return self._cached_tools

    async def call_tool(self, name: str, arguments: dict):
        """Call a tool on the appropriate server"""
        # Find which server has this tool
        tools_response = await self.list_tools()
        target_server = None

        for tool in tools_response.tools:
            if tool.name == name and hasattr(tool, '_server_name'):
                target_server = self.servers.get(tool._server_name)
                break

        if target_server is None:
            raise ValueError(f"Tool '{name}' not found in any connected server")

        return await target_server.call_tool(name, arguments)

    # Delegate other methods to the first available session
    def __getattr__(self, name):
        if self.servers:
            first_session = list(self.servers.values())[0]
            return getattr(first_session, name)
        raise AttributeError(f"No servers available for attribute '{name}'")


class MCPClient:
    def __init__(self, provider=None, model=None):
        self.servers: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
        self.provider = provider
        self.model = model

    async def connect_to_servers(self, config_path: str = "config.json"):
        """Connect to multiple MCP servers from config file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"Config file '{config_path}' not found. Creating example config...")
            self._create_example_config(config_path)
            return
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in config file: {e}")
            return

        mcp_servers = config.get('mcpServers', {})
        if not mcp_servers:
            print("No mcpServers found in config file")
            return

        print(f"Connecting to {len(mcp_servers)} server(s)...")

        for name, server_config in mcp_servers.items():
            try:
                await self._connect_single_server(name, server_config)
            except Exception as e:
                print(f"Failed to connect to '{name}': {e}")

    async def _connect_single_server(self, name: str, server_config: dict):
        """Connect to a single MCP server"""
        command = server_config['command']
        args = server_config.get('args', [])
        env = server_config.get('env', None)

        # Create server parameters
        server_params = StdioServerParameters(command=command, args=args, env=env)

        # Connect to server
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()

        # Get available tools
        response = await session.list_tools()
        tools = [tool.name for tool in response.tools]

        self.servers[name] = session
        print(f"✓ Connected to '{name}': {tools}")

    def _create_example_config(self, config_path: str):
        """Create an example config file"""
        example_config = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        "/path/to/directory"
                    ]
                },
                "weather": {
                    "command": "uv",
                    "args": [
                        "--directory",
                        "/path/to/weather/project",
                        "run",
                        "weather.py"
                    ]
                },
                "database": {
                    "command": "python",
                    "args": [
                        "database_server.py"
                    ],
                    "env": {
                        "DB_URL": "sqlite:///example.db"
                    }
                }
            }
        }

        with open(config_path, 'w') as f:
            json.dump(example_config, f, indent=4)

        print(f"Created example config at '{config_path}'. Please edit it with your server details.")

    def list_servers(self):
        """Display all connected servers"""
        if not self.servers:
            print("No servers connected")
            return

        print("\n📡 Connected Servers:")
        for name in self.servers.keys():
            print(f"  - {name}")

    async def ask_question(self, question: str):
        """Ask a question using all connected servers"""
        if not self.servers:
            return "No servers connected"

        # Create a wrapper that combines all sessions
        multi_session = MultiSessionWrapper(self.servers)

        provider = LLMProviderFactory.create_provider(
            provider_type=self.provider,
            session=multi_session,
            model=self.model
        )
        return await provider.ask(question)

    async def chat_loop(self):
        """Interactive chat loop"""
        if not self.servers:
            print("No servers connected. Exiting...")
            return

        print("\n🚀 MCP Client Ready!")
        print("Commands: 'list' (show servers), 'quit' (exit)")
        self.list_servers()

        while True:
            try:
                query = input("\n🧑 YOU: ").strip()

                if query.lower() == 'quit':
                    break
                elif query.lower() == 'list':
                    self.list_servers()
                    continue
                elif not query:
                    continue

                response = await self.ask_question(query)
                print(f"\n🤖 BOT: {response}")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")

    async def cleanup(self):
        """Clean up all connections"""
        await self.exit_stack.aclose()


async def main():
    # Parse command line arguments
    config_file = "config.json"
    provider = "ollama"
    model = None

    # Simple argument parsing
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--config" and i + 1 < len(sys.argv):
            config_file = sys.argv[i + 1]
        elif arg == "--provider" and i + 1 < len(sys.argv):
            provider = sys.argv[i + 1]
        elif arg == "--model" and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]

    print(f"Using config: {config_file}")
    print(f"Provider: {provider}")
    if model:
        print(f"Model: {model}")

    # Create and run client
    client = MCPClient(provider=provider, model=model)

    try:
        await client.connect_to_servers(config_file)
        await client.chat_loop()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())