"""unifier.py — Task deduplication and unification logic for G_TaskCenter.

Handles cross-platform duplicate detection using fuzzy string matching on
task title and optional due-date proximity. Merges duplicate tasks into a
single canonical representation while preserving provenance metadata.
"""

import logging
import re
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

try:
    from models import UnifiedTask, TaskPriority
except ImportError:
    from src.models import UnifiedTask, TaskPriority

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Similarity threshold (0.0 - 1.0). Tasks above this are considered duplicates.
DEFAULT_SIMILARITY_THRESHOLD: float = 0.80

# Maximum time difference between due dates to consider tasks as duplicates.
DEFAULT_DATE_WINDOW: timedelta = timedelta(days=1)

# Priority ranking for merge resolution (higher index wins).
_PRIORITY_RANK: Dict[str, int] = {
    TaskPriority.LOW: 0,
    "low": 0,
    TaskPriority.NORMAL: 1,
    "normal": 1,
    TaskPriority.HIGH: 2,
    "high": 2,
}


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

# Common prefixes injected by the sync engine when pushing to Notion.
_SOURCE_PREFIX_RE = re.compile(r"^\[(gmail|outlook|notion|slack|jira)\]\s*", re.IGNORECASE)

# Noise words / characters that should not affect similarity.
_NOISE_RE = re.compile(r"[^\w\s]", re.UNICODE)


def normalize_task(title: str) -> str:
    """Normalize a task title for comparison.

    Steps:
        1. Strip leading source tags like [GMAIL], [OUTLOOK].
        2. Lower-case.
        3. Remove non-alphanumeric / non-space characters.
        4. Collapse whitespace.
        5. Strip leading/trailing whitespace.

    Args:
        title: Raw task title string.

    Returns:
        Cleaned, lowered, whitespace-collapsed string.
    """
    text = _SOURCE_PREFIX_RE.sub("", title)
    text = text.lower()
    text = _NOISE_RE.sub(" ", text)
    text = " ".join(text.split())
    return text.strip()


# ---------------------------------------------------------------------------
# Similarity computation
# ---------------------------------------------------------------------------


def compute_similarity(title_a: str, title_b: str) -> float:
    """Compute fuzzy similarity between two task titles.

    Uses ``difflib.SequenceMatcher`` on the *normalized* forms. The ratio
    returned is between 0.0 (completely different) and 1.0 (identical).

    Args:
        title_a: First task title (raw or normalized).
        title_b: Second task title (raw or normalized).

    Returns:
        Float similarity ratio in [0.0, 1.0].
    """
    norm_a = normalize_task(title_a)
    norm_b = normalize_task(title_b)

    if not norm_a or not norm_b:
        return 0.0

    return SequenceMatcher(None, norm_a, norm_b).ratio()


def _dates_are_close(
    date_a: Optional[datetime],
    date_b: Optional[datetime],
    window: timedelta = DEFAULT_DATE_WINDOW,
) -> bool:
    """Return True if both dates are within *window* of each other, or if
    either date is None (unknown dates should not block dedup)."""
    if date_a is None or date_b is None:
        return True
    return abs(date_a - date_b) <= window


# ---------------------------------------------------------------------------
# Merging
# ---------------------------------------------------------------------------


def _pick_higher_priority(a: str, b: str) -> str:
    """Return the higher of two priority values."""
    rank_a = _PRIORITY_RANK.get(a, 1)
    rank_b = _PRIORITY_RANK.get(b, 1)
    return a if rank_a >= rank_b else b


def merge_duplicates(tasks: List[UnifiedTask]) -> UnifiedTask:
    """Merge a cluster of duplicate tasks into a single canonical task.

    Merge strategy:
        - **id / source**: Keep the first task's id and source (canonical).
        - **title**: Keep the longest title (most descriptive).
        - **snippet**: Keep the first non-empty snippet.
        - **status**: Prefer non-completed statuses.
        - **priority**: Keep the highest priority across the cluster.
        - **due_date**: Keep the earliest due date.
        - **link**: Keep the first non-empty link.

    Args:
        tasks: List of UnifiedTask instances that are duplicates of each other.

    Returns:
        A single merged UnifiedTask.
    """
    if len(tasks) == 1:
        return tasks[0]

    # Start with a copy of the first task as canonical base
    canonical = tasks[0].model_copy()

    for other in tasks[1:]:
        # Longest title wins
        if len(other.title) > len(canonical.title):
            canonical.title = other.title

        # First non-empty snippet
        if not canonical.snippet and other.snippet:
            canonical.snippet = other.snippet

        # Highest priority wins
        canonical.priority = _pick_higher_priority(canonical.priority, other.priority)

        # Earliest due date
        if other.due_date is not None:
            if canonical.due_date is None or other.due_date < canonical.due_date:
                canonical.due_date = other.due_date

        # First non-empty link
        if not canonical.link and other.link:
            canonical.link = other.link

    return canonical


# ---------------------------------------------------------------------------
# Main unification pipeline
# ---------------------------------------------------------------------------


def unify_tasks(
    tasks: List[UnifiedTask],
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    date_window: timedelta = DEFAULT_DATE_WINDOW,
) -> List[UnifiedTask]:
    """Deduplicate and unify a list of tasks from heterogeneous sources.

    Algorithm (O(n^2) pairwise — acceptable for typical personal task volumes
    of < 500 items):
        1. For each unprocessed task, find all other tasks whose normalized
           title similarity exceeds ``similarity_threshold`` AND whose due
           dates are within ``date_window``.
        2. Group matched tasks into a cluster.
        3. Merge each cluster into a single canonical UnifiedTask.

    Args:
        tasks: Raw list of UnifiedTask from all integrations.
        similarity_threshold: Minimum similarity ratio to consider a pair
                              as duplicates (default 0.80).
        date_window: Maximum due-date difference allowed for dedup.

    Returns:
        Deduplicated list of UnifiedTask instances.
    """
    if not tasks:
        return []

    n = len(tasks)
    visited: List[bool] = [False] * n
    unified: List[UnifiedTask] = []

    # Pre-compute normalized titles for efficiency
    normalized: List[str] = [normalize_task(t.title) for t in tasks]

    for i in range(n):
        if visited[i]:
            continue

        cluster: List[UnifiedTask] = [tasks[i]]
        visited[i] = True

        for j in range(i + 1, n):
            if visited[j]:
                continue

            sim = SequenceMatcher(None, normalized[i], normalized[j]).ratio()
            if sim >= similarity_threshold and _dates_are_close(
                tasks[i].due_date, tasks[j].due_date, date_window
            ):
                cluster.append(tasks[j])
                visited[j] = True
                logger.debug(
                    "Duplicate detected (sim=%.2f): '%s' <-> '%s'",
                    sim,
                    tasks[i].title,
                    tasks[j].title,
                )

        merged = merge_duplicates(cluster)
        unified.append(merged)

    dedup_count = n - len(unified)
    if dedup_count > 0:
        logger.info(
            "Unified %d tasks into %d (removed %d duplicates).",
            n,
            len(unified),
            dedup_count,
        )

    return unified
