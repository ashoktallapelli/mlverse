from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging
import tempfile
import json

from app.agents.study_agent import build_agent, use_agent, get_agent_info, reset_agents

executor = ThreadPoolExecutor(max_workers=4)


def run_in_thread(func, *args):
    """Run function in thread pool"""
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(executor, func, *args)


async def get_agent_status(request: Request):
    """Get current agent status"""
    try:
        agent_info = get_agent_info()
        return JSONResponse({
            "is_active": agent_info['is_active'],
            "agent_type": agent_info['type'],
            "pdf_ready": agent_info['pdf_ready'],
            "youtube_ready": agent_info['youtube_ready']
        })
    except Exception as e:
        logging.exception("Failed to get agent status")
        return JSONResponse({"error": str(e)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


async def reset_agent(request: Request):
    """Reset all agents"""
    try:
        await run_in_thread(reset_agents)
        return JSONResponse({"message": "All agents have been reset successfully"})
    except Exception as e:
        logging.exception("Failed to reset agents")
        return JSONResponse({"error": str(e)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


async def build_study_agent(request: Request):
    """Build agent from content path"""
    try:
        data = await request.json()
        content_path = data.get("content_path")
        agent_type = data.get("agent_type", "auto")

        if not content_path:
            return JSONResponse(
                {"error": "Missing content_path"},
                status_code=HTTP_400_BAD_REQUEST
            )

        # Build agent in thread
        await run_in_thread(build_agent, content_path, agent_type)

        agent_info = get_agent_info()
        return JSONResponse({
            "message": f"{agent_info['type'].upper()} agent built successfully!",
            "agent_type": agent_info['type'],
            "is_active": agent_info['is_active']
        })

    except Exception as e:
        logging.exception("Failed to build agent")
        return JSONResponse({"error": str(e)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


async def upload_pdf(request: Request):
    """Upload and process PDF file"""
    try:
        form = await request.form()
        file = form.get("file")
        if not file:
            return JSONResponse({"error": "Missing file"}, status_code=HTTP_400_BAD_REQUEST)

        filename = file.filename
        if not filename.endswith(".pdf"):
            return JSONResponse(
                {"error": "Only PDF files supported"},
                status_code=HTTP_400_BAD_REQUEST
            )

        # Save to temporary file
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(contents)
            pdf_path = tmp_file.name

        # Build PDF agent
        await run_in_thread(build_agent, pdf_path, 'pdf')

        return JSONResponse({
            "message": "PDF uploaded and agent built successfully!",
            "agent_type": "pdf",
            "content_info": f"File: {filename}"
        })

    except Exception as e:
        logging.exception("Failed to upload and process PDF")
        return JSONResponse({"error": str(e)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


async def ask_question(request: Request):
    """Ask question to active agent"""
    try:
        data = await request.json()
        question = data.get("question")
        if not question:
            return JSONResponse({"error": "Missing question"}, status_code=HTTP_400_BAD_REQUEST)

        # Check if agent is active
        agent_info = get_agent_info()
        if not agent_info['is_active']:
            return JSONResponse(
                {"error": "No agent is active. Please build an agent first."},
                status_code=HTTP_400_BAD_REQUEST
            )

        # Get answer from agent
        answer = await use_agent(question)

        return JSONResponse({
            "answer": answer,
            "agent_type": agent_info['type'],
            "question": question
        })

    except Exception as e:
        logging.exception("Failed to answer question")
        return JSONResponse({"error": str(e)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


# Legacy route for backward compatibility
async def upload_pdf_legacy(request: Request):
    """Legacy PDF upload route"""
    return await upload_pdf(request)