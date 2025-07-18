# 📚 AI Study Buddy

**AI Study Buddy** is a comprehensive AI-powered document analysis and question-answering system that helps users study smarter by analyzing documents (PDFs) and YouTube videos, then answering natural language questions based on their content using AI and vector search technologies.

---

## 🎯 Core Purpose

The application helps users study smarter by analyzing documents (PDFs) and YouTube videos, then answering natural language questions based on their content using AI and vector search technologies.

---

## 🚀 Key Features

- ✅ **Document Upload**: Local PDF files or URLs
- ✅ **YouTube Integration**: Automatic transcript extraction and analysis
- ✅ **Semantic Search**: Fast, context-aware question answering
- ✅ **Multi-Document Support**: Build knowledge bases from multiple sources
- ✅ **Multiple Interfaces**: CLI, Web (Streamlit), and API (FastAPI)
- ✅ **Containerized Deployment**: Docker Compose with Ollama integration
- ✅ **Persistent Storage**: SQLite for sessions, vector DBs for embeddings
- ✅ **Auto Content Detection**: Automatically determines if input is PDF or YouTube
- ✅ **Agent Caching**: Reuses built agents for efficiency

---

## 🏗️ Architecture Overview

### Tech Stack
- **Python 3.12+** with modern AI frameworks
- **Agno Framework** for building AI agents
- **Vector Databases**: LanceDB, ChromaDB, or FAISS for semantic search
- **LLM Support**: Ollama (local), Groq, OpenAI models
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **Multiple Interfaces**: CLI, Web (Streamlit), and API (FastAPI)
- **Docker** for containerization and deployment

### Key Components

1. **Multi-Interface Design** (`main.py`):
   - CLI mode for command-line interactions
   - Web interface using Streamlit
   - API mode with FastAPI/Uvicorn

2. **AI Agents** (`app/agents/`):
   - **PDF Agent**: Processes and answers questions about PDF documents
   - **YouTube Agent**: Analyzes YouTube video transcripts
   - **Study Agent**: Unified interface that auto-detects content type

3. **Data Processing Pipeline**:
   - **PDF Ingestion**: Extracts text using PyPDF2
   - **Text Chunking**: Splits content into manageable pieces (500 chars with 50 char overlap)
   - **Embedding**: Converts text to vector representations using SentenceTransformers
   - **Vector Storage**: Indexes embeddings in LanceDB/ChromaDB/FAISS for fast retrieval

4. **Configuration System**:
   - Flexible LLM provider switching (Ollama/Groq/OpenAI)
   - Vector database selection (FAISS/ChromaDB/LanceDB)
   - Environment-based configuration

---

## 🔄 Workflow

1. **Content Ingestion**: User uploads PDF or provides YouTube URLs
2. **Processing**: Text extraction → chunking → embedding generation
3. **Indexing**: Store embeddings in vector database
4. **Query Processing**: User asks questions → semantic search → LLM generates answers
5. **Response**: Contextual answers with source references

---

## 📂 Project Structure

```
study-buddy/
├── app/
│   ├── agents/          # AI agent implementations
│   │   ├── pdf_agent.py      # PDF document processing agent
│   │   ├── youtube_agent.py  # YouTube video analysis agent
│   │   └── study_agent.py    # Unified agent interface
│   ├── embedding/       # Text embedding and vector operations
│   │   ├── embedder.py       # SentenceTransformer embedding
│   │   ├── indexer.py        # Vector database indexing
│   │   └── retriever.py      # Semantic search retrieval
│   ├── ingestion/       # Data processing pipeline
│   │   ├── pdf_reader.py     # PDF text extraction
│   │   └── chunker.py        # Text chunking utilities
│   └── utils/           # Utility modules and logging
├── config/              # Configuration management
│   ├── settings.py           # App settings and vector DB config
│   └── llm_config.py         # LLM and embedding model setup
├── interfaces/          # Multiple user interfaces
│   ├── cli/                  # Command-line interface
│   ├── web/                  # Streamlit web interface
│   └── api/                  # FastAPI REST interface
├── data/                # Persistent data storage
│   ├── faiss/               # FAISS vector indices
│   ├── chroma/              # ChromaDB storage
│   ├── lancedb/             # LanceDB storage
│   └── *.db                 # SQLite session databases
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### Local Development Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/study-buddy.git
    cd study-buddy
    ```

2. **Create virtual environment:**
    ```bash
    python3.12 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**
    ```bash
    cp .env.example .env
    # Edit .env with your API keys and preferences
    ```

5. **Run the application:**
    ```bash
    # CLI Mode
    python main.py --mode cli
    
    # Web Interface
    python main.py --mode web
    
    # API Server
    python main.py --mode api
    ```

---

### Docker Deployment

**Quick Start with Docker Compose:**

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

**Services Available:**
- **Ollama**: `http://localhost:11434` (Local LLM server)
- **Web Interface**: `http://localhost:8501` (Streamlit)
- **API Server**: `http://localhost:1000` (FastAPI)

---

## 🚀 Usage Examples

### CLI Interface

```bash
# Upload and process a PDF
python main.py --mode cli upload "/path/to/document.pdf"

# Start interactive Q&A session
python main.py --mode cli ask

# Direct question
python main.py --mode cli ask "What are the main topics in this document?"
```

### Web Interface

1. Navigate to `http://localhost:8501`
2. Choose content type (PDF or YouTube)
3. Upload file or enter URL
4. Click "Build Agent"
5. Start asking questions!

### API Interface

```bash
# Health check
curl http://localhost:1000/health

# Upload document (example endpoint)
curl -X POST "http://localhost:1000/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"

# Ask question (example endpoint)
curl -X POST "http://localhost:1000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "Summarize the main points"}'
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# LLM Provider Configuration
LLM_PROVIDER=ollama          # Options: ollama, groq, openai
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_ID=llama3.2
GROQ_MODEL_ID=meta-llama/llama-4-scout-17b-16e-instruct

# API Keys (if using external providers)
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
ANTHROPIC_API_KEY=your_anthropic_key

# Vector Database Selection
VECTOR_DB=chroma             # Options: faiss, chroma, lancedb

# Application Settings
DEBUG=True
AGNO_TELEMETRY=false
TOKENIZERS_PARALLELISM=false
```

### Vector Database Options

- **FAISS**: Fast, in-memory similarity search (default)
- **ChromaDB**: Persistent vector database with metadata
- **LanceDB**: Modern vector database with SQL-like queries

---

## 🛠️ Deployment Options

### Local Development
- Direct Python execution with virtual environment
- Ideal for development and testing

### Docker Containers
- Multi-container setup with Ollama for local LLM inference
- Production-ready with health checks and monitoring
- Automatic service orchestration

### Cloud Deployment
- Configurable for remote LLM providers (OpenAI, Groq)
- Scalable architecture for production workloads
- Environment-based configuration management

---

## 💡 Smart Features

### Auto Content Detection
Automatically determines if input is PDF or YouTube URL and routes to appropriate agent.

### Agent Caching
Built agents are cached and reused for efficiency, avoiding redundant processing.

### Multiple Vector DB Support
Choose vector database based on your performance and persistence needs:
- **FAISS**: Fastest for in-memory operations
- **ChromaDB**: Best for persistent storage with metadata
- **LanceDB**: Modern choice with advanced querying

### Session Management
Persistent chat history and agent state across interactions.

### Health Monitoring
Docker containers include proper health checks and monitoring for production deployment.

---

## 🔧 Advanced Usage

### Custom Embedding Models
Modify `config/llm_config.py` to use different embedding models:

```python
def get_embedding_model():
    # Use different SentenceTransformer model
    st_model = SentenceTransformer("your-preferred-model", device=device)
    return SentenceTransformerEmbedder(
        id="your-model-id",
        sentence_transformer_client=st_model
    )
```

### Custom LLM Providers
Add new LLM providers in `config/llm_config.py`:

```python
def get_custom_llm():
    return YourCustomLLM(api_key="your_key")
```

### Extending Content Types
Create new agents in `app/agents/` following the existing pattern:

```python
class CustomAgent:
    def __init__(self, content_source):
        # Initialize your agent
        pass
    
    async def get_response(self, question: str) -> str:
        # Process question and return response
        pass
```
