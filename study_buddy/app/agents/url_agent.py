from typing import List

from agno.agent import Agent
from agno.knowledge.url import UrlKnowledge
from agno.storage.sqlite import SqliteStorage
from agno.vectordb.lancedb import LanceDb, SearchType
from dotenv import load_dotenv

from app.utils.logger import logger
from config.llm_config import get_llm, get_embedding_model

load_dotenv()


class URLAgent:
    def __init__(self, urls: List[str] = None):
        self.urls = urls if isinstance(urls, list) else [urls] if urls else []
        self.llm = get_llm()
        self.agent = self.create_agent()

    def get_url_knowledge(self):
        embedder = get_embedding_model()
        knowledge = UrlKnowledge(
            urls=self.urls,
            vector_db=LanceDb(
                uri="data/lancedb",
                table_name="agno_docs",
                search_type=SearchType.hybrid,
                embedder=embedder,
            ),
        )

        # knowledge = UrlKnowledge(
        #     urls=["url"],
        #     vector_db=ChromaDb(
        #         path="data/chromadb",
        #         embedder = self.embedder,
        #         collection="agno_docs"
        #     )
        # )
        return knowledge

    def create_agent(self) -> Agent:
        # Store agent sessions in a SQLite database
        storage = SqliteStorage(table_name="agent_sessions", db_file="data/url_agent.db")

        url_agent = Agent(
            name="Study buddy",
            model=self.llm,
            instructions=[
                "Search your knowledge before answering the question.",
                "Only include the output in your response. No other text.",
            ],
            knowledge=self.get_url_knowledge(),
            storage=storage,
            add_datetime_to_instructions=True,
            # Add the chat history to the messages
            add_history_to_messages=True,
            # Number of history runs
            num_history_runs=3,
            markdown=True,
        )
        url_agent.knowledge.load(recreate=False)
        return url_agent

    async def get_response(self, message: str):
        try:
            response = await self.agent.arun(message, stream=False)
            # agent.print_response(message, stream=True)
            return response.content
        except Exception as e:
            logger.info(f"Error in get_response: {e}")
            return None
