from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
from app.embedding.retriever import retrieve_relevant_chunks

app = FastAPI()


class ToolInput(BaseModel):
    query: str


@app.post("/run")
async def run_tool(request: Request):
    body = await request.json()
    query = body.get("input", {}).get("query", "")
    if not query:
        return {"error": "Missing query"}

    chunks = retrieve_relevant_chunks(query)
    return {
        "output": {
            "chunks": chunks
        }
    }
