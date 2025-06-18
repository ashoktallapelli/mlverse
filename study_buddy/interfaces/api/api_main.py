from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import asyncio
from app.agents.study_agent import build_agent, use_agent, get_agent_info, reset_agents
from interfaces.api.models import (
    QueryRequest, QueryResponse, UploadResponse,
    BuildAgentRequest, BuildAgentResponse, AgentStatusResponse
)

app = FastAPI(title="AI Study Buddy API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI Study Buddy API is running"}


@app.get("/agent/status", response_model=AgentStatusResponse)
def get_agent_status():
    """Get current agent status and information"""
    agent_info = get_agent_info()
    return AgentStatusResponse(
        is_active=agent_info['is_active'],
        agent_type=agent_info['type'],
        pdf_ready=agent_info['pdf_ready'],
        youtube_ready=agent_info['youtube_ready']
    )


@app.post("/agent/reset")
def reset_agent():
    """Reset all agents and clear cache"""
    reset_agents()
    return {"message": "All agents have been reset successfully"}


@app.post("/upload/pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            pdf_path = tmp_file.name

        # Build PDF agent
        build_agent(pdf_path, 'pdf')

        return UploadResponse(
            message="PDF uploaded and agent built successfully!",
            agent_type="pdf",
            content_info=f"File: {file.filename}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/agent/build", response_model=BuildAgentResponse)
async def build_study_agent(req: BuildAgentRequest):
    """Build an agent from content path (PDF URL or YouTube URLs)"""
    try:
        build_agent(req.content_path, req.agent_type)

        agent_info = get_agent_info()
        return BuildAgentResponse(
            message=f"{req.agent_type.upper()} agent built successfully!",
            agent_type=agent_info['type'],
            is_active=agent_info['is_active']
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building agent: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query_agent(req: QueryRequest):
    """Ask a question to the active agent"""
    try:
        agent_info = get_agent_info()
        if not agent_info['is_active']:
            raise HTTPException(
                status_code=400,
                detail="No agent is active. Please build an agent first using /agent/build or /upload/pdf"
            )

        answer = await use_agent(req.question)

        return QueryResponse(
            answer=answer,
            agent_type=agent_info['type'],
            question=req.question
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering query: {str(e)}")


# Legacy endpoint for backward compatibility
@app.post("/upload", response_model=UploadResponse)
async def upload_notes_legacy(file: UploadFile = File(...)):
    """Legacy upload endpoint - redirects to /upload/pdf"""
    return await upload_pdf(file)