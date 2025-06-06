from agno.agent import Agent
from agno.models.ollama import Ollama

from config.llm_config import llm

study_agent = Agent(
    name="Agno Assist",
    model=Ollama(id="llama3.2"),
    system_message="You are a helpful study assistant. Use the notes to answer user questions clearly and concisely.",
    add_datetime_to_instructions=True,
    # Add the chat history to the messages
    add_history_to_messages=True,
    # Number of history runs
    num_history_runs=3,
    markdown=True,
)


def answer_with_context(question, context_chunks):
    context = "\n".join(context_chunks)
    prompt = f"""You are a helpful study assistant. Use the following notes to answer the question.
    Context: {context}
    Question: {question}
    Answer:"""

    response = study_agent.run(prompt)
    return response.messages[-1].content  # ✅ Access like an object, not a dict
