"""Assign Next command - Select and assign next task

Selects the highest priority eligible task and generates
an instruction for a Claude session to execute:
- Applies phase gate filtering
- Uses priority engine for task selection
- Generates skill-specific instructions
- Writes instruction file for session pickup
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from ..core import PhaseGate, PriorityEngine, SkillRegistry, Task
from ..config import ChoisorConfig, ConfigLoader
from ..generators import InstructionGeneratorFactory


def handle_assign_next(
    project_root: Path,
    request_id: Optional[str] = None
) -> Tuple[Optional[Dict[str, Any]], str, str]:
    """Select and assign next task.

    Selects the highest priority eligible task, generates an
    instruction, and marks the task as assigned.

    Args:
        project_root: Project root path
        request_id: Optional request ID (generated if not provided)

    Returns:
        Tuple of (task_dict, instruction_text, message)
        - task_dict is None if no eligible tasks
        - instruction_text is empty if no task assigned
        - message contains status/error information
    """
    # Load config
    loader = ConfigLoader(project_root)
    config = loader.load()

    # Load project-specific config (defaults to hallain settings if not present)
    project_config = loader.load_project()

    # Check if assignment is disabled
    if not config.assignment.enabled:
        return None, "", "Assignment disabled by configuration"

    # Load tasks
    tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"
    tasks = _load_tasks(tasks_path)

    if not tasks:
        return None, "", "No tasks found. Run 'scan' command first."

    # Load workflow if available
    workflow = loader.load_workflow() if loader.has_workflow() else None

    # Discover skills with workflow config
    skills_root = project_root / config.paths.skills_root
    registry = SkillRegistry(skills_root)
    registry.discover(workflow=workflow)

    # Calculate phase gate based on auto_to_max setting
    # auto_to_max=true: allow phases 1 to max_allowed_phase
    # auto_to_max=false: only allow current_phase
    if config.phase_gate.auto_to_max:
        config_max_phase = config.phase_gate.max_allowed_phase
        if config_max_phase is not None:
            max_allowed_phase = config_max_phase
        else:
            phase_gate = PhaseGate()
            max_allowed_phase = phase_gate.get_max_allowed_phase(tasks)
        target_phase = None  # Allow any phase up to max
    else:
        # Only allow current_phase
        max_allowed_phase = config.current_phase or 1
        target_phase = config.current_phase or 1

    # Get enabled domains
    enabled_domains = config.work_scope.enabled_domains

    # Select next task using priority engine
    priority_engine = PriorityEngine()
    next_task_dict = priority_engine.select_next_task(
        tasks,
        max_allowed_phase,
        enabled_domains=enabled_domains,
        target_phase=target_phase
    )

    if not next_task_dict:
        return None, "", "No eligible tasks found (all completed or phase gate blocked)"

    # Convert to Task object for instruction generation
    next_task = Task.from_dict(next_task_dict)

    # Get skill for task
    skill = registry.get_skill(next_task.stage, next_task.phase)
    if skill is None:
        return None, "", f"Skill not found for stage {next_task.stage} phase {next_task.phase}"

    # Generate session ID
    session_id = request_id or str(uuid.uuid4())[:8]

    # Build instruction context
    context = {
        "config": config,
        "project_root": project_root,
        "max_allowed_phase": max_allowed_phase,
        "auto_to_max": config.phase_gate.auto_to_max,
        "session_id": session_id,
        "registry": registry,
    }

    # Generate instruction (pass project_config for project-specific paths)
    instruction_gen = InstructionGeneratorFactory.create(next_task.stage, project_config)
    instruction_text, model_id = instruction_gen.generate(next_task, skill, context)

    # Mark task as assigned
    _mark_task_assigned(tasks, next_task.id, session_id)
    _save_tasks(tasks_path, tasks)

    # Write instruction file
    _write_instruction_file(project_root, session_id, instruction_text, next_task)

    # Return updated task dict
    updated_task_dict = next(
        (t for t in tasks if t.get("id") == next_task.id),
        next_task_dict
    )

    message = (
        f"Assigned {next_task.feature_id} "
        f"(Stage {next_task.stage} Phase {next_task.phase}) "
        f"to session {session_id}"
    )

    return updated_task_dict, instruction_text, message


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
    header = f"""# Choisor Session Instruction
# Session ID: {session_id}
# Task ID: {task.id}
# Feature: {task.feature_id}
# Stage: {task.stage}
# Phase: {task.phase}
# Generated: {datetime.now().isoformat()}
# =============================================================================

"""

    with open(instruction_path, "w", encoding="utf-8") as f:
        f.write(header + instruction_text)
