import asyncio
import streamlit as st
import tempfile
import os
from app.agents.study_agent import build_agent, use_agent

st.set_page_config(page_title="📘 AI Study Buddy", layout="wide")
st.title("📘 AI Study Buddy")

# --- Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent_built" not in st.session_state:
    st.session_state.agent_built = False
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False
if "current_pdf_path" not in st.session_state:
    st.session_state.current_pdf_path = ""

# --- Sidebar: PDF Setup and Agent Building
with st.sidebar:
    st.header("📂 Setup PDF Agent")

    # PDF Input Options
    input_method = st.radio(
        "Choose PDF input method:",
        ["📁 Upload Local File", "🔗 Enter URL/Path"],
        index=0
    )

    pdf_path = ""

    if input_method == "📁 Upload Local File":
        uploaded_file = st.file_uploader(
            "Upload a PDF file",
            type=["pdf"],
            help="Select a PDF file from your computer"
        )

        if uploaded_file is not None:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.read())
                pdf_path = tmp_file.name
                st.session_state.current_pdf_path = pdf_path

            st.success(f"📄 File uploaded: {uploaded_file.name}")

    else:  # URL/Path input
        pdf_path = st.text_input(
            "Enter PDF URL or file path:",
            value=st.session_state.current_pdf_path,
            placeholder="e.g., https://example.com/file.pdf or /path/to/file.pdf",
            help="Enter either a URL to a PDF file or a local file path"
        )
        st.session_state.current_pdf_path = pdf_path

    # Build Agent Button
    st.markdown("---")

    if pdf_path:
        if st.button("🔨 Build Agent", type="primary", use_container_width=True):
            try:
                with st.spinner("Building PDF agent..."):
                    build_agent(pdf_path)
                    st.session_state.agent_built = True
                    st.session_state.pdf_processed = True
                st.success("✅ PDF Agent built successfully!")
                st.balloons()  # Fun animation
            except Exception as e:
                st.error(f"❌ Error building agent: {str(e)}")
                st.session_state.agent_built = False
                st.session_state.pdf_processed = False
    else:
        st.button("🔨 Build Agent", disabled=True, use_container_width=True)
        st.info("Please select a PDF file or enter a path first")

    # Agent Status Indicator
    st.markdown("---")
    if st.session_state.agent_built:
        st.success("🤖 **Agent Status:** Ready")
        st.info("💡 You can now ask questions!")
    else:
        st.warning("⚠️ **Agent Status:** Not Ready")

    # Action Buttons
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    with col2:
        if st.button("🔄 Reset Agent", use_container_width=True):
            st.session_state.agent_built = False
            st.session_state.pdf_processed = False
            st.session_state.current_pdf_path = ""
            st.session_state.chat_history = []
            st.rerun()

# --- Main Chat Interface
if st.session_state.agent_built:
    st.markdown("### 🧠 Ask a question about your PDF")

    # Chat Input
    question = st.chat_input("Enter your question here...", key="chat_input")

    # Process question
    if question:
        with st.spinner("🤔 Thinking..."):
            try:
                # Use asyncio to run the async function
                answer = asyncio.run(use_agent(question))

                # Save to chat history
                st.session_state.chat_history.append((question, answer))

            except Exception as e:
                st.error(f"❌ Error getting response: {str(e)}")

    # Display Chat History using Streamlit's native chat components
    if st.session_state.chat_history:
        st.markdown("### 💬 Chat History")

        for i, (q, a) in enumerate(st.session_state.chat_history):
            # User question
            with st.chat_message("user", avatar="👤"):
                st.markdown(q)

            # AI response
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(a)
    else:
        st.info("💡 Ask your first question to get started!")

else:
    # Instructions when agent is not built
    st.markdown("### 🚀 Getting Started")

    # Use native Streamlit components instead of custom HTML
    with st.container():
        st.info("""
        📋 **How to use AI Study Buddy:**

        1. **Choose your PDF input method** in the sidebar
        2. **Upload a file** or **enter a URL/path**
        3. **Click "Build Agent"** to process the PDF
        4. **Start asking questions** about the PDF content
        """)

    st.markdown("### 📖 Examples")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **📁 File Upload:**
        - Research papers
        - Study notes  
        - Textbook chapters
        - Documentation
        """)

    with col2:
        st.markdown("""
        **🔗 URL Examples:**
        - `https://example.com/paper.pdf`
        - `file:///C:/Documents/notes.pdf`
        - `/home/user/study_material.pdf`
        """)

# --- Footer
st.markdown("---")
st.caption("Powered by Agno Framework - AI Study Buddy 🤖 | Built with ❤️ using Streamlit")