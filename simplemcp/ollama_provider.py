import json
from typing import Optional

import ollama
from mcp import ClientSession


class OllamaProvider:
    def __init__(self, session: ClientSession, ollama_model="llama3.2"):
        self.session: Optional[ClientSession] = session
        self.ollama_model = ollama_model

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

    async def ask_ollama(self, query: str) -> str:
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
                model=self.ollama_model,  # Make sure this model supports tool calling
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
