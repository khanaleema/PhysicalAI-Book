FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
# Install dependencies with timeout and retry
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --timeout=300 -r requirements.txt && \
    pip install --no-cache-dir --timeout=300 fastembed>=0.2.0

# Copy application code (use .dockerignore to exclude unnecessary files)
COPY . .

# Create cache directory for FastEmbedding
RUN mkdir -p /tmp/huggingface_cache && chmod 777 /tmp/huggingface_cache

# Set environment variables
ENV EMBEDDING_PROVIDER=huggingface
ENV EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
ENV PYTHONUNBUFFERED=1

# Expose port (use PORT env var or default to 7860)
EXPOSE ${PORT:-7860}

# Run the application
# Use PORT environment variable if available, otherwise default to 7860
# app.py is in the backend directory root
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
