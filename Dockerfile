# Dockerfile for Clippy API
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY setup.py .
COPY pyproject.toml .
COPY MANIFEST.in .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY clippy/ ./clippy/
COPY start_server.py .
COPY docker-start.sh .

# Install the package
RUN pip install -e .

# Create output directory
RUN mkdir -p /app/output

# Set environment variables
ENV CLIPPY_HOST=0.0.0.0
ENV CLIPPY_PORT=8000
ENV CLIPPY_WORKERS=4
ENV CLIPPY_OUTPUT_DIR=/app/output

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the server
CMD ["./docker-start.sh"]
