"""Stop command - Stop a running session and release task

Stops a running session and returns its assigned task to pending status:
- Finds session by ID or task/feature ID
- Sets session state to idle
- Releases task back to pending status
- Clears assignment references
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


def handle_stop(
    project_root: Path,
    session_id: Optional[str] = None,
    task_id: Optional[str] = None,
    feature_id: Optional[str] = None
) -> Tuple[bool, str]:
    """Stop a running session and release its task.

    Can identify session by:
    - session_id: Direct session ID (full or prefix)
    - task_id: Task ID currently assigned to session
    - feature_id: Feature ID (e.g., FEAT-CM-001)

    Args:
        project_root: Project root path
        session_id: Optional session ID to stop
        task_id: Optional task ID to find session
        feature_id: Optional feature ID to find session

    Returns:
        Tuple of (success, message)
    """
    sessions_path = project_root / ".choisor" / "sessions" / "sessions.json"
    tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"

    # Load sessions
    sessions = _load_json(sessions_path)
    if not sessions:
        return False, "No sessions found"

    # Load tasks
    tasks = _load_json(tasks_path)

    # Find target session
    target_session = None
    target_task = None

    if session_id:
        # Find by session ID (supports prefix match)
        for session in sessions:
            sid = session.get("id", "")
            if sid == session_id or sid.startswith(session_id):
                target_session = session
                break
        if not target_session:
            return False, f"Session not found: {session_id}"

    elif task_id:
        # Find session by current_task_id
        for session in sessions:
            if session.get("current_task_id") == task_id:
                target_session = session
                break
        if not target_session:
            return False, f"No session found with task: {task_id}"

    elif feature_id:
        # Find task by feature_id, then find session
        feature_upper = feature_id.upper()
        for task in tasks:
            task_feature = task.get("feature_id", "").upper()
            if task_feature == feature_upper:
                task_id = task.get("id")
                break
        if not task_id:
            return False, f"Task not found for feature: {feature_id}"

        for session in sessions:
            if session.get("current_task_id") == task_id:
                target_session = session
                break
        if not target_session:
            return False, f"No running session for feature: {feature_id}"

    else:
        # Find any running session
        for session in sessions:
            state = session.get("state") or session.get("status")
            if state in ("running", "assigned", "busy"):
                target_session = session
                break
        if not target_session:
            return False, "No running sessions found"

    # Get session state
    state = target_session.get("state") or target_session.get("status")
    if state == "idle":
        return False, f"Session {target_session['id'][:8]} is already idle"

    # Get current task ID
    current_task_id = target_session.get("current_task_id")

    # Update session to idle
    target_session["state"] = "idle"
    target_session["current_task_id"] = None
    target_session["completed_at"] = datetime.now().isoformat()

    # Find and update task if exists
    stopped_task_info = None
    if current_task_id and tasks:
        for task in tasks:
            if task.get("id") == current_task_id:
                target_task = task
                stopped_task_info = {
                    "task_id": current_task_id,
                    "feature_id": task.get("feature_id"),
                    "title": task.get("title"),
                }
                # Reset task to pending
                task["status"] = "pending"
                task["assigned_session"] = None
                task["updated_at"] = datetime.now().isoformat()
                break

    # Save updates
    _save_json(sessions_path, sessions)
    if tasks:
        _save_json(tasks_path, tasks)

    # Build message
    session_short = target_session["id"][:8]
    if stopped_task_info:
        msg = (
            f"Stopped session {session_short}\n"
            f"  Task: {stopped_task_info['task_id']}\n"
            f"  Feature: {stopped_task_info['feature_id']}\n"
            f"  Status: assigned -> pending"
        )
    else:
        msg = f"Stopped session {session_short} (no task assigned)"

    return True, msg


def handle_stop_all(project_root: Path) -> Tuple[int, str]:
    """Stop all running sessions.

    Args:
        project_root: Project root path

    Returns:
        Tuple of (stopped_count, message)
    """
    sessions_path = project_root / ".choisor" / "sessions" / "sessions.json"
    tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"

    sessions = _load_json(sessions_path)
    tasks = _load_json(tasks_path)

    if not sessions:
        return 0, "No sessions found"

    stopped_count = 0
    task_ids_to_reset = []

    for session in sessions:
        state = session.get("state") or session.get("status")
        if state in ("running", "assigned", "busy"):
            current_task_id = session.get("current_task_id")
            if current_task_id:
                task_ids_to_reset.append(current_task_id)

            session["state"] = "idle"
            session["current_task_id"] = None
            session["completed_at"] = datetime.now().isoformat()
            stopped_count += 1

    # Reset tasks
    if tasks and task_ids_to_reset:
        for task in tasks:
            if task.get("id") in task_ids_to_reset:
                task["status"] = "pending"
                task["assigned_session"] = None
                task["updated_at"] = datetime.now().isoformat()

    # Save
    _save_json(sessions_path, sessions)
    if tasks:
        _save_json(tasks_path, tasks)

    if stopped_count == 0:
        return 0, "No running sessions to stop"

    return stopped_count, f"Stopped {stopped_count} session(s), released {len(task_ids_to_reset)} task(s)"


def _load_json(path: Path) -> List[Dict[str, Any]]:
    """Load JSON file."""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_json(path: Path, data: List[Dict[str, Any]]) -> None:
    """Save JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
