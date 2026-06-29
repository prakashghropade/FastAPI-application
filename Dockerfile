# ================================================
# Stage 1: Build stage
# ================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install compiler utilities for package compilation if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Initialize virtual env to cleanly segregate packages
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ================================================
# Stage 2: Production stage
# ================================================
FROM python:3.12-slim AS production

# Set environment paths
ENV PATH="/opt/venv/bin:$PATH"
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install curl for health checking
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual env from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy source code and config files
COPY . .

# Set up logging directory and scripts permissions
RUN mkdir -p logs && \
    chmod -R 775 logs && \
    chmod +x start.sh

# Create a non-privileged app user for safety
RUN addgroup --system appgroup && \
    adduser --system --group appuser && \
    chown -R appuser:appgroup /app /opt/venv

# Run subsequent commands under non-root app user
USER appuser

# Expose internal port
EXPOSE 8000

# Docker Healthcheck to verify FastAPI service status
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application using start.sh wrapper
CMD ["sh", "start.sh"]
