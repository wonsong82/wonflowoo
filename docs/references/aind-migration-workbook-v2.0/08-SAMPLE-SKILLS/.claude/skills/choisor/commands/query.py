"""Query command - Query tasks with filters

Provides flexible querying of tasks with various filter options:
- Status filter (pending, assigned, completed, skip, failed)
- Domain filter (PA, CM, SM, etc.)
- Stage/Phase filter
- Priority filter
- Skip reason filter

Supports multiple output formats: table, json, csv
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

from ..config import ConfigLoader


def handle_query(
    project_root: Path,
    status: Optional[str] = None,
    domain: Optional[str] = None,
    stage: Optional[int] = None,
    phase: Optional[int] = None,
    priority: Optional[str] = None,
    skip_reason_filter: Optional[str] = None,
    show_list: bool = False,
    output_format: str = "table",
    limit: Optional[int] = None,
    no_stats: bool = False,
) -> Dict[str, Any]:
    """Query tasks with filters.

    Args:
        project_root: Project root path
        status: Filter by status (pending, assigned, completed, skip, failed)
        domain: Filter by domain code (e.g., "PA", "CM")
        stage: Filter by stage number (1-5)
        phase: Filter by phase number (1-5)
        priority: Filter by priority label (e.g., "P0-Foundation")
        skip_reason_filter: Filter by skip reason substring
        show_list: If True, show full task list
        output_format: Output format (table, json, csv)
        limit: Maximum number of tasks to return
        no_stats: If True, suppress statistics

    Returns:
        Query result dictionary
    """
    # Load tasks
    tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"
    tasks = _load_tasks(tasks_path)

    if not tasks:
        print("No tasks found. Run 'scan' command first.")
        return {"count": 0, "tasks": []}

    # Apply filters
    filtered = tasks

    if status:
        filtered = [t for t in filtered if t.get("status") == status]

    if domain:
        domain_upper = domain.upper()
        filtered = [
            t for t in filtered
            if (
                t.get("metadata", {}).get("domain", "").upper() == domain_upper
                or t.get("domain", "").upper() == domain_upper
            )
        ]

    if stage is not None:
        filtered = [t for t in filtered if t.get("stage") == stage]

    if phase is not None:
        filtered = [
            t for t in filtered
            if (
                t.get("phase") == phase
                or t.get("metadata", {}).get("phase") == phase
            )
        ]

    if priority:
        filtered = [
            t for t in filtered
            if t.get("metadata", {}).get("priority_label") == priority
        ]

    if skip_reason_filter:
        filtered = [
            t for t in filtered
            if skip_reason_filter.lower() in (t.get("skip_reason") or "").lower()
        ]

    # Apply limit
    if limit and limit > 0:
        filtered = filtered[:limit]

    # Print results
    if not no_stats:
        _print_stats(tasks, filtered, status, domain, stage, phase)

    if show_list:
        _print_task_list(filtered, output_format)

    return {
        "count": len(filtered),
        "tasks": filtered,
    }


def _load_tasks(tasks_path: Path) -> List[Dict[str, Any]]:
    """Load tasks from JSON file.

    Args:
        tasks_path: Path to tasks.json

    Returns:
        List of task dictionaries
    """
    if not tasks_path.exists():
        return []

    try:
        with open(tasks_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _print_stats(
    all_tasks: List[Dict[str, Any]],
    filtered: List[Dict[str, Any]],
    status: Optional[str],
    domain: Optional[str],
    stage: Optional[int],
    phase: Optional[int],
) -> None:
    """Print query statistics.

    Args:
        all_tasks: All tasks
        filtered: Filtered tasks
        status: Status filter used
        domain: Domain filter used
        stage: Stage filter used
        phase: Phase filter used
    """
    print(f"\n=== Task Query Results ===\n")

    # Filter description
    filters_used = []
    if status:
        filters_used.append(f"status={status}")
    if domain:
        filters_used.append(f"domain={domain.upper()}")
    if stage is not None:
        filters_used.append(f"stage={stage}")
    if phase is not None:
        filters_used.append(f"phase={phase}")

    if filters_used:
        print(f"Filters: {', '.join(filters_used)}")
    print(f"Found: {len(filtered)} / {len(all_tasks)} tasks")
    print()

    # Group by status
    status_counts = _count_by_field(filtered, lambda t: t.get("status", "unknown"))
    if status_counts:
        print("By Status:")
        for s, count in sorted(status_counts.items()):
            print(f"  {s}: {count}")
        print()

    # Group by domain
    domain_counts = _count_by_field(
        filtered,
        lambda t: (
            t.get("metadata", {}).get("domain", "").upper()
            or t.get("domain", "").upper()
            or "?"
        )
    )
    if domain_counts:
        print("By Domain:")
        for d, count in sorted(domain_counts.items()):
            print(f"  {d}: {count}")
        print()

    # Group by complexity
    complexity_counts = _count_by_field(
        filtered,
        lambda t: t.get("metadata", {}).get("complexity_estimate", "?")
    )
    if complexity_counts:
        print("By Complexity:")
        for c, count in sorted(complexity_counts.items()):
            print(f"  {c}: {count}")
        print()


def _count_by_field(
    tasks: List[Dict[str, Any]],
    getter: Callable[[Dict[str, Any]], str]
) -> Dict[str, int]:
    """Count tasks grouped by a field.

    Args:
        tasks: List of task dictionaries
        getter: Function to extract field value

    Returns:
        Dictionary mapping field value to count
    """
    counts: Dict[str, int] = {}
    for task in tasks:
        value = getter(task)
        counts[value] = counts.get(value, 0) + 1
    return counts


def _print_task_list(
    tasks: List[Dict[str, Any]],
    output_format: str
) -> None:
    """Print task list in specified format.

    Args:
        tasks: List of task dictionaries
        output_format: Output format (table, json, csv)
    """
    if not tasks:
        print("No tasks match the query.")
        return

    if output_format == "json":
        print(json.dumps(tasks, indent=2, ensure_ascii=False))
        return

    if output_format == "csv":
        _print_csv(tasks)
        return

    # Default: table format
    _print_table(tasks)


def _print_table(tasks: List[Dict[str, Any]]) -> None:
    """Print tasks as formatted table.

    Args:
        tasks: List of task dictionaries
    """
    # Header
    print(f"{'ID':<40} {'Status':<12} {'Domain':<8} {'S':<3} {'P':<3} {'Complexity':<10}")
    print("-" * 80)

    for task in tasks:
        task_id = task.get("id", "?")[:40]
        status = task.get("status", "?")
        metadata = task.get("metadata", {})
        domain = (metadata.get("domain") or task.get("domain", "?"))[:8].upper()
        stage = task.get("stage", "?")
        phase = task.get("phase", metadata.get("phase", "?"))
        complexity = metadata.get("complexity_estimate", "?")

        print(f"{task_id:<40} {status:<12} {domain:<8} {stage:<3} {phase:<3} {complexity:<10}")

        # Print skip reason if available
        if task.get("skip_reason"):
            print(f"  Skip: {task['skip_reason']}")


def _print_csv(tasks: List[Dict[str, Any]]) -> None:
    """Print tasks as CSV.

    Args:
        tasks: List of task dictionaries
    """
    # Header
    print("id,feature_id,status,domain,stage,phase,complexity,skip_reason")

    for task in tasks:
        task_id = task.get("id", "")
        metadata = task.get("metadata", {})
        feature_id = metadata.get("feature_id") or task.get("feature_id", "")
        status = task.get("status", "")
        domain = (metadata.get("domain") or task.get("domain", "")).upper()
        stage = task.get("stage", "")
        phase = task.get("phase", metadata.get("phase", ""))
        complexity = metadata.get("complexity_estimate", "")
        skip_reason = (task.get("skip_reason") or "").replace(",", ";")

        print(f"{task_id},{feature_id},{status},{domain},{stage},{phase},{complexity},{skip_reason}")
