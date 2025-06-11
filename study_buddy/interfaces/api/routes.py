from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging

from app.ingestion.pdf_reader import extract_text_from_pdf
from app.ingestion.chunker import chunk_text
from app.embedding.embedder import embed_text
from app.embedding.indexer import index_text_chunks
from app.embedding.retriever import retrieve_relevant_chunks
from app.agents.study_agent import answer_with_context

executor = ThreadPoolExecutor(max_workers=4)

def run_in_thread(func, *args):
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(executor, func, *args)


async def upload_pdf(request: Request):
    try:
        form = await request.form()
        file = form.get("file")
        if not file:
            return JSONResponse({"error": "Missing file"}, status_code=HTTP_400_BAD_REQUEST)

        filename = file.filename
        if not filename.endswith(".pdf"):
            return JSONResponse({"error": "Only PDF files supported"}, status_code=HTTP_400_BAD_REQUEST)

        contents = await file.read()
        text = await run_in_thread(extract_text_from_pdf, contents)

        if not text.strip():
            return JSONResponse({"error": "PDF contains no extractable text"}, status_code=HTTP_400_BAD_REQUEST)

        chunks = await run_in_thread(chunk_text, text)
        embeddings = await run_in_thread(embed_text, chunks)
        await run_in_thread(index_text_chunks, chunks, embeddings)

        return JSONResponse({
            "message": "File indexed successfully",
            "chunks_indexed": len(chunks)
        })

    except Exception as e:
        logging.exception("Failed to upload and index PDF")
        return JSONResponse({"error": str(e)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


async def ask_question(request: Request):
    try:
        data = await request.json()
        question = data.get("question")
        if not question:
            return JSONResponse({"error": "Missing question"}, status_code=HTTP_400_BAD_REQUEST)

        chunks = await run_in_thread(retrieve_relevant_chunks, question)
        answer = await run_in_thread(answer_with_context, question, chunks)

        return JSONResponse({"answer": answer})

    except Exception as e:
        logging.exception("Failed to answer question")
        return JSONResponse({"error": str(e)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
