"""Generator Base Classes - Abstract interfaces for task and instruction generation

Provides abstract base classes for:
- TaskGenerator: Creates tasks from project source scanning
- InstructionGenerator: Creates instructions for Claude sessions
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import json

from ..core import Task, TaskStatus, Skill, SkillRegistry
from ..config import ChoisorConfig


class TaskGenerator(ABC):
    """Abstract base class for task generators.

    Task generators are responsible for creating Task objects from
    project source scanning. Each stage may have a specialized
    generator that understands its specific input format.

    Example:
        >>> generator = Stage4TaskGenerator()
        >>> tasks = generator.generate(project_root, config, registry)
        >>> for task in tasks:
        ...     print(task.feature_id, task.skill_id)
    """

    @abstractmethod
    def get_stage(self) -> int:
        """Return stage number (1-5).

        Returns:
            Stage number this generator handles
        """
        pass

    @abstractmethod
    def generate(
        self,
        project_root: Path,
        config: ChoisorConfig,
        registry: SkillRegistry
    ) -> List[Task]:
        """Generate tasks for this stage.

        Args:
            project_root: Project root path
            config: Choisor configuration
            registry: Skill registry for skill lookups

        Returns:
            List of Task objects
        """
        pass

    def scan_and_save(
        self,
        project_root: Path,
        config: ChoisorConfig,
        registry: SkillRegistry,
        tasks_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Scan and save tasks to JSON file.

        Generates tasks, merges with existing tasks (avoiding duplicates),
        and saves to the tasks file.

        Args:
            project_root: Project root path
            config: Choisor configuration
            registry: Skill registry for skill lookups
            tasks_path: Optional path to tasks JSON file

        Returns:
            Result dict with added, skipped, and total counts
        """
        # Determine tasks file path
        if tasks_path is None:
            tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"

        # Load existing tasks
        existing_tasks: List[Dict[str, Any]] = []
        if tasks_path.exists():
            try:
                with open(tasks_path, "r", encoding="utf-8") as f:
                    existing_tasks = json.load(f)
            except (json.JSONDecodeError, IOError):
                existing_tasks = []

        # Get existing feature IDs for this stage to prevent duplicates
        stage = self.get_stage()
        existing_feature_ids = {
            t.get("feature_id")
            for t in existing_tasks
            if t.get("stage") == stage and t.get("feature_id")
        }

        # Generate new tasks
        new_tasks = self.generate(project_root, config, registry)

        # Merge, avoiding duplicates
        added_count = 0
        skipped_count = 0

        for task in new_tasks:
            if task.feature_id in existing_feature_ids:
                skipped_count += 1
                continue
            existing_tasks.append(task.to_dict())
            existing_feature_ids.add(task.feature_id)
            added_count += 1

        # Save
        tasks_path.parent.mkdir(parents=True, exist_ok=True)
        with open(tasks_path, "w", encoding="utf-8") as f:
            json.dump(existing_tasks, f, indent=2, ensure_ascii=False)

        result = {
            "added": added_count,
            "skipped": skipped_count,
            "total": len(existing_tasks),
            "stage": stage,
        }

        return result

    def get_summary(
        self,
        project_root: Path,
        tasks_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Get summary of tasks by domain for this stage.

        Args:
            project_root: Project root path
            tasks_path: Optional path to tasks JSON file

        Returns:
            Summary dict with domain breakdown
        """
        if tasks_path is None:
            tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"

        if not tasks_path.exists():
            return {"error": "tasks.json not found"}

        with open(tasks_path, "r", encoding="utf-8") as f:
            tasks = json.load(f)

        stage = self.get_stage()
        stage_tasks = [t for t in tasks if t.get("stage") == stage]

        summary: Dict[str, Any] = {
            "stage": stage,
            "total": len(stage_tasks),
            "domains": {},
        }

        # Aggregate by domain
        for task in stage_tasks:
            domain = task.get("domain", "unknown").upper()
            status = task.get("status", "unknown")

            if domain not in summary["domains"]:
                summary["domains"][domain] = {"total": 0, "by_status": {}}

            summary["domains"][domain]["total"] += 1
            summary["domains"][domain]["by_status"][status] = (
                summary["domains"][domain]["by_status"].get(status, 0) + 1
            )

        return summary

    def _get_priority_label(self, domain: str, config: ChoisorConfig) -> str:
        """Get priority label for a domain.

        Args:
            domain: Domain code (e.g., "PA", "CM")
            config: Choisor configuration

        Returns:
            Priority label (e.g., "P0-Foundation", "P2-Core")
        """
        domain_lower = domain.lower()
        for label, domains in config.domain_priority_map.items():
            if domain_lower in [d.lower() for d in domains]:
                return label
        return "P2-Core"  # Default priority


class InstructionGenerator(ABC):
    """Abstract base class for instruction generators.

    Instruction generators create the textual instructions that guide
    Claude sessions in executing tasks. Each stage may have specialized
    instruction formatting.

    Example:
        >>> generator = DefaultInstructionGenerator()
        >>> instruction, model_id = generator.generate(task, skill, context)
        >>> print(instruction)  # Multi-line instruction text
    """

    @abstractmethod
    def generate(
        self,
        task: Task,
        skill: Skill,
        context: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Generate instruction text and model ID.

        Args:
            task: Task to generate instruction for
            skill: Skill associated with the task
            context: Additional context containing:
                - config: ChoisorConfig
                - project_root: Path
                - session_id: str
                - max_allowed_phase: int
                - auto_to_max: bool
                - all_tasks: List[Task]

        Returns:
            Tuple of (instruction_text, model_id)
        """
        pass

    def _build_header(self, task: Task, skill: Skill) -> List[str]:
        """Build common instruction header.

        Args:
            task: Task object
            skill: Skill object

        Returns:
            List of header lines
        """
        return [
            f"# {task.title}",
            "",
            "## Task Information",
            f"- **Feature ID**: {task.feature_id}",
            f"- **Domain**: {task.domain.upper()}",
            f"- **Stage**: {task.stage}",
            f"- **Phase**: {task.phase}",
            f"- **Skill**: {skill.id}",
            "",
        ]

    def _build_skill_section(self, skill: Skill) -> List[str]:
        """Build skill invocation section.

        Args:
            skill: Skill object

        Returns:
            List of skill section lines
        """
        return [
            "## Required Skill",
            "",
            f"**You MUST invoke the `{skill.name}` skill:**",
            "",
            "```",
            f"{skill.invocation}",
            "```",
            "",
        ]

    def _build_environment_section(
        self,
        task: Task,
        project_root: Path,
        config: ChoisorConfig
    ) -> List[str]:
        """Build environment information section.

        Args:
            task: Task object
            project_root: Project root path
            config: Choisor configuration

        Returns:
            List of environment section lines
        """
        return [
            "## Project Environment",
            f"- **Project Root**: {project_root}",
            f"- **Source Code**: {config.paths.source_base}/",
            f"- **Specs Output**: {config.paths.specs_root}/",
            "",
        ]

    def _build_output_path_section(
        self,
        task: Task,
        config: ChoisorConfig,
        max_allowed_phase: int,
        auto_to_max: bool
    ) -> List[str]:
        """Build output path section.

        Args:
            task: Task object
            config: Choisor configuration
            max_allowed_phase: Maximum allowed phase number
            auto_to_max: Whether to auto-advance to max phase

        Returns:
            List of output path section lines
        """
        stage_output = config.paths.stage_outputs.get(
            task.stage, f"stage{task.stage}-outputs"
        )
        priority_label = self._get_priority_label(task.domain, config)
        base_output = f"{config.paths.specs_root}/{stage_output}"

        lines = [
            "## Output Path",
            "",
        ]

        if auto_to_max and max_allowed_phase > task.phase:
            lines.append("**Output paths for each phase:**")
            lines.append("")
            for phase in range(task.phase, max_allowed_phase + 1):
                output_path = (
                    f"{base_output}/phase{phase}/{priority_label}/"
                    f"{task.domain.upper()}/{task.feature_id}/"
                )
                lines.append(f"- **Phase {phase}**: `{output_path}`")
            lines.append("")
        else:
            output_path = (
                f"{base_output}/phase{task.phase}/{priority_label}/"
                f"{task.domain.upper()}/{task.feature_id}/"
            )
            lines.append(f"**All outputs should be written to:** `{output_path}`")
            lines.append("")

        return lines

    def _build_commit_section(
        self,
        task: Task,
        context: Dict[str, Any]
    ) -> List[str]:
        """Build commit instruction section.

        Args:
            task: Task object
            context: Context dict with config and session_id

        Returns:
            List of commit section lines
        """
        config: ChoisorConfig = context.get("config")
        if config is None or not config.auto_commit.enabled:
            return []

        if not config.auto_commit.commit_on_completion:
            return []

        session_id = context.get("session_id", "")

        return [
            "## Commit on Completion",
            "",
            "Commit your changes after completing the task.",
            "",
            "Commit message template:",
            "```",
            f"stage{task.stage} phase{task.phase} completion for {task.feature_id}",
            "",
            f"Session ID: {session_id}",
            f"Domain: {task.domain.upper()}",
            f"Skill: {task.skill_id}",
            "```",
            "",
        ]

    def _get_priority_label(self, domain: str, config: ChoisorConfig) -> str:
        """Get priority label for a domain.

        Args:
            domain: Domain code
            config: Choisor configuration

        Returns:
            Priority label
        """
        domain_lower = domain.lower()
        for label, domains in config.domain_priority_map.items():
            if domain_lower in [d.lower() for d in domains]:
                return label
        return "P2-Core"
