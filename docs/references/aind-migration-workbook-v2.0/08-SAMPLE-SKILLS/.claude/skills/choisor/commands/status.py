"""Status command - Display current project status

Shows workflow status including:
- Current stage/phase position
- Task counts by status
- Phase gate progression
- Active sessions
- Pending tasks
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..core import PhaseGate, SkillRegistry, Task, TaskStatus
from ..config import ChoisorConfig, ConfigLoader


def handle_status(project_root: Path) -> None:
    """Display current project status.

    Shows comprehensive workflow status including stage/phase position,
    task statistics, phase gate status, and pending work.

    Args:
        project_root: Project root path
    """
    print(f"\n=== Choisor Status ===\n")
    print(f"Project: {project_root.name}")
    print(f"Path: {project_root}\n")

    # Load config
    loader = ConfigLoader(project_root)
    config = loader.load()

    # Load tasks
    tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"
    tasks = _load_tasks(tasks_path)

    if not tasks:
        print("Note: tasks.json not found or empty. Run 'scan' command first.\n")

    # Current Stage/Phase status
    print(f"Current: Stage {config.current_stage} / Phase {config.current_phase}")

    # Phase Gate status
    phase_gate = PhaseGate()
    max_allowed_phase = phase_gate.get_max_allowed_phase(
        tasks, override=config.current_phase
    )
    print(f"Max Allowed Phase: {max_allowed_phase}")

    # Work Scope status
    if config.work_scope.enabled_domains:
        domains = ", ".join(d.upper() for d in config.work_scope.enabled_domains)
        print(f"Enabled Domains: {domains}")
    else:
        print("Enabled Domains: All")

    # Task status summary
    status_counts = _count_by_status(tasks)
    print(f"\nTasks:")
    print(f"  Total: {len(tasks)}")
    for status, count in sorted(status_counts.items()):
        print(f"  {status.capitalize()}: {count}")

    # Phase progress
    if tasks:
        phase_status = phase_gate.get_phase_status(tasks, max_allowed_phase)
        print(f"\nPhase Progress:")
        for phase, info in sorted(phase_status.items()):
            completed_icon = "+" if info["completed"] else "o"
            allowed_icon = "+" if info["allowed"] else "x"
            print(
                f"  [{completed_icon}] Phase {phase}: {info['progress']} "
                f"({info['task_progress']} tasks) [allowed: {allowed_icon}]"
            )

    # Session status
    sessions_path = project_root / ".choisor" / "sessions" / "sessions.json"
    sessions = _load_sessions(sessions_path)
    _print_sessions(sessions, tasks, config.default_model)

    # Pending tasks
    _print_pending_tasks(tasks, config.work_scope.enabled_domains)

    print("")


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


def _load_sessions(sessions_path: Path) -> List[Dict[str, Any]]:
    """Load sessions from JSON file.

    Args:
        sessions_path: Path to sessions.json

    Returns:
        List of session dictionaries
    """
    if not sessions_path.exists():
        return []

    try:
        with open(sessions_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _count_by_status(tasks: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count tasks by status.

    Args:
        tasks: List of task dictionaries

    Returns:
        Dictionary mapping status to count
    """
    counts: Dict[str, int] = {}
    for task in tasks:
        status = task.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _get_task_complexity(task_id: str, tasks: List[Dict[str, Any]]) -> str:
    """Get complexity estimate for a task.

    Args:
        task_id: Task ID or feature ID
        tasks: List of task dictionaries

    Returns:
        Complexity string or "?"
    """
    for t in tasks:
        if t.get("id") == task_id or t.get("feature_id") == task_id:
            return t.get("metadata", {}).get("complexity_estimate", "?")
    return "?"


def _print_sessions(
    sessions: List[Dict[str, Any]],
    tasks: List[Dict[str, Any]],
    default_model: str
) -> None:
    """Print session status.

    Args:
        sessions: List of session dictionaries
        tasks: List of task dictionaries
        default_model: Default model ID
    """
    if not sessions:
        print(f"\nSessions: None active for this project")
        return

    # Split active and idle sessions
    active_sessions = [s for s in sessions if s.get("status") != "idle"]
    idle_sessions = [s for s in sessions if s.get("status") == "idle"]

    print(f"\nSessions:")

    # Active sessions with model and complexity info
    if active_sessions:
        print(f"  Active:")
        for session in active_sessions:
            status = session.get("status", "unknown")
            task_id = session.get("current_task_id", "")
            complexity = _get_task_complexity(task_id, tasks) if task_id else "?"
            model = session.get("last_used_model", default_model)

            # Shorten model name
            if "opus" in model.lower():
                model_short = "opus"
            elif "sonnet" in model.lower():
                model_short = "sonnet"
            elif "haiku" in model.lower():
                model_short = "haiku"
            else:
                model_short = model[:10]

            session_id_short = session["id"][:8] if session.get("id") else "?"
            task_info = f" | {task_id}" if task_id else ""
            print(
                f"    {session_id_short}: {status} | {model_short} | "
                f"{complexity}{task_info}"
            )

    # Idle sessions count
    if idle_sessions:
        print(f"  Idle: {len(idle_sessions)} session(s)")


def _print_pending_tasks(
    tasks: List[Dict[str, Any]],
    enabled_domains: Optional[List[str]]
) -> None:
    """Print pending tasks summary.

    Args:
        tasks: List of task dictionaries
        enabled_domains: Optional list of enabled domains
    """
    pending = [t for t in tasks if t.get("status") == "pending"]

    # Filter by domain if specified
    if enabled_domains:
        enabled_lower = [d.lower() for d in enabled_domains]
        pending = [
            t for t in pending
            if t.get("metadata", {}).get("domain", "").lower() in enabled_lower
            or t.get("domain", "").lower() in enabled_lower
        ]

    if not pending:
        return

    # Sort by complexity (HIGH > MEDIUM > LOW)
    complexity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    pending.sort(
        key=lambda t: (
            complexity_order.get(
                t.get("metadata", {}).get("complexity_estimate", "MEDIUM"), 1
            ),
            t.get("id", "")
        )
    )

    print(f"\nPending Tasks ({len(pending)}):")
    for task in pending[:10]:
        meta = task.get("metadata", {})
        feature_id = meta.get("feature_id") or task.get("feature_id") or task.get("id", "?")
        complexity = meta.get("complexity_estimate", "?")
        domain = (meta.get("domain") or task.get("domain", "?")).upper()
        print(f"  {feature_id}: {complexity} ({domain})")

    if len(pending) > 10:
        print(f"  ... and {len(pending) - 10} more")
