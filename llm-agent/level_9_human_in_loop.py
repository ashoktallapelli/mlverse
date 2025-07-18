"""🤝 Human-in-the-Loop: Adding User Confirmation to Tool Calls

This example shows how to implement human-in-the-loop functionality in your Agno tools.
It shows how to:
- Add tool hooks to tools for user confirmation
- Handle user input during tool execution
- Gracefully cancel operations based on user choice

Some practical applications:
- Confirming sensitive operations before execution
- Reviewing API calls before they're made
- Validating data transformations
- Approving automated actions in critical systems

Run `pip install openai httpx rich agno` to install dependencies.
"""

import json
from typing import Any, Callable, Dict, Iterator

import httpx
from agno.agent import Agent
from agno.exceptions import StopAgentRun
from agno.models.ollama import Ollama
from agno.tools import tool
from rich.console import Console
from rich.prompt import Prompt

# This is the console instance used by the print_response method
# We can use this to stop and restart the live display and ask for user confirmation
console = Console()


def confirmation_hook(
        function_name: str, function_call: Callable, arguments: Dict[str, Any]
):
    # Get the live display instance from the console
    live = console._live

    # Stop the live display temporarily so we can ask for user confirmation
    live.stop()  # type: ignore

    # Ask for confirmation
    console.print(f"\nAbout to run [bold blue]{function_name}[/]")
    message = (
        Prompt.ask("Do you want to continue?", choices=["y", "n"], default="y")
        .strip()
        .lower()
    )

    # Restart the live display
    live.start()  # type: ignore

    # If the user does not want to continue, raise a StopExecution exception
    if message != "y":
        raise StopAgentRun(
            "Tool call cancelled by user",
            agent_message="Stopping execution as permission was not granted.",
        )

    # Call the function
    result = function_call(**arguments)

    # Optionally transform the result

    return result


@tool(tool_hooks=[confirmation_hook])
def get_top_hackernews_stories(num_stories: int) -> str:
    """Fetch top stories from Hacker News.

    Args:
        num_stories (int): Number of stories to retrieve

    Returns:
        str: JSON string containing story details
    """
    # Fetch top story IDs
    response = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json")
    story_ids = response.json()

    # Yield story details
    final_stories = []
    for story_id in story_ids[:num_stories]:
        story_response = httpx.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        )
        story = story_response.json()
        if "text" in story:
            story.pop("text", None)
        final_stories.append(story)

    return json.dumps(final_stories)


# Initialize the agent with a tech-savvy personality and clear instructions
agent = Agent(
    model=Ollama(id="llama3.2"),
    tools=[get_top_hackernews_stories],
    markdown=True,
)

agent.print_response(
    "Fetch the top 2 hackernews stories?", stream=True, console=console
)
