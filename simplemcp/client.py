import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import ollama
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variable from .env


# Initialize Ollama client
client = ollama.Client(host='http://localhost:11434')


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

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
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    def format_tools_for_ollama(self, tools):
        """Format MCP tools for Ollama's expected format"""
        formatted_tools = []
        for tool in tools:
            formatted_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            formatted_tools.append(formatted_tool)
        return formatted_tools

    async def process_query(self, query: str) -> str:
        """Process a query using Ollama and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # Get available tools from MCP server
        tools_response = await self.session.list_tools()
        available_tools = self.format_tools_for_ollama(tools_response.tools)

        # Initial Ollama API call
        try:
            response = ollama.chat(
                model='llama3.2',  # Make sure this model supports tool calling
                messages=messages,
                tools=available_tools,
                options={
                    'num_predict': 1000,
                    'temperature': 0.7,
                }
            )
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            # Fallback without tools if model doesn't support them
            response = ollama.chat(
                model='llama3.2',
                messages=messages,
                options={
                    'num_predict': 1000,
                    'temperature': 0.7,
                }
            )

        # Process response and handle tool calls
        final_text = []

        # Handle Ollama response format
        if 'message' in response:
            message = response['message']

            # Check if there's regular content
            if 'content' in message and message['content']:
                final_text.append(message['content'])

            # Check for tool calls
            if 'tool_calls' in message and message['tool_calls']:
                for tool_call in message['tool_calls']:
                    try:
                        tool_name = tool_call['function']['name']

                        # Handle tool arguments - they might be string or dict
                        tool_args_raw = tool_call['function']['arguments']
                        if isinstance(tool_args_raw, str):
                            tool_args = json.loads(tool_args_raw)
                        else:
                            tool_args = tool_args_raw

                        final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                        # Execute tool call via MCP
                        result = await self.session.call_tool(tool_name, tool_args)

                        # Handle result content properly
                        if hasattr(result, 'content'):
                            if isinstance(result.content, list):
                                # If content is a list, extract text from each item
                                result_text = ""
                                for item in result.content:
                                    if hasattr(item, 'text'):
                                        result_text += item.text
                                    else:
                                        result_text += str(item)
                            else:
                                result_text = str(result.content)
                        else:
                            result_text = str(result)

                        final_text.append(f"Tool result: {result_text}")

                        # Add tool result to conversation
                        messages.append({
                            "role": "assistant",
                            "content": message['content'] or "",
                            "tool_calls": message['tool_calls']
                        })

                        messages.append({
                            "role": "tool",
                            "content": result_text,
                            "tool_call_id": tool_call.get('id', f"{tool_name}_result")
                        })

                        # Get follow-up response from Ollama
                        follow_up_response = ollama.chat(
                            model='llama3.2',
                            messages=messages,
                            tools=available_tools,
                            options={
                                'num_predict': 1000,
                                'temperature': 0.7,
                            }
                        )

                        if 'message' in follow_up_response and 'content' in follow_up_response['message']:
                            final_text.append(follow_up_response['message']['content'])

                    except Exception as e:
                        final_text.append(f"Error executing tool {tool_name}: {str(e)}")
                        print(f"Debug - Tool call error: {e}")
                        print(f"Debug - Tool args type: {type(tool_args_raw)}")
                        print(f"Debug - Tool args value: {tool_args_raw}")

        return "\n".join(final_text) if final_text else "No response generated."

    async def anthropic_process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # # Initial Claude API call
        # response = self.anthropic.messages.create(
        #     model="claude-3-5-sonnet-20241022",
        #     max_tokens=1000,
        #     messages=messages,
        #     tools=available_tools
        # )

        # response = client.chat(
        #     model='llama3.2',  # or your preferred model
        #     messages=messages,
        #     tools=available_tools,
        #     options={
        #         'num_predict': 1000,  # equivalent to max_tokens
        #         'temperature': 0.7,
        #     }
        # )

        # Process response and handle tool calls
        final_text = []

        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                assistant_message_content.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }
                    ]
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\nResponse: " + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys
    asyncio.run(main())
