# Use Python 3.11 slim image optimized for M2
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for M2 compatibility
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/outputs logs credentials

# Create non-root user for security
RUN useradd -m -u 1000 research-user && \
    chown -R research-user:research-user /app
USER research-user

# Set Python path
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Start application
CMD ["python", "src/main.py"]