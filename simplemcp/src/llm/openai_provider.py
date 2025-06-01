import json
import logging
from typing import List, Dict, Any

from mcp import ClientSession
from openai import OpenAI

from llm.llm_provider import LLMProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    def __init__(self, session: ClientSession, model: str = "gpt-4o", api_key: str = None):
        super().__init__(session)
        self.model = model
        self.client = OpenAI(api_key=api_key)  # Uses OPENAI_API_KEY env var if api_key is None

    def format_tools(self, tools) -> List[Dict[str, Any]]:
        """Format MCP tools for OpenAI's expected format"""
        return [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in tools]

    async def ask(self, query: str) -> str:
        """Process a query using OpenAI and available tools"""
        messages = [{"role": "user", "content": query}]

        try:
            available_tools = await self.get_formatted_tools()
            response = await self._call_openai(messages, available_tools)
            return await self._process_openai_response(response, messages, available_tools)

        except Exception as e:
            logger.error(f"Error in OpenAI processing: {e}")
            return f"Error processing query with OpenAI: {str(e)}"

    async def _call_openai(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        """Make API call to OpenAI with error handling"""
        try:
            if tools:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=1000,
                    temperature=0.7
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
            return response
        except Exception as e:
            logger.warning(f"OpenAI tool calling failed, trying without tools: {e}")
            # Fallback without tools
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            return response

    async def _process_openai_response(self, response, messages: List[Dict], available_tools: List[Dict]) -> str:
        """Process OpenAI response and handle tool calls"""
        final_text = []

        if not response.choices or not response.choices[0].message:
            return "No valid response from OpenAI"

        message = response.choices[0].message

        # Add regular content
        if message.content:
            final_text.append(message.content)

        # Handle tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                try:
                    tool_name = tool_call.function.name
                    tool_args = self._parse_tool_arguments(tool_call.function.arguments)

                    # Execute tool call
                    result = await self.session.call_tool(tool_name, tool_args)
                    result_text = self.extract_result_content(result)

                    final_text.append(f"[Called {tool_name}]")
                    logger.info(f"Tool {tool_name} executed successfully")

                    # Update conversation history for follow-up
                    messages.append({
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                        ]
                    })
                    messages.append({
                        "role": "tool",
                        "content": result_text,
                        "tool_call_id": tool_call.id
                    })

                    # Get follow-up response
                    follow_up_response = await self._call_openai(messages, available_tools)
                    if follow_up_response.choices and follow_up_response.choices[0].message.content:
                        final_text.append(follow_up_response.choices[0].message.content)

                except Exception as e:
                    error_msg = f"Error executing tool {tool_name}: {str(e)}"
                    final_text.append(error_msg)
                    logger.error(f"{error_msg}. Args: {tool_call.function.arguments}")

        return "\n".join(final_text) if final_text else "No response generated."

    def _parse_tool_arguments(self, args_raw: str) -> Dict[str, Any]:
        """Parse tool arguments from JSON string"""
        try:
            return json.loads(args_raw)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tool arguments as JSON: {e}")
            return {}
