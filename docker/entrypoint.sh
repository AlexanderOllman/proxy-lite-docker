#!/bin/bash
set -e

# Source the Python virtual environment
source /app/proxy-lite/.venv/bin/activate

# Set environment variables from Docker arguments
export PROXY_LITE_API_BASE=${MODEL_API:-https://convergence-ai-demo-api.hf.space/v1}
export PROXY_LITE_MODEL=${MODEL_ID:-convergence-ai/proxy-lite-3b}
export PROXY_LITE_VIEWPORT_WIDTH=${VIEWPORT_WIDTH:-1280}
export PROXY_LITE_VIEWPORT_HEIGHT=${VIEWPORT_HEIGHT:-1920}
export PROXY_LITE_HOMEPAGE=${HOMEPAGE:-https://www.google.com}
export PROXY_LITE_HEADLESS=${HEADLESS:-true}

# Print configuration
echo "Starting Proxy-Lite with:"
echo "API Base: $PROXY_LITE_API_BASE"
echo "Model: $PROXY_LITE_MODEL"
echo "Viewport: ${PROXY_LITE_VIEWPORT_WIDTH}x${PROXY_LITE_VIEWPORT_HEIGHT}"
echo "Homepage: $PROXY_LITE_HOMEPAGE"
echo "Headless: $PROXY_LITE_HEADLESS"

# Start API server
exec python /app/api_server.py 