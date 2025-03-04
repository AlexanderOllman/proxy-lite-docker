#!/bin/bash
set -e

# Set environment variables from Docker arguments
export PROXY_LITE_API_BASE=${MODEL_API:-https://convergence-ai-demo-api.hf.space/v1}
export PROXY_LITE_MODEL=${MODEL_ID:-convergence-ai/proxy-lite-3b}
export PROXY_LITE_VIEWPORT_WIDTH=${VIEWPORT_WIDTH:-1280}
export PROXY_LITE_VIEWPORT_HEIGHT=${VIEWPORT_HEIGHT:-1920}
export PROXY_LITE_HOMEPAGE=${HOMEPAGE:-https://www.google.com}
export PROXY_LITE_HEADLESS=${HEADLESS:-true}

# Set PYTHONPATH to include the src directory
export PYTHONPATH=/app/proxy-lite/src:$PYTHONPATH

# Print configuration
echo "Starting Proxy-Lite with:"
echo "API Base: $PROXY_LITE_API_BASE"
echo "Model: $PROXY_LITE_MODEL"
echo "Viewport: ${PROXY_LITE_VIEWPORT_WIDTH}x${PROXY_LITE_VIEWPORT_HEIGHT}"
echo "Homepage: $PROXY_LITE_HOMEPAGE"
echo "Headless: $PROXY_LITE_HEADLESS"
echo "PYTHONPATH: $PYTHONPATH"

# Start API server
exec python /app/api_server.py 