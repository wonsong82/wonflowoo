"""Scan command - Feature scanning and task generation

Scans for tasks based on the current stage:
- Stage 1: Scan legacy source for controller/handler files
- Stage 4: Scan spec files for code generation tasks
- Stage 5: Scan completed Stage 4 tasks for assurance tasks

Automatically syncs tasks after scanning.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..core import SkillRegistry, Task, TaskStatus
from ..config import ChoisorConfig, ConfigLoader
from ..generators import TaskGeneratorFactory, create_task_generator


def handle_scan(
    project_root: Path,
    stage: Optional[int] = None
) -> Dict[str, Any]:
    """Scan for tasks and update tasks.json.

    Scans for features based on the current or specified stage
    and generates tasks for each feature found.

    Args:
        project_root: Project root path
        stage: Optional stage number to scan (uses current_stage if not specified)

    Returns:
        Scan result dictionary with counts
    """
    print(f"\n=== Scanning Feature Inventory ===\n")

    # Load config
    loader = ConfigLoader(project_root)
    config = loader.load()

    # Load project-specific config (defaults to hallain settings if not present)
    project_config = loader.load_project()

    # Ensure .choisor/tasks directory exists
    tasks_dir = project_root / ".choisor" / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    # Check for workflow.yaml (plugin mode)
    workflow = loader.load_workflow() if loader.has_workflow() else None
    workflow_mode = workflow is not None

    # Discover skills with workflow config
    skills_root = project_root / config.paths.skills_root
    registry = SkillRegistry(skills_root)
    registry.discover(workflow=workflow)

    # Determine stage to scan
    target_stage = stage if stage is not None else config.current_stage
    print(f"Target Stage: {target_stage}")

    # Work scope info
    if config.work_scope.enabled_domains:
        domains = ", ".join(d.upper() for d in config.work_scope.enabled_domains)
        print(f"Enabled Domains: {domains}")
    else:
        print("Enabled Domains: All")

    print(f"Mode: {'Plugin (workflow.yaml)' if workflow_mode else 'Legacy'}")
    print()

    # Use unified generator (auto-detects workflow.yaml)
    unified_generator = create_task_generator(project_root)

    # Generate new tasks
    new_tasks = unified_generator.generate(
        stage=target_stage,
        config=config,
        registry=registry,
        project_config=project_config,
    )
    print(f"Scanned {len(new_tasks)} features for Stage {target_stage}")

    # Load existing tasks
    tasks_path = tasks_dir / "tasks.json"
    existing_tasks = _load_existing_tasks(tasks_path)

    # Merge tasks (preserve existing, add new)
    merged_tasks, added_count, updated_count = _merge_tasks(
        existing_tasks, new_tasks
    )

    # Save merged tasks
    _save_tasks(tasks_path, merged_tasks)

    # Auto-sync after scan
    print(f"\n=== Synchronizing Task States ===\n")
    from .sync import handle_sync
    handle_sync(project_root, auto_mode=True)

    # Print results
    print(f"\nResults:")
    print(f"  New tasks: {added_count}")
    print(f"  Updated tasks: {updated_count}")
    print(f"  Total tasks: {len(merged_tasks)}")
    print()

    result = {
        "added": added_count,
        "updated": updated_count,
        "total": len(merged_tasks),
        "stage": target_stage,
    }

    return result


def _load_existing_tasks(tasks_path: Path) -> List[Dict[str, Any]]:
    """Load existing tasks from JSON file.

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


def _merge_tasks(
    existing: List[Dict[str, Any]],
    new_tasks: List[Task]
) -> tuple[List[Dict[str, Any]], int, int]:
    """Merge new tasks with existing tasks.

    Preserves existing task status and metadata while updating
    from new task scan.

    Args:
        existing: Existing task dictionaries
        new_tasks: Newly scanned Task objects

    Returns:
        Tuple of (merged_tasks, added_count, updated_count)
    """
    # Index existing tasks by feature_id
    existing_by_feature: Dict[str, Dict[str, Any]] = {}
    for task in existing:
        feature_id = (
            task.get("feature_id")
            or task.get("metadata", {}).get("feature_id")
            or task.get("category")
        )
        if feature_id:
            # Use composite key: feature_id + stage + phase
            stage = task.get("stage", 1)
            phase = task.get("phase", task.get("metadata", {}).get("phase", 1))
            key = f"{feature_id}:{stage}:{phase}"
            existing_by_feature[key] = task

    merged: List[Dict[str, Any]] = []
    added_count = 0
    updated_count = 0
    processed_keys = set()

    # Process new tasks
    for new_task in new_tasks:
        key = f"{new_task.feature_id}:{new_task.stage}:{new_task.phase}"

        if key in existing_by_feature:
            # Update existing task with new metadata
            existing_task = existing_by_feature[key]
            _update_task_metadata(existing_task, new_task)
            merged.append(existing_task)
            updated_count += 1
        else:
            # Add new task
            merged.append(new_task.to_dict())
            added_count += 1

        processed_keys.add(key)

    # Keep existing tasks not in new scan
    for key, task in existing_by_feature.items():
        if key not in processed_keys:
            merged.append(task)

    return merged, added_count, updated_count


def _update_task_metadata(
    existing: Dict[str, Any],
    new_task: Task
) -> None:
    """Update existing task with metadata from new scan.

    Preserves status, timestamps, and session info while
    updating metadata fields.

    Args:
        existing: Existing task dictionary
        new_task: New Task object from scan
    """
    new_dict = new_task.to_dict()
    metadata = existing.get("metadata", {})

    # Update select fields from new task
    for key in ["priority_label", "spec_path", "controller_path", "source"]:
        if key in new_dict.get("metadata", {}):
            metadata[key] = new_dict["metadata"][key]

    # Update complexity if provided
    if "complexity_estimate" in new_dict.get("metadata", {}):
        metadata["complexity_estimate"] = new_dict["metadata"]["complexity_estimate"]
    if "complexity_reasoning" in new_dict.get("metadata", {}):
        metadata["complexity_reasoning"] = new_dict["metadata"]["complexity_reasoning"]
    if "endpoint_count" in new_dict.get("metadata", {}):
        metadata["endpoint_count"] = new_dict["metadata"]["endpoint_count"]

    existing["metadata"] = metadata

    # Update description and estimated duration
    existing["description"] = new_dict.get("description", existing.get("description", ""))
    if new_dict.get("estimated_duration"):
        existing["estimated_duration"] = new_dict["estimated_duration"]


def _save_tasks(tasks_path: Path, tasks: List[Dict[str, Any]]) -> None:
    """Save tasks to JSON file.

    Args:
        tasks_path: Path to tasks.json
        tasks: List of task dictionaries
    """
    with open(tasks_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
