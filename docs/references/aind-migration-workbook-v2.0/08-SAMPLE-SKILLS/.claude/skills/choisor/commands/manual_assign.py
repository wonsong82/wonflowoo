"""Manual Assign command - Manually assign a specific feature

Allows manual assignment of a specific feature task:
- Bypasses priority engine selection
- Respects phase gate constraints
- Generates instruction same as auto-assign
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from ..core import PhaseGate, SkillRegistry, Task
from ..config import ChoisorConfig, ConfigLoader
from ..generators import InstructionGeneratorFactory


def handle_manual_assign(
    project_root: Path,
    feature_id: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Manually assign a specific feature.

    Allows direct assignment of a feature task, bypassing
    the priority engine but still respecting phase gate.

    Args:
        project_root: Project root path
        feature_id: Feature ID to assign (e.g., "FEAT-PA-001")
        session_id: Optional session ID (generated if not provided)

    Returns:
        Result dictionary with assignment details
    """
    if not feature_id:
        return {"success": False, "error": "Feature ID required"}

    print(f"\n=== Manual Assignment: {feature_id} ===\n")

    # Load config
    loader = ConfigLoader(project_root)
    config = loader.load()

    # Load project-specific config (defaults to hallain settings if not present)
    project_config = loader.load_project()

    # Load tasks
    tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"
    tasks = _load_tasks(tasks_path)

    if not tasks:
        return {"success": False, "error": "tasks.json not found. Run 'scan' first."}

    # Find task by feature ID
    task_dict = _find_task_by_feature(tasks, feature_id)

    if task_dict is None:
        # List available features
        available = _list_available_features(tasks)
        return {
            "success": False,
            "error": f"Task not found for feature '{feature_id}'",
            "available_features": available[:10],
        }

    # Check phase gate
    phase_gate = PhaseGate()
    max_allowed_phase = phase_gate.get_max_allowed_phase(tasks)

    task_phase = task_dict.get("phase", task_dict.get("metadata", {}).get("phase", 1))

    if not phase_gate.can_proceed_to_phase(task_phase, max_allowed_phase):
        return {
            "success": False,
            "error": f"Phase gate blocked: phase {task_phase} not allowed (max: {max_allowed_phase})",
        }

    # Check current status
    current_status = task_dict.get("status", "pending")

    if current_status == "completed":
        return {
            "success": False,
            "error": f"Task already completed at {task_dict.get('completed_at')}",
        }

    if current_status == "assigned":
        existing_session = task_dict.get("assigned_session")
        print(f"Warning: Task already assigned to session {existing_session}")
        # Continue anyway for manual override

    # Load workflow if available
    workflow = loader.load_workflow() if loader.has_workflow() else None

    # Discover skills with workflow config
    skills_root = project_root / config.paths.skills_root
    registry = SkillRegistry(skills_root)
    registry.discover(workflow=workflow)

    # Convert to Task object
    task = Task.from_dict(task_dict)

    # Get skill for task
    skill = registry.get_skill(task.stage, task.phase)
    if skill is None:
        return {
            "success": False,
            "error": f"Skill not found for stage {task.stage} phase {task.phase}",
        }

    # Generate session ID
    assign_session_id = session_id or str(uuid.uuid4())[:8]

    # Build instruction context
    context = {
        "config": config,
        "project_root": project_root,
        "max_allowed_phase": max_allowed_phase,
        "auto_to_max": config.phase_gate.auto_to_max,
        "session_id": assign_session_id,
        "registry": registry,
    }

    # Generate instruction (pass project_config for project-specific paths)
    instruction_gen = InstructionGeneratorFactory.create(task.stage, project_config)
    instruction_text, model_id = instruction_gen.generate(task, skill, context)

    # Mark task as assigned
    _mark_task_assigned(tasks, task.id, assign_session_id)
    _save_tasks(tasks_path, tasks)

    # Write instruction file
    _write_instruction_file(project_root, assign_session_id, instruction_text, task)

    print(f"Manual assignment completed:")
    print(f"  Task: {task.title}")
    print(f"  Phase: {task.phase}")
    print(f"  Session: {assign_session_id}")
    print(f"  Priority: {task.priority}/10")
    if task.estimated_duration:
        print(f"  Estimated: {task.estimated_duration} minutes")
    print()

    return {
        "success": True,
        "task_id": task.id,
        "feature_id": task.feature_id,
        "session_id": assign_session_id,
        "instruction_path": str(
            project_root / ".choisor" / "instructions" / f"instruction-{assign_session_id}.txt"
        ),
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


def _find_task_by_feature(
    tasks: List[Dict[str, Any]],
    feature_id: str
) -> Optional[Dict[str, Any]]:
    """Find task by feature ID.

    Args:
        tasks: List of task dictionaries
        feature_id: Feature ID to find

    Returns:
        Task dictionary or None
    """
    for task in tasks:
        # Check various locations for feature_id
        task_feature = (
            task.get("feature_id")
            or task.get("metadata", {}).get("feature_id")
            or task.get("category")
        )

        if task_feature == feature_id:
            # Prefer pending tasks
            if task.get("status") in ("pending", "skip"):
                return task

    # If no pending found, return any match
    for task in tasks:
        task_feature = (
            task.get("feature_id")
            or task.get("metadata", {}).get("feature_id")
            or task.get("category")
        )
        if task_feature == feature_id:
            return task

    return None


def _list_available_features(tasks: List[Dict[str, Any]]) -> List[str]:
    """List available feature IDs.

    Args:
        tasks: List of task dictionaries

    Returns:
        List of feature IDs
    """
    features = []
    for task in tasks:
        feature_id = (
            task.get("feature_id")
            or task.get("metadata", {}).get("feature_id")
            or task.get("category")
        )
        if feature_id and feature_id not in features:
            features.append(feature_id)
    return features


def _mark_task_assigned(
    tasks: List[Dict[str, Any]],
    task_id: str,
    session_id: str
) -> None:
    """Mark a task as assigned to a session.

    Args:
        tasks: List of task dictionaries
        task_id: Task ID to mark
        session_id: Session ID to assign
    """
    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = "assigned"
            task["assigned_session"] = session_id
            task["updated_at"] = datetime.now().isoformat()
            break


def _write_instruction_file(
    project_root: Path,
    session_id: str,
    instruction_text: str,
    task: Task
) -> None:
    """Write instruction file for session pickup.

    Args:
        project_root: Project root path
        session_id: Session identifier
        instruction_text: Generated instruction text
        task: Task object
    """
    instructions_dir = project_root / ".choisor" / "instructions"
    instructions_dir.mkdir(parents=True, exist_ok=True)

    instruction_path = instructions_dir / f"instruction-{session_id}.txt"

    # Build header with metadata
    header = f"""# Choisor Manual Session Instruction
# Session ID: {session_id}
# Task ID: {task.id}
# Feature: {task.feature_id}
# Stage: {task.stage}
# Phase: {task.phase}
# Assignment Type: Manual
# Generated: {datetime.now().isoformat()}
# =============================================================================

"""

    with open(instruction_path, "w", encoding="utf-8") as f:
        f.write(header + instruction_text)
