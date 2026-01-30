# Multi-stage build for Python FastAPI application (AI-assisted via Docker AI)
# Based on Docker AI optimization recommendations

# Build stage - install dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage - minimal image
FROM python:3.13-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/')"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
