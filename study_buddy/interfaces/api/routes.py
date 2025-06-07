from starlette.requests import Request
from starlette.responses import JSONResponse
from app.ingestion.pdf_reader import extract_text_from_pdf
from app.ingestion.chunker import chunk_text
from app.embedding.embedder import embed_text
from app.embedding.indexer import index_text_chunks
from app.embedding.retriever import retrieve_relevant_chunks
from app.agents.study_agent import answer_with_context

async def upload_pdf(request: Request):
    form = await request.form()
    file = form["file"]
    contents = await file.read()
    text = extract_text_from_pdf(contents)
    chunks = chunk_text(text)
    embeddings = embed_text(chunks)
    index_text_chunks(chunks, embeddings)
    return JSONResponse({"message": "File indexed successfully"})

async def ask_question(request: Request):
    data = await request.json()
    question = data["question"]
    chunks = retrieve_relevant_chunks(question)
    answer = answer_with_context(question, chunks)
    return JSONResponse({"answer": answer})
