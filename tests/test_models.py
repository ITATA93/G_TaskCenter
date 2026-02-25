"""
test_models.py - Model validation tests for G_TaskCenter.

Tests the Pydantic data models (UnifiedTask, TaskSource, TaskPriority).
"""

import os
import sys
import pytest
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from models import UnifiedTask, TaskSource, TaskPriority


class TestTaskSource:
    """Test TaskSource enum."""

    def test_notion_value(self):
        assert TaskSource.NOTION == "notion"

    def test_gmail_value(self):
        assert TaskSource.GMAIL == "gmail"

    def test_outlook_value(self):
        assert TaskSource.OUTLOOK == "outlook"

    def test_all_sources_defined(self):
        sources = [s.value for s in TaskSource]
        assert "notion" in sources
        assert "gmail" in sources
        assert "outlook" in sources
        assert len(sources) == 3


class TestTaskPriority:
    """Test TaskPriority enum."""

    def test_low_value(self):
        assert TaskPriority.LOW == "low"

    def test_normal_value(self):
        assert TaskPriority.NORMAL == "normal"

    def test_high_value(self):
        assert TaskPriority.HIGH == "high"

    def test_all_priorities_defined(self):
        priorities = [p.value for p in TaskPriority]
        assert len(priorities) == 3


class TestUnifiedTask:
    """Test UnifiedTask Pydantic model."""

    def test_minimal_valid_task(self):
        task = UnifiedTask(
            id="task-001",
            source=TaskSource.NOTION,
            title="Test Task",
            status="pending",
        )
        assert task.id == "task-001"
        assert task.source == "notion"
        assert task.title == "Test Task"
        assert task.status == "pending"
        assert task.priority == "normal"  # default
        assert task.snippet is None
        assert task.due_date is None
        assert task.link is None

    def test_full_task_with_all_fields(self):
        due = datetime(2026, 3, 1, 12, 0, 0)
        task = UnifiedTask(
            id="task-002",
            source=TaskSource.GMAIL,
            title="Review email",
            snippet="Please review the attached document",
            status="in_progress",
            priority=TaskPriority.HIGH,
            due_date=due,
            link="https://mail.google.com/mail/u/0/#inbox/abc123",
        )
        assert task.source == "gmail"
        assert task.priority == "high"
        assert task.due_date == due
        assert task.snippet == "Please review the attached document"
        assert "mail.google.com" in task.link

    def test_model_dump_returns_dict(self):
        task = UnifiedTask(
            id="task-003",
            source=TaskSource.OUTLOOK,
            title="Outlook task",
            status="active",
        )
        data = task.model_dump()
        assert isinstance(data, dict)
        assert data["id"] == "task-003"
        assert data["source"] == "outlook"
        assert data["priority"] == "normal"

    def test_invalid_source_raises(self):
        with pytest.raises(ValueError):
            UnifiedTask(
                id="task-bad",
                source="invalid_source",
                title="Bad task",
                status="pending",
            )

    def test_missing_required_field_raises(self):
        with pytest.raises(ValueError):
            UnifiedTask(
                id="task-no-title",
                source=TaskSource.NOTION,
                # title is missing
                status="pending",
            )

    def test_priority_default_is_normal(self):
        task = UnifiedTask(
            id="task-default",
            source=TaskSource.NOTION,
            title="Default priority",
            status="pending",
        )
        assert task.priority == "normal"

    def test_enum_values_serialized_as_strings(self):
        """Config use_enum_values = True should serialize enums to strings."""
        task = UnifiedTask(
            id="task-enum",
            source=TaskSource.GMAIL,
            title="Enum check",
            status="pending",
            priority=TaskPriority.LOW,
        )
        # With use_enum_values=True, these should be plain strings
        assert isinstance(task.source, str)
        assert isinstance(task.priority, str)

    def test_model_dump_round_trip(self):
        """Verify a task can be dumped and reconstructed."""
        original = UnifiedTask(
            id="task-roundtrip",
            source=TaskSource.OUTLOOK,
            title="Roundtrip test",
            status="pending",
            priority=TaskPriority.HIGH,
        )
        data = original.model_dump()
        reconstructed = UnifiedTask(**data)
        assert reconstructed.id == original.id
        assert reconstructed.source == original.source
        assert reconstructed.title == original.title
