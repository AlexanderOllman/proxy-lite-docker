FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
# Set UV cache directory to a location the proxy user can write to
ENV UV_CACHE_DIR=/home/proxy/.cache/uv

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    gnupg \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install browser dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN id -u proxy &>/dev/null || useradd -m -s /bin/bash proxy

# Install uv for better Python package management
RUN pip install --no-cache-dir uv

# Create app directory and set permissions
WORKDIR /app
COPY --chown=proxy:proxy ./proxy-lite /app/proxy-lite

# Create cache directory for uv and set proper permissions
RUN mkdir -p /home/proxy/.cache/uv && chown -R proxy:proxy /home/proxy/.cache

# Switch to the proxy user
USER proxy

# Setup virtual environment and install dependencies
RUN cd /app/proxy-lite && \
    [ -f pyproject.toml ] || echo "[build-system]\nrequires = []\nbuild-backend = \"setuptools.build_meta\"" > pyproject.toml && \
    uv venv --python 3.11 --python-preference managed && \
    . .venv/bin/activate && \
    uv sync && \
    uv pip install -e .

# Install Playwright browsers
RUN cd /app/proxy-lite && \
    . .venv/bin/activate && \
    playwright install --with-deps chromium

# Create required directories for screenshots and GIFs
RUN mkdir -p /app/proxy-lite/screenshots /app/proxy-lite/gifs

# Set up API server script
COPY --chown=proxy:proxy ./docker/api_server.py /app/
COPY --chown=proxy:proxy ./docker/entrypoint.sh /app/

# Make the entrypoint script executable
USER root
RUN chmod +x /app/entrypoint.sh
USER proxy

# Expose port for API
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 