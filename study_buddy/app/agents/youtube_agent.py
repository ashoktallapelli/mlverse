import shutil
from pathlib import Path
from typing import List, Optional

from agno.agent import Agent
from agno.knowledge.youtube import YouTubeKnowledgeBase
from agno.storage.sqlite import SqliteStorage
from agno.vectordb.lancedb import LanceDb, SearchType

from config.llm_config import get_llm, get_embedding_model
from app.utils.logger import logger


class YouTubeAgent:
    def __init__(self, urls: Optional[List[str]] = None):
        self.urls = urls or []

        self._clear_vector_data()

        self.llm = get_llm()
        self.embedder = get_embedding_model()
        self.vector_db = LanceDb(
            uri="data/lancedb",
            table_name="youtube_docs",
            search_type=SearchType.vector,
            embedder=self.embedder,
        )
        self.storage = SqliteStorage(
            table_name="youtube_sessions",
            db_file="data/youtube_agent.db",
        )

        self.knowledge = self._build_knowledge()
        self.agent = self._build_agent()

    def _clear_vector_data(self):
        """Delete LanceDB and optionally SQLite storage before building new agent"""
        lance_path = Path("data/lancedb/youtube_docs")
        sqlite_path = Path("data/youtube_agent.db")

        if lance_path.exists():
            logger.info("Clearing vector DB at %s", lance_path)
            shutil.rmtree(lance_path)

        if sqlite_path.exists():
            logger.info("Deleting session DB at %s", sqlite_path)
            sqlite_path.unlink()

    def _build_knowledge(self):
        if not self.urls:
            raise ValueError("You must pass at least one YouTube URL")

        logger.info("Loading YouTube videos: %s", self.urls)
        return YouTubeKnowledgeBase(
            urls=self.urls,
            vector_db=self.vector_db,
        )

    def _build_agent(self) -> Agent:
        self.knowledge.load(recreate=True)

        return Agent(
            name="YouTube Assistant",
            model=self.llm,
            instructions=[
                "Answer questions based on the content of the YouTube videos provided.",
                "Only include the output in your response. No other text.",
            ],
            knowledge=self.knowledge,
            storage=self.storage,
            add_references=True,
            search_knowledge=False,
            show_tool_calls=True,
            markdown=True,
        )

    async def get_response(self, message: str) -> Optional[str]:
        try:
            resp = await self.agent.arun(message, stream=False)
            return resp.content
        except Exception as e:
            logger.error("Error in YouTubeAgent.get_response", exc_info=e)
            return None
