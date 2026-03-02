"""slack.py — Slack integration for G_TaskCenter.

Reads task-like messages from Slack channels (starred messages, messages with
specific reactions, or messages matching keyword filters) and exposes them
as UnifiedTask instances.

Requires:
    - SLACK_BOT_TOKEN: Bot User OAuth Token (xoxb-...) with scopes:
        channels:history, channels:read, reactions:read, stars:read, users:read
    - SLACK_TASK_CHANNELS: Comma-separated channel IDs to monitor (optional,
        defaults to all public channels the bot is in).
    - SLACK_TASK_REACTION: Reaction emoji name that marks a message as a task
        (default: "white_check_mark").

Install:  pip install slack_sdk
"""

import os
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Protocol

import requests

try:
    from models import UnifiedTask, TaskSource, TaskPriority
except ImportError:
    from src.models import UnifiedTask, TaskSource, TaskPriority

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_TASK_CHANNELS = os.environ.get("SLACK_TASK_CHANNELS", "")
SLACK_TASK_REACTION = os.environ.get("SLACK_TASK_REACTION", "white_check_mark")
SLACK_API_BASE = "https://slack.com/api"


# ---------------------------------------------------------------------------
# TaskSource extension — add SLACK to the enum at runtime only if not present
# ---------------------------------------------------------------------------

# Since TaskSource is a StrEnum in models.py, we reference "slack" directly
# as the source value. The UnifiedTask model uses use_enum_values = True,
# so raw strings are accepted.
_SLACK_SOURCE = "slack"


# ---------------------------------------------------------------------------
# Typed Interface (Protocol)
# ---------------------------------------------------------------------------


class SlackTaskSource(Protocol):
    """Protocol defining the contract for Slack-based task sources."""

    def list_tasks(self, limit: int = 50) -> List[UnifiedTask]:
        """Fetch task-like messages from Slack."""
        ...

    def mark_task_done(self, channel_id: str, message_ts: str) -> bool:
        """React to a message indicating the task is resolved."""
        ...


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slack_headers() -> Dict[str, str]:
    """Build auth headers for Slack Web API."""
    return {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
    }


def _get_channel_ids() -> List[str]:
    """Return configured channel IDs, or discover public channels the bot is in."""
    if SLACK_TASK_CHANNELS:
        return [c.strip() for c in SLACK_TASK_CHANNELS.split(",") if c.strip()]

    # Auto-discover channels the bot has joined
    try:
        resp = requests.get(
            f"{SLACK_API_BASE}/conversations.list",
            headers=_slack_headers(),
            params={"types": "public_channel", "limit": 200},
        )
        data = resp.json()
        if data.get("ok"):
            return [ch["id"] for ch in data.get("channels", []) if ch.get("is_member")]
    except Exception as exc:
        logger.error("Failed to list Slack channels: %s", exc)
    return []


def _ts_to_datetime(ts: str) -> Optional[datetime]:
    """Convert a Slack message timestamp to a Python datetime."""
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc)
    except (ValueError, TypeError):
        return None


def _extract_priority(text: str) -> TaskPriority:
    """Infer priority from message text keywords."""
    lower = text.lower()
    if any(kw in lower for kw in ("urgent", "asap", "critical", "blocker")):
        return TaskPriority.HIGH
    if any(kw in lower for kw in ("low priority", "nice to have", "whenever")):
        return TaskPriority.LOW
    return TaskPriority.NORMAL


# ---------------------------------------------------------------------------
# Public API (implements SlackTaskSource protocol)
# ---------------------------------------------------------------------------


def list_slack_tasks(limit: int = 50) -> List[UnifiedTask]:
    """Fetch messages with the task reaction from monitored Slack channels.

    This implementation searches channel histories for messages that have
    the configured reaction emoji (default: ``white_check_mark``), treating
    each such message as a pending task.

    Args:
        limit: Maximum number of tasks to return across all channels.

    Returns:
        List of UnifiedTask instances sourced from Slack.
    """
    if not SLACK_BOT_TOKEN:
        logger.warning("SLACK_BOT_TOKEN not set. Slack integration disabled.")
        return []

    channels = _get_channel_ids()
    if not channels:
        logger.info("No Slack channels configured or discoverable.")
        return []

    tasks: List[UnifiedTask] = []

    for channel_id in channels:
        if len(tasks) >= limit:
            break

        try:
            # Fetch recent messages
            resp = requests.get(
                f"{SLACK_API_BASE}/conversations.history",
                headers=_slack_headers(),
                params={"channel": channel_id, "limit": min(limit * 2, 200)},
            )
            data = resp.json()
            if not data.get("ok"):
                logger.warning("Slack API error for channel %s: %s", channel_id, data.get("error"))
                continue

            for msg in data.get("messages", []):
                if len(tasks) >= limit:
                    break

                # Check if message has the task reaction
                reactions = msg.get("reactions", [])
                has_task_reaction = any(
                    r.get("name") == SLACK_TASK_REACTION for r in reactions
                )

                if not has_task_reaction:
                    continue

                text = msg.get("text", "")
                title = text[:120] + ("..." if len(text) > 120 else "")
                ts = msg.get("ts", "")

                task = UnifiedTask(
                    id=f"slack-{channel_id}-{ts}",
                    source=_SLACK_SOURCE,
                    title=title,
                    snippet=text[:300] if len(text) > 120 else None,
                    status="Pending",
                    priority=_extract_priority(text),
                    due_date=_ts_to_datetime(ts),
                    link=f"https://app.slack.com/client/{channel_id}/p{ts.replace('.', '')}",
                )
                tasks.append(task)

        except Exception as exc:
            logger.error("Error fetching Slack tasks from channel %s: %s", channel_id, exc)

    logger.info("Retrieved %d task(s) from Slack.", len(tasks))
    return tasks


def mark_slack_task_done(channel_id: str, message_ts: str) -> bool:
    """Add a 'done' reaction to a Slack message, signaling task completion.

    Args:
        channel_id: Slack channel ID.
        message_ts: Message timestamp (e.g., '1234567890.123456').

    Returns:
        True if the reaction was added successfully.
    """
    if not SLACK_BOT_TOKEN:
        return False

    try:
        resp = requests.post(
            f"{SLACK_API_BASE}/reactions.add",
            headers=_slack_headers(),
            json={
                "channel": channel_id,
                "name": "heavy_check_mark",
                "timestamp": message_ts,
            },
        )
        data = resp.json()
        if data.get("ok"):
            logger.info("Marked Slack task done: %s/%s", channel_id, message_ts)
            return True
        else:
            logger.warning("Failed to mark Slack task done: %s", data.get("error"))
            return False
    except Exception as exc:
        logger.error("Error marking Slack task done: %s", exc)
        return False
