from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class QueryRequest(BaseModel):
    question: str = Field(..., description="Question to ask the agent")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Agent's response")
    agent_type: Optional[str] = Field(None, description="Type of agent that answered (pdf/youtube)")
    question: str = Field(..., description="Original question")

class UploadResponse(BaseModel):
    message: str = Field(..., description="Success message")
    agent_type: Optional[str] = Field(None, description="Type of agent created")
    content_info: Optional[str] = Field(None, description="Information about the processed content")

class BuildAgentRequest(BaseModel):
    content_path: str = Field(..., description="Path to PDF file, PDF URL, or YouTube URL(s)")
    agent_type: Literal["pdf", "youtube", "auto"] = Field(
        default="auto",
        description="Type of agent to build (pdf, youtube, or auto-detect)"
    )

class BuildAgentResponse(BaseModel):
    message: str = Field(..., description="Success message")
    agent_type: str = Field(..., description="Type of agent built")
    is_active: bool = Field(..., description="Whether the agent is active")

class AgentStatusResponse(BaseModel):
    is_active: bool = Field(..., description="Whether any agent is active")
    agent_type: Optional[str] = Field(None, description="Type of active agent")
    pdf_ready: bool = Field(..., description="Whether PDF agent is ready")
    youtube_ready: bool = Field(..., description="Whether YouTube agent is ready")

# Legacy models for backward compatibility
class LegacyQueryResponse(BaseModel):
    answer: str
    context: List[str] = []