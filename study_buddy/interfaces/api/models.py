from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    context: List[str]

class UploadResponse(BaseModel):
    message: str
