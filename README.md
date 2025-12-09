# A2A Protocol Test Environment

A multi-agent system demonstrating A2A protocol using the Agent Development Kit (ADK) and Strands Agents.

## Architecture

```
                              ┌─────────────────┐
                      A2A     │   math_agent    │
               ┌─────────────>│   (port 8001)   │
               │              └─────────────────┘
               │
┌──────────────┴──┐           ┌─────────────────┐
│   coordinator   │    A2A    │  lookup_agent   │
│   (port 8000)   │──────────>│   (port 8002)   │
└──────────────┬──┘           └─────────────────┘
               │
               │              ┌─────────────────┐
               │      A2A     │  strands_agent  │
               └─────────────>│   (port 8004)   │
                              └─────────────────┘

┌─────────────────┐
│    adk_api      │  (Headless API - same coordinator agent)
│   (port 8003)   │
└─────────────────┘
```

- **coordinator**: Web UI that routes requests to specialized agents (Google ADK)
- **math_agent**: Handles math operations - add, multiply, prime check (Google ADK)
- **lookup_agent**: Handles data lookups - weather, timezone (Google ADK)
- **strands_agent**: System operations - shell commands, Python REPL, AWS CLI (Strands Agents)
- **adk_api**: Headless REST API endpoint (no web UI) with session service

## Prerequisites

- Docker and Docker Compose
- Google API Key ([get one here](https://aistudio.google.com/apikey))
- AWS credentials configured in `~/.aws` (for strands_agent AWS operations)

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
| "List files in current directory" | strands_agent |
| "Run aws s3 ls" | strands_agent |
| "Execute python: print(2**10)" | strands_agent |

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
| coordinator | 8000 | Web UI with session persistence (Google ADK) |
| math_agent | 8001 | A2A math operations agent (Google ADK) |
| lookup_agent | 8002 | A2A data lookup agent (Google ADK) |
| adk_api | 8003 | Headless REST API (Google ADK) |
| strands_agent | 8004 | Shell/Python/AWS agent (Strands Agents) |
| postgres | 5432 | Session storage database |

## Strands Agent

The strands_agent provides system operations capabilities powered by [Strands Agents](https://github.com/strands-agents/strands-agents).

### Features

- **Shell commands**: Execute any shell command (`ls`, `cat`, `grep`, etc.)
- **Python REPL**: Run Python code with persistent state
- **AWS CLI**: Pre-installed AWS CLI with credentials from `~/.aws`

### Configuration

The strands_agent uses these environment variables:

| Variable | Description |
|----------|-------------|
| `AWS_PROFILE` | AWS profile to use (set in `.env`) |
| `BYPASS_TOOL_CONSENT` | Skip confirmation prompts (headless mode) |
| `PYTHON_REPL_INTERACTIVE` | Disable PTY mode for Python REPL |

### AWS Setup

1. Ensure your AWS credentials are configured in `~/.aws/`
2. Set the `AWS_PROFILE` in your `.env` file:
   ```
   AWS_PROFILE=your-profile-name
   ```

## Stop

```bash
docker compose down
```

## Stop and Remove Data

```bash
docker compose down -v
```
