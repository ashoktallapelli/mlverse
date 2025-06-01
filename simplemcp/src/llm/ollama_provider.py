import json
import logging
from typing import List, Dict, Any

import ollama
from mcp import ClientSession

from llm.llm_provider import LLMProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    def __init__(self, session: ClientSession, model: str = "llama3.2", host: str = "http://localhost:11434"):
        super().__init__(session)
        self.model = model
        self.client = ollama.Client(host=host)

    def format_tools(self, tools) -> List[Dict[str, Any]]:
        """Format MCP tools for Ollama's expected format"""
        return [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in tools]

    async def ask(self, query: str) -> str:
        """Process a query using Ollama and available tools"""
        messages = [{"role": "user", "content": query}]

        try:
            available_tools = await self.get_formatted_tools()
            response = await self._call_ollama(messages, available_tools)
            return await self._process_ollama_response(response, messages, available_tools)

        except Exception as e:
            logger.error(f"Error in Ollama processing: {e}")
            return f"Error processing query with Ollama: {str(e)}"

    async def _call_ollama(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        """Make API call to Ollama with error handling"""
        try:
            if tools:
                return self.client.chat(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    options={
                        'num_predict': 1000,
                        'temperature': 0.7,
                    }
                )
            else:
                return self.client.chat(
                    model=self.model,
                    messages=messages,
                    options={
                        'num_predict': 1000,
                        'temperature': 0.7,
                    }
                )
        except Exception as e:
            logger.warning(f"Ollama tool calling failed, trying without tools: {e}")
            # Fallback without tools
            return self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    'num_predict': 1000,
                    'temperature': 0.7,
                }
            )

    async def _process_ollama_response(self, response: Dict, messages: List[Dict], available_tools: List[Dict]) -> str:
        """Process Ollama response and handle tool calls"""
        final_text = []

        if 'message' not in response:
            return "No valid response from Ollama"

        message = response['message']

        # Add regular content
        if message.get('content'):
            final_text.append(message['content'])

        # Handle tool calls
        if message.get('tool_calls'):
            for tool_call in message['tool_calls']:
                try:
                    tool_name = tool_call['function']['name']
                    tool_args = self._parse_tool_arguments(tool_call['function']['arguments'])

                    # Execute tool call
                    result = await self.session.call_tool(tool_name, tool_args)
                    result_text = self.extract_result_content(result)

                    final_text.append(f"[Called {tool_name}]")
                    logger.info(f"Tool {tool_name} executed successfully")

                    # Update conversation history for follow-up
                    messages.append({
                        "role": "assistant",
                        "content": message.get('content', ''),
                        "tool_calls": message['tool_calls']
                    })
                    messages.append({
                        "role": "tool",
                        "content": result_text,
                        "tool_call_id": tool_call.get('id', f"{tool_name}_result")
                    })

                    # Get follow-up response
                    follow_up_response = await self._call_ollama(messages, available_tools)
                    if (follow_up_response.get('message', {}).get('content')):
                        final_text.append(follow_up_response['message']['content'])

                except Exception as e:
                    error_msg = f"Error executing tool {tool_name}: {str(e)}"
                    final_text.append(error_msg)
                    logger.error(f"{error_msg}. Args: {tool_call.get('function', {}).get('arguments')}")

        return "\n".join(final_text) if final_text else "No response generated."

    def _parse_tool_arguments(self, args_raw) -> Dict[str, Any]:
        """Parse tool arguments handling both string and dict formats"""
        if isinstance(args_raw, str):
            try:
                return json.loads(args_raw)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tool arguments as JSON: {e}")
                return {}
        elif isinstance(args_raw, dict):
            return args_raw
        else:
            logger.warning(f"Unexpected argument type: {type(args_raw)}")
            return {}
