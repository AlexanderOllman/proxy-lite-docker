#!/bin/bash

# Build script for proxy-lite-docker
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

# Navigate to workspace directory
cd "$WORKSPACE_DIR"

# Run check_files.sh to verify file structure
echo "Running file structure check..."
if [ -f "./check_files.sh" ]; then
  ./check_files.sh
else
  echo "check_files.sh not found, skipping file check."
fi

echo "Building proxy-lite-docker..."

# Clear Docker build cache for this image
echo "Cleaning Docker build cache..."
docker builder prune -f --filter "until=24h" --filter "type=unused"

# Build the Docker image without using cache
docker build --no-cache -t fheonix/proxy-lite-docker:0.0.1 -f Dockerfile .
# docker build -t proxy-lite-docker -f Dockerfile .

echo "Docker image built successfully: proxy-lite-docker"
echo ""
echo "Pushing the image to Docker Hub..."
# Check if the image exists in Docker Hub and push it if it does not exist
docker push fheonix/proxy-lite-docker:0.0.1
echo "Image pushed successfully to Docker Hub"
echo ""
echo "To run the container:"
echo "docker run -p 8000:8000 proxy-lite-docker"
echo ""
echo "To run with a custom LLM API endpoint:"
echo "docker run -p 8000:8000 -e MODEL_API=http://example.com:8080/v1 proxy-lite-docker"
echo ""
echo "For more options, see docker/README.md" 