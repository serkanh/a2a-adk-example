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
