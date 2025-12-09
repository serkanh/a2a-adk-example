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
# AGENT_HOST is the hostname used in agent card URL (for Docker networking)
AGENT_HOST = os.environ.get("AGENT_HOST", "localhost")
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
    },
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
# http_url sets the URL in the agent card for Docker networking
a2a_server = A2AServer(
    agent=strands_agent,
    host=HOST,
    port=PORT,
    http_url=f"http://{AGENT_HOST}:{PORT}",
)

# Expose FastAPI app for uvicorn
app = a2a_server.to_fastapi_app()

if __name__ == "__main__":
    # Direct execution (for local testing)
    a2a_server.serve()
