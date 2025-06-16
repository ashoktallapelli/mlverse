import asyncio
from typing import Optional, List

from dotenv import load_dotenv

from agno.team import Team
from app.utils.logger import logger
from app.utils.pdf_utils import filter_pdf_and_non_pdf, classify_pdf_list
from config.llm_config import get_llm

load_dotenv()


async def run_team_agent(
    message: str,
    local_pdfs: Optional[List[str]] = None,
    url_pdfs: Optional[List[str]] = None,
) -> str:
    """
    Runs the Study Buddy Team agent, coordinating PDF and URL sub-agents to answer a question.

    :param message:    The user's query.
    :param local_pdfs: List of file paths to local PDF documents.
    :param url_pdfs:   List of URLs pointing to PDF documents.
    :returns:          Consolidated markdown answer with inline citations.
    """
    logger.info("Starting Team agent with message: %s", message)

    # Build sub-agents based on provided sources
    sub_agents = []
    if local_pdfs:
        sub_agents.append(PdfAgent(local_pdfs, local_pdfs=True).agent)
    if url_pdfs:
        sub_agents.append(PdfAgent(url_pdfs, local_pdfs=False).agent)

    if not sub_agents:
        warning = "No PDF sources provided; nothing to process."
        logger.warning(warning)
        return warning

    # Initialize the team
    study_team = Team(
        name="Study Buddy Team",
        mode="coordinate",
        model=get_llm(),
        members=sub_agents,
        instructions=[
            "You have access to two knowledge bases: local PDFs and URL-based PDFs.",
            f"Answer the user's question: \"{message}\"",
            "Pull facts from all sources, merge into a coherent markdown summary,",
            "and inline-cite each fact with its filename or URL.",
        ],
        markdown=True,
        show_members_responses=False,
        enable_agentic_context=True,
        add_datetime_to_instructions=True,
        success_criteria=(
            "Produce one consolidated answer summarizing content from all PDFs "
            "with inline citations."
        ),
    )

    try:
        logger.info("Running Team agent...")
        response = await study_team.arun(message=message, stream=False)
        logger.info("Team agent completed successfully.")
        return response.content if hasattr(response, 'content') else str(response)

    except Exception as e:
        logger.error("Error in Team agent", exc_info=e)
        return "Error: failed to generate team response."


async def answer_with_pdfs(
    question: str,
    pdf_paths: Optional[List[str]] = None,
    url_pdfs: Optional[List[str]] = None,
) -> str:
    """Convenience wrapper to query PDFs using the team agent."""
    if not pdf_paths and not url_pdfs:
        return "No PDF sources provided."
    return await run_team_agent(question, local_pdfs=pdf_paths, url_pdfs=url_pdfs)


import asyncio
from app.agents.pdf_agent import PdfAgent
from app.agents.url_agent import URLAgent


async def smoke_test():
    pdf_agent = PdfAgent(
        urls=["/Users/ashoktallapelli/Downloads/pdfs/datamall.pdf"],
        local_pdfs=True
    ).agent
    resp = await pdf_agent.arun("List the key topics covered in this PDF.", stream=False)
    print("PDF Agent response:\n", resp.content)

    url_agent = URLAgent(
        ["https://docs.agno.com/introduction.md"]
    ).agent
    resp2 = await url_agent.arun("What is Agno?", stream=False)
    print("URL Agent response:\n", resp2.content)


# asyncio.run(smoke_test())


if __name__ == "__main__":
    paths = ["/Users/ashoktallapelli/Downloads/pdfs/resume.pdf"]
    pdfs, non_pdfs = filter_pdf_and_non_pdf(paths)
    _local_pdfs, _url_pdfs = classify_pdf_list(pdfs, verify_urls=True)

    answer = asyncio.run(
        run_team_agent(
            "Summarize all the key insights from these documents and pages.",
            _local_pdfs,
            _url_pdfs,
        )
    )
    print(answer)
