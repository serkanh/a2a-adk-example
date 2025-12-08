"""ADK API server with PostgreSQL DatabaseSessionService (headless, no web UI)."""

import os
from google.adk.cli.fast_api import get_fast_api_app

# Read PostgreSQL connection details from environment variables
db_user = os.getenv("POSTGRES_USER", "postgres")
db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
db_host = os.getenv("POSTGRES_HOST", "localhost")
db_port = os.getenv("POSTGRES_PORT", "5432")
db_name = os.getenv("POSTGRES_DB", "adk_sessions")

# Construct the async SQLAlchemy connection string (asyncpg driver)
db_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create FastAPI app with DatabaseSessionService but NO web UI
# Exposes API endpoints: /run, /run_sse, /apps/{app_name}/users/{user_id}/sessions/{session_id}
app = get_fast_api_app(
    agents_dir="/app/agents",
    session_service_uri=db_url,
    allow_origins=["*"],
    web=False,
)
