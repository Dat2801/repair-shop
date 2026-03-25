# ---- Build Stage ----
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies for mysqlclient / pymysql
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime Stage ----
FROM python:3.10-slim

WORKDIR /app

# Runtime MySQL client library (needed by pymysql at import time is pure-python,
# but kept here in case you switch to mysqlclient later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Cloud Run injects PORT env var (default 8080)
ENV PORT=8080

# Run as non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE ${PORT}

# Start gunicorn – workers & timeout tuned for Cloud Run
CMD exec gunicorn wsgi:app \
    --bind "0.0.0.0:${PORT}" \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
