"""Clean Restart command - Reset features to clean state for rework

Provides functionality to restart features from a target phase:
- Backs up existing outputs
- Deletes outputs from target phase onwards
- Resets task status to pending
- Optionally runs scan to refresh tasks
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..config import ConfigLoader


def handle_clean_restart(
    project_root: Path,
    feature_ids: List[str],
    target_phase: int = 2,
    backup: bool = True,
    auto_scan: bool = True
) -> Dict[str, Any]:
    """Reset features to clean state for rework.

    Deletes outputs from target_phase onwards and resets tasks
    to pending status, enabling rework from a specific phase.

    Args:
        project_root: Project root path
        feature_ids: List of feature IDs to restart
        target_phase: Phase to restart from (default: 2)
        backup: Whether to create backup (default: True)
        auto_scan: Whether to run scan after restart (default: True)

    Returns:
        Result dictionary with operation details
    """
    print(f"\n=== Choisor Clean Restart ===\n")

    if not feature_ids:
        return {"success": False, "error": "No feature IDs provided"}

    # Remove empty strings
    feature_ids = [f for f in feature_ids if f]

    if not feature_ids:
        return {"success": False, "error": "No valid feature IDs provided"}

    # Load config
    loader = ConfigLoader(project_root)
    config = loader.load()

    # Validate target phase
    if target_phase < 1 or target_phase > 5:
        return {"success": False, "error": f"Invalid target_phase: {target_phase}"}

    print(f"Clean Restart Configuration:")
    print(f"  Features: {len(feature_ids)}")
    print(f"  Target Phase: {target_phase}")
    print(f"  Backup: {'Yes' if backup else 'No'}")
    print(f"  Auto Scan: {'Yes' if auto_scan else 'No'}")
    print()

    # Determine phases to clean (target and all downstream)
    phases_to_clean = list(range(target_phase, 6))  # target_phase to 5
    print(f"Phases to clean: {', '.join(map(str, phases_to_clean))}")
    print(f"Reason: Cleaning phase {target_phase} invalidates all downstream phases")
    print()

    # Specs root
    specs_root = project_root / config.paths.specs_root

    # Step 1: Backup outputs if requested
    backup_root = None
    if backup:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_root = Path(f"/tmp/choisor_clean_restart_backup_{timestamp}")
        backup_root.mkdir(parents=True, exist_ok=True)

        print(f"1. Backing up outputs...")
        print(f"   Backup location: {backup_root}")
        print()

        backed_up = _backup_outputs(
            specs_root, feature_ids, phases_to_clean, backup_root, config
        )
        print(f"   Backed up {backed_up} output directories")
        print()

    # Step 2: Delete outputs
    print(f"2. Deleting outputs...")
    deleted = _delete_outputs(specs_root, feature_ids, phases_to_clean, config)
    print(f"   Deleted {deleted} output directories")
    print()

    # Step 3: Reset tasks in tasks.json
    print(f"3. Resetting tasks to phase {target_phase} pending...")
    tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"
    reset_count = _reset_tasks(tasks_path, feature_ids, target_phase)
    print(f"   Reset {reset_count} task(s)")
    print()

    # Step 4: Auto scan if requested
    if auto_scan:
        print(f"4. Running scan to update task states...")
        print()
        from .scan import handle_scan
        handle_scan(project_root)

    print()
    print("=" * 80)
    print(f"\nClean Restart Complete!")
    print(f"  - Features: {len(feature_ids)}")
    print(f"  - Target Phase: {target_phase}")
    if backup_root:
        print(f"  - Backup: {backup_root}")
    print()
    print("Next steps:")
    print("  1. Run /choisor status to verify")
    print("  2. Assign tasks with daemon or manual assignment")
    print("=" * 80)

    return {
        "success": True,
        "features": feature_ids,
        "target_phase": target_phase,
        "deleted": deleted,
        "reset_tasks": reset_count,
        "backup_path": str(backup_root) if backup_root else None,
    }


def _backup_outputs(
    specs_root: Path,
    feature_ids: List[str],
    phases_to_clean: List[int],
    backup_root: Path,
    config: Any
) -> int:
    """Backup output directories before deletion.

    Args:
        specs_root: Specs root directory
        feature_ids: Feature IDs to backup
        phases_to_clean: Phases to backup
        backup_root: Backup destination directory
        config: Choisor configuration

    Returns:
        Number of directories backed up
    """
    backed_up = 0

    for phase in phases_to_clean:
        stage_output = config.paths.stage_outputs.get(1, "stage1-outputs")
        phase_output = specs_root / stage_output / f"phase{phase}"

        if not phase_output.exists():
            continue

        for feat_id in feature_ids:
            feat_dirs = _find_feature_directories(phase_output, feat_id)

            for feat_dir in feat_dirs:
                backup_path = backup_root / f"phase{phase}" / feat_id
                try:
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                    shutil.copytree(feat_dir, backup_path)
                    backed_up += 1
                    print(f"   + phase{phase}/{feat_id}")
                except Exception as e:
                    print(f"   x phase{phase}/{feat_id} - {e}")

    return backed_up


def _delete_outputs(
    specs_root: Path,
    feature_ids: List[str],
    phases_to_clean: List[int],
    config: Any
) -> int:
    """Delete output directories.

    Args:
        specs_root: Specs root directory
        feature_ids: Feature IDs to delete
        phases_to_clean: Phases to delete
        config: Choisor configuration

    Returns:
        Number of directories deleted
    """
    deleted = 0

    for phase in phases_to_clean:
        stage_output = config.paths.stage_outputs.get(1, "stage1-outputs")
        phase_output = specs_root / stage_output / f"phase{phase}"

        if not phase_output.exists():
            continue

        for feat_id in feature_ids:
            feat_dirs = _find_feature_directories(phase_output, feat_id)

            for feat_dir in feat_dirs:
                try:
                    shutil.rmtree(feat_dir)
                    deleted += 1
                except Exception as e:
                    print(f"   x {feat_id} - {e}")

    return deleted


def _find_feature_directories(phase_output: Path, feature_id: str) -> List[Path]:
    """Find all directories matching feature ID in phase output.

    Args:
        phase_output: Phase output directory
        feature_id: Feature ID to find

    Returns:
        List of matching directory paths
    """
    matches = []

    # Search pattern: phase_output/{priority}/{domain}/{feature_id}
    for priority_dir in phase_output.iterdir():
        if not priority_dir.is_dir():
            continue

        for domain_dir in priority_dir.iterdir():
            if not domain_dir.is_dir():
                continue

            feat_dir = domain_dir / feature_id
            if feat_dir.exists() and feat_dir.is_dir():
                matches.append(feat_dir)

    return matches


def _reset_tasks(
    tasks_path: Path,
    feature_ids: List[str],
    target_phase: int
) -> int:
    """Reset tasks to pending for target phase.

    Args:
        tasks_path: Path to tasks.json
        feature_ids: Feature IDs to reset
        target_phase: Phase to reset to

    Returns:
        Number of tasks reset
    """
    if not tasks_path.exists():
        print("   Warning: tasks.json not found - skipping task reset")
        return 0

    try:
        with open(tasks_path, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    except (json.JSONDecodeError, IOError):
        print("   Warning: Could not read tasks.json")
        return 0

    # Create backup
    backup_path = f"{tasks_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    print(f"   Backed up tasks.json to: {backup_path}")

    # Convert feature_ids to set for faster lookup
    feature_id_set = set(feature_ids)
    reset_count = 0

    # Reset matching tasks
    for task in tasks:
        task_feature = (
            task.get("feature_id")
            or task.get("metadata", {}).get("feature_id")
            or task.get("category")
        )

        if task_feature in feature_id_set:
            # Get task's current phase
            task_phase = task.get("phase", task.get("metadata", {}).get("phase", 1))

            # Reset if task phase >= target_phase
            if task_phase >= target_phase:
                task["status"] = "pending"
                task["completed_at"] = None
                task["assigned_session"] = None
                task["skip_reason"] = None
                task["updated_at"] = datetime.now().isoformat()

                # Update phase in metadata if needed
                metadata = task.get("metadata", {})
                metadata["phase"] = target_phase
                task["metadata"] = metadata

                reset_count += 1

    # Remove duplicate phase tasks (if resetting to earlier phase)
    if target_phase < 3:
        tasks_to_keep = []
        seen_features = {}

        for task in tasks:
            task_feature = (
                task.get("feature_id")
                or task.get("metadata", {}).get("feature_id")
                or task.get("category")
            )
            task_phase = task.get("phase", task.get("metadata", {}).get("phase", 1))

            if task_feature in feature_id_set:
                # Keep only lowest phase task
                key = f"{task_feature}:{task.get('stage', 1)}"
                if key not in seen_features or task_phase < seen_features[key]["phase"]:
                    seen_features[key] = {"phase": task_phase, "task": task}
            else:
                tasks_to_keep.append(task)

        # Add back the kept feature tasks
        for data in seen_features.values():
            tasks_to_keep.append(data["task"])

        tasks = tasks_to_keep

    # Save updated tasks
    with open(tasks_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

    return reset_count
