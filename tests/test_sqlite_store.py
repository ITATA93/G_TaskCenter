"""test_sqlite_store.py — Tests for src/db/sqlite_store.py.

Uses in-memory and temporary SQLite databases. No external services required.
"""

import os
import sys
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone

# Ensure src/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models import UnifiedTask, TaskSource, TaskPriority
from db.sqlite_store import (
    init_db,
    get_connection,
    save_task,
    save_tasks,
    get_tasks,
    delete_task,
    register_source,
    get_sources,
    mark_synced,
    get_sync_log,
)


def _make_task(
    id: str = "test-001",
    source: str = "gmail",
    title: str = "Test task",
    status: str = "Pending",
    priority: str = "normal",
    due_date: datetime = None,
    snippet: str = None,
    link: str = None,
) -> UnifiedTask:
    return UnifiedTask(
        id=id,
        source=source,
        title=title,
        status=status,
        priority=priority,
        due_date=due_date,
        snippet=snippet,
        link=link,
    )


class TestInitDb(unittest.TestCase):
    """Tests for init_db() schema creation."""

    def test_creates_tables(self):
        """init_db creates tasks, sources, and sync_log tables."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            conn = init_db(db_path)

            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = sorted([row["name"] for row in cursor.fetchall()])

            self.assertIn("tasks", tables)
            self.assertIn("sources", tables)
            self.assertIn("sync_log", tables)
            conn.close()

    def test_idempotent(self):
        """init_db can be called multiple times without error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            conn1 = init_db(db_path)
            conn1.close()
            conn2 = init_db(db_path)
            conn2.close()


class TestTaskCRUD(unittest.TestCase):
    """Tests for save_task, save_tasks, get_tasks, delete_task."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.conn = init_db(self.db_path)

    def tearDown(self):
        self.conn.close()

    def test_save_and_retrieve_task(self):
        """save_task persists a task; get_tasks retrieves it."""
        task = _make_task(
            id="gmail-001",
            title="Reply to Alice",
            source="gmail",
            priority="high",
            snippet="Urgent reply needed",
            link="https://mail.google.com/001",
        )
        save_task(self.conn, task)

        results = get_tasks(self.conn)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "gmail-001")
        self.assertEqual(results[0].title, "Reply to Alice")
        self.assertEqual(results[0].priority, "high")
        self.assertEqual(results[0].snippet, "Urgent reply needed")

    def test_save_task_upsert(self):
        """save_task updates an existing task on conflict."""
        task_v1 = _make_task(id="t1", title="Version 1")
        save_task(self.conn, task_v1)

        task_v2 = _make_task(id="t1", title="Version 2 updated")
        save_task(self.conn, task_v2)

        results = get_tasks(self.conn)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Version 2 updated")

    def test_save_tasks_batch(self):
        """save_tasks inserts multiple tasks."""
        tasks = [
            _make_task(id=f"t{i}", title=f"Task {i}") for i in range(5)
        ]
        count = save_tasks(self.conn, tasks)
        self.assertEqual(count, 5)

        results = get_tasks(self.conn)
        self.assertEqual(len(results), 5)

    def test_get_tasks_filter_by_source(self):
        """get_tasks filters by source."""
        save_task(self.conn, _make_task(id="g1", source="gmail", title="Gmail task"))
        save_task(self.conn, _make_task(id="n1", source="notion", title="Notion task"))

        gmail_tasks = get_tasks(self.conn, source="gmail")
        self.assertEqual(len(gmail_tasks), 1)
        self.assertEqual(gmail_tasks[0].source, "gmail")

    def test_get_tasks_filter_by_status(self):
        """get_tasks filters by status."""
        save_task(self.conn, _make_task(id="t1", status="Pending"))
        save_task(self.conn, _make_task(id="t2", status="Done"))

        pending = get_tasks(self.conn, status="Pending")
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].id, "t1")

    def test_get_tasks_limit(self):
        """get_tasks respects the limit parameter."""
        for i in range(20):
            save_task(self.conn, _make_task(id=f"t{i}", title=f"Task {i}"))

        results = get_tasks(self.conn, limit=5)
        self.assertEqual(len(results), 5)

    def test_delete_task(self):
        """delete_task removes a task by ID."""
        save_task(self.conn, _make_task(id="to-delete"))
        self.assertTrue(delete_task(self.conn, "to-delete"))
        self.assertEqual(len(get_tasks(self.conn)), 0)

    def test_delete_nonexistent_task(self):
        """delete_task returns False when task doesn't exist."""
        self.assertFalse(delete_task(self.conn, "nonexistent"))

    def test_task_with_due_date(self):
        """save_task and get_tasks handle due_date correctly."""
        due = datetime(2026, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        save_task(self.conn, _make_task(id="dated", due_date=due))

        results = get_tasks(self.conn)
        self.assertEqual(len(results), 1)
        self.assertIsNotNone(results[0].due_date)
        self.assertEqual(results[0].due_date.year, 2026)
        self.assertEqual(results[0].due_date.month, 6)
        self.assertEqual(results[0].due_date.day, 15)


class TestSourceManagement(unittest.TestCase):
    """Tests for register_source and get_sources."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.conn = init_db(self.db_path)

    def tearDown(self):
        self.conn.close()

    def test_register_and_list_sources(self):
        """register_source adds a source; get_sources retrieves it."""
        register_source(self.conn, "gmail", enabled=True)
        register_source(self.conn, "slack", enabled=False, config_json='{"channel": "C123"}')

        sources = get_sources(self.conn)
        self.assertEqual(len(sources), 2)
        names = {s["name"] for s in sources}
        self.assertIn("gmail", names)
        self.assertIn("slack", names)

    def test_register_source_upsert(self):
        """register_source updates existing source on conflict."""
        register_source(self.conn, "gmail", enabled=True)
        register_source(self.conn, "gmail", enabled=False)

        sources = get_sources(self.conn)
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["enabled"], 0)  # SQLite stores as int


class TestSyncLog(unittest.TestCase):
    """Tests for mark_synced and get_sync_log."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.conn = init_db(self.db_path)

    def tearDown(self):
        self.conn.close()

    def test_mark_synced_creates_log_entry(self):
        """mark_synced adds an entry to sync_log."""
        register_source(self.conn, "gmail")
        mark_synced(self.conn, "gmail", "pull", 10, "success", "Pulled 10 tasks")

        log = get_sync_log(self.conn)
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["source"], "gmail")
        self.assertEqual(log[0]["operation"], "pull")
        self.assertEqual(log[0]["task_count"], 10)
        self.assertEqual(log[0]["status"], "success")

    def test_mark_synced_updates_source_last_sync(self):
        """mark_synced updates last_sync_at on the source record."""
        register_source(self.conn, "notion")
        mark_synced(self.conn, "notion", "full_sync", 5)

        sources = get_sources(self.conn)
        notion_src = next(s for s in sources if s["name"] == "notion")
        self.assertIsNotNone(notion_src["last_sync_at"])

    def test_get_sync_log_filter_by_source(self):
        """get_sync_log filters by source."""
        register_source(self.conn, "gmail")
        register_source(self.conn, "outlook")
        mark_synced(self.conn, "gmail", "pull", 5)
        mark_synced(self.conn, "outlook", "pull", 3)

        gmail_log = get_sync_log(self.conn, source="gmail")
        self.assertEqual(len(gmail_log), 1)
        self.assertEqual(gmail_log[0]["source"], "gmail")

    def test_get_sync_log_limit(self):
        """get_sync_log respects the limit parameter."""
        register_source(self.conn, "gmail")
        for i in range(10):
            mark_synced(self.conn, "gmail", f"op_{i}", i)

        log = get_sync_log(self.conn, limit=3)
        self.assertEqual(len(log), 3)

    def test_sync_log_error_status(self):
        """mark_synced stores error status and message."""
        register_source(self.conn, "slack")
        mark_synced(self.conn, "slack", "pull", 0, "error", "API rate limited")

        log = get_sync_log(self.conn)
        self.assertEqual(log[0]["status"], "error")
        self.assertEqual(log[0]["message"], "API rate limited")


class TestGetConnection(unittest.TestCase):
    """Tests for the get_connection context manager."""

    def test_context_manager(self):
        """get_connection yields a working connection and closes it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            with get_connection(db_path) as conn:
                save_task(conn, _make_task(id="ctx-test"))
                results = get_tasks(conn)
                self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
