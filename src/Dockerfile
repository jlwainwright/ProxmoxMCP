# ProxmoxMCP Dockerfile
# Optimized for production deployment with security best practices

FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src

# Create non-root user for security
RUN groupadd --gid 1000 proxmox && \
    useradd --uid 1000 --gid proxmox --shell /bin/bash --create-home proxmox

# Install system dependencies and security updates
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.in requirements-dev.in ./
COPY pyproject.toml setup.py ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install uv && \
    uv pip install --system -r requirements.in && \
    pip install -e .

# Copy source code
COPY src/ ./src/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R proxmox:proxmox /app

# Switch to non-root user
USER proxmox

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import proxmox_mcp; print('OK')" || exit 1

# Expose ports (8080 for HTTP mode, configurable)
EXPOSE 8080

# Default command - can be overridden for different modes
CMD ["python", "-m", "proxmox_mcp.server"]