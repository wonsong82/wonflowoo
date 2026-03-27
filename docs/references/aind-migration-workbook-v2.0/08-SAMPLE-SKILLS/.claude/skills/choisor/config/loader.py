"""Choisor 2.0 Configuration Loader

Provides loading and saving functionality for Choisor configuration
using YAML format. Supports default configuration creation and
project root discovery.
"""

from pathlib import Path
from typing import Optional, Union
import yaml

from .schema import ChoisorConfig, StageConfig
from .project_schema import ProjectConfig
from .workflow_schema import (
    WorkflowConfig,
    StageConfig as WorkflowStageConfig,
    PhaseConfig,
    PhaseType,
    TaskSourceConfig,
)


class ConfigLoader:
    """Load and save Choisor configuration.

    Handles YAML-based configuration persistence with support for
    default configuration creation and custom config paths.

    Attributes:
        project_root: Root directory of the project
        choisor_dir: Directory containing Choisor configuration
        config_path: Path to the main configuration file
    """

    DEFAULT_CONFIG_NAME = "config.yaml"
    PROJECT_CONFIG_NAME = "project.yaml"
    WORKFLOW_CONFIG_NAME = "workflow.yaml"

    def __init__(self, project_root: Path):
        """Initialize the configuration loader.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.choisor_dir = self.project_root / ".choisor"
        self.config_path = self.choisor_dir / self.DEFAULT_CONFIG_NAME
        self.project_config_path = self.choisor_dir / self.PROJECT_CONFIG_NAME
        self.workflow_config_path = self.choisor_dir / self.WORKFLOW_CONFIG_NAME

    def load(self, config_path: Optional[Path] = None) -> ChoisorConfig:
        """Load configuration from YAML file.

        If the configuration file does not exist, returns a default
        configuration with pre-populated stage mappings.

        Args:
            config_path: Optional custom config path. If not provided,
                        uses the default config path.

        Returns:
            ChoisorConfig instance populated from YAML or defaults
        """
        path = config_path or self.config_path

        if not path.exists():
            return self._create_default_config()

        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        # Map legacy config fields to new schema
        data = self._map_legacy_config(data)

        # Convert stage configs if present
        if 'stages' in data and isinstance(data['stages'], dict):
            stages = {}
            for stage_num, stage_data in data['stages'].items():
                # Handle both int and string keys from YAML
                # Also handle legacy "stage1" format -> 1
                if isinstance(stage_num, str):
                    if stage_num.startswith('stage'):
                        stage_key = int(stage_num.replace('stage', ''))
                    elif stage_num.isdigit():
                        stage_key = int(stage_num)
                    else:
                        continue  # Skip invalid keys
                else:
                    stage_key = stage_num
                if isinstance(stage_data, dict):
                    # Convert legacy phase strings to integers
                    stage_data = self._convert_legacy_stage_data(stage_data)
                    stages[stage_key] = StageConfig(**stage_data)
                else:
                    stages[stage_key] = stage_data
            data['stages'] = stages

        config = ChoisorConfig(**data)

        # Merge project properties from project.yaml (single source of truth)
        config = self._merge_project_config(config)

        return config

    def save(self, config: ChoisorConfig, config_path: Optional[Path] = None) -> None:
        """Save configuration to YAML file.

        Creates parent directories if they don't exist.

        Args:
            config: ChoisorConfig instance to save
            config_path: Optional custom config path. If not provided,
                        uses the default config path.
        """
        path = config_path or self.config_path
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict for YAML serialization
        data = config.model_dump()

        # Convert stage configs to dicts
        if 'stages' in data:
            stages = {}
            for stage_num, stage_config in data['stages'].items():
                if isinstance(stage_config, StageConfig):
                    stages[stage_num] = stage_config.model_dump()
                else:
                    stages[stage_num] = stage_config
            data['stages'] = stages

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )

    def _map_legacy_config(self, data: dict) -> dict:
        """Map legacy config fields to new schema.

        Legacy config.yaml uses different field names than the schema.
        This method maps them appropriately.

        Args:
            data: Raw config dict from YAML

        Returns:
            Config dict with mapped fields
        """
        result = data.copy()

        # Map claude_code.max_sessions -> parallel.max_parallel_sessions
        if 'claude_code' in result:
            claude_code = result['claude_code']
            if 'max_sessions' in claude_code:
                max_sessions = claude_code['max_sessions']
                if 'parallel' not in result:
                    result['parallel'] = {}
                result['parallel']['max_parallel_sessions'] = max_sessions

        # Map assignment field to AssignmentConfig format
        # New format: assignment: {enabled: true, delay: 60}
        # Legacy formats:
        #   - assignment: true/false (simple bool)
        #   - assignment: {pause_assignment: true/false}
        if 'assignment' in result:
            assignment_val = result['assignment']
            if isinstance(assignment_val, bool):
                # Simple boolean: true = enabled, false = disabled
                result['assignment'] = {'enabled': assignment_val, 'delay': None}
            elif isinstance(assignment_val, dict):
                if 'pause_assignment' in assignment_val:
                    # Legacy format: invert pause_assignment
                    result['assignment'] = {
                        'enabled': not assignment_val['pause_assignment'],
                        'delay': None
                    }
                # else: already in new format {enabled, delay}

        # Map current.stage/phase -> current_stage/current_phase
        if 'current' in result:
            current = result['current']
            if 'stage' in current:
                stage_str = current['stage']
                if isinstance(stage_str, str) and stage_str.startswith('stage'):
                    result['current_stage'] = int(stage_str.replace('stage', ''))
                elif isinstance(stage_str, int):
                    result['current_stage'] = stage_str
            if 'phase' in current:
                phase_str = current['phase']
                if isinstance(phase_str, str) and phase_str.startswith('phase'):
                    result['current_phase'] = int(phase_str.replace('phase', ''))
                elif isinstance(phase_str, int):
                    result['current_phase'] = phase_str

        # Map phase_gate.max_allowed_phase (string "phase3" -> int 3)
        if 'phase_gate' in result and isinstance(result['phase_gate'], dict):
            phase_gate = result['phase_gate']
            max_phase = phase_gate.get('max_allowed_phase')
            if max_phase is not None:
                if isinstance(max_phase, str) and max_phase.startswith('phase'):
                    phase_gate['max_allowed_phase'] = int(max_phase.replace('phase', ''))
                elif isinstance(max_phase, str) and max_phase.isdigit():
                    phase_gate['max_allowed_phase'] = int(max_phase)
                elif isinstance(max_phase, int):
                    phase_gate['max_allowed_phase'] = max_phase

        # Map work_scope.enabled_domains
        if 'work_scope' in result:
            work_scope = result['work_scope']
            # Ensure it's in the right format
            if 'enabled_domains' not in result.get('work_scope', {}):
                result['work_scope'] = work_scope

        return result

    def _convert_legacy_stage_data(self, stage_data: dict) -> dict:
        """Convert legacy stage data with string phases to integer phases.

        Args:
            stage_data: Stage configuration dict that may have legacy format

        Returns:
            Converted stage data with integer phases
        """
        result = stage_data.copy()

        # Convert phases list: ["phase1", "phase2"] -> [1, 2]
        if 'phases' in result and isinstance(result['phases'], list):
            new_phases = []
            for phase in result['phases']:
                if isinstance(phase, str) and phase.startswith('phase'):
                    new_phases.append(int(phase.replace('phase', '')))
                elif isinstance(phase, int):
                    new_phases.append(phase)
                elif isinstance(phase, str) and phase.isdigit():
                    new_phases.append(int(phase))
            result['phases'] = new_phases

        # Convert skills dict: {"phase1": "skill"} -> {1: "skill"}
        if 'skills' in result and isinstance(result['skills'], dict):
            new_skills = {}
            for key, value in result['skills'].items():
                if isinstance(key, str) and key.startswith('phase'):
                    new_skills[int(key.replace('phase', ''))] = value
                elif isinstance(key, int):
                    new_skills[key] = value
                elif isinstance(key, str) and key.isdigit():
                    new_skills[int(key)] = value
            result['skills'] = new_skills

        return result

    def _merge_project_config(self, config: ChoisorConfig) -> ChoisorConfig:
        """Merge project properties from project.yaml into config.

        project.yaml is the single source of truth for:
        - domain_priority_map: Domain groupings by priority tier
        - stages: Stage definitions with skill mappings
        - task_sources: Task source locations
        - paths.specs_root: Specifications root directory

        Args:
            config: ChoisorConfig instance to update

        Returns:
            Updated ChoisorConfig with merged project properties
        """
        if not self.project_config_path.exists():
            return config

        try:
            project_config = self.load_project()

            # Merge domain_priority_map
            if project_config.domain.priority_map:
                has_content = any(
                    domains for domains in project_config.domain.priority_map.values()
                )
                if has_content:
                    config.domain_priority_map = project_config.domain.priority_map

            # Merge stages from project.yaml if config doesn't have them
            if project_config.stages and not config.stages:
                for stage_key, stage_def in project_config.stages.items():
                    # Convert "stage1" -> 1
                    if isinstance(stage_key, str) and stage_key.startswith('stage'):
                        stage_num = int(stage_key.replace('stage', ''))
                    elif isinstance(stage_key, int):
                        stage_num = stage_key
                    else:
                        continue

                    # Convert phase/skill keys from strings to integers
                    phases = []
                    for phase in stage_def.phases:
                        if isinstance(phase, str) and phase.startswith('phase'):
                            phases.append(int(phase.replace('phase', '')))
                        elif isinstance(phase, int):
                            phases.append(phase)

                    skills = {}
                    for phase_key, skill in stage_def.skills.items():
                        if isinstance(phase_key, str) and phase_key.startswith('phase'):
                            skills[int(phase_key.replace('phase', ''))] = skill
                        elif isinstance(phase_key, int):
                            skills[phase_key] = skill

                    config.stages[stage_num] = StageConfig(
                        name=stage_def.name,
                        phases=phases,
                        skills=skills
                    )

            # Merge specs_root from project.yaml paths
            if project_config.paths.specs_root:
                config.paths.specs_root = project_config.paths.specs_root

            # Merge source_base from project.yaml paths
            if project_config.paths.source_base:
                config.paths.source_base = project_config.paths.source_base

            # Merge task_sources from project.yaml
            if project_config.task_sources:
                from .schema import TaskSourcesConfig as SchemaTaskSourcesConfig
                config.task_sources = SchemaTaskSourcesConfig(
                    feature_inventory_base=project_config.task_sources.feature_inventory_base,
                    feature_inventory_pattern=project_config.task_sources.feature_inventory_pattern,
                    stage1_specs=project_config.task_sources.stage1_specs,
                    stage4_specs=project_config.task_sources.stage4_specs
                )

        except Exception:
            pass  # Keep config's values if project.yaml fails to load

        return config

    def _create_default_config(self) -> ChoisorConfig:
        """Create default configuration with stage mappings.

        Returns:
            ChoisorConfig with pre-populated stage configurations
            matching the 5-stage migration workflow.
        """
        config = ChoisorConfig()

        # Set up default stage configurations
        config.stages = {
            1: StageConfig(
                name="Discovery",
                description="Feature inventory and deep analysis",
                phases=[1, 2, 3, 4],
                skills={
                    1: "s1-01-discovery-feature-inventory",
                    2: "s1-02-discovery-miplatform-protocol",
                    3: "s1-03-discovery-deep-analysis",
                    4: "s1-04-discovery-spec-generation",
                }
            ),
            2: StageConfig(
                name="Validation",
                description="Ground truth comparison and gap analysis",
                phases=[1, 2, 3, 4],
                skills={
                    1: "s2-01-validation-source-inventory",
                    2: "s2-02-validation-structural-comparison",
                    3: "s2-03-validation-gap-analysis",
                    4: "s2-04-validation-spec-completion",
                }
            ),
            3: StageConfig(
                name="Preparation",
                description="Architecture design and generation specs",
                phases=[1, 2, 3, 4, 5],
                skills={
                    1: "s3-01-preparation-dependency-graph",
                    2: "s3-02-preparation-interface-extraction",
                    3: "s3-03-preparation-technical-debt",
                    4: "s3-04-preparation-architecture-design",
                    5: "s3-05-preparation-generation-spec",
                }
            ),
            4: StageConfig(
                name="Generation",
                description="Code generation and integration",
                phases=[1, 2, 3, 4, 5],
                skills={
                    1: "s4-01-generation-project-scaffold",
                    2: "s4-02-generation-mini-pilot",
                    3: "s4-03-generation-domain-batch",
                    4: "s4-04-generation-test-generation",
                    5: "s4-05-generation-integration-build",
                }
            ),
            5: StageConfig(
                name="Assurance",
                description="Quality validation and gate checks",
                phases=[1, 2, 3, 4, 5],
                skills={
                    1: "s5-01-assurance-structural-check",
                    2: "s5-02-assurance-functional-validation",
                    3: "s5-03-assurance-api-contract-test",
                    4: "s5-04-assurance-performance-baseline",
                    5: "s5-05-assurance-quality-gate",
                }
            ),
        }

        return config

    def ensure_config_dir(self) -> Path:
        """Ensure the .choisor directory exists.

        Returns:
            Path to the .choisor directory
        """
        self.choisor_dir.mkdir(parents=True, exist_ok=True)
        return self.choisor_dir

    def load_project(self, config_path: Optional[Path] = None) -> ProjectConfig:
        """Load project configuration from YAML file.

        If project.yaml does not exist, returns a default ProjectConfig
        with hallain settings for backward compatibility.

        Args:
            config_path: Optional custom config path. If not provided,
                        uses the default project config path.

        Returns:
            ProjectConfig instance populated from YAML or defaults
        """
        from .project_schema import StageDefinitionConfig, TaskSourcesConfig

        path = config_path or self.project_config_path

        if not path.exists():
            return ProjectConfig()  # Return hallain defaults

        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        # Convert stages dict to StageDefinitionConfig objects
        if 'stages' in data and isinstance(data['stages'], dict):
            stages = {}
            for stage_key, stage_data in data['stages'].items():
                if isinstance(stage_data, dict):
                    stages[stage_key] = StageDefinitionConfig(**stage_data)
                else:
                    stages[stage_key] = stage_data
            data['stages'] = stages

        # Convert task_sources dict to TaskSourcesConfig object
        if 'task_sources' in data and isinstance(data['task_sources'], dict):
            data['task_sources'] = TaskSourcesConfig(**data['task_sources'])

        return ProjectConfig(**data)

    def save_project(
        self,
        config: ProjectConfig,
        config_path: Optional[Path] = None
    ) -> None:
        """Save project configuration to YAML file.

        Creates parent directories if they don't exist.

        Args:
            config: ProjectConfig instance to save
            config_path: Optional custom config path. If not provided,
                        uses the default project config path.
        """
        path = config_path or self.project_config_path
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict for YAML serialization
        data = config.model_dump()

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )


    def has_workflow(self) -> bool:
        """Check if workflow.yaml exists.

        Returns:
            True if workflow.yaml exists, False otherwise
        """
        return self.workflow_config_path.exists()

    def load_workflow(
        self, config_path: Optional[Path] = None
    ) -> Optional[WorkflowConfig]:
        """Load workflow configuration from YAML file.

        If workflow.yaml does not exist, returns None (use legacy mode).

        Args:
            config_path: Optional custom config path. If not provided,
                        uses the default workflow config path.

        Returns:
            WorkflowConfig instance or None if file doesn't exist
        """
        path = config_path or self.workflow_config_path

        if not path.exists():
            return None

        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        # Handle nested 'workflow' key if present
        if 'workflow' in data:
            data = data['workflow']

        # Convert stages list to StageConfig objects
        if 'stages' in data and isinstance(data['stages'], list):
            stages = []
            for stage_data in data['stages']:
                # Convert phases list to PhaseConfig objects
                if 'phases' in stage_data and isinstance(stage_data['phases'], list):
                    phases = []
                    for phase_data in stage_data['phases']:
                        # Convert type string to PhaseType enum
                        if 'type' in phase_data and isinstance(phase_data['type'], str):
                            phase_data['type'] = PhaseType(phase_data['type'])
                        phases.append(PhaseConfig(**phase_data))
                    stage_data['phases'] = phases
                stages.append(WorkflowStageConfig(**stage_data))
            data['stages'] = stages

        # Convert task_sources dict to TaskSourceConfig objects
        if 'task_sources' in data and isinstance(data['task_sources'], dict):
            task_sources = {}
            for key, source_data in data['task_sources'].items():
                if isinstance(source_data, dict):
                    task_sources[key] = TaskSourceConfig(**source_data)
                else:
                    task_sources[key] = source_data
            data['task_sources'] = task_sources

        return WorkflowConfig(**data)

    def save_workflow(
        self,
        config: WorkflowConfig,
        config_path: Optional[Path] = None
    ) -> None:
        """Save workflow configuration to YAML file.

        Creates parent directories if they don't exist.

        Args:
            config: WorkflowConfig instance to save
            config_path: Optional custom config path. If not provided,
                        uses the default workflow config path.
        """
        path = config_path or self.workflow_config_path
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict for YAML serialization
        data = self._workflow_to_dict(config)

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(
                {'workflow': data},
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )

    def _workflow_to_dict(self, config: WorkflowConfig) -> dict:
        """Convert WorkflowConfig to dict for YAML serialization.

        Args:
            config: WorkflowConfig instance

        Returns:
            Dictionary representation
        """
        data = {
            'name': config.name,
            'description': config.description,
            'skill_pattern': config.skill_pattern,
            'skill_dir': config.skill_dir,
        }

        # Convert stages
        if config.stages:
            stages = []
            for stage in config.stages:
                stage_dict = {
                    'id': stage.id,
                    'number': stage.number,
                    'name': stage.name,
                    'description': stage.description,
                    'output_dir': stage.output_dir,
                }
                if stage.parallel_pairs:
                    stage_dict['parallel_pairs'] = stage.parallel_pairs
                if stage.generator:
                    stage_dict['generator'] = stage.generator
                if stage.validator:
                    stage_dict['validator'] = stage.validator

                # Convert phases
                if stage.phases:
                    phases = []
                    for phase in stage.phases:
                        phase_dict = {
                            'id': phase.id,
                            'number': phase.number,
                            'name': phase.name,
                            'type': phase.type.value,
                            'skill': phase.skill,
                        }
                        if phase.outputs:
                            phase_dict['outputs'] = phase.outputs
                        if phase.generator:
                            phase_dict['generator'] = phase.generator
                        if phase.validator:
                            phase_dict['validator'] = phase.validator
                        if phase.prerequisites:
                            phase_dict['prerequisites'] = phase.prerequisites
                        phases.append(phase_dict)
                    stage_dict['phases'] = phases

                stages.append(stage_dict)
            data['stages'] = stages

        # Convert task_sources
        if config.task_sources:
            task_sources = {}
            for key, source in config.task_sources.items():
                if isinstance(source, TaskSourceConfig):
                    task_sources[key] = {
                        'path': source.path,
                        'pattern': source.pattern,
                    }
                else:
                    task_sources[key] = source
            data['task_sources'] = task_sources

        return data


def load_config(project_root: Union[str, Path]) -> ChoisorConfig:
    """Convenience function to load configuration.

    Args:
        project_root: Root directory of the project

    Returns:
        ChoisorConfig instance
    """
    loader = ConfigLoader(Path(project_root))
    return loader.load()


def load_project_config(project_root: Union[str, Path]) -> ProjectConfig:
    """Convenience function to load project configuration.

    Args:
        project_root: Root directory of the project

    Returns:
        ProjectConfig instance (defaults to hallain settings if no project.yaml)
    """
    loader = ConfigLoader(Path(project_root))
    return loader.load_project()


def find_project_root() -> Optional[Path]:
    """Find project root by looking for marker directories.

    Searches upward from current working directory for a directory
    containing .choisor/ or .claude/ subdirectory.

    Returns:
        Path to project root if found, None otherwise
    """
    current = Path.cwd()
    while current != current.parent:
        if (current / ".choisor").is_dir() or (current / ".claude").is_dir():
            return current
        current = current.parent
    return None
