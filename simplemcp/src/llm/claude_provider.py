import logging
from typing import List, Dict, Any

from anthropic import Anthropic
from mcp import ClientSession

from llm.llm_provider import LLMProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeProvider(LLMProvider):
    def __init__(self, session: ClientSession, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(session)
        self.anthropic = Anthropic()
        self.model = model

    def format_tools(self, tools) -> List[Dict[str, Any]]:
        """Format MCP tools for Claude's expected format"""
        return [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in tools]

    async def ask(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [{"role": "user", "content": query}]
        available_tools = await self.get_formatted_tools()

        try:
            # Initial Claude API call
            response = self.anthropic.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=messages,
                tools=available_tools
            )

            return await self._process_claude_response(response, messages, available_tools)

        except Exception as e:
            logger.error(f"Error in Claude API call: {e}")
            return f"Error processing query with Claude: {str(e)}"

    async def _process_claude_response(self, response, messages: List[Dict], available_tools: List[Dict]) -> str:
        """Process Claude response and handle tool calls recursively"""
        final_text = []
        assistant_message_content = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                try:
                    # Execute tool call
                    result = await self.session.call_tool(tool_name, tool_args)
                    result_text = self.extract_result_content(result)

                    final_text.append(f"[Called {tool_name}]")
                    logger.info(f"Tool {tool_name} executed successfully")

                    # Update conversation history
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
                                "content": result_text
                            }
                        ]
                    })

                    # Get follow-up response from Claude
                    follow_up_response = self.anthropic.messages.create(
                        model=self.model,
                        max_tokens=1000,
                        messages=messages,
                        tools=available_tools
                    )

                    if follow_up_response.content and follow_up_response.content[0].text:
                        final_text.append(follow_up_response.content[0].text)

                except Exception as e:
                    error_msg = f"Error executing tool {tool_name}: {str(e)}"
                    final_text.append(error_msg)
                    logger.error(error_msg)

        return "\n".join(final_text)
