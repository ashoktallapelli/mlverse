from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.python import PythonTools

agent = Agent(
    model=Ollama(id='llama3.2'),
    tools=[PythonTools()], show_tool_calls=True)
agent.print_response("Write a python script for fibonacci series and display the result till the 10th number")
