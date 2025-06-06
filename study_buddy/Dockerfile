FROM python:3.10-slim
ENV PYTHONPATH=/app

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

CMD ["python", "main.py", "--mode", "api"]
