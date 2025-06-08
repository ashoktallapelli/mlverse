import asyncio

import streamlit as st

from app.embedding.embedder import embed_text
from app.ingestion.chunker import chunk_text
from app.ingestion.pdf_reader import extract_text_from_pdf
from app.embedding.indexer import index_text_chunks
from app.embedding.retriever import retrieve_relevant_chunks
from app.agents.study_agent import answer_with_context
from config.settings import VECTOR_DB

st.set_page_config(page_title="📘 AI Study Buddy", layout="wide")
st.title("📘 AI Study Buddy")

# --- Chat History State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "contexts" not in st.session_state:
    st.session_state.contexts = []

# --- Sidebar: File Upload and Actions
with st.sidebar:
    st.header("📂 Upload Notes")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file:
        with st.spinner("Extracting and indexing your notes..."):
            pdf_bytes = uploaded_file.read()
            text = extract_text_from_pdf(pdf_bytes)
            chunks = chunk_text(text)
            embeddings = embed_text(chunks)
            index_text_chunks(chunks, embeddings)
            st.success("✅ PDF processed and indexed!")

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.contexts = []

# --- Chat Input
st.markdown("### 🧠 Ask a question about your notes")
question = st.chat_input("Enter your question here...")

def get_data_sync(ques, chunks_):
    return asyncio.run(answer_with_context(ques, chunks_))

# --- Process question
if question:
    with st.spinner("🤔 Retrieving and thinking..."):
        context_chunks = retrieve_relevant_chunks(question)
        answer = get_data_sync(question, context_chunks)

        # Save to chat history and contexts
        st.session_state.chat_history.append((question, answer))
        st.session_state.contexts.append(context_chunks)

# --- Display Chat History
for idx, (q, a) in enumerate(st.session_state.chat_history):
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"**You:**\n\n{q}")

    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(f"**Study Buddy:**\n\n{a}", unsafe_allow_html=True)

        # Show cited chunks (collapsed)
        with st.expander("📎 Show Source Notes"):
            for i, chunk in enumerate(st.session_state.contexts[idx]):
                st.markdown(f"**Snippet {i+1}:**\n\n```text\n{chunk.strip()}\n```")

# --- Footer
st.markdown("---")
st.caption(f"Powered by {VECTOR_DB.upper()}, SentenceTransformers, and LLM agents via Agno/Phidata")
