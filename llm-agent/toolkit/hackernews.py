from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.hackernews import HackerNewsTools

agent = Agent(
    name="Hackernews Team",
    model=Ollama(id='llama3.2'),
    tools=[HackerNewsTools()],
    show_tool_calls=True,
    markdown=True,
)

agent.print_response(
    "Write an engaging summary of the "
    "users with the top 2 stories on hackernews. "
    "Please mention the stories as well.",
)