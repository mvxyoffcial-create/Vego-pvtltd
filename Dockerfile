# Final Production Dockerfile for VegGo
# Optimized multi-stage build

# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ============================================
# Stage 2: Runtime - Final image
# ============================================
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r veggo && useradd -r -g veggo veggo

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install Python packages from wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copy application code
COPY --chown=veggo:veggo app ./app
COPY --chown=veggo:veggo main.py .
COPY --chown=veggo:veggo init_db.py .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/uploads /app/static && \
    chown -R veggo:veggo /app

# Switch to non-root user
USER veggo

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Expose port 8000
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
# For development: use --reload
# For production: use --workers 4
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
