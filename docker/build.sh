#!/bin/bash

# Build script for proxy-lite-docker
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

echo "Building proxy-lite-docker..."

# Navigate to workspace directory
cd "$WORKSPACE_DIR"

# Build the Docker image
docker build -t proxy-lite-docker -f docker/Dockerfile .

echo "Docker image built successfully: proxy-lite-docker"
echo ""
echo "To run the container:"
echo "docker run -p 8000:8000 proxy-lite-docker"
echo ""
echo "To run with a custom LLM API endpoint:"
echo "docker run -p 8000:8000 -e MODEL_API=http://example.com:8080/v1 proxy-lite-docker"
echo ""
echo "For more options, see docker/README.md" 