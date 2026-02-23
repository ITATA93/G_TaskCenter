"""notion.py — Notion integration for G_TaskCenter."""

import os
import logging
from typing import List, Optional
from datetime import datetime
from notion_client import Client

try:
    from models import UnifiedTask, TaskSource, TaskPriority
except ImportError:
    from src.models import UnifiedTask, TaskSource, TaskPriority

logger = logging.getLogger(__name__)


def get_notion_client():
    """Return an initialized Notion client."""
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        logger.warning("NOTION_TOKEN not found in environment.")
        return None
    return Client(auth=token)


def _parse_property(prop: dict) -> str:
    """Robust parser for different Notion property types."""
    ptype = prop.get("type")
    if ptype == "title":
        return "".join([t.get("plain_text", "") for t in prop.get("title", [])])
    elif ptype == "rich_text":
        return "".join([t.get("plain_text", "") for t in prop.get("rich_text", [])])
    elif ptype == "select":
        return (
            prop.get("select", {}).get("name", "Unknown")
            if prop.get("select")
            else "Unknown"
        )
    elif ptype == "status":
        return (
            prop.get("status", {}).get("name", "Unknown")
            if prop.get("status")
            else "Unknown"
        )
    elif ptype == "date":
        return prop.get("date", {}).get("start", "") if prop.get("date") else ""
    return str(prop)


def list_notion_tasks(database_id: Optional[str] = None) -> List[UnifiedTask]:
    """List tasks from a specific Notion database using cursor pagination."""
    client = get_notion_client()
    db_id = database_id or os.environ.get("NOTION_TASKS_DB_ID")

    if not client or not db_id:
        return []

    unified_tasks: List[UnifiedTask] = []
    has_more = True
    next_cursor = None

    try:
        while has_more:
            kwargs = {
                "database_id": db_id,
                "filter": {"property": "Status", "select": {"does_not_equal": "Done"}},
            }
            if next_cursor:
                kwargs["start_cursor"] = next_cursor

            results = client.databases.query(**kwargs)

            for page in results.get("results", []):
                props = page.get("properties", {})

                # Finding the actual title property regardless of its name
                title = "Untitled"
                for k, v in props.items():
                    if v.get("type") == "title":
                        title = _parse_property(v)
                        break

                status = _parse_property(props.get("Status", {}))

                raw_priority = _parse_property(props.get("Priority", {})).lower()
                priority = TaskPriority.NORMAL
                if "high" in raw_priority or "urgent" in raw_priority:
                    priority = TaskPriority.HIGH
                elif "low" in raw_priority:
                    priority = TaskPriority.LOW

                date_str = _parse_property(props.get("Due Date", {}))
                due_date = None
                if date_str:
                    try:
                        due_date = datetime.fromisoformat(
                            date_str.replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass

                task = UnifiedTask(
                    id=page["id"],
                    source=TaskSource.NOTION,
                    title=title,
                    status=status,
                    priority=priority,
                    due_date=due_date,
                    link=page.get("url", ""),
                )
                unified_tasks.append(task)

            has_more = results.get("has_more", False)
            next_cursor = results.get("next_cursor")

        return unified_tasks
    except Exception as e:
        logger.error(f"Error listing Notion tasks: {e}")
        return []


def create_task(
    title: str, priority: TaskPriority = TaskPriority.NORMAL
) -> Optional[UnifiedTask]:
    """Create a new task in the configured Notion database."""
    client = get_notion_client()
    db_id = os.environ.get("NOTION_TASKS_DB_ID")

    if not client or not db_id:
        return None

    try:
        new_page = client.pages.create(
            parent={"database_id": db_id},
            properties={
                "Name": {  # Standardizing on Name for creation
                    "title": [{"text": {"content": title}}]
                },
                "Status": {"select": {"name": "Not started"}},
                "Priority": {"select": {"name": priority.capitalize()}},
            },
        )
        return UnifiedTask(
            id=new_page["id"],
            source=TaskSource.NOTION,
            title=title,
            status="Not started",
            priority=priority,
            link=new_page.get("url", ""),
        )
    except Exception as e:
        logger.error(f"Failed to create Notion task: {e}")
        return None
