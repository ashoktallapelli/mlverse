# App settings
APP_NAME = "AI Study Buddy"

# Vector DB backend: "faiss" or "chroma"
# Can be overridden with the VECTOR_DB environment variable
import os
VECTOR_DB = os.getenv("VECTOR_DB", "faiss").lower()
