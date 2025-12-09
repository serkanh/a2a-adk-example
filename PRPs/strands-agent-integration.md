# PRP: AWS Strands Agent Integration with A2A Protocol

## Overview

Add a new headless agent based on the AWS Strands framework that exposes `shell` and `python_repl` tools via the A2A (Agent-to-Agent) protocol. This agent will integrate with the existing Google ADK-based coordinator as a sub-agent, enabling system administration and scripting capabilities.

## Architecture

```
                         Docker Network (a2a-network)
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  ┌─────────────────────┐                   ┌─────────────────────┐          │
│  │   coordinator       │      A2A          │   strands_agent     │          │
│  │   (Google ADK)      │<─────────────────>│   (AWS Strands)     │          │
│  │   Port: 8000        │                   │   Port: 8004        │          │
│  │   + RemoteA2aAgent  │                   │   A2AServer         │          │
│  └─────────┬───────────┘                   │   Tools: shell,     │          │
│            │                               │   python_repl       │          │
│            │ A2A                           │   Model: Gemini     │          │
│            │                               └─────────────────────┘          │
│            │                                                                 │
│            ▼                                                                 │
│  ┌─────────────────────┐      ┌─────────────────────┐                       │
│  │ math_agent (8001)   │      │ lookup_agent (8002) │                       │
│  │ Google ADK          │      │ Google ADK          │                       │
│  └─────────────────────┘      └─────────────────────┘                       │
│                                                                              │
│  ┌─────────────────────┐      ┌─────────────────────┐                       │
│  │ adk_api (8003)      │      │ postgres (5432)     │                       │
│  │ Google ADK          │      │ Database            │                       │
│  └─────────────────────┘      └─────────────────────┘                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

| Agent | Framework | Port | Tools | Model | Exposure Method |
|-------|-----------|------|-------|-------|-----------------|
| **coordinator** | Google ADK | 8000 | Sub-agent delegation | Gemini | `adk web` + RemoteA2aAgent |
| **math_agent** | Google ADK | 8001 | add_numbers, multiply, check_prime | Gemini | `to_a2a()` + uvicorn |
| **lookup_agent** | Google ADK | 8002 | get_weather, get_timezone | Gemini | `to_a2a()` + uvicorn |
| **strands_agent** | AWS Strands | 8004 | shell, python_repl | Gemini | `A2AServer` + uvicorn |

## Documentation References

### AWS Strands Documentation (Primary)
- **A2A Protocol Guide**: https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/
- **Multi-Agent Example**: https://strandsagents.com/latest/documentation/docs/examples/python/multi_agent_example/multi_agent_example/
- **Quickstart Guide**: https://strandsagents.com/latest/documentation/docs/user-guide/quickstart/
- **Strands Tools Reference**: https://github.com/strands-agents/tools
- **Gemini Model Provider**: https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/gemini/

### Local Documentation (in `docs/` folder)
- `docs/strands-a2a.md` - A2A server setup and configuration
- `docs/strands-multi-agent-example.md` - Multi-agent patterns
- `docs/quickstart.md` - Basic Strands setup
- `docs/gemini.md` - Gemini model provider configuration

### A2A Protocol Specification
- **A2A GitHub**: https://github.com/a2aproject/A2A
- **A2A Python SDK**: https://github.com/a2aproject/a2a-python
- **A2A Documentation**: https://a2aproject.github.io/A2A/latest/

### Existing Codebase References
- `agents/math_agent/agent.py` - Example headless A2A agent pattern
- `agents/coordinator/agent.py` - RemoteA2aAgent usage pattern
- `docker-compose.yml` - Service orchestration pattern
- `Dockerfile.headless` - Headless agent container pattern

## Prerequisites

- Python 3.10+ (Strands requires 3.10+)
- Docker and Docker Compose
- Google API Key for Gemini (same as coordinator)
  - Get from: https://aistudio.google.com/apikey

## Project Structure (After Implementation)

```
a2a-adk-example/
├── docker-compose.yml              # Updated with strands_agent service
├── Dockerfile.strands              # NEW: Strands-specific Dockerfile
├── requirements.strands.txt        # NEW: Strands dependencies
├── agents/
│   ├── coordinator/
│   │   └── agent.py                # Updated with strands_agent sub-agent
│   ├── math_agent/
│   ├── lookup_agent/
│   └── strands_agent/              # NEW: Strands agent directory
│       ├── __init__.py
│       └── agent.py
└── .env.example                    # Already has GOOGLE_API_KEY
```

## Implementation Details

### Key Strands Concepts

#### 1. Creating an A2A Server with Strands and Gemini Model

From `docs/gemini.md`, Strands supports Gemini via `strands-agents[gemini]`:

```python
# agents/strands_agent/agent.py
import os
import logging
from strands import Agent
from strands.models.gemini import GeminiModel
from strands.multiagent.a2a import A2AServer
from strands_tools import shell, python_repl

logging.basicConfig(level=logging.INFO)

PORT = int(os.environ.get("PORT", 8004))
HOST = os.environ.get("HOST", "0.0.0.0")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configure Gemini model (same as coordinator uses)
model = GeminiModel(
    client_args={
        "api_key": GOOGLE_API_KEY,
    },
    model_id="gemini-2.0-flash",
    params={
        "temperature": 0.7,
        "max_output_tokens": 2048,
    }
)

# Create Strands agent with shell and python_repl tools
strands_agent = Agent(
    model=model,
    name="strands_agent",
    description="System operations agent with shell and Python REPL capabilities for scripting and automation tasks.",
    tools=[shell, python_repl],
    callback_handler=None,  # Disable console output for headless mode
)

# Create A2A server
a2a_server = A2AServer(
    agent=strands_agent,
    host=HOST,
    port=PORT,
)

# For uvicorn deployment, expose the FastAPI app
app = a2a_server.to_fastapi_app()
```

#### 2. Consuming Strands Agent from Google ADK Coordinator

The A2A protocol is a standard, so Google ADK's `RemoteA2aAgent` should be able to consume any A2A-compliant agent. The key difference is the agent card endpoint:

- **Google ADK**: `/.well-known/agent-card.json`
- **Strands/A2A Standard**: `/.well-known/agent.json`

```python
# agents/coordinator/agent.py - Updated
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

STRANDS_AGENT_URL = os.environ.get("STRANDS_AGENT_URL", "http://localhost:8004")

# Connect to Strands agent via A2A
# Note: Strands uses standard A2A protocol with agent card at /.well-known/agent.json
strands_agent = RemoteA2aAgent(
    name="strands_agent",
    description="Remote agent for system operations using shell and Python REPL tools. Use for shell commands, script execution, and automation tasks.",
    agent_card=f"{STRANDS_AGENT_URL}/.well-known/agent.json",
)
```

#### 3. Tool Documentation

**shell tool** (from strands-agents-tools):
- Executes shell commands with PTY support
- Supports single commands, sequential commands, parallel execution
- Returns command output with exit codes
- **Note**: Does not work on Windows

**python_repl tool** (from strands-agents-tools):
- Executes Python code in a REPL environment
- State persistence across calls
- Supports data analysis, scripting, complex logic
- **Note**: Does not work on Windows

### Docker Configuration

#### Dockerfile.strands

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck and other system utilities
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Strands-specific requirements
COPY requirements.strands.txt .
RUN pip install --no-cache-dir -r requirements.strands.txt

# Copy agent code
COPY agents/strands_agent/ ./agents/strands_agent/

ENV PORT=8004
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Run with uvicorn
CMD ["uvicorn", "agents.strands_agent.agent:app", "--host", "0.0.0.0", "--port", "8004"]
```

#### requirements.strands.txt

```
strands-agents[a2a,gemini]>=1.0.0
strands-agents-tools>=0.2.0
uvicorn>=0.30.0
```

#### docker-compose.yml Addition

```yaml
  strands_agent:
    build:
      context: .
      dockerfile: Dockerfile.strands
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8004
      - HOST=0.0.0.0
    ports:
      - "8004:8004"
    networks:
      - a2a-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8004/.well-known/agent.json"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### Agent Implementations

#### agents/strands_agent/agent.py

```python
"""Strands Agent - Headless A2A service for shell and Python operations using Gemini."""
import os
import logging
from strands import Agent
from strands.models.gemini import GeminiModel
from strands.multiagent.a2a import A2AServer
from strands_tools import shell, python_repl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get("PORT", 8004))
HOST = os.environ.get("HOST", "0.0.0.0")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Configure Gemini model (matches coordinator's model for consistency)
model = GeminiModel(
    client_args={
        "api_key": GOOGLE_API_KEY,
    },
    model_id="gemini-2.0-flash",
    params={
        "temperature": 0.7,
        "max_output_tokens": 2048,
    }
)

# Create Strands agent with shell and python_repl tools
strands_agent = Agent(
    model=model,
    name="strands_agent",
    description="System operations agent with shell and Python REPL capabilities. Can execute shell commands, run Python scripts, and perform automation tasks.",
    system_prompt="""You are a helpful system administration assistant with access to shell commands and Python execution.

CAPABILITIES:
- Execute shell commands for system operations
- Run Python code for data processing and scripting
- File operations, text processing, and automation

SAFETY RULES:
- Never execute destructive commands without explicit user confirmation
- Avoid commands that could compromise system security
- Report errors clearly and suggest alternatives

Always explain what commands you're running and why.""",
    tools=[shell, python_repl],
    callback_handler=None,  # Disable console output for headless mode
)

# Create A2A server
a2a_server = A2AServer(
    agent=strands_agent,
    host=HOST,
    port=PORT,
)

# Expose FastAPI app for uvicorn
app = a2a_server.to_fastapi_app()

if __name__ == "__main__":
    # Direct execution (for local testing)
    a2a_server.serve()
```

#### agents/strands_agent/__init__.py

```python
from .agent import strands_agent, app
```

#### Updated agents/coordinator/agent.py

```python
"""Coordinator Agent - Web interface that orchestrates remote A2A agents."""
import os
from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

# Get URLs from environment (for Docker) or use defaults (for local dev)
MATH_AGENT_URL = os.environ.get("MATH_AGENT_URL", "http://localhost:8001")
LOOKUP_AGENT_URL = os.environ.get("LOOKUP_AGENT_URL", "http://localhost:8002")
STRANDS_AGENT_URL = os.environ.get("STRANDS_AGENT_URL", "http://localhost:8004")

# Connect to remote math agent via A2A (Google ADK)
math_agent = RemoteA2aAgent(
    name="math_agent",
    description="Remote agent for mathematical operations: addition, multiplication, and prime number checking.",
    agent_card=f"{MATH_AGENT_URL}/.well-known/agent-card.json",
)

# Connect to remote lookup agent via A2A (Google ADK)
lookup_agent = RemoteA2aAgent(
    name="lookup_agent",
    description="Remote agent for data lookups: weather information and timezone data.",
    agent_card=f"{LOOKUP_AGENT_URL}/.well-known/agent-card.json",
)

# Connect to remote Strands agent via A2A
# Note: Strands uses standard A2A protocol with agent.json (not agent-card.json)
strands_agent = RemoteA2aAgent(
    name="strands_agent",
    description="Remote agent for system operations with shell and Python REPL capabilities. Use for shell commands, script execution, and automation tasks.",
    agent_card=f"{STRANDS_AGENT_URL}/.well-known/agent.json",
)

root_agent = Agent(
    model="gemini-2.0-flash",
    name="coordinator",
    description="Main coordinator that orchestrates specialized remote agents for math, data lookups, and system operations.",
    instruction="""You are a helpful coordinator assistant that routes requests to specialized agents.

ROUTING RULES:
- For mathematical operations (adding numbers, multiplying, checking if a number is prime), delegate to math_agent
- For data lookups (weather, timezone, current time in cities), delegate to lookup_agent
- For shell commands, Python scripting, or system administration tasks, delegate to strands_agent
- For simple questions, greetings, or general conversation, respond directly

Always be helpful and explain what you're doing when delegating to other agents.
If an agent returns an error, explain the issue to the user clearly.""",
    sub_agents=[math_agent, lookup_agent, strands_agent],
)
```

## Implementation Tasks

Execute these tasks in order:

### Task 1: Create Strands Agent Package
- Create `agents/strands_agent/` directory
- Create `agents/strands_agent/__init__.py`
- Create `agents/strands_agent/agent.py` with:
  - GeminiModel configuration with GOOGLE_API_KEY
  - Strands Agent with shell and python_repl tools
  - A2AServer configuration
  - FastAPI app export for uvicorn

### Task 2: Create Strands Docker Configuration
- Create `requirements.strands.txt` with Strands dependencies:
  - `strands-agents[a2a,gemini]>=1.0.0`
  - `strands-agents-tools>=0.2.0`
  - `uvicorn>=0.30.0`
- Create `Dockerfile.strands` with:
  - Python 3.11 base image
  - Strands packages installation
  - uvicorn CMD for running the A2A server

### Task 3: Update Docker Compose
- Add `strands_agent` service to `docker-compose.yml` with:
  - Dockerfile.strands build
  - GOOGLE_API_KEY environment variable (same as other agents)
  - Port 8004 mapping
  - Health check for `/.well-known/agent.json`
  - Network: a2a-network

### Task 4: Update Coordinator Agent
- Update `agents/coordinator/agent.py` to:
  - Add `STRANDS_AGENT_URL` environment variable
  - Create `strands_agent` RemoteA2aAgent connection
  - Add strands_agent to sub_agents list
  - Update routing instructions

### Task 5: Update Docker Compose Environment Variables
- Update coordinator service with `STRANDS_AGENT_URL=http://strands_agent:8004`
- Update adk_api service with `STRANDS_AGENT_URL=http://strands_agent:8004`

### Task 6: Add Service Dependencies (Optional)
- Add strands_agent to coordinator's depends_on (if needed for startup ordering)

## Validation Gates

### Syntax & Linting
```bash
# Install dev dependencies
pip install ruff mypy

# Check Strands agent
ruff check agents/strands_agent/

# Check coordinator updates
ruff check agents/coordinator/

# Type checking (optional)
mypy agents/strands_agent/ --ignore-missing-imports
```

### Local Testing (Strands Agent Only)
```bash
# Set up Google API key (same as coordinator)
export GOOGLE_API_KEY=your_google_api_key

# Install Strands dependencies
pip install 'strands-agents[a2a,gemini]' strands-agents-tools uvicorn

# Start Strands agent
uvicorn agents.strands_agent.agent:app --host 0.0.0.0 --port 8004

# In another terminal, verify agent card
curl http://localhost:8004/.well-known/agent.json
```

### Docker Testing
```bash
# Build and start all services
docker-compose up --build

# In another terminal, check health
docker-compose ps

# Test Strands agent card
curl http://localhost:8004/.well-known/agent.json

# Test all agent cards
curl http://localhost:8001/.well-known/agent-card.json  # math_agent
curl http://localhost:8002/.well-known/agent-card.json  # lookup_agent
curl http://localhost:8004/.well-known/agent.json       # strands_agent

# Access coordinator web UI
open http://localhost:8000
```

### Functional Testing (via Web UI at localhost:8000)

| Test Query | Expected Behavior |
|------------|-------------------|
| "Hello" | Direct response from coordinator |
| "Add 5 and 3" | Delegated to math_agent |
| "Run the command 'ls -la'" | Delegated to strands_agent |
| "Execute Python code to calculate factorial of 5" | Delegated to strands_agent |
| "What's the weather in Tokyo?" | Delegated to lookup_agent |
| "List all files and then calculate 2+2" | Both strands_agent and math_agent invoked |

## Known Gotchas & Troubleshooting

### 1. Agent Card Path Difference
- **Google ADK** uses: `/.well-known/agent-card.json`
- **Strands/A2A Standard** uses: `/.well-known/agent.json`
- Ensure coordinator points to correct path for each agent type

### 2. Google API Key
- Strands agent uses the same `GOOGLE_API_KEY` as the coordinator
- Ensure key has Gemini API access enabled
- Get key from: https://aistudio.google.com/apikey

### 3. Gemini Model Installation
- Must install with gemini extra: `pip install 'strands-agents[gemini]'`
- Error `ModuleNotFoundError: No module named 'google.genai'` means gemini extra not installed

### 4. Shell/Python REPL Limitations
- These tools do NOT work on Windows containers
- Use Linux-based Docker images
- Some commands may be restricted in container environment

### 5. A2A Protocol Compatibility
- Both Google ADK and Strands implement A2A protocol
- If RemoteA2aAgent fails, check agent card format compatibility
- Fallback: Use Strands' `A2AClientToolProvider` in a custom tool

### 6. Health Check Timing
- Strands agent may take longer to start than ADK agents
- Adjust health check interval/retries if needed
- Default: 10s interval, 5s timeout, 5 retries

### 7. Rate Limiting
- Gemini API has rate limits
- If you see `ModelThrottledException`, implement backoff or reduce request frequency
- Consider using `gemini-2.5-flash` for better rate limits

## Error Handling Strategy

1. **Agent Connection Failures**: RemoteA2aAgent will throw errors if strands_agent is unreachable. The coordinator's instruction tells it to explain errors clearly.

2. **API Key Errors**: Strands will fail to initialize if GOOGLE_API_KEY is invalid. Check Docker logs for authentication errors.

3. **Tool Execution Errors**: shell and python_repl tools return structured error responses. The agent should explain these to users.

4. **A2A Protocol Mismatches**: If agent card format is incompatible, the RemoteA2aAgent will fail to resolve. Check agent card content at the endpoint.

## Fallback Approach

If direct RemoteA2aAgent integration fails due to A2A protocol differences, implement a custom tool wrapper:

```python
# Alternative: Wrap Strands A2A client as a tool
from strands_tools.a2a_client import A2AClientToolProvider

# In coordinator, use A2AClientToolProvider
strands_provider = A2AClientToolProvider(
    known_agent_urls=[STRANDS_AGENT_URL]
)

# Add to coordinator tools instead of sub_agents
root_agent = Agent(
    ...
    tools=[strands_provider.tools],  # or combine with sub_agents
)
```

## Success Criteria

- [ ] Strands agent starts successfully in Docker
- [ ] Health check passes for strands_agent (agent.json accessible)
- [ ] Coordinator can route requests to strands_agent
- [ ] Shell commands execute and return results
- [ ] Python REPL executes code and returns results
- [ ] All existing agents (math, lookup) continue to work
- [ ] No regressions in coordinator functionality

## PRP Confidence Score: 8/10

**Strengths:**
- Uses same model (Gemini) as coordinator for consistency
- Same API key simplifies configuration
- Clear architecture and integration approach
- Comprehensive documentation references
- Fallback approach if direct integration fails
- Detailed troubleshooting section

**Potential Risks:**
- A2A protocol compatibility between Google ADK and Strands (agent card format difference)
- First integration of Strands with ADK ecosystem
- Shell/Python REPL tools have security implications in container

**Mitigation:**
- Test agent card compatibility first
- Verify API key before Docker deployment
- Use fallback A2AClientToolProvider if needed
- Start with local testing before Docker
