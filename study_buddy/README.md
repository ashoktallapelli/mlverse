study_buddy/
│
├── app/
│   ├── agents/                 # Agent logic (RAG, LLM)
│   │   └── study_agent.py
│   ├── embedding/              # Embeddings + vector DB logic
│   │   ├── embedder.py
│   │   ├── indexer.py
│   │   └── retriever.py
│   ├── ingestion/              # PDF parser, text chunker
│   │   ├── pdf_reader.py
│   │   └── chunker.py
│   └── utils/                  # Logging, helpers
│       └── logger.py
│
├── interfaces/
│   ├── api/                    # Starlette backend
│   │   ├── main.py             # Starlette app
│   │   └── routes.py           # Upload and ask endpoints
│   ├── cli/                    # Typer or Click-based CLI
│   │   └── main.py
│   └── web/                    # Web UI (Streamlit or Gradio)
│       └── main.py
│
├── config/                     # Config settings
│   ├── settings.py
│   └── llm_config.py
│
├── data/                       # Uploaded files and vector index
│   ├── uploads/
│   └── faiss/                  # or chroma/
│
├── tests/
│   └── test_embedder.py
│
├── Dockerfile
├── requirements.txt
├── .env
└── main.py                     # Entry point to select CLI, Web, or API


Run CLI:
python main.py --mode cli upload "<path_to_pdf>"
python main.py --mode cli ask "<question to ask>"

Run Web:
PYTHONPATH=. python main.py --mode web

Set `VECTOR_DB=chroma` to use a persistent Chroma database instead of FAISS.
