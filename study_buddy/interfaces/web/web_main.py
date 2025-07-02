import asyncio
import streamlit as st
import tempfile
import os
from app.agents.study_agent import build_agent, use_agent, get_agent_info, reset_agents

st.set_page_config(page_title="📘 AI Study Buddy", layout="wide")
st.title("📘 AI Study Buddy")

# --- Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent_built" not in st.session_state:
    st.session_state.agent_built = False
if "pdf_content_path" not in st.session_state:  # Separate for PDF
    st.session_state.pdf_content_path = ""
if "youtube_content_path" not in st.session_state:  # Separate for YouTube
    st.session_state.youtube_content_path = ""
if "agent_type" not in st.session_state:
    st.session_state.agent_type = "pdf"
if "previous_agent_type" not in st.session_state:
    st.session_state.previous_agent_type = "pdf"

# --- Sidebar: Content Setup and Agent Building
with st.sidebar:
    st.header("📂 Setup Study Agent")

    # Agent Type Selection
    agent_type = st.selectbox(
        "Choose content type:",
        ["📄 PDF Document", "🎥 YouTube Video(s)"],
        index=0
    )

    # Update agent type in session state and detect changes
    current_agent_type = "pdf" if agent_type == "📄 PDF Document" else "youtube"

    # Check if agent type changed
    if st.session_state.previous_agent_type != current_agent_type:
        st.session_state.agent_type = current_agent_type
        st.session_state.previous_agent_type = current_agent_type
        # Reset agent when switching types
        if st.session_state.agent_built:
            reset_agents()
            st.session_state.agent_built = False
    else:
        st.session_state.agent_type = current_agent_type

    content_path = ""

    # PDF Input Section
    if st.session_state.agent_type == "pdf":
        st.markdown("#### 📄 PDF Input")

        # PDF Input Options
        pdf_input_method = st.radio(
            "Choose PDF input method:",
            ["📁 Upload Local File", "🔗 Enter URL/Path"],
            index=0,
            key="pdf_input_method"
        )

        if pdf_input_method == "📁 Upload Local File":
            uploaded_file = st.file_uploader(
                "Upload a PDF file",
                type=["pdf"],
                help="Select a PDF file from your computer",
                key="pdf_file_uploader"
            )

            if uploaded_file is not None:
                # Save uploaded file to temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    content_path = tmp_file.name
                    st.session_state.pdf_content_path = content_path

                st.success(f"📄 File uploaded: {uploaded_file.name}")

        else:  # URL/Path input
            content_path = st.text_input(
                "Enter PDF URL or file path:",
                value=st.session_state.pdf_content_path,  # Use PDF-specific state
                placeholder="e.g., https://example.com/file.pdf or /path/to/file.pdf",
                help="Enter either a URL to a PDF file or a local file path",
                key="pdf_path_input"
            )
            st.session_state.pdf_content_path = content_path

    # YouTube Input Section
    else:
        st.markdown("#### 🎥 YouTube Input")

        youtube_urls = st.text_area(
            "Enter YouTube URL(s):",
            value=st.session_state.youtube_content_path,  # Use YouTube-specific state
            placeholder="Enter one or more YouTube URLs (one per line or comma-separated)\n\nExample:\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ\nhttps://youtu.be/dQw4w9WgXcQ",
            help="Enter YouTube URLs separated by commas or new lines",
            height=100,
            key="youtube_urls_input"
        )

        if youtube_urls:
            # Clean and process URLs
            urls_list = []
            for url in youtube_urls.replace('\n', ',').split(','):
                url = url.strip()
                if url:
                    urls_list.append(url)

            content_path = ','.join(urls_list)
            st.session_state.youtube_content_path = content_path

            if urls_list:
                st.info(f"📹 {len(urls_list)} YouTube URL(s) entered")
        else:
            st.session_state.youtube_content_path = ""

    # Build Agent Button
    st.markdown("---")

    if content_path:
        if st.button("🔨 Build Agent", type="primary", use_container_width=True):
            try:
                with st.spinner(f"Building {st.session_state.agent_type.upper()} agent..."):
                    build_agent(content_path, st.session_state.agent_type)
                    st.session_state.agent_built = True

                st.success("✅ Agent built successfully!")
                st.balloons()

                # Show agent info
                agent_info = get_agent_info()
                if agent_info['type'] == 'pdf':
                    st.info("📄 PDF Agent ready for questions!")
                elif agent_info['type'] == 'youtube':
                    st.info("🎥 YouTube Agent ready for questions!")

            except Exception as e:
                st.error(f"❌ Error building agent: {str(e)}")
                st.session_state.agent_built = False
    else:
        st.button("🔨 Build Agent", disabled=True, use_container_width=True)
        if st.session_state.agent_type == "pdf":
            st.info("Please select a PDF file or enter a path first")
        else:
            st.info("Please enter at least one YouTube URL first")

    # Agent Status Indicator
    st.markdown("---")
    if st.session_state.agent_built:
        agent_info = get_agent_info()
        if agent_info['type'] == 'pdf':
            st.success("🤖 **PDF Agent:** Ready")
        elif agent_info['type'] == 'youtube':
            st.success("🤖 **YouTube Agent:** Ready")
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
            reset_agents()
            st.session_state.agent_built = False
            # Clear both content paths
            st.session_state.pdf_content_path = ""
            st.session_state.youtube_content_path = ""
            st.session_state.chat_history = []
            st.rerun()

# --- Main Chat Interface
if st.session_state.agent_built:
    agent_info = get_agent_info()
    content_type = "PDF" if agent_info['type'] == 'pdf' else "YouTube videos"

    st.markdown(f"### 🧠 Ask a question about your {content_type}")

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

        1. **Choose your content type** (PDF or YouTube) in the sidebar
        2. **Upload/enter your content** (file, URL, or YouTube links)
        3. **Click "Build Agent"** to process the content
        4. **Start asking questions** about the content
        """)

    st.markdown("### 📖 Supported Content Types")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **📄 PDF Documents:**
        - Research papers
        - Study notes  
        - Textbook chapters
        - Documentation
        - Local files or URLs
        """)

    with col2:
        st.markdown("""
        **🎥 YouTube Videos:**
        - Educational videos
        - Lectures and tutorials
        - Documentaries
        - Multiple videos supported
        - Automatic transcription
        """)

    st.markdown("### 🔗 Example URLs")

    with st.expander("📄 PDF Examples"):
        st.code("""
        https://example.com/research_paper.pdf
        file:///C:/Documents/notes.pdf
        /home/user/study_material.pdf
        """)

    with st.expander("🎥 YouTube Examples"):
        st.code("""
        https://www.youtube.com/watch?v=dQw4w9WgXcQ
        https://youtu.be/dQw4w9WgXcQ

        Multiple videos (comma or line separated):
        https://www.youtube.com/watch?v=video1,
        https://www.youtube.com/watch?v=video2
        """)

# --- Footer
st.markdown("---")
st.caption("Powered by Agno Framework - AI Study Buddy 🤖 | Built with ❤️ using Streamlit")