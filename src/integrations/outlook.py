"""outlook.py — Outlook integration for G_TaskCenter."""

import os
import msal
import logging
import requests
from typing import List, Optional

try:
    from models import UnifiedTask, TaskSource, TaskPriority
except ImportError:
    from src.models import UnifiedTask, TaskSource, TaskPriority

logger = logging.getLogger(__name__)

CLIENT_ID = os.environ.get("OUTLOOK_CLIENT_ID")
TENANT_ID = os.environ.get("OUTLOOK_TENANT_ID")
CLIENT_SECRET = os.environ.get("OUTLOOK_CLIENT_SECRET")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/Tasks.ReadWrite"]
CACHE_FILE = os.environ.get("OUTLOOK_TOKEN_CACHE", "credentials/outlook_cache.bin")


def _load_cache():
    """Load the MSAL token cache."""
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache.deserialize(f.read())
    return cache


def _save_cache(cache):
    """Save the MSAL token cache."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())


def get_access_token():
    """Get access token for Microsoft Graph API safely leveraging the cache."""
    if not all([CLIENT_ID, TENANT_ID, CLIENT_SECRET]):
        logger.warning("Outlook credentials not fully provided in env.")
        return None

    cache = _load_cache()
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
        token_cache=cache,
    )

    # Attempt to acquire silently from cache
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])

    if not result:
        # Fallback to daemon token (Client Credentials flow)
        result = app.acquire_token_for_client(scopes=SCOPES)

    _save_cache(cache)
    return result.get("access_token")


def list_outlook_tasks() -> List[UnifiedTask]:
    """List tasks from Outlook using Microsoft Graph API with pagination."""
    token = get_access_token()
    if not token:
        return []

    headers = {"Authorization": f"Bearer {token}"}
    list_url = "https://graph.microsoft.com/v1.0/me/todo/lists"
    unified_tasks: List[UnifiedTask] = []

    try:
        # First get the task lists
        list_resp = requests.get(list_url, headers=headers)
        if list_resp.status_code != 200:
            logger.error(f"Failed to fetch Outlook task lists: {list_resp.text}")
            return []

        lists = list_resp.json().get("value", [])

        for t_list in lists:
            list_id = t_list["id"]
            # Fetch tasks iteratively navigating pagination links
            tasks_url = (
                f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks"
            )

            while tasks_url:
                tasks_resp = requests.get(tasks_url, headers=headers)
                if tasks_resp.status_code == 200:
                    data = tasks_resp.json()
                    tasks = data.get("value", [])

                    for task in tasks:
                        if task["status"] != "completed":
                            priority = TaskPriority.NORMAL
                            if task.get("importance") == "high":
                                priority = TaskPriority.HIGH
                            elif task.get("importance") == "low":
                                priority = TaskPriority.LOW

                            unified_tasks.append(
                                UnifiedTask(
                                    id=task["id"],
                                    source=TaskSource.OUTLOOK,
                                    title=task["title"],
                                    status=task["status"],
                                    priority=priority,
                                    link=f"https://to-do.office.com/tasks/id/{task['id']}",
                                )
                            )

                    tasks_url = data.get("@odata.nextLink", None)
                else:
                    break

        return unified_tasks
    except Exception as e:
        logger.error(f"Error listing Outlook tasks: {e}")
        return []


def complete_outlook_task(list_id: str, task_id: str) -> bool:
    """Mark an Outlook task as completed."""
    token = get_access_token()
    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks/{task_id}"

    try:
        resp = requests.patch(url, headers=headers, json={"status": "completed"})
        return resp.status_code in [200, 204]
    except Exception as e:
        logger.error(f"Failed to complete Outlook task: {e}")
        return False
