from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Static
from app.embedding.retriever import retrieve_relevant_chunks
from app.agents.study_agent import answer_with_context

class StudyBuddyApp(App):
    CSS_PATH = "styles.css"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("🧠 Welcome to Study Buddy! Ask a question below:", id="header"),
            Input(placeholder="Ask a question...", id="input"),
            Static("", id="response"),
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        question = event.value
        response_widget = self.query_one("#response", Static)

        if question.strip().lower() in {"exit", "quit"}:
            await self.action_quit()

        try:
            chunks = retrieve_relevant_chunks(question)
            answer = answer_with_context(question, chunks)
            response_widget.update(f"🤖 {answer}")
        except Exception as e:
            response_widget.update(f"❌ Error: {e}")

