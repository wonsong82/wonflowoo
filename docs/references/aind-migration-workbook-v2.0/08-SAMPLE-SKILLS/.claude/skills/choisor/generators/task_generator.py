"""Task Generators - Factory pattern for stage-specific task generation

Provides task generators for each migration stage:
- DefaultTaskGenerator: Generic generator for stages without specific logic
- Stage1TaskGenerator: Discovery stage task generation from controller scan
- Stage4TaskGenerator: Code generation tasks from spec files
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Type, Optional

import yaml

from .base import TaskGenerator
from ..core import Task, TaskStatus, SkillRegistry
from ..config import ChoisorConfig, ProjectConfig


class DefaultTaskGenerator(TaskGenerator):
    """Default task generator for stages without specific logic.

    Used for stages that follow a generic pattern of reading
    feature inventory and creating tasks for each feature.
    """

    def __init__(self, stage: int):
        """Initialize with stage number.

        Args:
            stage: Stage number (1-5)
        """
        self._stage = stage

    def get_stage(self) -> int:
        """Return stage number."""
        return self._stage

    def generate(
        self,
        project_root: Path,
        config: ChoisorConfig,
        registry: SkillRegistry
    ) -> List[Task]:
        """Generate tasks from feature specs.

        Scans the specs directory for feature definitions and
        creates a task for each feature.

        Args:
            project_root: Project root path
            config: Choisor configuration
            registry: Skill registry for skill lookups

        Returns:
            List of Task objects
        """
        tasks: List[Task] = []

        # Get the default skill for this stage (phase 1)
        skill = registry.get_skill(self._stage, 1)
        if skill is None:
            return tasks

        # Look for feature inventory
        specs_root = project_root / config.paths.specs_root
        stage_output_dir = config.paths.stage_outputs.get(
            self._stage, f"stage{self._stage}-outputs"
        )
        inventory_path = specs_root / stage_output_dir / "feature-inventory.yaml"

        if not inventory_path.exists():
            return tasks

        # Read feature inventory
        try:
            with open(inventory_path, "r", encoding="utf-8") as f:
                inventory = yaml.safe_load(f) or {}
        except (yaml.YAMLError, IOError):
            return tasks

        # Domain filter
        enabled_domains = None
        if config.work_scope.enabled_domains:
            enabled_domains = [d.upper() for d in config.work_scope.enabled_domains]

        # Create tasks for each feature
        features = inventory.get("features", [])
        for feature in features:
            feature_id = feature.get("feature_id", "")
            domain = feature.get("domain", "").upper()

            if enabled_domains and domain not in enabled_domains:
                continue

            priority_label = self._get_priority_label(domain, config)

            task = Task(
                id=f"{skill.id}-{feature_id}",
                stage=self._stage,
                phase=1,
                skill_id=skill.id,
                feature_id=feature_id,
                domain=domain,
                status=TaskStatus.PENDING,
                title=f"[{skill.id}] {feature_id}",
                priority=self._calculate_priority(priority_label),
                metadata={
                    "priority_label": priority_label,
                    "source": "feature-inventory",
                }
            )
            tasks.append(task)

        return tasks

    def _calculate_priority(self, priority_label: str) -> int:
        """Calculate numeric priority from label.

        Args:
            priority_label: Priority label (e.g., "P0-Foundation")

        Returns:
            Numeric priority (1-10, higher = more important)
        """
        priority_map = {
            "P0-Foundation": 10,
            "P1-Hub": 8,
            "P2-Core": 5,
            "P3-Supporting": 3,
        }
        return priority_map.get(priority_label, 5)


class Stage1TaskGenerator(TaskGenerator):
    """Stage 1 (Discovery) task generator.

    Generates discovery tasks from feature inventory files
    located in work/specs/stage1-outputs/phase1/{priority}/{domain}/.

    Respects phase_types configuration:
    - domain: One task per domain (e.g., phase1, phase2)
    - feature: One task per feature (e.g., phase3, phase4)

    Attributes:
        _project_config: Project-specific configuration for phase types.
    """

    def __init__(self, project_config: Optional[ProjectConfig] = None):
        """Initialize with optional project configuration.

        Args:
            project_config: Project-specific config. If None, uses defaults.
        """
        self._project_config = project_config or ProjectConfig()

    def get_stage(self) -> int:
        """Return stage number."""
        return 1

    def generate(
        self,
        project_root: Path,
        config: ChoisorConfig,
        registry: SkillRegistry
    ) -> List[Task]:
        """Generate discovery tasks from feature inventory files.

        Reads feature inventory YAML files from stage1-outputs/phase1
        and creates tasks based on phase_type:
        - domain-level phases: ONE task per domain
        - feature-level phases: ONE task per feature

        Args:
            project_root: Project root path
            config: Choisor configuration
            registry: Skill registry for skill lookups

        Returns:
            List of Task objects
        """
        tasks: List[Task] = []

        # Generate tasks only for current_phase
        # auto_to_max handling is done at instruction generation time:
        # - auto_to_max=true: instruction tells agent to proceed to max_allowed_phase
        # - auto_to_max=false: instruction tells agent to complete only current_phase
        target_phases = [config.current_phase or 1]

        if not target_phases:
            target_phases = [1]

        # Domain filter
        enabled_domains = None
        if config.work_scope.enabled_domains:
            enabled_domains = [d.upper() for d in config.work_scope.enabled_domains]

        # Inventory path: work/specs/stage1-outputs/phase1/{priority}/{domain}/
        specs_root = project_root / config.paths.specs_root
        stage1_output = config.paths.stage_outputs.get(1, "stage1-outputs")
        phase1_path = specs_root / stage1_output / "phase1"

        if not phase1_path.exists():
            return tasks

        # Separate phases by type
        domain_phases = [
            p for p in target_phases
            if self._project_config.phase_types.get_phase_type(1, p) == "domain"
        ]
        feature_phases = [
            p for p in target_phases
            if self._project_config.phase_types.get_phase_type(1, p) == "feature"
        ]

        # Track created domain tasks to avoid duplicates
        created_domain_tasks: Dict[str, bool] = {}

        # Scan priority directories (P0, P1, P2, P3)
        for priority_dir in phase1_path.iterdir():
            if not priority_dir.is_dir():
                continue

            priority_name = priority_dir.name  # e.g., "P0", "P1", "P2", "P3"

            # Map to priority label
            priority_label = self._priority_dir_to_label(priority_name)

            # Scan domain directories
            for domain_dir in priority_dir.iterdir():
                if not domain_dir.is_dir():
                    continue

                # Domain directory name is the domain code (e.g., "CM", "PA")
                domain = domain_dir.name.upper()

                # Skip if domain not in enabled list
                if enabled_domains and domain not in enabled_domains:
                    continue

                # Read feature inventory
                inventory_path = domain_dir / "feature-inventory.yaml"
                if not inventory_path.exists():
                    continue

                try:
                    with open(inventory_path, "r", encoding="utf-8") as f:
                        inventory = yaml.safe_load(f) or {}
                except (yaml.YAMLError, IOError):
                    continue

                # Generate DOMAIN-LEVEL tasks (one per domain per phase)
                for phase in domain_phases:
                    task_key = f"{domain}-phase{phase}"
                    if task_key in created_domain_tasks:
                        continue
                    created_domain_tasks[task_key] = True

                    skill = registry.get_skill(1, phase)
                    if skill is None:
                        continue

                    task = Task(
                        id=f"{skill.id}-{domain}",
                        stage=1,
                        phase=phase,
                        skill_id=skill.id,
                        feature_id=f"DOMAIN-{domain}",
                        domain=domain,
                        status=TaskStatus.PENDING,
                        title=f"[{skill.id}] {domain} Domain",
                        priority=self._calculate_priority(priority_label, "medium"),
                        metadata={
                            "priority_label": priority_label,
                            "task_type": "domain",
                            "inventory_path": str(inventory_path),
                            "feature_count": len(inventory.get("features", [])),
                            "source": "feature-inventory",
                        }
                    )
                    tasks.append(task)

                # Generate FEATURE-LEVEL tasks (one per feature per phase)
                features = inventory.get("features", [])
                for feature in features:
                    feature_id = feature.get("feature_id", "")
                    if not feature_id:
                        continue

                    screen_id = feature.get("screen_id", "")
                    name = feature.get("name", "")
                    complexity = feature.get("complexity", "medium")

                    for phase in feature_phases:
                        skill = registry.get_skill(1, phase)
                        if skill is None:
                            continue

                        task = Task(
                            id=f"{skill.id}-{feature_id}",
                            stage=1,
                            phase=phase,
                            skill_id=skill.id,
                            feature_id=feature_id,
                            domain=domain,
                            status=TaskStatus.PENDING,
                            title=f"[{skill.id}] {feature_id} - {name or screen_id}",
                            priority=self._calculate_priority(priority_label, complexity),
                            metadata={
                                "priority_label": priority_label,
                                "task_type": "feature",
                                "screen_id": screen_id,
                                "name": name,
                                "complexity": complexity,
                                "inventory_path": str(inventory_path),
                                "source": "feature-inventory",
                            }
                        )
                        tasks.append(task)

        return tasks

    def _priority_dir_to_label(self, priority_dir: str) -> str:
        """Convert priority directory name to priority label.

        Supports both legacy format (P0, P1, P2, P3) and
        current format (P0-Foundation, P1-Hub, P2-Core, P3-Supporting).

        Args:
            priority_dir: Directory name (e.g., "P0", "P1-Hub")

        Returns:
            Priority label (e.g., "P0-Foundation")
        """
        # Current format - return as-is if already in correct format
        current_format = {"P0-Foundation", "P1-Hub", "P2-Core", "P3-Supporting"}
        if priority_dir in current_format:
            return priority_dir

        # Legacy format mapping
        legacy_mapping = {
            "P0": "P0-Foundation",
            "P1": "P1-Hub",
            "P2": "P2-Core",
            "P3": "P3-Supporting",
        }
        return legacy_mapping.get(priority_dir, "P2-Core")

    def _calculate_priority(self, priority_label: str, complexity: str = "medium") -> int:
        """Calculate numeric priority from label and complexity.

        Args:
            priority_label: Priority label (e.g., "P0-Foundation")
            complexity: Complexity level (low, medium, high)

        Returns:
            Numeric priority (1-10, higher = more important)
        """
        # Base priority from label
        base_map = {
            "P0-Foundation": 10,
            "P1-Hub": 8,
            "P2-Core": 5,
            "P3-Supporting": 3,
        }
        base = base_map.get(priority_label, 5)

        # Adjust by complexity (prioritize simpler tasks)
        complexity_adjust = {
            "low": 1,
            "medium": 0,
            "high": -1,
        }
        adjust = complexity_adjust.get(complexity.lower(), 0)

        return max(1, min(10, base + adjust))


class Stage4TaskGenerator(TaskGenerator):
    """Stage 4 (Generation) task generator - code generation tasks.

    Generates code generation tasks from Stage 1 Phase 3 deep analysis
    specifications. Each feature spec becomes a code generation task.

    Attributes:
        _project_config: Project-specific configuration for feature patterns,
                        domain settings, and path templates.
    """

    def __init__(self, project_config: Optional[ProjectConfig] = None):
        """Initialize with optional project configuration.

        Args:
            project_config: Project-specific config. If None, uses hallain defaults.
        """
        self._project_config = project_config or ProjectConfig()

    def get_stage(self) -> int:
        """Return stage number."""
        return 4

    def generate(
        self,
        project_root: Path,
        config: ChoisorConfig,
        registry: SkillRegistry
    ) -> List[Task]:
        """Generate code generation tasks from specs.

        Scans stage1 phase3 specs for features and creates
        code generation tasks with complexity estimates.

        Args:
            project_root: Project root path
            config: Choisor configuration
            registry: Skill registry for skill lookups

        Returns:
            List of Task objects
        """
        tasks: List[Task] = []

        # Get skill for stage 4, phase 3 (domain batch generation)
        skill = registry.get_skill(4, 3)
        if skill is None:
            # Fallback to phase 1
            skill = registry.get_skill(4, 1)
            if skill is None:
                return tasks

        # Specs input path (from Stage 1 Phase 3)
        specs_root = project_root / config.paths.specs_root
        stage1_output = config.paths.stage_outputs.get(1, "stage1-outputs")
        specs_path = specs_root / stage1_output / "phase3"

        if not specs_path.exists():
            return tasks

        # Domain filter
        enabled_domains = None
        if config.work_scope.enabled_domains:
            enabled_domains = [d.upper() for d in config.work_scope.enabled_domains]

        # Scan specs directory structure: phase3/{priority}/{domain}/{feature}/
        for priority_dir in specs_path.iterdir():
            if not priority_dir.is_dir():
                continue

            priority_label = priority_dir.name

            for domain_dir in priority_dir.iterdir():
                if not domain_dir.is_dir():
                    continue

                # Domain directory name is the domain code (e.g., "CM", "PA")
                domain_name = domain_dir.name.upper()

                if enabled_domains and domain_name not in enabled_domains:
                    continue

                for feature_dir in domain_dir.iterdir():
                    if not feature_dir.is_dir():
                        continue

                    # Use project config for feature ID prefix check
                    if not feature_dir.name.startswith(
                        self._project_config.feature.id_prefix
                    ):
                        continue

                    # Skip GAP tasks if configured (manual processing required)
                    if (
                        self._project_config.feature.skip_gap_features
                        and self._project_config.feature.gap_suffix in feature_dir.name
                    ):
                        continue

                    feature_id = feature_dir.name

                    # Skip configured domains (e.g., CM - common module)
                    skip_domains = [
                        d.upper() for d in self._project_config.domain.skip_domains
                    ]
                    if domain_name in skip_domains:
                        continue

                    # Calculate complexity
                    complexity = self._calculate_complexity(feature_dir)

                    task = Task(
                        id=f"{feature_id}-codegen",
                        stage=4,
                        phase=3,
                        skill_id=skill.id,
                        feature_id=feature_id,
                        domain=domain_name,
                        status=TaskStatus.PENDING,
                        title=f"[{skill.id}] {feature_id} Code Generation",
                        priority=self._complexity_to_priority(
                            complexity["estimate"], priority_label
                        ),
                        metadata={
                            "priority_label": priority_label,
                            "spec_path": str(feature_dir),
                            "complexity_estimate": complexity["estimate"],
                            "complexity_reasoning": complexity["reasoning"],
                            "endpoint_count": complexity.get("endpoint_count", 0),
                            "source": "stage1-phase3-specs",
                        },
                        estimated_duration=self._estimate_duration(complexity),
                    )
                    tasks.append(task)

        return tasks

    def _calculate_complexity(self, feature_dir: Path) -> Dict[str, Any]:
        """Calculate feature complexity from spec files.

        Args:
            feature_dir: Feature specification directory

        Returns:
            Complexity dict with estimate, reasoning, and endpoint_count
        """
        main_yaml = feature_dir / "main.yaml"
        endpoint_count = 0

        if main_yaml.exists():
            try:
                with open(main_yaml, "r", encoding="utf-8") as f:
                    main_data = yaml.safe_load(f) or {}

                # Check for pre-computed complexity
                if "complexity" in main_data:
                    raw_complexity = main_data.get("complexity", "MEDIUM")

                    if isinstance(raw_complexity, dict):
                        tier = raw_complexity.get("tier", "medium").upper()
                        raw_complexity = tier

                    # Parse complexity string (may have "(reason)" suffix)
                    parsed = (
                        raw_complexity.split("(")[0].strip().upper()
                        if isinstance(raw_complexity, str)
                        else "MEDIUM"
                    )

                    complexity_mapping = {
                        "SIMPLE": "LOW",
                        "HIGH": "HIGH",
                        "MEDIUM": "MEDIUM",
                        "LOW": "LOW",
                    }
                    normalized = complexity_mapping.get(parsed, "MEDIUM")

                    return {
                        "estimate": normalized,
                        "reasoning": main_data.get(
                            "complexity_reasoning", "From main.yaml"
                        ),
                        "endpoint_count": main_data.get("endpoint_count", 0),
                    }

                # Count endpoints from operations
                endpoint_count = main_data.get("endpoint_count", 0)
                if endpoint_count == 0:
                    operations = main_data.get("operations", [])
                    if isinstance(operations, list):
                        endpoint_count = len(operations)

            except Exception:
                pass

        # Fallback: count api-specs
        api_specs_dir = feature_dir / "api-specs"
        if api_specs_dir.exists() and endpoint_count == 0:
            endpoint_count = len(list(api_specs_dir.glob("*.yaml")))

        # Determine complexity from endpoint count
        if endpoint_count >= 20:
            estimate = "HIGH"
            reasoning = f"High complexity: {endpoint_count} endpoints"
        elif endpoint_count >= 5:
            estimate = "MEDIUM"
            reasoning = f"Medium complexity: {endpoint_count} endpoints"
        else:
            estimate = "LOW"
            reasoning = f"Low complexity: {endpoint_count} endpoints"

        return {
            "estimate": estimate,
            "reasoning": reasoning,
            "endpoint_count": endpoint_count,
        }

    def _complexity_to_priority(
        self,
        complexity: str,
        priority_label: str
    ) -> int:
        """Convert complexity and priority label to numeric priority.

        Args:
            complexity: Complexity estimate (LOW, MEDIUM, HIGH)
            priority_label: Domain priority label

        Returns:
            Numeric priority (1-10)
        """
        # Base priority from domain
        base_map = {
            "P0-Foundation": 10,
            "P1-Hub": 8,
            "P2-Core": 5,
            "P3-Supporting": 3,
        }
        base = base_map.get(priority_label, 5)

        # Adjust by complexity (prioritize simpler tasks for faster completion)
        complexity_adjust = {
            "LOW": 1,
            "MEDIUM": 0,
            "HIGH": -1,
        }

        return max(1, min(10, base + complexity_adjust.get(complexity, 0)))

    def _estimate_duration(self, complexity: Dict[str, Any]) -> int:
        """Estimate task duration in minutes.

        Args:
            complexity: Complexity info dict

        Returns:
            Estimated minutes
        """
        estimate = complexity.get("estimate", "MEDIUM")
        duration_map = {
            "LOW": 15,
            "MEDIUM": 30,
            "HIGH": 60,
        }
        return duration_map.get(estimate, 30)


class Stage5TaskGenerator(TaskGenerator):
    """Stage 5 (Assurance) task generator.

    Generates quality assurance tasks for completed Stage 4 features.
    """

    def get_stage(self) -> int:
        """Return stage number."""
        return 5

    def generate(
        self,
        project_root: Path,
        config: ChoisorConfig,
        registry: SkillRegistry
    ) -> List[Task]:
        """Generate assurance tasks from completed Stage 4 features.

        Args:
            project_root: Project root path
            config: Choisor configuration
            registry: Skill registry

        Returns:
            List of Task objects
        """
        tasks: List[Task] = []

        skill = registry.get_skill(5, 1)
        if skill is None:
            return tasks

        # Load existing tasks
        import json
        tasks_path = project_root / ".choisor" / "tasks" / "tasks.json"
        if not tasks_path.exists():
            return tasks

        try:
            with open(tasks_path, "r", encoding="utf-8") as f:
                all_task_dicts = json.load(f)
        except (json.JSONDecodeError, IOError):
            return tasks

        completed_stage4 = [
            t for t in all_task_dicts
            if t.get("stage") == 4 and t.get("status") == "completed"
        ]

        # Check for existing stage 5 tasks
        existing_stage5_features = {
            t.get("feature_id")
            for t in all_task_dicts
            if t.get("stage") == 5
        }

        # Domain filter
        enabled_domains = None
        if config.work_scope.enabled_domains:
            enabled_domains = [d.upper() for d in config.work_scope.enabled_domains]

        for stage4_task in completed_stage4:
            feature_id = stage4_task.get("feature_id")
            domain = stage4_task.get("domain", "").upper()

            if feature_id in existing_stage5_features:
                continue

            if enabled_domains and domain not in enabled_domains:
                continue

            priority_label = self._get_priority_label(domain, config)

            task = Task(
                id=f"{feature_id}-assurance",
                stage=5,
                phase=1,
                skill_id=skill.id,
                feature_id=feature_id,
                domain=domain,
                status=TaskStatus.PENDING,
                title=f"[{skill.id}] {feature_id} Quality Assurance",
                metadata={
                    "priority_label": priority_label,
                    "source_task_id": stage4_task.get("id"),
                    "complexity_estimate": stage4_task.get("metadata", {}).get(
                        "complexity_estimate", "MEDIUM"
                    ),
                }
            )
            tasks.append(task)

        return tasks


class TaskGeneratorFactory:
    """Factory for creating stage-specific task generators.

    Example:
        >>> generator = TaskGeneratorFactory.create(4)
        >>> isinstance(generator, Stage4TaskGenerator)
        True
    """

    _generators: Dict[int, Type[TaskGenerator]] = {
        1: Stage1TaskGenerator,
        2: DefaultTaskGenerator,
        3: DefaultTaskGenerator,
        4: Stage4TaskGenerator,
        5: Stage5TaskGenerator,
    }

    @classmethod
    def create(
        cls,
        stage: int,
        project_config: Optional[ProjectConfig] = None
    ) -> TaskGenerator:
        """Create task generator for stage.

        Args:
            stage: Stage number (1-5)
            project_config: Optional project-specific configuration

        Returns:
            TaskGenerator instance for the stage
        """
        generator_class = cls._generators.get(stage)

        if generator_class is None:
            return DefaultTaskGenerator(stage)

        if generator_class == DefaultTaskGenerator:
            return DefaultTaskGenerator(stage)

        # Pass project_config to generators that support it
        if generator_class == Stage1TaskGenerator:
            return Stage1TaskGenerator(project_config)
        if generator_class == Stage4TaskGenerator:
            return Stage4TaskGenerator(project_config)

        return generator_class()

    @classmethod
    def register(cls, stage: int, generator_class: Type[TaskGenerator]) -> None:
        """Register custom generator for stage.

        Args:
            stage: Stage number
            generator_class: TaskGenerator subclass
        """
        cls._generators[stage] = generator_class

    @classmethod
    def get_available_stages(cls) -> List[int]:
        """Get list of registered stage numbers.

        Returns:
            List of stage numbers
        """
        return sorted(cls._generators.keys())
