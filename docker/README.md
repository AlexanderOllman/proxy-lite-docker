# Proxy-Lite Docker

This directory contains Docker configuration files to run Proxy-Lite as a containerized service.

## Features

- Runs Proxy-Lite inside a Docker container
- Exposes an HTTP API to submit and track tasks
- Configurable via environment variables
- Works with external LLM API endpoints

## Prerequisites

- Docker and Docker Compose installed
- Access to an LLM API that supports Proxy-Lite (default: convergence-ai/proxy-lite-3b)

## Quick Start

```bash
# Build and start the container
docker-compose up -d

# Or using docker run
docker build -t proxy-lite-docker -f docker/Dockerfile .
docker run -p 8000:8000 proxy-lite-docker
```

## Configuration

Configure the container using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_API` | URL of the LLM API endpoint | https://convergence-ai-demo-api.hf.space/v1 |
| `MODEL_ID` | Model ID to use | convergence-ai/proxy-lite-3b |
| `VIEWPORT_WIDTH` | Browser viewport width | 1280 |
| `VIEWPORT_HEIGHT` | Browser viewport height | 1920 |
| `HOMEPAGE` | Default homepage URL | https://www.google.com |
| `HEADLESS` | Run browser in headless mode | true |

Example:

```bash
docker run -p 8000:8000 \
  -e MODEL_API=http://example.com:8080/v1 \
  -e MODEL_ID=my-custom-model \
  proxy-lite-docker
```

## API Endpoints

### Run a Task

```
POST /run
Content-Type: application/json

{
  "task": "Find some restaurants near Kings Cross"
}
```

Response:

```json
{
  "task_id": "5f8d5e1c-c123-4812-8d7e-58b3a06bfe3a"
}
```

### Get Task Status

```
GET /tasks/{task_id}
```

Response:

```json
{
  "id": "5f8d5e1c-c123-4812-8d7e-58b3a06bfe3a",
  "status": "completed",
  "task": "Find some restaurants near Kings Cross",
  "created_at": 1708642853.4567,
  "updates": ["Task started", "Task completed successfully"],
  "result": { ... },
  "screenshot_path": "/app/proxy-lite/screenshots/5f8d5e1c-c123-4812-8d7e-58b3a06bfe3a.png",
  "gif_path": "/app/proxy-lite/gifs/5f8d5e1c-c123-4812-8d7e-58b3a06bfe3a.gif",
  "error": null
}
```

### Get All Tasks

```
GET /tasks
```

### Get Resources

```
GET /screenshots/{task_id}.png
GET /gifs/{task_id}.gif
```

### Health Check

```
GET /health
```

## Example Usage

```bash
# Submit a task
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task": "Find information about Paris"}'

# Check task status
curl http://localhost:8000/tasks/5f8d5e1c-c123-4812-8d7e-58b3a06bfe3a
``` 