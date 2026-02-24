"""mcp_server.py — LEGACY/ALTERNATIVE MCP Server for G_TaskCenter.

NOTE: This is a convenience wrapper with a reduced tool surface (4 read-only tools).
The CANONICAL MCP server is src/server.py, which exposes the full tool set
(10 tools including write operations and n8n workflow automation) with Pydantic
model serialization. Prefer src/server.py for production and MCP registration.

This file is retained for backward compatibility and lightweight read-only usage.
"""

import logging
from typing import List, Optional
from json import dumps
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Import integrations from src/integrations
from src.integrations.gmail import list_task_emails
from src.integrations.notion import list_notion_tasks
from src.integrations.outlook import list_outlook_tasks

# Load environment variables (from .env file)
load_dotenv()

# Initialize FastMCP Server
mcp = FastMCP("g-taskcenter")

logger = logging.getLogger(__name__)

@mcp.lifespan
async def on_startup(server: FastMCP):
    """Initialize startup logic here if needed."""
    logger.info("g-taskcenter MCP server initialized.")
    yield
    logger.info("g-taskcenter MCP server shutdown.")

@mcp.tool()
async def get_all_tasks(source: Optional[str] = None) -> str:
    """
    Fetch and unify tasks from all integrated sources (Gmail, Notion, Outlook).
    
    Args:
        source: Optional filter for source (e.g., 'gmail', 'notion', 'outlook').
    """
    unified_tasks = []
    
    if not source or source.lower() == "gmail":
        gmail_tasks = list_task_emails()
        unified_tasks.extend(gmail_tasks)
        
    if not source or source.lower() == "notion":
        notion_tasks = list_notion_tasks()
        unified_tasks.extend(notion_tasks)
        
    if not source or source.lower() == "outlook":
        outlook_tasks = list_outlook_tasks()
        unified_tasks.extend(outlook_tasks)
        
    if not unified_tasks:
        return "No tasks found or all integrations are unconfigured."
        
    return dumps(unified_tasks, indent=2)

@mcp.tool()
async def list_recent_emails() -> str:
    """Fetch recent task-related emails from Gmail."""
    tasks = list_task_emails()
    if not tasks:
        return "No task-related emails found or Gmail integration unconfigured."
    return dumps(tasks, indent=2)

@mcp.tool()
async def sync_notion_backlog() -> str:
    """List pending tasks from the configured Notion database."""
    tasks = list_notion_tasks()
    if not tasks:
        return "No Notion tasks found or integration unconfigured."
    return dumps(tasks, indent=2)

@mcp.tool()
async def list_outlook_todo() -> str:
    """Fetch pending tasks from Microsoft To-Do/Outlook."""
    tasks = list_outlook_tasks()
    if not tasks:
        return "No Outlook tasks found or integration unconfigured."
    return dumps(tasks, indent=2)

if __name__ == "__main__":
    mcp.run()
