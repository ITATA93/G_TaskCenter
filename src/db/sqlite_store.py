"""sqlite_store.py — SQLite persistence layer for G_TaskCenter.

Provides local storage for unified tasks, source metadata, and
synchronization logs. This enables offline mode and historical queries
without re-fetching from remote APIs.

Schema:
    tasks      — Canonical task records (mirrors UnifiedTask fields).
    sources    — Registered integration sources and their last-sync time.
    sync_log   — Append-only log of sync operations for auditability.

The default database path is ``data/taskcenter.db`` relative to the project
root. Override via the ``TASKCENTER_DB_PATH`` environment variable.
"""

import os
import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Dict, Generator, List, Optional

try:
    from models import UnifiedTask, TaskPriority
except ImportError:
    from src.models import UnifiedTask, TaskPriority

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_DB_PATH = os.environ.get(
    "TASKCENTER_DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "taskcenter.db"),
)

# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id              TEXT    PRIMARY KEY,
    source          TEXT    NOT NULL,
    title           TEXT    NOT NULL,
    snippet         TEXT,
    status          TEXT    NOT NULL DEFAULT 'Pending',
    priority        TEXT    NOT NULL DEFAULT 'normal',
    due_date        TEXT,
    link            TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sources (
    name            TEXT    PRIMARY KEY,
    enabled         INTEGER NOT NULL DEFAULT 1,
    last_sync_at    TEXT,
    config_json     TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sync_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT    NOT NULL,
    operation       TEXT    NOT NULL,
    task_count      INTEGER NOT NULL DEFAULT 0,
    status          TEXT    NOT NULL DEFAULT 'success',
    message         TEXT,
    timestamp       TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_source ON tasks(source);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_sync_log_source ON sync_log(source);
CREATE INDEX IF NOT EXISTS idx_sync_log_timestamp ON sync_log(timestamp);
"""

# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------


def init_db(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Initialize the SQLite database and create tables if needed.

    Args:
        db_path: Path to the SQLite file. Defaults to TASKCENTER_DB_PATH
                 env var or ``data/taskcenter.db``.

    Returns:
        An open sqlite3.Connection with WAL mode enabled.
    """
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(_SCHEMA_SQL)
    conn.commit()

    logger.info("Database initialized at %s", path)
    return conn


@contextmanager
def get_connection(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager that yields an initialized DB connection.

    Usage::

        with get_connection() as conn:
            save_task(conn, task)
    """
    conn = init_db(db_path)
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Task CRUD
# ---------------------------------------------------------------------------


def save_task(conn: sqlite3.Connection, task: UnifiedTask) -> None:
    """Insert or update a task in the database.

    Uses INSERT OR REPLACE to upsert. The ``updated_at`` timestamp is
    refreshed on every write.

    Args:
        conn: Open SQLite connection.
        task: UnifiedTask instance to persist.
    """
    now = datetime.now(timezone.utc).isoformat()
    due = task.due_date.isoformat() if task.due_date else None

    conn.execute(
        """
        INSERT OR REPLACE INTO tasks
            (id, source, title, snippet, status, priority, due_date, link, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task.id,
            task.source,
            task.title,
            task.snippet,
            task.status,
            task.priority,
            due,
            task.link,
            now,
        ),
    )
    conn.commit()


def save_tasks(conn: sqlite3.Connection, tasks: List[UnifiedTask]) -> int:
    """Batch-save multiple tasks.

    Args:
        conn: Open SQLite connection.
        tasks: List of UnifiedTask instances.

    Returns:
        Number of tasks saved.
    """
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for t in tasks:
        due = t.due_date.isoformat() if t.due_date else None
        rows.append((t.id, t.source, t.title, t.snippet, t.status, t.priority, due, t.link, now))

    conn.executemany(
        """
        INSERT OR REPLACE INTO tasks
            (id, source, title, snippet, status, priority, due_date, link, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    return len(rows)


def get_tasks(
    conn: sqlite3.Connection,
    source: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[UnifiedTask]:
    """Retrieve tasks from the database with optional filters.

    Args:
        conn: Open SQLite connection.
        source: Filter by source (e.g., 'gmail', 'notion').
        status: Filter by status string.
        limit: Maximum number of records to return.

    Returns:
        List of UnifiedTask instances.
    """
    query = "SELECT * FROM tasks WHERE 1=1"
    params: list = []

    if source:
        query += " AND source = ?"
        params.append(source)
    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)

    cursor = conn.execute(query, params)
    tasks: List[UnifiedTask] = []

    for row in cursor.fetchall():
        due_date = None
        if row["due_date"]:
            try:
                due_date = datetime.fromisoformat(row["due_date"])
            except (ValueError, TypeError):
                pass

        task = UnifiedTask(
            id=row["id"],
            source=row["source"],
            title=row["title"],
            snippet=row["snippet"],
            status=row["status"],
            priority=row["priority"],
            due_date=due_date,
            link=row["link"],
        )
        tasks.append(task)

    return tasks


def delete_task(conn: sqlite3.Connection, task_id: str) -> bool:
    """Delete a task by ID.

    Returns:
        True if a row was deleted.
    """
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Source management
# ---------------------------------------------------------------------------


def register_source(
    conn: sqlite3.Connection,
    name: str,
    enabled: bool = True,
    config_json: Optional[str] = None,
) -> None:
    """Register or update an integration source.

    Args:
        conn: Open SQLite connection.
        name: Source identifier (e.g., 'gmail', 'slack').
        enabled: Whether the source is active.
        config_json: Optional JSON string with source-specific config.
    """
    conn.execute(
        """
        INSERT OR REPLACE INTO sources (name, enabled, config_json)
        VALUES (?, ?, ?)
        """,
        (name, int(enabled), config_json),
    )
    conn.commit()


def get_sources(conn: sqlite3.Connection) -> List[Dict]:
    """List all registered sources."""
    cursor = conn.execute("SELECT * FROM sources ORDER BY name")
    return [dict(row) for row in cursor.fetchall()]


# ---------------------------------------------------------------------------
# Sync log
# ---------------------------------------------------------------------------


def mark_synced(
    conn: sqlite3.Connection,
    source: str,
    operation: str,
    task_count: int,
    status: str = "success",
    message: Optional[str] = None,
) -> None:
    """Record a sync operation in the log and update the source's last_sync_at.

    Args:
        conn: Open SQLite connection.
        source: Source name (e.g., 'gmail').
        operation: Description of the operation (e.g., 'pull', 'push', 'full_sync').
        task_count: Number of tasks processed.
        status: 'success' or 'error'.
        message: Optional details / error message.
    """
    now = datetime.now(timezone.utc).isoformat()

    conn.execute(
        """
        INSERT INTO sync_log (source, operation, task_count, status, message, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (source, operation, task_count, status, message, now),
    )

    # Update source last_sync_at
    conn.execute(
        "UPDATE sources SET last_sync_at = ? WHERE name = ?",
        (now, source),
    )
    conn.commit()


def get_sync_log(
    conn: sqlite3.Connection,
    source: Optional[str] = None,
    limit: int = 50,
) -> List[Dict]:
    """Retrieve recent sync log entries.

    Args:
        conn: Open SQLite connection.
        source: Optional filter by source.
        limit: Maximum entries to return.

    Returns:
        List of log entry dicts.
    """
    query = "SELECT * FROM sync_log"
    params: list = []

    if source:
        query += " WHERE source = ?"
        params.append(source)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor = conn.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]
