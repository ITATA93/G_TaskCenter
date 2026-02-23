"""models.py — Data models for G_TaskCenter unified tasks."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class TaskSource(str, Enum):
    NOTION = "notion"
    GMAIL = "gmail"
    OUTLOOK = "outlook"


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class UnifiedTask(BaseModel):
    """
    Standardized task model representing a pending actionable item
    across any integrated platform.
    """

    id: str = Field(description="Unique identifier from the source platform")
    source: TaskSource = Field(description="The platform where the task originated")
    title: str = Field(description="The display title or subject of the task")
    snippet: Optional[str] = Field(
        default=None, description="A brief excerpt or description"
    )
    status: str = Field(description="Current status string from the platform")
    priority: TaskPriority = Field(
        default=TaskPriority.NORMAL, description="Normalized priority level"
    )
    due_date: Optional[datetime] = Field(
        default=None, description="When the task is due"
    )
    link: Optional[str] = Field(
        default=None, description="Direct URL to open the task in the browser"
    )

    class Config:
        use_enum_values = True
