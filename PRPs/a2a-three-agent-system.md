# PRP: A2A Three-Agent System with Docker Compose

## Overview

Build a 3-agent system that communicates via Google's Agent2Agent (A2A) protocol using the Agent Development Kit (ADK). The system demonstrates multi-agent collaboration where a coordinator agent orchestrates two specialized headless agents.

## Architecture

```
                         Docker Network (a2a-network)
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  ┌─────────────────────┐      A2A       ┌─────────────────────┐     │
│  │   coordinator       │<──────────────>│   math_agent        │     │
│  │   (Agent 1)         │                │   (Agent 2)         │     │
│  │   Port: 8000        │                │   Port: 8001        │     │
│  │   adk web           │                │   uvicorn + to_a2a  │     │
│  │   + RemoteA2aAgent  │                │   Headless          │     │
│  └──────────┬──────────┘                └─────────────────────┘     │
│             │                                                        │
│             │ A2A                                                     │
│             │                           ┌─────────────────────┐     │
│             └──────────────────────────>│   lookup_agent      │     │
│                                         │   (Agent 3)         │     │
│                                         │   Port: 8002        │     │
│                                         │   uvicorn + to_a2a  │     │
│                                         │   Headless          │     │
│                                         └─────────────────────┘     │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
         ▲
         │ Exposed to localhost:8000
         │
    User Browser
```

### Agent Responsibilities

| Agent | Role | Capability | Exposure Method |
|-------|------|------------|-----------------|
| **coordinator** | Orchestrator | Routes requests to appropriate agent | `adk web` (port 8000) |
| **math_agent** | Specialist | Mathematical operations (add, multiply, check prime) | `to_a2a()` + uvicorn (port 8001) |
| **lookup_agent** | Specialist | Data lookups (weather, time zones) | `to_a2a()` + uvicorn (port 8002) |

## Documentation References

### Primary Documentation
- **A2A Overview**: https://google.github.io/adk-docs/a2a/
- **Exposing Agents via A2A**: https://google.github.io/adk-docs/a2a/quickstart-exposing/
- **Consuming A2A Agents**: https://google.github.io/adk-docs/a2a/quickstart-consuming/
- **Multi-Agent Systems**: https://google.github.io/adk-docs/agents/multi-agents/
- **Python Quickstart**: https://google.github.io/adk-docs/get-started/python/
- **Deployment Options**: https://google.github.io/adk-docs/deploy/cloud-run/

### Code Examples
- **ADK Python Repository**: https://github.com/google/adk-python
- **ADK Samples**: https://github.com/google/adk-samples
- **ADK Made Simple**: https://github.com/chongdashu/adk-made-simple

## Prerequisites

- Python 3.10+ (ADK v1.19.0+ requires Python 3.10+)
- Docker and Docker Compose
- Google API Key for Gemini (from https://aistudio.google.com/apikey)

## Project Structure

```
a2a-adk-example/
├── docker-compose.yml
├── .env.example
├── .env                      # Created by user (gitignored)
├── requirements.txt
├── agents/
│   ├── coordinator/          # Agent 1 - Web interface + A2A consumer
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── math_agent/           # Agent 2 - Headless A2A server
│   │   ├── __init__.py
│   │   └── agent.py
│   └── lookup_agent/         # Agent 3 - Headless A2A server
│       ├── __init__.py
│       └── agent.py
├── Dockerfile.coordinator
├── Dockerfile.headless
└── PRPs/
    └── a2a-three-agent-system.md
```

## Implementation Details

### Key ADK Concepts

#### 1. Exposing an Agent via A2A (`to_a2a()`)

```python
# For headless agents (math_agent, lookup_agent)
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

root_agent = Agent(
    model="gemini-2.0-flash",
    name="math_agent",
    description="Agent specialized in mathematical operations",
    instruction="You perform mathematical calculations accurately.",
    tools=[add_numbers, multiply_numbers, check_prime],
)

# This creates an A2A-compatible FastAPI app
# Auto-generates agent card at /.well-known/agent-card.json
a2a_app = to_a2a(root_agent, port=8001)
```

#### 2. Consuming Remote A2A Agents (`RemoteA2aAgent`)

```python
# For coordinator agent
from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

# Connect to remote math agent
math_agent = RemoteA2aAgent(
    name="math_agent",
    description="Remote agent for mathematical operations",
    agent_card="http://math_agent:8001/.well-known/agent-card.json"
)

# Connect to remote lookup agent
lookup_agent = RemoteA2aAgent(
    name="lookup_agent",
    description="Remote agent for data lookups",
    agent_card="http://lookup_agent:8002/.well-known/agent-card.json"
)

root_agent = Agent(
    model="gemini-2.0-flash",
    name="coordinator",
    description="Main coordinator that orchestrates specialized agents",
    instruction="""You are a helpful coordinator.
    - For math operations (add, multiply, prime checking), delegate to math_agent
    - For lookups (weather, time zones), delegate to lookup_agent
    - Answer simple questions directly""",
    sub_agents=[math_agent, lookup_agent],
)
```

#### 3. Running the Coordinator with `adk web`

```bash
# From agents/ directory
adk web --port 8000
```

#### 4. Running Headless Agents with uvicorn

```bash
# For math_agent
uvicorn agents.math_agent.agent:a2a_app --host 0.0.0.0 --port 8001

# For lookup_agent
uvicorn agents.lookup_agent.agent:a2a_app --host 0.0.0.0 --port 8002
```

### Docker Configuration

#### docker-compose.yml

```yaml
version: '3.8'

services:
  math_agent:
    build:
      context: .
      dockerfile: Dockerfile.headless
      args:
        AGENT_NAME: math_agent
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8001
    ports:
      - "8001:8001"
    networks:
      - a2a-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/.well-known/agent-card.json"]
      interval: 10s
      timeout: 5s
      retries: 5

  lookup_agent:
    build:
      context: .
      dockerfile: Dockerfile.headless
      args:
        AGENT_NAME: lookup_agent
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8002
    ports:
      - "8002:8002"
    networks:
      - a2a-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/.well-known/agent-card.json"]
      interval: 10s
      timeout: 5s
      retries: 5

  coordinator:
    build:
      context: .
      dockerfile: Dockerfile.coordinator
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - MATH_AGENT_URL=http://math_agent:8001
      - LOOKUP_AGENT_URL=http://lookup_agent:8002
    ports:
      - "8000:8000"
    networks:
      - a2a-network
    depends_on:
      math_agent:
        condition: service_healthy
      lookup_agent:
        condition: service_healthy

networks:
  a2a-network:
    driver: bridge
```

#### Dockerfile.headless (for math_agent and lookup_agent)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/ ./agents/

ARG AGENT_NAME
ENV AGENT_NAME=${AGENT_NAME}
ENV PORT=8001

CMD uvicorn agents.${AGENT_NAME}.agent:a2a_app --host 0.0.0.0 --port ${PORT}
```

#### Dockerfile.coordinator

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/ ./agents/

ENV PORT=8000

# adk web serves the coordinator agent
CMD adk web agents/ --port ${PORT} --host 0.0.0.0
```

#### requirements.txt

```
google-adk[a2a]>=1.8.0
uvicorn>=0.30.0
```

### Agent Implementations

#### agents/math_agent/agent.py

```python
"""Math Agent - Headless A2A service for mathematical operations."""
import os
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a


def add_numbers(a: float, b: float) -> dict:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Dictionary with the sum result
    """
    return {"result": a + b, "operation": "addition"}


def multiply_numbers(a: float, b: float) -> dict:
    """Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Dictionary with the product result
    """
    return {"result": a * b, "operation": "multiplication"}


def check_prime(n: int) -> dict:
    """Check if a number is prime.

    Args:
        n: The number to check

    Returns:
        Dictionary indicating if the number is prime
    """
    if n < 2:
        return {"number": n, "is_prime": False, "reason": "Numbers less than 2 are not prime"}
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return {"number": n, "is_prime": False, "reason": f"Divisible by {i}"}
    return {"number": n, "is_prime": True, "reason": "No divisors found"}


root_agent = Agent(
    model="gemini-2.0-flash",
    name="math_agent",
    description="Agent specialized in mathematical operations including addition, multiplication, and prime number checking.",
    instruction="""You are a mathematical assistant.
    Use the provided tools to perform calculations accurately.
    Always show your work and explain the results clearly.""",
    tools=[add_numbers, multiply_numbers, check_prime],
)

# Create A2A-compatible app
PORT = int(os.environ.get("PORT", 8001))
a2a_app = to_a2a(root_agent, port=PORT)
```

#### agents/math_agent/__init__.py

```python
from .agent import root_agent
```

#### agents/lookup_agent/agent.py

```python
"""Lookup Agent - Headless A2A service for data lookups."""
import os
from datetime import datetime
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a


# Simulated data for demonstration
WEATHER_DATA = {
    "new york": {"temp": 72, "condition": "Sunny", "humidity": 45},
    "london": {"temp": 58, "condition": "Cloudy", "humidity": 70},
    "tokyo": {"temp": 68, "condition": "Partly Cloudy", "humidity": 55},
    "sydney": {"temp": 75, "condition": "Clear", "humidity": 40},
    "paris": {"temp": 62, "condition": "Rainy", "humidity": 80},
}

TIMEZONE_OFFSETS = {
    "new york": -5,
    "london": 0,
    "tokyo": 9,
    "sydney": 11,
    "paris": 1,
    "los angeles": -8,
}


def get_weather(city: str) -> dict:
    """Get current weather for a city.

    Args:
        city: Name of the city

    Returns:
        Dictionary with weather information
    """
    city_lower = city.lower()
    if city_lower in WEATHER_DATA:
        data = WEATHER_DATA[city_lower]
        return {
            "city": city,
            "temperature_f": data["temp"],
            "condition": data["condition"],
            "humidity_percent": data["humidity"],
            "status": "success"
        }
    return {
        "city": city,
        "status": "not_found",
        "message": f"Weather data not available for {city}. Available cities: {', '.join(WEATHER_DATA.keys())}"
    }


def get_timezone(city: str) -> dict:
    """Get timezone information for a city.

    Args:
        city: Name of the city

    Returns:
        Dictionary with timezone and current time
    """
    city_lower = city.lower()
    if city_lower in TIMEZONE_OFFSETS:
        offset = TIMEZONE_OFFSETS[city_lower]
        utc_now = datetime.utcnow()
        local_hour = (utc_now.hour + offset) % 24
        return {
            "city": city,
            "utc_offset": offset,
            "current_time": f"{local_hour:02d}:{utc_now.minute:02d}",
            "status": "success"
        }
    return {
        "city": city,
        "status": "not_found",
        "message": f"Timezone data not available for {city}. Available cities: {', '.join(TIMEZONE_OFFSETS.keys())}"
    }


root_agent = Agent(
    model="gemini-2.0-flash",
    name="lookup_agent",
    description="Agent specialized in data lookups including weather information and timezone data.",
    instruction="""You are a data lookup assistant.
    Use the provided tools to retrieve information.
    Present the data in a clear, formatted manner.""",
    tools=[get_weather, get_timezone],
)

# Create A2A-compatible app
PORT = int(os.environ.get("PORT", 8002))
a2a_app = to_a2a(root_agent, port=PORT)
```

#### agents/lookup_agent/__init__.py

```python
from .agent import root_agent
```

#### agents/coordinator/agent.py

```python
"""Coordinator Agent - Web interface that orchestrates remote A2A agents."""
import os
from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

# Get URLs from environment (for Docker) or use defaults (for local dev)
MATH_AGENT_URL = os.environ.get("MATH_AGENT_URL", "http://localhost:8001")
LOOKUP_AGENT_URL = os.environ.get("LOOKUP_AGENT_URL", "http://localhost:8002")

# Connect to remote math agent via A2A
math_agent = RemoteA2aAgent(
    name="math_agent",
    description="Remote agent for mathematical operations: addition, multiplication, and prime number checking.",
    agent_card=f"{MATH_AGENT_URL}/.well-known/agent-card.json"
)

# Connect to remote lookup agent via A2A
lookup_agent = RemoteA2aAgent(
    name="lookup_agent",
    description="Remote agent for data lookups: weather information and timezone data.",
    agent_card=f"{LOOKUP_AGENT_URL}/.well-known/agent-card.json"
)

root_agent = Agent(
    model="gemini-2.0-flash",
    name="coordinator",
    description="Main coordinator that orchestrates specialized remote agents for math and data lookups.",
    instruction="""You are a helpful coordinator assistant that routes requests to specialized agents.

ROUTING RULES:
- For mathematical operations (adding numbers, multiplying, checking if a number is prime), delegate to math_agent
- For data lookups (weather, timezone, current time in cities), delegate to lookup_agent
- For simple questions, greetings, or general conversation, respond directly

Always be helpful and explain what you're doing when delegating to other agents.
If an agent returns an error, explain the issue to the user clearly.""",
    sub_agents=[math_agent, lookup_agent],
)
```

#### agents/coordinator/__init__.py

```python
from .agent import root_agent
```

### Environment Configuration

#### .env.example

```bash
# Google API Key for Gemini
# Get your key from: https://aistudio.google.com/apikey
GOOGLE_API_KEY=your_google_api_key_here
```

## Implementation Tasks

Execute these tasks in order:

### Task 1: Initialize Project Structure
- Create directory structure as specified
- Create `requirements.txt` with dependencies
- Create `.env.example` and add `.env` to `.gitignore`
- Initialize git repository (optional)

### Task 2: Implement Math Agent (Agent 2)
- Create `agents/math_agent/__init__.py`
- Create `agents/math_agent/agent.py` with:
  - Tool functions: `add_numbers`, `multiply_numbers`, `check_prime`
  - Agent definition with appropriate model, name, description, instruction
  - A2A app creation using `to_a2a()`

### Task 3: Implement Lookup Agent (Agent 3)
- Create `agents/lookup_agent/__init__.py`
- Create `agents/lookup_agent/agent.py` with:
  - Tool functions: `get_weather`, `get_timezone`
  - Simulated data stores for weather and timezone
  - Agent definition with appropriate model, name, description, instruction
  - A2A app creation using `to_a2a()`

### Task 4: Implement Coordinator Agent (Agent 1)
- Create `agents/coordinator/__init__.py`
- Create `agents/coordinator/agent.py` with:
  - Environment variable handling for agent URLs
  - RemoteA2aAgent connections for math_agent and lookup_agent
  - Root agent with clear routing instructions
  - Sub-agents configuration

### Task 5: Create Docker Configuration
- Create `Dockerfile.headless` for math and lookup agents
- Create `Dockerfile.coordinator` for coordinator agent
- Create `docker-compose.yml` with:
  - Three services (coordinator, math_agent, lookup_agent)
  - Proper networking (a2a-network)
  - Health checks for headless agents
  - Dependency ordering (coordinator depends on others)
  - Port mappings (8000, 8001, 8002)

### Task 6: Test Local Development
- Set up `.env` with valid `GOOGLE_API_KEY`
- Test math_agent standalone: `uvicorn agents.math_agent.agent:a2a_app --port 8001`
- Test lookup_agent standalone: `uvicorn agents.lookup_agent.agent:a2a_app --port 8002`
- Test coordinator: `adk web agents/ --port 8000`

### Task 7: Test Docker Deployment
- Build and run: `docker-compose up --build`
- Verify all containers are healthy
- Access coordinator at http://localhost:8000
- Test A2A communication through the web interface

## Validation Gates

### Linting & Type Checking
```bash
# Install dev dependencies
pip install ruff mypy

# Run linter
ruff check agents/

# Run type checker (optional, may need type stubs)
mypy agents/ --ignore-missing-imports
```

### Local Agent Testing
```bash
# Terminal 1: Start math_agent
GOOGLE_API_KEY=your_key uvicorn agents.math_agent.agent:a2a_app --port 8001

# Terminal 2: Start lookup_agent
GOOGLE_API_KEY=your_key uvicorn agents.lookup_agent.agent:a2a_app --port 8002

# Terminal 3: Start coordinator
GOOGLE_API_KEY=your_key adk web agents/ --port 8000

# Verify agent cards are accessible
curl http://localhost:8001/.well-known/agent-card.json
curl http://localhost:8002/.well-known/agent-card.json
```

### Docker Testing
```bash
# Build and start all services
docker-compose up --build

# In another terminal, check health
docker-compose ps

# Test agent cards
curl http://localhost:8001/.well-known/agent-card.json
curl http://localhost:8002/.well-known/agent-card.json

# Access web UI
open http://localhost:8000
```

### Functional Testing (via Web UI at localhost:8000)

Test these queries to verify A2A communication:

| Test Query | Expected Behavior |
|------------|-------------------|
| "Hello" | Direct response from coordinator |
| "Add 5 and 3" | Delegated to math_agent, returns 8 |
| "Is 17 a prime number?" | Delegated to math_agent, returns true |
| "What's the weather in Tokyo?" | Delegated to lookup_agent, returns weather data |
| "What time is it in London?" | Delegated to lookup_agent, returns timezone data |
| "Multiply 7 by 8 and tell me the weather in Paris" | Both agents invoked |

## Known Gotchas & Troubleshooting

### 1. Python Version
ADK v1.19.0+ requires Python 3.10+. Ensure your Dockerfile uses Python 3.10 or higher.

### 2. Agent Card URL Format
The `agent_card` parameter in `RemoteA2aAgent` expects the full URL to the agent card JSON:
```python
# Correct
agent_card="http://math_agent:8001/.well-known/agent-card.json"

# Incorrect
agent_card="http://math_agent:8001"
```

### 3. Docker Networking
Inside Docker, services communicate via service names (e.g., `http://math_agent:8001`), not `localhost`. Environment variables handle this.

### 4. Health Check Dependencies
The coordinator must wait for headless agents to be healthy before starting. The `depends_on` with `condition: service_healthy` handles this.

### 5. GOOGLE_API_KEY
- Must be set in `.env` file
- Used by all three agents for Gemini API access
- Get key from: https://aistudio.google.com/apikey

### 6. Port Conflicts
Default ports are 8000 (coordinator), 8001 (math_agent), 8002 (lookup_agent). Modify docker-compose.yml if these conflict with existing services.

### 7. Model Selection
Using `gemini-2.0-flash` for cost-efficiency. For better reasoning, consider `gemini-2.0-pro` or `gemini-pro-preview`.

## Error Handling Strategy

1. **Agent Connection Failures**: RemoteA2aAgent will throw errors if the remote agent is unreachable. The coordinator's instruction tells it to explain errors clearly to users.

2. **Invalid Inputs**: Tool functions return error dictionaries with status and message fields for graceful handling.

3. **Missing API Key**: Docker-compose validates environment variables are present; agents will fail fast with clear error messages.

## Success Criteria

- [ ] All three agents start successfully in Docker
- [ ] Health checks pass for math_agent and lookup_agent
- [ ] Coordinator web UI accessible at http://localhost:8000
- [ ] Math operations delegated correctly to math_agent
- [ ] Lookup operations delegated correctly to lookup_agent
- [ ] Direct queries handled by coordinator without delegation
- [ ] Agent cards accessible at `.well-known/agent-card.json` endpoints

## PRP Confidence Score: 8/10

**Strengths:**
- Comprehensive architecture documentation
- Clear implementation steps with code examples
- Multiple validation methods (local, Docker)
- Detailed troubleshooting section

**Potential Risks:**
- ADK API may have undocumented behaviors
- Docker health checks may need adjustment based on actual startup times
- `adk web` behavior in Docker container may need testing
- Gemini API rate limits could affect testing

**Mitigation:**
- Start with local testing before Docker
- Use official documentation URLs for reference
- Test incrementally (one agent at a time)
