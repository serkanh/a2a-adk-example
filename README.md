# A2A Protocol Test Environment

A multi-agent system demonstrating A2A protocol using the Agent Development Kit (ADK).

## Architecture

```
┌─────────────────┐      A2A       ┌─────────────────┐
│   coordinator   │<──────────────>│   math_agent    │
│   (port 8000)   │                │   (port 8001)   │
└────────┬────────┘                └─────────────────┘
         │ A2A
         │                         ┌─────────────────┐
         └────────────────────────>│  lookup_agent   │
                                   │   (port 8002)   │
                                   └─────────────────┘

┌─────────────────┐
│    adk_api      │  (Headless API - same coordinator agent)
│   (port 8003)   │
└─────────────────┘
```

- **coordinator**: Web UI that routes requests to specialized agents
- **math_agent**: Handles math operations (add, multiply, prime check)
- **lookup_agent**: Handles data lookups (weather, timezone)
- **adk_api**: Headless REST API endpoint (no web UI) with session service

## Prerequisites

- Docker and Docker Compose
- Google API Key ([get one here](https://aistudio.google.com/apikey))

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd a2a-adk-example

# Set up environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Start all agents
docker compose up --build

# Access the web UI
open http://localhost:8000
```

## Test Queries (Web UI)

| Query | Agent |
|-------|-------|
| "Add 5 and 3" | math_agent |
| "Is 17 prime?" | math_agent |
| "Weather in Tokyo?" | lookup_agent |
| "Time in London?" | lookup_agent |

## ADK API Usage (Headless)

The ADK API service runs on port 8003 and provides REST endpoints for programmatic access.

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/list-apps` | GET | List available agents |
| `/apps/{app}/users/{user}/sessions/{session}` | POST | Create/update session |
| `/run` | POST | Run agent (returns all events) |
| `/run_sse` | POST | Run agent (Server-Sent Events) |

### Step 1: Create a Session

Before sending queries, create a session:

```bash
curl -X POST http://localhost:8003/apps/coordinator/users/user_1/sessions/session_1 \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Step 2: Send a Query

```bash
curl -X POST http://localhost:8003/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "coordinator",
    "user_id": "user_1",
    "session_id": "session_1",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What is 5 + 3?"}]
    },
    "streaming": false
  }'
```

### Streaming Response (SSE)

For real-time streaming responses:

```bash
curl -X POST http://localhost:8003/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "coordinator",
    "user_id": "user_1",
    "session_id": "session_1",
    "new_message": {
      "role": "user",
      "parts": [{"text": "Is 17 a prime number?"}]
    },
    "streaming": true
  }'
```

### List Available Agents

```bash
curl http://localhost:8003/list-apps
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| coordinator | 8000 | Web UI with session persistence |
| math_agent | 8001 | A2A math operations agent |
| lookup_agent | 8002 | A2A data lookup agent |
| adk_api | 8003 | Headless REST API |
| postgres | 5432 | Session storage database |

## Stop

```bash
docker compose down
```

## Stop and Remove Data

```bash
docker compose down -v
```
