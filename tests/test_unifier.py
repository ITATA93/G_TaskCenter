"""test_unifier.py — Tests for src/dedup/unifier.py.

Covers normalization, similarity scoring, merge logic, and the full
deduplication pipeline.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

# Ensure src/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models import UnifiedTask, TaskSource, TaskPriority
from dedup.unifier import (
    normalize_task,
    compute_similarity,
    merge_duplicates,
    unify_tasks,
    DEFAULT_SIMILARITY_THRESHOLD,
)


def _make_task(
    id: str = "t1",
    source: str = "gmail",
    title: str = "Test task",
    status: str = "Pending",
    priority: str = "normal",
    due_date: datetime = None,
    snippet: str = None,
    link: str = None,
) -> UnifiedTask:
    """Helper to build a UnifiedTask with sensible defaults."""
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


class TestNormalizeTask(unittest.TestCase):
    """Tests for normalize_task()."""

    def test_strips_source_prefix(self):
        """Removes [GMAIL], [OUTLOOK], etc. prefixes."""
        self.assertEqual(normalize_task("[GMAIL] Buy groceries"), "buy groceries")
        self.assertEqual(normalize_task("[Outlook] Team meeting"), "team meeting")

    def test_lowercases(self):
        self.assertEqual(normalize_task("Buy GROCERIES"), "buy groceries")

    def test_removes_punctuation(self):
        result = normalize_task("Fix bug #123 (urgent!)")
        self.assertNotIn("#", result)
        self.assertNotIn("(", result)
        self.assertNotIn("!", result)

    def test_collapses_whitespace(self):
        self.assertEqual(normalize_task("  buy   groceries  "), "buy groceries")

    def test_empty_string(self):
        self.assertEqual(normalize_task(""), "")

    def test_only_prefix(self):
        self.assertEqual(normalize_task("[GMAIL] "), "")


class TestComputeSimilarity(unittest.TestCase):
    """Tests for compute_similarity()."""

    def test_identical_titles(self):
        sim = compute_similarity("Buy groceries", "Buy groceries")
        self.assertAlmostEqual(sim, 1.0)

    def test_identical_after_normalization(self):
        sim = compute_similarity("[GMAIL] Buy groceries", "[OUTLOOK] Buy groceries!")
        self.assertGreater(sim, 0.95)

    def test_completely_different(self):
        sim = compute_similarity("Buy groceries", "Schedule dentist appointment")
        self.assertLess(sim, 0.5)

    def test_similar_titles(self):
        sim = compute_similarity("Fix the login bug", "Fix login bug")
        self.assertGreater(sim, 0.80)

    def test_empty_string_returns_zero(self):
        self.assertEqual(compute_similarity("", "something"), 0.0)
        self.assertEqual(compute_similarity("", ""), 0.0)


class TestMergeDuplicates(unittest.TestCase):
    """Tests for merge_duplicates()."""

    def test_single_task_unchanged(self):
        task = _make_task(title="Solo task")
        merged = merge_duplicates([task])
        self.assertEqual(merged.title, "Solo task")
        self.assertEqual(merged.id, task.id)

    def test_longest_title_wins(self):
        t1 = _make_task(id="t1", title="Fix bug")
        t2 = _make_task(id="t2", title="Fix the login bug on production")
        merged = merge_duplicates([t1, t2])
        self.assertEqual(merged.title, "Fix the login bug on production")
        # id from the first task (canonical)
        self.assertEqual(merged.id, "t1")

    def test_highest_priority_wins(self):
        t1 = _make_task(id="t1", priority="low")
        t2 = _make_task(id="t2", priority="high")
        merged = merge_duplicates([t1, t2])
        self.assertEqual(merged.priority, "high")

    def test_earliest_due_date_wins(self):
        early = datetime(2026, 3, 1, tzinfo=timezone.utc)
        late = datetime(2026, 3, 15, tzinfo=timezone.utc)
        t1 = _make_task(id="t1", due_date=late)
        t2 = _make_task(id="t2", due_date=early)
        merged = merge_duplicates([t1, t2])
        self.assertEqual(merged.due_date, early)

    def test_none_due_date_replaced(self):
        date = datetime(2026, 3, 1, tzinfo=timezone.utc)
        t1 = _make_task(id="t1", due_date=None)
        t2 = _make_task(id="t2", due_date=date)
        merged = merge_duplicates([t1, t2])
        self.assertEqual(merged.due_date, date)

    def test_first_nonempty_snippet(self):
        t1 = _make_task(id="t1", snippet=None)
        t2 = _make_task(id="t2", snippet="Some detail here")
        merged = merge_duplicates([t1, t2])
        self.assertEqual(merged.snippet, "Some detail here")

    def test_first_nonempty_link(self):
        t1 = _make_task(id="t1", link=None)
        t2 = _make_task(id="t2", link="https://example.com/task")
        merged = merge_duplicates([t1, t2])
        self.assertEqual(merged.link, "https://example.com/task")


class TestUnifyTasks(unittest.TestCase):
    """Tests for unify_tasks() — full deduplication pipeline."""

    def test_empty_list(self):
        self.assertEqual(unify_tasks([]), [])

    def test_no_duplicates(self):
        tasks = [
            _make_task(id="t1", title="Buy groceries"),
            _make_task(id="t2", title="Schedule dentist"),
            _make_task(id="t3", title="Review PR #42"),
        ]
        result = unify_tasks(tasks)
        self.assertEqual(len(result), 3)

    def test_exact_duplicates_merged(self):
        tasks = [
            _make_task(id="t1", source="gmail", title="Fix login bug"),
            _make_task(id="t2", source="outlook", title="Fix login bug"),
        ]
        result = unify_tasks(tasks)
        self.assertEqual(len(result), 1)

    def test_similar_titles_merged(self):
        tasks = [
            _make_task(id="t1", source="gmail", title="[GMAIL] Fix the login bug"),
            _make_task(id="t2", source="notion", title="Fix login bug"),
        ]
        result = unify_tasks(tasks)
        self.assertEqual(len(result), 1)

    def test_different_titles_not_merged(self):
        tasks = [
            _make_task(id="t1", title="Buy groceries"),
            _make_task(id="t2", title="Fix the login bug on prod"),
        ]
        result = unify_tasks(tasks)
        self.assertEqual(len(result), 2)

    def test_due_date_window_respected(self):
        base = datetime(2026, 3, 1, tzinfo=timezone.utc)
        tasks = [
            _make_task(id="t1", title="Same task", due_date=base),
            _make_task(
                id="t2",
                title="Same task",
                due_date=base + timedelta(days=30),
            ),
        ]
        # Large date gap should prevent merge (default window is 1 day)
        result = unify_tasks(tasks)
        self.assertEqual(len(result), 2)

    def test_due_date_within_window_merged(self):
        base = datetime(2026, 3, 1, tzinfo=timezone.utc)
        tasks = [
            _make_task(id="t1", title="Same task", due_date=base),
            _make_task(
                id="t2",
                title="Same task",
                due_date=base + timedelta(hours=12),
            ),
        ]
        result = unify_tasks(tasks)
        self.assertEqual(len(result), 1)

    def test_custom_threshold(self):
        tasks = [
            _make_task(id="t1", title="Fix login bug"),
            _make_task(id="t2", title="Fix login issue"),
        ]
        # With a very high threshold, these should NOT be merged
        result = unify_tasks(tasks, similarity_threshold=0.99)
        self.assertEqual(len(result), 2)

        # With a lower threshold, they should be merged
        result = unify_tasks(tasks, similarity_threshold=0.60)
        self.assertEqual(len(result), 1)

    def test_three_way_merge(self):
        tasks = [
            _make_task(id="t1", source="gmail", title="Deploy v2.0", priority="low"),
            _make_task(id="t2", source="outlook", title="Deploy v2.0", priority="high"),
            _make_task(id="t3", source="notion", title="Deploy v2.0", priority="normal"),
        ]
        result = unify_tasks(tasks)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].priority, "high")


if __name__ == "__main__":
    unittest.main()
