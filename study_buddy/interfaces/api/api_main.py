from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.ingestion.pdf_reader import extract_text_from_pdf
from app.ingestion.chunker import chunk_text
from app.embedding.embedder import embed_text
from app.embedding.indexer import index_text_chunks
from app.embedding.retriever import retrieve_relevant_chunks
from app.agents.study_agent import answer_with_context
from interfaces.api.models import QueryRequest, QueryResponse, UploadResponse

app = FastAPI(title="AI Study Buddy API")

# Optional: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload", response_model=UploadResponse)
async def upload_notes(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()
    try:
        text = extract_text_from_pdf(pdf_bytes)
        chunks = chunk_text(text)
        embeddings = embed_text(chunks)
        index_text_chunks(chunks, embeddings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    return UploadResponse(message="PDF processed and indexed successfully!")

@app.post("/query", response_model=QueryResponse)
async def query_notes(req: QueryRequest):
    try:
        context_chunks = retrieve_relevant_chunks(req.question)
        answer = answer_with_context(req.question, context_chunks)
        return QueryResponse(answer=answer, context=context_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering query: {str(e)}")
