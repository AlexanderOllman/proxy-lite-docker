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

# Create workdir and config directories
WORKDIR /app
RUN mkdir -p /app/.config /app/proxy-lite/screenshots /app/proxy-lite/gifs

# Copy files
COPY ./proxy-lite /app/proxy-lite
COPY ./requirements.txt /app/requirements.txt
COPY ./docker/api_server.py /app/
COPY ./docker/entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Install Python packages as root
RUN pip install -r /app/requirements.txt && \
    pip install -e /app/proxy-lite && \
    playwright install --with-deps chromium

# Create a non-root user for running the app
RUN useradd -m -s /bin/bash proxy
RUN chown -R proxy:proxy /app /home/proxy

# Switch to proxy user for running the application
USER proxy
ENV HOME=/home/proxy

# Expose port for API
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 