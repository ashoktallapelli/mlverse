# LLM Agent with MCP Server

This project implements an AI agent using the phidata framework, Ollama + Llama LLM, and integrates with an MCP server using FastMCP and FastAPI.

## Prerequisites

1. Install Ollama from https://ollama.ai/
2. Pull the Llama2 model:
```bash
ollama pull llama2
```

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the MCP server:
```bash
python mcp_server.py
```

2. In a new terminal, run the agent:
```bash
python main.py
```

## Project Structure

- `main.py`: Main agent implementation
- `mcp_server.py`: MCP server implementation
- `agent/`: Agent-related modules
  - `tools.py`: Tool implementations (web search, etc.)
  - `config.py`: Configuration settings
  - `prompts.py`: Agent prompts
