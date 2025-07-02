# 📚 AI Study Buddy

**AI Study Buddy** is an intelligent assistant that helps users study smarter by analyzing documents (e.g. PDFs) and answering questions based on their content. Built with modern AI frameworks and vector search technologies, it provides fast and accurate responses to help users extract knowledge from their documents.

---

## 🚀 Features

- ✅ Upload and analyze PDF documents
- ✅ Ask natural-language questions about uploaded content
- ✅ Fast semantic search using vector embeddings
- ✅ Supports multi-document knowledge base
- ✅ Runs locally or deployable via Docker
- ✅ Extensible for future data sources (e.g. YouTube videos, web pages)

---

## 🛠️ Tech Stack

- **Python 3.12+**
- **Agno Framework** for building AI agents
- **Vector Database**: LanceDB (or alternatives like ChromaDB)
- **Embedding Models** for text representation
- **LLM** (local or remote, e.g. Ollama, OpenAI models)
- **Docker** for containerization and deployment

---

## 📂 Project Structure

study-buddy/
├── app/
│   ├── agents/          # AI agent implementations
│   ├── knowledge/       # Knowledge base integrations
│   ├── utils/           # Utility modules and logging
│   ├── config/          # LLM and embedding configurations
│   └── main.py          # App entry point
├── data/                # Persistent data storage
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

---

## ⚙️ Installation

### Local Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/study-buddy.git
    cd study-buddy
    ```

2. **Create virtual environment:**

    ```bash
    python3.12 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the app:**

    ```bash
    python app/main.py
    ```

---

### Docker Setup

Build and run containers:

```bash
docker-compose up --build


Run CLI:
python main.py --mode cli upload "<path_to_pdf>"
python main.py --mode cli ask "<question to ask>"

Run Web:
PYTHONPATH=. python main.py --mode web

Set `VECTOR_DB=chroma` to use a persistent Chroma database instead of FAISS.
