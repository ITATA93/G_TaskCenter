"""jira.py — Jira integration for G_TaskCenter.

Reads assigned issues from Jira Cloud or Jira Server and exposes them as
UnifiedTask instances. Supports marking issues as done via transition.

Requires:
    - JIRA_BASE_URL: Jira instance URL (e.g., https://myorg.atlassian.net)
    - JIRA_USER_EMAIL: Email for Jira Cloud basic auth
    - JIRA_API_TOKEN: API token (Jira Cloud) or password (Jira Server)
    - JIRA_PROJECT_KEY: (optional) Filter issues to a specific project
    - JIRA_JQL_FILTER: (optional) Custom JQL override

Install:  pip install requests (already in requirements.txt)

Note: This uses the Jira REST API v2/v3 directly via requests rather than
the jira Python library, keeping dependencies minimal.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Protocol

import requests
from requests.auth import HTTPBasicAuth

try:
    from models import UnifiedTask, TaskSource, TaskPriority
except ImportError:
    from src.models import UnifiedTask, TaskSource, TaskPriority

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

JIRA_BASE_URL = os.environ.get("JIRA_BASE_URL", "")
JIRA_USER_EMAIL = os.environ.get("JIRA_USER_EMAIL", "")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "")
JIRA_JQL_FILTER = os.environ.get("JIRA_JQL_FILTER", "")

_JIRA_SOURCE = "jira"

# Map Jira priority names to TaskPriority
_JIRA_PRIORITY_MAP: Dict[str, TaskPriority] = {
    "highest": TaskPriority.HIGH,
    "high": TaskPriority.HIGH,
    "medium": TaskPriority.NORMAL,
    "low": TaskPriority.LOW,
    "lowest": TaskPriority.LOW,
}


# ---------------------------------------------------------------------------
# Typed Interface (Protocol)
# ---------------------------------------------------------------------------


class JiraTaskSource(Protocol):
    """Protocol defining the contract for Jira-based task sources."""

    def list_tasks(self, limit: int = 50) -> List[UnifiedTask]:
        """Fetch issues assigned to the current user from Jira."""
        ...

    def transition_issue(self, issue_key: str, transition_name: str) -> bool:
        """Move a Jira issue to a new status via workflow transition."""
        ...


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _jira_auth() -> Optional[HTTPBasicAuth]:
    """Build HTTP Basic auth for Jira REST API."""
    if not JIRA_USER_EMAIL or not JIRA_API_TOKEN:
        return None
    return HTTPBasicAuth(JIRA_USER_EMAIL, JIRA_API_TOKEN)


def _jira_headers() -> Dict[str, str]:
    """Standard headers for Jira REST API requests."""
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _build_jql() -> str:
    """Build the JQL query for fetching assigned incomplete issues."""
    if JIRA_JQL_FILTER:
        return JIRA_JQL_FILTER

    parts = ["assignee = currentUser()", "statusCategory != Done"]
    if JIRA_PROJECT_KEY:
        parts.append(f"project = {JIRA_PROJECT_KEY}")

    return " AND ".join(parts) + " ORDER BY priority DESC, updated DESC"


def _parse_due_date(fields: dict) -> Optional[datetime]:
    """Parse Jira duedate field to datetime."""
    raw = fields.get("duedate")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _parse_priority(fields: dict) -> TaskPriority:
    """Map Jira priority to TaskPriority enum."""
    prio = fields.get("priority", {})
    name = (prio.get("name", "") if isinstance(prio, dict) else "").lower()
    return _JIRA_PRIORITY_MAP.get(name, TaskPriority.NORMAL)


# ---------------------------------------------------------------------------
# Public API (implements JiraTaskSource protocol)
# ---------------------------------------------------------------------------


def list_jira_tasks(limit: int = 50) -> List[UnifiedTask]:
    """Fetch issues assigned to the authenticated user from Jira.

    Uses JQL to filter for non-Done issues in the configured project.
    Supports pagination via Jira's startAt/maxResults parameters.

    Args:
        limit: Maximum number of tasks to return.

    Returns:
        List of UnifiedTask instances sourced from Jira.
    """
    if not JIRA_BASE_URL:
        logger.warning("JIRA_BASE_URL not set. Jira integration disabled.")
        return []

    auth = _jira_auth()
    if auth is None:
        logger.warning("Jira credentials incomplete. Set JIRA_USER_EMAIL and JIRA_API_TOKEN.")
        return []

    jql = _build_jql()
    url = f"{JIRA_BASE_URL.rstrip('/')}/rest/api/2/search"
    tasks: List[UnifiedTask] = []
    start_at = 0
    page_size = min(limit, 50)

    while len(tasks) < limit:
        try:
            resp = requests.get(
                url,
                headers=_jira_headers(),
                auth=auth,
                params={
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": page_size,
                    "fields": "summary,status,priority,duedate,description",
                },
            )

            if resp.status_code != 200:
                logger.error("Jira API error (%d): %s", resp.status_code, resp.text[:300])
                break

            data = resp.json()
            issues = data.get("issues", [])
            if not issues:
                break

            for issue in issues:
                if len(tasks) >= limit:
                    break

                fields = issue.get("fields", {})
                key = issue.get("key", issue.get("id", ""))
                summary = fields.get("summary", "Untitled")
                status_name = fields.get("status", {}).get("name", "Unknown")
                description = fields.get("description") or ""

                task = UnifiedTask(
                    id=f"jira-{key}",
                    source=_JIRA_SOURCE,
                    title=summary,
                    snippet=description[:300] if description else None,
                    status=status_name,
                    priority=_parse_priority(fields),
                    due_date=_parse_due_date(fields),
                    link=f"{JIRA_BASE_URL.rstrip('/')}/browse/{key}",
                )
                tasks.append(task)

            # Pagination
            total = data.get("total", 0)
            start_at += len(issues)
            if start_at >= total:
                break

        except Exception as exc:
            logger.error("Error fetching Jira tasks: %s", exc)
            break

    logger.info("Retrieved %d task(s) from Jira.", len(tasks))
    return tasks


def transition_jira_issue(issue_key: str, transition_name: str = "Done") -> bool:
    """Transition a Jira issue to a new status (e.g., 'Done', 'In Progress').

    Finds the matching transition by name and executes it.

    Args:
        issue_key: Jira issue key (e.g., 'PROJ-123').
        transition_name: Target transition/status name.

    Returns:
        True if the transition was executed successfully.
    """
    if not JIRA_BASE_URL:
        return False

    auth = _jira_auth()
    if auth is None:
        return False

    # Strip the local prefix if present
    clean_key = issue_key.replace("jira-", "")
    transitions_url = f"{JIRA_BASE_URL.rstrip('/')}/rest/api/2/issue/{clean_key}/transitions"

    try:
        # 1. Get available transitions
        resp = requests.get(
            transitions_url,
            headers=_jira_headers(),
            auth=auth,
        )
        if resp.status_code != 200:
            logger.error("Failed to fetch transitions for %s: %s", clean_key, resp.text[:200])
            return False

        transitions = resp.json().get("transitions", [])
        target = next(
            (t for t in transitions if t["name"].lower() == transition_name.lower()),
            None,
        )

        if not target:
            available = [t["name"] for t in transitions]
            logger.warning(
                "Transition '%s' not found for %s. Available: %s",
                transition_name,
                clean_key,
                available,
            )
            return False

        # 2. Execute the transition
        resp = requests.post(
            transitions_url,
            headers=_jira_headers(),
            auth=auth,
            json={"transition": {"id": target["id"]}},
        )

        if resp.status_code in (200, 204):
            logger.info("Transitioned %s to '%s'.", clean_key, transition_name)
            return True
        else:
            logger.error("Transition failed for %s: %s", clean_key, resp.text[:200])
            return False

    except Exception as exc:
        logger.error("Error transitioning Jira issue %s: %s", clean_key, exc)
        return False
