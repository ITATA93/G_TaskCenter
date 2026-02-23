"""server.py — Official MCP local server for G_TaskCenter."""

import logging
from typing import List, Any
from dotenv import load_dotenv
from fastmcp import FastMCP

try:
    from models import UnifiedTask, TaskPriority
    from integrations.notion import list_notion_tasks, create_task
    from integrations.outlook import list_outlook_tasks, complete_outlook_task
    from integrations.gmail import list_task_emails, archive_email_task
    from integrations.n8n import (
        get_workflows,
        activate_workflow,
        test_execute_workflow,
        get_execution_status,
    )
except ImportError:
    from src.models import UnifiedTask, TaskPriority
    from src.integrations.notion import list_notion_tasks, create_task
    from src.integrations.outlook import list_outlook_tasks, complete_outlook_task
    from src.integrations.gmail import list_task_emails, archive_email_task
    from src.integrations.n8n import (
        get_workflows,
        activate_workflow,
        test_execute_workflow,
        get_execution_status,
    )

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("g_taskcenter_server")

# Initialize Server
mcp = FastMCP("G_TaskCenter")

# --- READ TOOLS ---


@mcp.tool()
def list_unified_tasks() -> List[dict]:
    """
    List all pending tasks from Notion, Outlook, and Gmail in a unified format.
    """
    logger.info("Fetching unified tasks from all configured sources...")
    unified_tasks: List[UnifiedTask] = []

    # 1. Notion
    notion_tasks = list_notion_tasks()
    unified_tasks.extend(notion_tasks)

    # 2. Outlook
    outlook_tasks = list_outlook_tasks()
    unified_tasks.extend(outlook_tasks)

    # 3. Gmail
    gmail_tasks = list_task_emails()
    unified_tasks.extend(gmail_tasks)

    # Serialize Pydantic objects for MCP consumption
    return [task.model_dump() for task in unified_tasks]


@mcp.tool()
def get_source_tasks(source: str) -> List[dict]:
    """Retrieve tasks from a specific service ('notion', 'outlook', or 'gmail')."""
    tasks: List[UnifiedTask] = []
    if source.lower() == "notion":
        tasks = list_notion_tasks()
    elif source.lower() == "outlook":
        tasks = list_outlook_tasks()
    elif source.lower() == "gmail":
        tasks = list_task_emails()
    return [t.model_dump() for t in tasks]


# --- WRITE / MUTATION TOOLS ---


@mcp.tool()
def create_notion_task(title: str, priority_level: str = "normal") -> dict:
    """Create a new task in Notion."""
    try:
        priority = TaskPriority(priority_level.lower())
    except ValueError:
        priority = TaskPriority.NORMAL

    task = create_task(title, priority)
    return task.model_dump() if task else {"error": "Failed to create task."}


@mcp.tool()
def complete_task_in_outlook(list_id: str, task_id: str) -> str:
    """Mark a task as complete in Outlook to-do."""
    success = complete_outlook_task(list_id, task_id)
    return "Task marked as complete" if success else "Failed to complete task"


@mcp.tool()
def archive_gmail(msg_id: str) -> str:
    """Archive an email in Gmail related to a task."""
    success = archive_email_task(msg_id)
    return "Email archived successfully" if success else "Failed to archive email"


# --- N8N WORKFLOW AUTOMATION TOOLS ---


@mcp.tool()
def list_n8n_workflows() -> List[dict]:
    """Retrieve all configured workflows from the linked n8n instance."""
    return get_workflows()


@mcp.tool()
def toggle_n8n_workflow(workflow_id: str, active: bool) -> str:
    """Enable or disable an n8n workflow."""
    success = activate_workflow(workflow_id, active)
    state_str = "activated" if active else "deactivated"
    return (
        f"Workflow {workflow_id} {state_str} successfully"
        if success
        else f"Failed to modify workflow {workflow_id}"
    )


@mcp.tool()
def test_n8n_workflow(workflow_id: str, payload_json: str = "{}") -> dict:
    """Trigger a manual execution of an n8n workflow for testing purposes."""
    import json

    try:
        payload = json.loads(payload_json)
    except:
        payload = {}
    return test_execute_workflow(workflow_id, payload)


@mcp.tool()
def check_n8n_execution(execution_id: str) -> dict:
    """Get the result or status of a specific n8n execution."""
    return get_execution_status(execution_id)


if __name__ == "__main__":
    # Start the MCP server via stdio transport
    mcp.run()
