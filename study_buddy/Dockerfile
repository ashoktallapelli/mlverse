# === Builder Stage ===
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements for layer caching
COPY requirements.txt .

# Install packages in a virtual environment
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# === Final Stage ===
FROM python:3.11-slim

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Create non-root user
RUN useradd --create-home appuser
USER appuser

# Copy virtualenv and app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser . .

EXPOSE 1000 8501

# Change this depending on your app type:
# For CLI / API
CMD ["python", "main.py", "--mode", "api"]

# For Streamlit (if used):
# CMD ["streamlit", "run", "main.py"]
