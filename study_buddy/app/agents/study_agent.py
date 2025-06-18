import asyncio
from typing import Optional
from dotenv import load_dotenv

from app.agents.pdf_agent import PdfAgent
from app.utils.logger import logger
from app.utils.pdf_utils import classify_pdf_path

load_dotenv()

# Global variable to cache the agent
pdf_agent: Optional[PdfAgent] = None


def build_agent(pdf_path: str):
    global pdf_agent

    pdf_type = classify_pdf_path(pdf_path)

    if pdf_type == 'local':
        pdf_agent = PdfAgent([pdf_path], local_pdfs=True)
    elif pdf_type == 'url':
        pdf_agent = PdfAgent([pdf_path], local_pdfs=False)
    else:
        raise ValueError(f"Invalid PDF file path: {pdf_path}")


async def use_agent(question: str) -> str:
    if not pdf_agent:
        raise RuntimeError("PDF agent has not been initialized. Call build_agent() first.")

    response = await pdf_agent.get_response(question)
    return response


# # Example usage
# async def main():
#     global pdf_agent
#     pdf_agent = None
#     build_agent("/path/to/your/pdf/file.pdf")
#     answer = await use_agent("Summarize the contents of the pdf file")
#     print("Agent response:\n", answer)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
