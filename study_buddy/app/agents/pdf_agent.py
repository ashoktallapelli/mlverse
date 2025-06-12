from pathlib import Path
from typing import List, Optional

from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.storage.sqlite import SqliteStorage
from agno.vectordb.lancedb import LanceDb, SearchType

from config.llm_config import get_llm, get_embedding_model
from app.utils.logger import logger


class PdfAgent:
    def __init__(
        self,
        urls: Optional[List[str]] = None,
        local_pdfs: bool = False,
    ):
        self.urls = urls or []
        self.local_pdfs = local_pdfs

        self.llm = get_llm()
        self.embedder = get_embedding_model()
        self.vector_db = LanceDb(
            uri="data/lancedb",
            table_name="pdf_docs",
            search_type=SearchType.vector,
            embedder=self.embedder,
        )
        self.storage = SqliteStorage(
            table_name="agent_sessions",
            db_file="data/pdf_agent.db",
        )

        # build knowledge & agent
        self.knowledge = self._build_knowledge()
        self.agent = self._build_agent()

    def _build_knowledge(self):
        if self.local_pdfs:
            if not self.urls:
                raise ValueError("When using local_pdfs=True, you must pass at least one file path")
            pdf_dir = Path(self.urls[0]).parent
            logger.info("Loading PDFs from directory: %s", pdf_dir)
            return PDFKnowledgeBase(
                path=str(pdf_dir),
                vector_db=self.vector_db,
            )
        else:
            logger.info("Loading remote PDF URLs: %s", self.urls)
            return PDFUrlKnowledgeBase(
                urls=self.urls,
                vector_db=self.vector_db,
            )

    def _build_agent(self) -> Agent:
        # index / load your knowledge
        self.knowledge.load(recreate=False)

        agent_config = {
            "name": "Study Buddy",
            "model": self.llm,
            "instructions": [
                "Search your knowledge before answering the question.",
                "Only include the output in your response. No other text.",
            ],
            "knowledge": self.knowledge,
            "storage": self.storage,
            "add_references": True,
            "search_knowledge": False,
            "show_tool_calls": True,
            "markdown": True,
        }
        return Agent(**agent_config)

    async def get_response(self, message: str) -> Optional[str]:
        try:
            resp = await self.agent.arun(message, stream=False)
            return resp.content
        except Exception as e:
            logger.error("Error in PdfAgent.get_response", exc_info=e)
            return None
