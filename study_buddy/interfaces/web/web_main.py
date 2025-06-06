import streamlit as st
from app.ingestion.pdf_reader import extract_text_from_pdf
from app.embedding.indexer import index_text
from app.embedding.retriever import retrieve_relevant_chunks
from app.agents.study_agent import answer_with_context

st.title("AI Study Buddy")

uploaded_file = st.file_uploader("Upload your notes (PDF)", type="pdf")
if uploaded_file:
    text = extract_text_from_pdf(uploaded_file.read())
    index_text(text)
    st.success("PDF indexed!")

question = st.text_input("Ask a question about your notes")
if st.button("Ask") and question:
    chunks = retrieve_relevant_chunks(question)
    answer = answer_with_context(question, chunks)
    st.write("**Answer:**", answer)
