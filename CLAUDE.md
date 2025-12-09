# A2A ADK Example Project

Multi-agent system demonstrating A2A protocol with Google ADK and Strands Agents.

## Project Structure

```
agents/
  coordinator/agent.py    # Main orchestrator (Google ADK) - routes to sub-agents
  math_agent/agent.py     # Math operations (Google ADK)
  lookup_agent/agent.py   # Data lookups (Google ADK)
  strands_agent/agent.py  # Shell/Python/AWS (Strands Agents)
server.py                 # Coordinator FastAPI server with web UI
adk_api.py                # Headless API server (no web UI)
docker-compose.yml        # Service orchestration
```

## Tech Stack

- **Google ADK**: Agent framework with A2A protocol support
- **Strands Agents**: AWS-focused agent framework with shell/Python tools
- **FastAPI/Uvicorn**: Web servers
- **PostgreSQL**: Session persistence
- **Docker Compose**: Container orchestration

## Common Commands

```bash
# Start all services
docker compose up --build

# Start specific service
docker compose up -d --build strands_agent

# View logs
docker compose logs -f coordinator
docker compose logs -f strands_agent

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# Rebuild single service
docker compose build strands_agent
```

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| coordinator | 8000 | Web UI |
| math_agent | 8001 | A2A endpoint |
| lookup_agent | 8002 | A2A endpoint |
| adk_api | 8003 | Headless REST API |
| strands_agent | 8004 | A2A endpoint |
| postgres | 5432 | Database |

## Code Conventions

- Agent modules expose `root_agent` or `strands_agent` as the main agent instance
- A2A apps expose `a2a_app` for uvicorn
- FastAPI apps expose `app` for uvicorn
- Use environment variables for configuration (see `.env.example`)
- Docker service names match agent names for networking

## Key Patterns

### Google ADK Agent
```python
from google.adk.agents.llm_agent import Agent
root_agent = Agent(model="gemini-2.0-flash", name="...", tools=[...])
```

### Strands Agent
```python
from strands import Agent
from strands.multiagent.a2a import A2AServer
strands_agent = Agent(model=model, name="...", tools=[...])
a2a_server = A2AServer(agent=strands_agent, host=HOST, port=PORT)
app = a2a_server.to_fastapi_app()
```

### RemoteA2aAgent (coordinator)
```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
agent = RemoteA2aAgent(name="...", agent_card=f"{URL}/.well-known/agent-card.json")
```

## Environment Variables

- `GOOGLE_API_KEY`: Required for Gemini models
- `AWS_PROFILE`: AWS profile for strands_agent
- `AGENT_HOST`: Docker hostname for agent card URLs
- `PORT`: Service port
- `BYPASS_TOOL_CONSENT`: Skip tool confirmation (headless mode)

## Testing API

```bash
# Create session
curl -X POST http://localhost:8003/apps/coordinator/users/u1/sessions/s1 \
  -H "Content-Type: application/json" -d '{}'

# Send query
curl -X POST http://localhost:8003/run \
  -H "Content-Type: application/json" \
  -d '{"app_name":"coordinator","user_id":"u1","session_id":"s1","new_message":{"role":"user","parts":[{"text":"List S3 buckets"}]},"streaming":false}'
```

## Important Notes

- ALWAYS use `AGENT_HOST` env var for Docker networking in agent cards
- Strands agent requires `BYPASS_TOOL_CONSENT=true` for headless operation
- Agent card endpoint is `/.well-known/agent-card.json` (not `agent.json`)
- Session must be created before calling `/run` or `/run_sse`
