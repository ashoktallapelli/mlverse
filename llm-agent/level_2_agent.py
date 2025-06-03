from agno.agent import Agent
from agno.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.url import UrlKnowledge
from agno.models.ollama import Ollama
from agno.storage.sqlite import SqliteStorage
from agno.vectordb.lancedb import LanceDb, SearchType

import shutil
import os

# Remove existing data
if os.path.exists("tmp"):
    shutil.rmtree("tmp")

# Load Agno documentation in a knowledge base
# You can also use `https://docs.agno.com/llms-full.txt` for the full documentation
knowledge = UrlKnowledge(
    urls=["https://docs.agno.com/introduction.md"],
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="agno_docs",
        search_type=SearchType.hybrid,
        # Use OpenAI for embeddings
        embedder=SentenceTransformerEmbedder(
            id="sentence-transformers/all-MiniLM-L6-v2",  # Fast and good quality
            # model="all-mpnet-base-v2",  # Higher quality but slower
            # model="multi-qa-mpnet-base-dot-v1",  # Good for Q&A
        ),
    ),
)

# Store agent sessions in a SQLite database
storage = SqliteStorage(table_name="agent_sessions", db_file="tmp/agent2.db")

agent = Agent(
    name="Agno Assist",
    model=Ollama(id="llama3.2"),
    instructions=[
        "Search your knowledge before answering the question.",
        "Only include the output in your response. No other text.",
    ],
    knowledge=knowledge,
    storage=storage,
    add_datetime_to_instructions=True,
    # Add the chat history to the messages
    add_history_to_messages=True,
    # Number of history runs
    num_history_runs=3,
    markdown=True,
)

if __name__ == "__main__":
    # Load the knowledge base, comment out after first run
    # Set recreate to True to recreate the knowledge base if needed
    agent.knowledge.load(recreate=False)
    agent.print_response("What is Agno?", stream=True)
