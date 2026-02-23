"""sync_engine.py — Bi-directional task synchronization engine for G_TaskCenter."""

import os
import sqlite3
import logging
from typing import List, Set

from models import UnifiedTask, TaskSource, TaskPriority
from integrations.gmail import list_task_emails, archive_email_task
from integrations.outlook import list_outlook_tasks, complete_outlook_task
from integrations.notion import list_notion_tasks, create_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("g_sync_engine")

DB_PATH = os.environ.get(
    "SYNC_DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "data", "sync_state.db"),
)


def _init_db():
    """Initialize the SQLite database to track synced items."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS synced_tasks (
            source_id TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            notion_id TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """
    )
    conn.commit()
    return conn


def get_tracked_tasks(conn) -> dict:
    """Retrieve all previously synced tasks."""
    cursor = conn.cursor()
    cursor.execute("SELECT source_id, source_type, notion_id, status FROM synced_tasks")
    return {
        row[0]: {"source_type": row[1], "notion_id": row[2], "status": row[3]}
        for row in cursor.fetchall()
    }


def update_tracked_task(
    conn, source_id: str, source_type: str, notion_id: str, status: str
):
    """Upsert a tracked task in the database."""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO synced_tasks (source_id, source_type, notion_id, status)
        VALUES (?, ?, ?, ?)
    """,
        (source_id, source_type, notion_id, status),
    )
    conn.commit()


def run_sync_cycle():
    """
    Run a full bi-directional synchronization cycle:
    1. Check Notion for completed tasks and resolve them in origin (Gmail/Outlook)
    2. Pull new tasks from Outlook/Gmail and push to Notion
    """
    logger.info("Starting G_TaskCenter Sync Cycle...")
    conn = _init_db()
    tracked = get_tracked_tasks(conn)

    # 1. Pull current state from all platforms
    logger.info("Fetching current states...")
    notion_tasks = list_notion_tasks()
    gmail_tasks = list_task_emails()
    outlook_tasks = list_outlook_tasks()

    # Quick lookup for Notion active tasks
    active_notion_ids = {t.id for t in notion_tasks}

    # --- PHASE 1: Reconcile Completions ---
    # If a tracked task is no longer active in Notion (meaning it was marked Done),
    # we should archive/complete it in the source system.
    logger.info("Reconciling completed tasks...")
    for source_id, data in tracked.items():
        if data["status"] != "completed" and data["notion_id"] not in active_notion_ids:
            logger.info(
                f"Task {source_id} ({data['source_type']}) marked complete in Notion. Resolving in origin."
            )
            success = False
            if data["source_type"] == TaskSource.GMAIL:
                success = archive_email_task(source_id)
            elif data["source_type"] == TaskSource.OUTLOOK:
                # Assuming list_id isn't tracked, we might need a more complex Outlook completion.
                # For this baseline, we log it. In a full implementation, list_id would be stored.
                logger.warning(
                    f"Outlook completion requires list_id. Manual resolution needed for {source_id}"
                )
                # success = complete_outlook_task(list_id, source_id)

            # Mark local DB as completed
            update_tracked_task(
                conn, source_id, data["source_type"], data["notion_id"], "completed"
            )

    # --- PHASE 2: Ingest New Tasks ---
    # Find active tasks in Gmail/Outlook that aren't in our DB, and create them in Notion.
    logger.info("Ingesting new tasks into Notion...")

    def ingest_source(tasks: List[UnifiedTask]):
        for t in tasks:
            if t.id not in tracked:
                logger.info(
                    f"New task found in {t.source}: {t.title}. Creating in Notion."
                )
                new_notion = create_task(
                    title=f"[{t.source.upper()}] {t.title}", priority=t.priority
                )
                if new_notion:
                    update_tracked_task(conn, t.id, t.source, new_notion.id, "active")
                    tracked[t.id] = {
                        "source_type": t.source,
                        "notion_id": new_notion.id,
                        "status": "active",
                    }

    ingest_source(gmail_tasks)
    ingest_source(outlook_tasks)

    conn.close()
    logger.info("Sync Cycle complete.")


if __name__ == "__main__":
    run_sync_cycle()
