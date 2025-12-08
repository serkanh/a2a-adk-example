# A2A Protocol Test Environment

A 3-agent system demonstrating A2A protocol using the Agent Development Kit (ADK).

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
```

- **coordinator**: Web UI that routes requests to specialized agents
- **math_agent**: Handles math operations (add, multiply, prime check)
- **lookup_agent**: Handles data lookups (weather, timezone)

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

## Test Queries

| Query | Agent |
|-------|-------|
| "Add 5 and 3" | math_agent |
| "Is 17 prime?" | math_agent |
| "Weather in Tokyo?" | lookup_agent |
| "Time in London?" | lookup_agent |

## Stop

```bash
docker compose down
```
