"""Sync command - Synchronize tasks with filesystem outputs

Checks each task's output directory and updates task status:
- Mark tasks as completed if outputs exist and pass validation
- Mark tasks as skip if outputs are empty
- Recover stale assigned tasks (session dead but task still assigned)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

from ..config import ChoisorConfig, ConfigLoader


def handle_sync(
    project_root: Path,
    auto_mode: bool = False
) -> Dict[str, Any]:
    """Synchronize tasks.json with filesystem outputs.

    Checks each task's expected output directory and updates
    task status based on output presence. Also recovers stale
    assigned tasks when the session is no longer active.

    Args:
        project_root: Project root path
        auto_mode: If True, suppress detailed output

    Returns:
        Sync result dictionary with counts
    """
    if not auto_mode:
        print(f"\n=== Synchronizing Task States ===\n")

    # Load config
    loader = ConfigLoader(project_root)
    config = loader.load()

    # Load tasks
    tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"
    tasks = _load_tasks(tasks_path)

    if not tasks:
        return {"synced": 0, "total": 0, "updates": {}}

    # Spec outputs root
    specs_root = project_root / config.paths.specs_root

    # Load active sessions to detect stale assigned tasks
    active_session_ids = _get_active_session_ids(project_root)

    # Track updates
    updates: Dict[str, int] = {
        "completed": 0,
        "skip": 0,
        "pending": 0,
        "stale_recovered": 0,
    }

    for task in tasks:
        status = task.get("status", "pending")

        # Handle assigned tasks - check if stale
        if status == "assigned":
            assigned_session = task.get("assigned_session")
            if assigned_session and assigned_session not in active_session_ids:
                # Session is no longer active - task is stale
                output_exists, _ = _check_task_output(task, specs_root, config)
                if output_exists:
                    # Output exists, mark as completed
                    task["status"] = "completed"
                    task["assigned_session"] = None
                    task["updated_at"] = datetime.now().isoformat()
                    updates["completed"] = updates.get("completed", 0) + 1
                    if not auto_mode:
                        print(f"  Stale task {task.get('id', 'unknown')[:12]} → completed (output exists)")
                else:
                    # No output, reset to pending
                    task["status"] = "pending"
                    task["assigned_session"] = None
                    task["updated_at"] = datetime.now().isoformat()
                    updates["stale_recovered"] = updates.get("stale_recovered", 0) + 1
                    if not auto_mode:
                        print(f"  Stale task {task.get('id', 'unknown')[:12]} → pending (no output)")
            continue

        # Skip already completed or in_progress tasks
        if status in ("completed", "in_progress"):
            continue

        # Check if outputs exist
        output_exists, output_reason = _check_task_output(task, specs_root, config)

        if output_exists:
            # Mark as completed if outputs exist
            if status != "completed":
                task["status"] = "completed"
                task["updated_at"] = datetime.now().isoformat()
                updates["completed"] = updates.get("completed", 0) + 1
        elif output_reason:
            # Mark as skip if output directory is empty
            if status != "skip":
                task["status"] = "skip"
                task["skip_reason"] = output_reason
                task["updated_at"] = datetime.now().isoformat()
                updates["skip"] = updates.get("skip", 0) + 1
        else:
            # Keep as pending
            if status == "skip":
                task["status"] = "pending"
                task["skip_reason"] = None
                task["updated_at"] = datetime.now().isoformat()
                updates["pending"] = updates.get("pending", 0) + 1

    # Save updated tasks
    _save_tasks(tasks_path, tasks)

    total_updates = sum(updates.values())

    if not auto_mode:
        print(f"Synced {total_updates} task(s):")
        for status, count in updates.items():
            if count > 0:
                print(f"  {status}: {count}")
        print()

    return {
        "synced": total_updates,
        "total": len(tasks),
        "updates": updates,
    }


def _get_active_session_ids(project_root: Path) -> Set[str]:
    """Get set of active session IDs.

    Active sessions are those in IDLE, ASSIGNED, or RUNNING state.

    Args:
        project_root: Project root path

    Returns:
        Set of active session IDs
    """
    sessions_path = project_root / ".choisor" / "sessions" / "sessions.json"

    if not sessions_path.exists():
        return set()

    try:
        with open(sessions_path, "r", encoding="utf-8") as f:
            sessions_data = json.load(f)

        active_states = {"idle", "assigned", "running"}
        return {
            s.get("id")
            for s in sessions_data
            if s.get("state") in active_states and s.get("id")
        }
    except (json.JSONDecodeError, IOError):
        return set()


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


def _save_tasks(tasks_path: Path, tasks: List[Dict[str, Any]]) -> None:
    """Save tasks to JSON file.

    Args:
        tasks_path: Path to tasks.json
        tasks: List of task dictionaries
    """
    with open(tasks_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def _check_task_output(
    task: Dict[str, Any],
    specs_root: Path,
    config: ChoisorConfig
) -> tuple[bool, Optional[str]]:
    """Check if task outputs exist.

    Args:
        task: Task dictionary
        specs_root: Path to specs root directory
        config: Choisor configuration

    Returns:
        Tuple of (output_exists, skip_reason)
    """
    # Get feature info
    feature_id = (
        task.get("feature_id")
        or task.get("metadata", {}).get("feature_id")
        or task.get("category")
    )

    if not feature_id:
        return False, None

    # Get stage and phase
    stage = task.get("stage", 1)
    phase = task.get("phase", task.get("metadata", {}).get("phase", 1))

    # Get output directory name from config
    stage_output = config.paths.stage_outputs.get(stage, f"stage{stage}-outputs")

    # Build expected output path
    # Pattern: {specs_root}/{stage_output}/phase{phase}/{priority}/{domain}/{feature_id}
    metadata = task.get("metadata", {})
    priority_label = metadata.get("priority_label", "P2-Core")
    domain = (metadata.get("domain") or task.get("domain", "")).upper()

    if not domain:
        return False, None

    # Search for feature directory in phase output
    phase_dir = specs_root / stage_output / f"phase{phase}"

    if not phase_dir.exists():
        return False, None

    # Try to find feature directory
    feature_dir = _find_feature_directory(phase_dir, feature_id, priority_label, domain)

    if feature_dir is None:
        return False, None

    # Check if directory has content
    if feature_dir.exists():
        content = list(feature_dir.iterdir())
        if not content:
            return False, "Empty output directory"

        # Check for main.yaml or other marker files
        has_main_yaml = (feature_dir / "main.yaml").exists()
        has_any_yaml = any(f.suffix == ".yaml" for f in content)

        if has_main_yaml or has_any_yaml:
            return True, None
        else:
            return False, "No YAML files in output"

    return False, None


def _find_feature_directory(
    phase_dir: Path,
    feature_id: str,
    priority_label: str,
    domain: str
) -> Optional[Path]:
    """Find feature directory in phase output structure.

    Args:
        phase_dir: Phase output directory
        feature_id: Feature ID to find
        priority_label: Priority label (e.g., "P2-Core")
        domain: Domain code

    Returns:
        Path to feature directory or None
    """
    # Try exact path first
    domain_lower = domain.lower()
    exact_path = phase_dir / priority_label / f"{domain_lower}" / feature_id

    if exact_path.exists():
        return exact_path

    # Search through priority directories
    for priority_dir in phase_dir.iterdir():
        if not priority_dir.is_dir():
            continue

        # Search through domain directories
        for domain_dir in priority_dir.iterdir():
            if not domain_dir.is_dir():
                continue

            # Check for feature directory
            feature_path = domain_dir / feature_id
            if feature_path.exists():
                return feature_path

    return None
