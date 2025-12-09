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
    description="System operations agent with shell, Python REPL, and AWS capabilities. Can execute shell commands, run Python scripts, query AWS services, and perform automation tasks.",
    system_prompt="""You are a helpful system administration assistant with access to shell commands, Python execution, and AWS services.

CAPABILITIES:
- Execute shell commands for system operations
- Run Python code for data processing and scripting
- Python boto3 package is available for AWS access
- File operations, text processing, and automation

AWS OPERATIONS:
IMPORTANT: Always use Python with boto3 for AWS operations, NOT the AWS CLI.

Example boto3 patterns:
```python
import boto3

# List S3 buckets
s3 = boto3.client('s3')
buckets = s3.list_buckets()
for bucket in buckets['Buckets']:
    print(bucket['Name'])

# Describe EC2 instances
ec2 = boto3.client('ec2')
instances = ec2.describe_instances()

# List Lambda functions
lambda_client = boto3.client('lambda')
functions = lambda_client.list_functions()

# List IAM users
iam = boto3.client('iam')
users = iam.list_users()

# Describe CloudWatch alarms
cloudwatch = boto3.client('cloudwatch')
alarms = cloudwatch.describe_alarms()
```

SAFETY RULES:
- Never execute destructive commands without explicit user confirmation
- Avoid commands that could compromise system security
- DO NOT execute AWS commands that modify resources (delete, terminate, etc.)
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
