"""gmail.py — Gmail integration for G_TaskCenter."""

import os
import pickle
import logging
from typing import List, Optional
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from tenacity import retry, wait_exponential, stop_after_attempt

try:
    from models import UnifiedTask, TaskSource, TaskPriority
except ImportError:
    from src.models import UnifiedTask, TaskSource, TaskPriority

logger = logging.getLogger(__name__)

# Scopes needed: Read and modify labels (to archive/mark read)
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    """Build and return a Gmail service object."""
    creds = None
    token_path = os.environ.get("GMAIL_TOKEN_PATH", "credentials/gmail_token.pickle")

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            logger.warning(
                "Gmail credentials not found or invalid. Manual auth required."
            )
            return None

    return build("gmail", "v1", credentials=creds)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _fetch_message_details(service, user_id, msg_id):
    """Fetch message detail with exponential backoff on failure."""
    return service.users().messages().get(userId=user_id, id=msg_id).execute()


def list_task_emails(
    query: str = "label:todo OR label:task OR subject:task AND is:unread",
    limit: int = 20,
) -> List[UnifiedTask]:
    """List emails matching a task-related query, utilizing pagination."""
    service = get_gmail_service()
    if not service:
        return []

    unified_tasks: List[UnifiedTask] = []

    try:
        # Paginating up to the limit
        page_token = None
        messages_fetched = 0

        while messages_fetched < limit:
            results = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    q=query,
                    maxResults=min(limit - messages_fetched, 100),
                    pageToken=page_token,
                )
                .execute()
            )

            messages = results.get("messages", [])
            if not messages:
                break

            for msg in messages:
                if messages_fetched >= limit:
                    break

                m = _fetch_message_details(service, "me", msg["id"])
                headers = m["payload"].get("headers", [])

                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"),
                    "No Subject",
                )
                snippet = m.get("snippet", "")

                # We can deduce priority from subject keywords
                priority = TaskPriority.NORMAL
                if "urgent" in subject.lower() or "asap" in subject.lower():
                    priority = TaskPriority.HIGH

                task = UnifiedTask(
                    id=msg["id"],
                    source=TaskSource.GMAIL,
                    title=subject,
                    snippet=snippet,
                    status="Pending" if "UNREAD" in m.get("labelIds", []) else "Read",
                    priority=priority,
                    link=f"https://mail.google.com/mail/u/0/#inbox/{msg['id']}",
                )
                unified_tasks.append(task)
                messages_fetched += 1

            page_token = results.get("nextPageToken")
            if not page_token:
                break

        return unified_tasks

    except Exception as e:
        logger.error(f"Error listing Gmail tasks: {e}")
        return []


def archive_email_task(msg_id: str) -> bool:
    """Archive an email by removing the INBOX label."""
    service = get_gmail_service()
    if not service:
        return False

    try:
        service.users().messages().modify(
            userId="me", id=msg_id, body={"removeLabelIds": ["INBOX"]}
        ).execute()
        logger.info(f"Successfully archived Gmail task {msg_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to archive Gmail task {msg_id}: {e}")
        return False
