"""Process Completion command - Task completion processing

Handles task completion with:
- Output validation using stage-specific validators
- Status update to completed/failed
- Optional auto-commit of outputs
- Instruction file cleanup
- Next task availability check
"""

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..core import Task, TaskStatus
from ..config import ChoisorConfig, ConfigLoader
from ..generators import ValidatorFactory


def handle_process_completion(
    project_root: Path,
    task_id: str,
    request_id: Optional[str] = None,
    success: bool = True
) -> Dict[str, Any]:
    """Process task completion with validation.

    Validates task outputs, updates task status, and optionally
    commits changes.

    Args:
        project_root: Project root path
        task_id: Task ID to complete
        request_id: Optional request ID for tracking
        success: Whether task succeeded (default True)

    Returns:
        Result dictionary with success status and details
    """
    # Load config
    loader = ConfigLoader(project_root)
    config = loader.load()

    # Load tasks
    tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"
    tasks = _load_tasks(tasks_path)

    if not tasks:
        return {"success": False, "error": "tasks.json not found"}

    # Find task
    task_dict = _find_task(tasks, task_id)
    if task_dict is None:
        return {"success": False, "error": f"Task {task_id} not found"}

    task = Task.from_dict(task_dict)

    if success:
        # Validate output
        validation_result = _validate_task_output(task, project_root, config)

        if not validation_result["passed"]:
            return {
                "success": False,
                "error": "Validation failed",
                "validation_errors": validation_result["errors"],
            }

        # Mark completed
        _mark_task_completed(tasks, task_id)

        # Auto-commit if enabled
        commit_message = None
        if config.auto_commit.enabled:
            commit_message = _auto_commit(project_root, task, config)

        # Archive instruction file before cleanup
        session_id = task_dict.get("assigned_session")
        if session_id:
            _archive_instruction_file(project_root, session_id, task_id)

    else:
        # Mark failed
        _mark_task_failed(tasks, task_id)

    # Save tasks
    _save_tasks(tasks_path, tasks)

    # Check for next task
    has_next_task = _check_has_next_task(tasks, config)

    return {
        "success": True,
        "task_completed": success,
        "task_id": task_id,
        "has_next_task": has_next_task,
        "commit_message": commit_message if success else None,
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


def _save_tasks(tasks_path: Path, tasks: List[Dict[str, Any]]) -> None:
    """Save tasks to JSON file.

    Args:
        tasks_path: Path to tasks.json
        tasks: List of task dictionaries
    """
    with open(tasks_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def _find_task(
    tasks: List[Dict[str, Any]],
    task_id: str
) -> Optional[Dict[str, Any]]:
    """Find task by ID.

    Args:
        tasks: List of task dictionaries
        task_id: Task ID to find

    Returns:
        Task dictionary or None
    """
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None


def _validate_task_output(
    task: Task,
    project_root: Path,
    config: ChoisorConfig
) -> Dict[str, Any]:
    """Validate task outputs using stage-specific validator.

    Args:
        task: Task object
        project_root: Project root path
        config: Choisor configuration

    Returns:
        Validation result dictionary
    """
    # Get validator for stage
    validator = ValidatorFactory.create(task.stage)

    # Build output path
    specs_root = project_root / config.paths.specs_root
    stage_output = config.paths.stage_outputs.get(task.stage, f"stage{task.stage}-outputs")

    # Get task metadata for path construction
    priority_label = task.metadata.get("priority_label", "P2-Core")
    domain_lower = task.domain.lower()

    output_path = (
        specs_root / stage_output / f"phase{task.phase}" /
        priority_label / f"{domain_lower}" / task.feature_id
    )

    # Run validation
    result = validator.validate(task, output_path, config)

    return {
        "passed": result.passed,
        "errors": result.errors,
        "warnings": result.warnings,
    }


def _mark_task_completed(tasks: List[Dict[str, Any]], task_id: str) -> None:
    """Mark task as completed.

    Args:
        tasks: List of task dictionaries
        task_id: Task ID to mark
    """
    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            task["updated_at"] = datetime.now().isoformat()
            task["assigned_session"] = None

            # Calculate actual duration if started timestamp exists
            if task.get("updated_at"):
                try:
                    started = datetime.fromisoformat(
                        task["updated_at"].replace("Z", "+00:00")
                    )
                    completed = datetime.now()
                    duration_minutes = int(
                        (completed - started).total_seconds() / 60
                    )
                    task["actual_duration"] = duration_minutes
                except Exception:
                    pass
            break


def _mark_task_failed(tasks: List[Dict[str, Any]], task_id: str) -> None:
    """Mark task as failed.

    Args:
        tasks: List of task dictionaries
        task_id: Task ID to mark
    """
    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = "failed"
            task["updated_at"] = datetime.now().isoformat()
            task["assigned_session"] = None
            break


def _auto_commit(
    project_root: Path,
    task: Task,
    config: ChoisorConfig
) -> Optional[str]:
    """Auto-commit task outputs.

    Args:
        project_root: Project root path
        task: Task object
        config: Choisor configuration

    Returns:
        Commit message if committed, None otherwise
    """
    try:
        # Check for changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )

        if not result.stdout.strip():
            return None  # No changes to commit

        # Build commit message
        commit_message = (
            f"stage{task.stage} phase{task.phase} completion for {task.feature_id}\n\n"
            f"Domain: {task.domain.upper()}\n"
            f"Skill: {task.skill_id}"
        )

        # Stage and commit
        subprocess.run(
            ["git", "add", "."],
            cwd=project_root,
            capture_output=True,
            timeout=30
        )

        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=project_root,
            capture_output=True,
            timeout=60
        )

        return commit_message

    except Exception as e:
        print(f"Auto-commit warning: {e}")
        return None


def _archive_instruction_file(
    project_root: Path,
    session_id: str,
    task_id: str
) -> None:
    """Archive instruction file before cleanup.

    Args:
        project_root: Project root path
        session_id: Session ID
        task_id: Task ID for archive naming
    """
    instruction_path = (
        project_root / ".choisor" / "instructions" / f"instruction-{session_id}.txt"
    )

    if not instruction_path.exists():
        return

    # Create archive directory
    archive_dir = project_root / ".choisor" / "logs" / "instructions"
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Archive with task_id and timestamp
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    archive_name = f"instruction-{task_id}-{timestamp}.txt"
    archive_path = archive_dir / archive_name

    try:
        shutil.copy2(instruction_path, archive_path)
        instruction_path.unlink()
    except OSError:
        pass


def _check_has_next_task(
    tasks: List[Dict[str, Any]],
    config: ChoisorConfig
) -> bool:
    """Check if there are more pending tasks.

    Args:
        tasks: List of task dictionaries
        config: Choisor configuration

    Returns:
        True if pending tasks exist
    """
    from ..core import PhaseGate, PriorityEngine

    phase_gate = PhaseGate()
    max_allowed_phase = phase_gate.get_max_allowed_phase(tasks)

    priority_engine = PriorityEngine()
    next_task = priority_engine.select_next_task(
        tasks,
        max_allowed_phase,
        enabled_domains=config.work_scope.enabled_domains
    )

    return next_task is not None
