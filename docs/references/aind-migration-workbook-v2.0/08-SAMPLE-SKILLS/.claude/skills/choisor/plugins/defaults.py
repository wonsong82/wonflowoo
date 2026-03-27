"""Default Plugin Implementations

Default implementations that work with workflow.yaml configuration.
These are used when no custom plugin is registered for a stage.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import yaml

from .base import (
    TaskGeneratorPlugin,
    InstructionGeneratorPlugin,
    ValidatorPlugin,
    ValidationResult,
)

if TYPE_CHECKING:
    from ..config import ChoisorConfig, ProjectConfig, WorkflowConfig, PhaseType
    from ..core import Task, SkillRegistry


class DefaultTaskGeneratorPlugin(TaskGeneratorPlugin):
    """Default task generator that works from workflow.yaml.

    Generates tasks based on phase type:
    - system: One task total
    - domain: One task per domain
    - feature: One task per feature
    """

    def __init__(
        self,
        stage_id: str,
        workflow: "WorkflowConfig",
        project_config: "ProjectConfig",
    ):
        """Initialize with stage and configuration.

        Args:
            stage_id: Stage identifier
            workflow: Workflow configuration
            project_config: Project configuration
        """
        self._stage_id = stage_id
        self._workflow = workflow
        self._project_config = project_config

    @property
    def stage_id(self) -> str:
        return self._stage_id

    def generate(
        self,
        project_root: Path,
        config: "ChoisorConfig",
        workflow: "WorkflowConfig",
        registry: "SkillRegistry",
        project_config: "ProjectConfig",
    ) -> List["Task"]:
        """Generate tasks based on workflow phase types.

        Args:
            project_root: Project root directory
            config: Choisor configuration
            workflow: Workflow definition
            registry: Skill registry
            project_config: Project configuration

        Returns:
            List of Task objects
        """
        from ..core import Task, TaskStatus
        from ..config import PhaseType

        tasks: List[Task] = []

        stage = workflow.get_stage(self._stage_id)
        if not stage:
            return tasks

        # Determine target phases based on phase gate
        target_phases = self._get_target_phases(config, stage)

        # Domain filter
        enabled_domains = None
        if config.work_scope.enabled_domains:
            enabled_domains = [d.upper() for d in config.work_scope.enabled_domains]

        for phase in stage.phases:
            if phase.number not in target_phases:
                continue

            skill = registry.get_skill(stage.number, phase.number)
            if skill is None:
                continue

            if phase.type == PhaseType.SYSTEM:
                # One task total
                task = Task(
                    id=f"{skill.id}-system",
                    stage=stage.number,
                    phase=phase.number,
                    skill_id=skill.id,
                    feature_id="SYSTEM",
                    domain="ALL",
                    status=TaskStatus.PENDING,
                    title=f"[{skill.id}] {phase.name}",
                    metadata={
                        "task_type": "system",
                        "phase_id": phase.id,
                        "source": "workflow",
                    },
                )
                tasks.append(task)

            elif phase.type == PhaseType.DOMAIN:
                # One task per domain
                domains = self._get_domains(project_root, config, workflow)
                for domain_info in domains:
                    domain = domain_info["domain"]
                    if enabled_domains and domain not in enabled_domains:
                        continue

                    task = Task(
                        id=f"{skill.id}-{domain}",
                        stage=stage.number,
                        phase=phase.number,
                        skill_id=skill.id,
                        feature_id=f"DOMAIN-{domain}",
                        domain=domain,
                        status=TaskStatus.PENDING,
                        title=f"[{skill.id}] {domain} Domain",
                        priority=self._calculate_priority(
                            domain_info.get("priority_label", "P2-Core")
                        ),
                        metadata={
                            "task_type": "domain",
                            "phase_id": phase.id,
                            "priority_label": domain_info.get("priority_label"),
                            "feature_count": domain_info.get("feature_count", 0),
                            "source": "workflow",
                        },
                    )
                    tasks.append(task)

            else:  # PhaseType.FEATURE
                # One task per feature
                features = self._get_features(project_root, config, workflow)
                for feature_info in features:
                    domain = feature_info["domain"]
                    if enabled_domains and domain not in enabled_domains:
                        continue

                    feature_id = feature_info["feature_id"]

                    # Skip GAP features if configured
                    if (
                        project_config.feature.skip_gap_features
                        and project_config.feature.gap_suffix in feature_id
                    ):
                        continue

                    task = Task(
                        id=f"{skill.id}-{feature_id}",
                        stage=stage.number,
                        phase=phase.number,
                        skill_id=skill.id,
                        feature_id=feature_id,
                        domain=domain,
                        status=TaskStatus.PENDING,
                        title=f"[{skill.id}] {feature_id} - {feature_info.get('name', '')}",
                        priority=self._calculate_priority(
                            feature_info.get("priority_label", "P2-Core"),
                            feature_info.get("complexity", "medium"),
                        ),
                        metadata={
                            "task_type": "feature",
                            "phase_id": phase.id,
                            "priority_label": feature_info.get("priority_label"),
                            "screen_id": feature_info.get("screen_id"),
                            "name": feature_info.get("name"),
                            "complexity": feature_info.get("complexity"),
                            "source": "workflow",
                        },
                    )
                    tasks.append(task)

        return tasks

    def _get_target_phases(
        self, config: "ChoisorConfig", stage: Any
    ) -> List[int]:
        """Get target phase numbers based on phase gate settings.

        Generate tasks only for current_phase.
        auto_to_max handling is done at instruction generation time:
        - auto_to_max=true: instruction tells agent to proceed to max_allowed_phase
        - auto_to_max=false: instruction tells agent to complete only current_phase
        """
        current_phase = config.current_phase or 1
        return [current_phase]

    def _get_domains(
        self,
        project_root: Path,
        config: "ChoisorConfig",
        workflow: "WorkflowConfig",
    ) -> List[Dict[str, Any]]:
        """Get domain information from feature inventory."""
        domains = []
        seen_domains = set()

        # Get feature inventory path from workflow task_sources
        source = workflow.task_sources.get("feature_inventory")
        if source and source.pattern:
            specs_root = project_root / config.paths.specs_root

            # Find all feature inventory files
            for inv_file in specs_root.glob(source.pattern.replace(
                config.paths.specs_root + "/", ""
            )):
                try:
                    with open(inv_file, "r", encoding="utf-8") as f:
                        inventory = yaml.safe_load(f) or {}
                except (yaml.YAMLError, IOError):
                    continue

                # Extract domain from path
                # Pattern: phase1/{priority}/{domain}/feature-inventory.yaml
                parts = inv_file.relative_to(specs_root).parts
                if len(parts) >= 3:
                    priority_dir = parts[-3]  # P0, P1, etc.
                    domain = parts[-2].upper()

                    if domain not in seen_domains:
                        seen_domains.add(domain)
                        domains.append({
                            "domain": domain,
                            "priority_label": self._priority_dir_to_label(priority_dir),
                            "feature_count": len(inventory.get("features", [])),
                        })

        return domains

    def _get_features(
        self,
        project_root: Path,
        config: "ChoisorConfig",
        workflow: "WorkflowConfig",
    ) -> List[Dict[str, Any]]:
        """Get feature information from feature inventory."""
        features = []

        source = workflow.task_sources.get("feature_inventory")
        if source and source.pattern:
            specs_root = project_root / config.paths.specs_root

            for inv_file in specs_root.glob(source.pattern.replace(
                config.paths.specs_root + "/", ""
            )):
                try:
                    with open(inv_file, "r", encoding="utf-8") as f:
                        inventory = yaml.safe_load(f) or {}
                except (yaml.YAMLError, IOError):
                    continue

                parts = inv_file.relative_to(specs_root).parts
                if len(parts) >= 3:
                    priority_dir = parts[-3]
                    domain = parts[-2].upper()
                    priority_label = self._priority_dir_to_label(priority_dir)

                    for feature in inventory.get("features", []):
                        features.append({
                            "feature_id": feature.get("feature_id", ""),
                            "domain": domain,
                            "priority_label": priority_label,
                            "screen_id": feature.get("screen_id", ""),
                            "name": feature.get("name", ""),
                            "complexity": feature.get("complexity", "medium"),
                        })

        return features

    def _priority_dir_to_label(self, priority_dir: str) -> str:
        """Convert priority directory name to priority label."""
        mapping = {
            "P0": "P0-Foundation",
            "P1": "P1-Hub",
            "P2": "P2-Core",
            "P3": "P3-Supporting",
        }
        return mapping.get(priority_dir, "P2-Core")

    def _calculate_priority(
        self, priority_label: str, complexity: str = "medium"
    ) -> int:
        """Calculate numeric priority from label and complexity."""
        base_map = {
            "P0-Foundation": 10,
            "P1-Hub": 8,
            "P2-Core": 5,
            "P3-Supporting": 3,
        }
        base = base_map.get(priority_label, 5)

        complexity_adjust = {
            "low": 1,
            "medium": 0,
            "high": -1,
        }
        adjust = complexity_adjust.get(complexity.lower(), 0)

        return max(1, min(10, base + adjust))


class DefaultInstructionGeneratorPlugin(InstructionGeneratorPlugin):
    """Default instruction generator using skill invocation."""

    def __init__(
        self,
        stage_id: str,
        workflow: "WorkflowConfig",
        project_config: "ProjectConfig",
    ):
        self._stage_id = stage_id
        self._workflow = workflow
        self._project_config = project_config

    @property
    def stage_id(self) -> str:
        return self._stage_id

    def generate(
        self,
        task: "Task",
        config: "ChoisorConfig",
        workflow: "WorkflowConfig",
        project_config: "ProjectConfig",
    ) -> str:
        """Generate default instruction using skill invocation.

        Args:
            task: Task to generate instructions for
            config: Choisor configuration
            workflow: Workflow definition
            project_config: Project configuration

        Returns:
            Instruction text
        """
        stage = workflow.get_stage(self._stage_id)
        if not stage:
            return f"Execute task: {task.title}"

        phase = stage.get_phase_by_number(task.phase)
        if not phase:
            return f"Execute task: {task.title}"

        skill_name = phase.skill or task.skill_id

        instruction = f"""Execute skill: /{skill_name}

Task: {task.title}
Domain: {task.domain}
Feature: {task.feature_id}

Follow the skill instructions to complete this task."""

        return instruction


class DefaultValidatorPlugin(ValidatorPlugin):
    """Default validator checking for expected output files."""

    def __init__(
        self,
        stage_id: str,
        workflow: "WorkflowConfig",
        project_config: "ProjectConfig",
    ):
        self._stage_id = stage_id
        self._workflow = workflow
        self._project_config = project_config

    @property
    def stage_id(self) -> str:
        return self._stage_id

    def validate(
        self,
        task: "Task",
        output_path: Path,
        workflow: "WorkflowConfig",
    ) -> ValidationResult:
        """Validate task output by checking expected files exist.

        Args:
            task: Completed task
            output_path: Path to task outputs
            workflow: Workflow definition

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        expected = self.get_expected_outputs(task, workflow)
        if not expected:
            # No expected outputs defined, assume valid
            return result

        for pattern in expected:
            # Check if pattern contains wildcard
            if "*" in pattern:
                matches = list(output_path.glob(pattern))
                if not matches:
                    result.add_warning(f"No files matching pattern: {pattern}")
            else:
                file_path = output_path / pattern
                if not file_path.exists():
                    result.add_error(f"Missing expected file: {pattern}")

        return result
