import json
import httpx

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools import tool
from typing import Any, Callable, Dict


def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Hook function that wraps the tool execution"""
    print(f"About to call {function_name} with arguments: {arguments}")
    result = function_call(**arguments)
    print(f"Function call completed with result: {result}")
    return result


@tool(
    name="fetch_hackernews_stories",  # Custom name for the tool (otherwise the function name is used)
    description="Get top stories from Hacker News",  # Custom description (otherwise the function docstring is used)
    show_result=True,  # Show result after function call
    stop_after_tool_call=False,  # Return the result immediately after the tool call and stop the agent
    tool_hooks=[logger_hook],  # Hook to run before and after execution
    requires_confirmation=False,  # Requires user confirmation before execution
    cache_results=True,  # Enable caching of results
    cache_dir="/tmp/agno_cache",  # Custom cache directory
    cache_ttl=3600  # Cache TTL in seconds (1 hour)
)
def get_top_stories_from_hacker_news(num_stories: int = 10) -> str:
    """
    This function returns the top 10 stories

    Args:
        num_stories: Input the number of stories

    Returns:
        Returns the top 10 stores
    """

    # Fetch the story ids
    response = httpx.get('https://hacker-news.firebaseio.com/v0/topstories.json')
    story_ids = response.json()

    # Story details
    stories = []
    for story_id in story_ids[:num_stories]:
        story_response = httpx.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json')
        story = story_response.json()
        if 'text' in story:
            story.pop("text", None)
        stories.append(story)
    return json.dumps(stories)


agent = Agent(
    model=Ollama(id="llama3.2"),
    tools=[get_top_stories_from_hacker_news])
agent.print_response("Show me the top news from Hacker News")
