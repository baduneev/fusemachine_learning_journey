FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-docker.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-docker.txt

COPY app ./app
COPY data/documents ./data/documents

RUN mkdir -p /app/data/chroma_db

CMD ["python", "-m", "app.rag.rag_pipeline"]