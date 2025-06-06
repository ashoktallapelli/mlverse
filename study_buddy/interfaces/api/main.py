from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
from interfaces.api.routes import upload_pdf, ask_question

routes = [
    Route("/upload", upload_pdf, methods=["POST"]),
    Route("/ask", ask_question, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
