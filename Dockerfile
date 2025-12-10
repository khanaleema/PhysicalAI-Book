FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Hugging Face uses port 7860 by default)
EXPOSE 7860

# Run the application
# Use app.py for Hugging Face Spaces compatibility
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
