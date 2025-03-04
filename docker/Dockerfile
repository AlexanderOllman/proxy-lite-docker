FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV XDG_CONFIG_HOME=/app/.config
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

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

# Create app directory and set permissions
WORKDIR /app
COPY --chown=proxy:proxy ./proxy-lite /app/proxy-lite

# Copy requirements.txt
COPY --chown=proxy:proxy ./requirements.txt /app/requirements.txt

# Create directories for output and config
RUN mkdir -p /app/proxy-lite/screenshots /app/proxy-lite/gifs /app/.config && \
    chown -R proxy:proxy /app/proxy-lite /app/.config

# Switch to the proxy user for installations
USER proxy

# Install base requirements first (faster packages)
RUN python -m pip install --upgrade pip && \
    python -m pip install setuptools wheel

# Install requirements in two steps to avoid timeouts
RUN pip install omegaconf openai pydantic rich tenacity aiohttp pillow pre-commit

# Install larger packages separately
RUN pip install torch torchvision
RUN pip install opencv-python opencv-python-headless
RUN pip install streamlit transformers
RUN pip install playwright playwright-stealth

# Install the proxy-lite package and playwright browsers
RUN cd /app/proxy-lite && \
    pip install -e . && \
    PYTHONPATH=/app/proxy-lite/src playwright install --with-deps chromium

# Set up API server script and entrypoint
USER root
COPY --chown=proxy:proxy ./docker/api_server.py /app/
COPY --chown=proxy:proxy ./docker/entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Switch back to proxy user for running the application
USER proxy

# Expose port for API
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 