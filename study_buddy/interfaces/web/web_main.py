import streamlit as st

from app.embedding.embedder import embed_text
from app.ingestion.chunker import chunk_text
from app.ingestion.pdf_reader import extract_text_from_pdf
from app.embedding.indexer import index_text_chunks
from app.embedding.retriever import retrieve_relevant_chunks
from app.agents.study_agent import answer_with_context

st.set_page_config(page_title="📘 AI Study Buddy", layout="wide")
st.title("📘 AI Study Buddy")

# --- Session state to hold chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- File upload and indexing
with st.sidebar:
    st.header("Upload your notes")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file:
        with st.spinner("Extracting and indexing your notes..."):
            pdf_bytes = uploaded_file.read()
            text = extract_text_from_pdf(pdf_bytes)
            chunks = chunk_text(text)
            embeddings = embed_text(chunks)
            index_text_chunks(chunks, embeddings)
            st.success("✅ PDF processed and indexed!")

    if st.button("Clear Chat"):
        st.session_state.chat_history = []

# --- Main chat interface
st.markdown("### Ask questions from your notes below")

question = st.chat_input("Ask a question")

if question:
    with st.spinner("Thinking..."):
        context_chunks = retrieve_relevant_chunks(question)
        answer = answer_with_context(question, context_chunks)

        # Save question & answer to history
        st.session_state.chat_history.append((question, answer))

# --- Display chat history in scrollable style
for q, a in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        st.markdown(a)
