import asyncio
import shutil
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from app.agents.pdf_agent import PdfAgent
from app.agents.youtube_agent import YouTubeAgent
from app.utils.logger import logger
from app.utils.app_utils import classify_pdf_path

load_dotenv()

# Global variables to cache agents
pdf_agent: Optional[PdfAgent] = None
youtube_agent: Optional[YouTubeAgent] = None
current_agent_type: Optional[str] = None  # 'pdf' or 'youtube'


def build_pdf_agent(pdf_path: str):
    """Build PDF agent from PDF path"""
    global pdf_agent, current_agent_type

    pdf_type = classify_pdf_path(pdf_path)

    if pdf_type == 'local':
        pdf_agent = PdfAgent([pdf_path], local_pdfs=True)
    elif pdf_type == 'url':
        pdf_agent = PdfAgent([pdf_path], local_pdfs=False)
    else:
        raise ValueError(f"Invalid PDF file path: {pdf_path}")

    current_agent_type = 'pdf'
    logger.info(f"PDF agent built successfully with path: {pdf_path}")


def build_youtube_agent(youtube_urls: list):
    """Build YouTube agent from list of YouTube URLs"""
    global youtube_agent, current_agent_type

    if not youtube_urls:
        raise ValueError("At least one YouTube URL is required")

    # Validate YouTube URLs
    for url in youtube_urls:
        if not _is_valid_youtube_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")

    youtube_agent = YouTubeAgent(urls=youtube_urls)
    current_agent_type = 'youtube'
    logger.info(f"YouTube agent built successfully with URLs: {youtube_urls}")


def build_agent(content_path: str, agent_type: str = 'auto'):
    """
    Build agent based on content type

    Args:
        content_path: Path to PDF file or YouTube URL(s) (comma-separated)
        agent_type: 'pdf', 'youtube', or 'auto' (auto-detect)
    """
    global current_agent_type

    if agent_type == 'auto':
        agent_type = _detect_content_type(content_path)

    if agent_type == 'pdf':
        build_pdf_agent(content_path)
    elif agent_type == 'youtube':
        # Handle multiple YouTube URLs (comma-separated)
        youtube_urls = [url.strip() for url in content_path.split(',')]
        build_youtube_agent(youtube_urls)
    else:
        raise ValueError(f"Unsupported agent type: {agent_type}")


async def use_agent(question: str) -> str:
    """Use the currently active agent to answer questions"""
    global pdf_agent, youtube_agent, current_agent_type

    if current_agent_type == 'pdf':
        if not pdf_agent:
            raise RuntimeError("PDF agent has not been initialized. Call build_agent() first.")
        response = await pdf_agent.get_response(question)
    elif current_agent_type == 'youtube':
        if not youtube_agent:
            raise RuntimeError("YouTube agent has not been initialized. Call build_agent() first.")
        response = await youtube_agent.get_response(question)
    else:
        raise RuntimeError("No agent has been initialized. Call build_agent() first.")

    return response


def get_agent_info() -> dict:
    """Get information about the currently active agent"""
    global current_agent_type

    return {
        'type': current_agent_type,
        'is_active': current_agent_type is not None,
        'pdf_ready': pdf_agent is not None,
        'youtube_ready': youtube_agent is not None
    }


def reset_agents():
    """Reset all agents and clear cache"""
    global pdf_agent, youtube_agent, current_agent_type

    pdf_agent = None
    youtube_agent = None
    current_agent_type = None
    logger.info("All agents have been reset")





# Legacy function for backward compatibility
def build_pdf_agent_legacy(pdf_path: str):
    """Legacy function - use build_agent() instead"""
    build_pdf_agent(pdf_path)


# Example usage
async def main():
    global pdf_agent
    pdf_agent = None
    build_agent("https://www.youtube.com/watch?v=K5KVEU3aaeQ")
    answer = await use_agent("Summarize the contents of the video file")
    print("Agent response:\n", answer)


if __name__ == "__main__":
    asyncio.run(main())
