# Choisor Plugin Architecture Design

## Overview

Choisor 2.0 Plugin Architecture enables project-specific workflow definitions
without modifying core orchestrator code.

## Directory Structure

```
project-root/
├── .choisor/
│   ├── config.yaml           # Orchestrator settings (existing)
│   ├── project.yaml          # Project settings (existing)
│   ├── workflow.yaml         # Workflow definition (NEW)
│   └── plugins/              # Project-specific plugins (NEW)
│       ├── __init__.py
│       ├── generators/
│       │   ├── __init__.py
│       │   └── discovery_generator.py
│       └── validators/
│           ├── __init__.py
│           └── discovery_validator.py
├── .claude/skills/           # Project-specific skills
│   └── {skill-name}/
│       └── SKILL.md
└── work/specs/               # Stage outputs
```

## Core Components

### 1. WorkflowConfig (workflow.yaml)

Defines the project's stage/phase structure:

```yaml
# .choisor/workflow.yaml
workflow:
  name: "hallain_tft"
  description: "Spring MVC to Spring Boot migration"

  # Skill discovery pattern (supports {stage}, {phase} placeholders)
  skill_pattern: "s{stage}-{phase:02d}-*"
  skill_dir: ".claude/skills"

  stages:
    - id: "discovery"
      number: 1
      name: "Discovery"
      description: "Feature discovery and analysis"
      output_dir: "stage1-outputs"
      phases:
        - id: "feature-inventory"
          number: 1
          type: "domain"           # domain | feature | system
          skill: "s1-01-discovery-feature-inventory"
          outputs:
            - "feature-inventory.yaml"
        - id: "miplatform-protocol"
          number: 2
          type: "domain"
          skill: "s1-02-discovery-miplatform-protocol"
          outputs:
            - "miplatform-protocol.yaml"
        - id: "deep-analysis"
          number: 3
          type: "feature"
          skill: "s1-03-discovery-deep-analysis"
          outputs:
            - "summary.yaml"
            - "main.yaml"
        - id: "spec-generation"
          number: 4
          type: "feature"
          skill: "s1-04-discovery-spec-generation"
          outputs:
            - "main.yaml"
            - "api-specs/*.yaml"

    - id: "validation"
      number: 2
      name: "Validation"
      # ... phases

    - id: "preparation"
      number: 3
      name: "Preparation"
      # ... phases

    - id: "generation"
      number: 4
      name: "Generation"
      parallel_pairs:
        - ["domain-batch", "test-generation"]
      phases:
        - id: "project-scaffold"
          number: 1
          type: "system"
          skill: "s4-01-generation-project-scaffold"
        - id: "mini-pilot"
          number: 2
          type: "system"
          skill: "s4-02-generation-mini-pilot"
        - id: "domain-batch"
          number: 3
          type: "feature"
          skill: "s4-03-generation-domain-batch"
          generator: "generators.code_generation"  # Custom generator
        - id: "test-generation"
          number: 4
          type: "feature"
          skill: "s4-04-generation-test-generation"
        - id: "integration-build"
          number: 5
          type: "system"
          skill: "s4-05-generation-integration-build"

    - id: "assurance"
      number: 5
      name: "Assurance"
      # ... phases

  # Task source configuration
  task_sources:
    feature_inventory:
      path: "work/specs/stage1-outputs/phase1/{priority}/{domain}/feature-inventory.yaml"
      pattern: "work/specs/stage1-outputs/phase1/**/feature-inventory.yaml"

    specs:
      path: "work/specs/stage1-outputs/phase3/{priority}/{domain}/{feature}/"
```

### 2. Plugin Base Classes

```python
# .claude/skills/choisor/plugins/base.py

from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

class TaskGeneratorPlugin(ABC):
    """Base class for task generator plugins."""

    @property
    @abstractmethod
    def stage_id(self) -> str:
        """Return stage ID this generator handles (e.g., 'discovery')."""
        pass

    @abstractmethod
    def generate(
        self,
        project_root: Path,
        config: "ChoisorConfig",
        workflow: "WorkflowConfig",
        registry: "SkillRegistry",
        project_config: "ProjectConfig",
    ) -> List["Task"]:
        """Generate tasks for this stage."""
        pass


class InstructionGeneratorPlugin(ABC):
    """Base class for instruction generator plugins."""

    @property
    @abstractmethod
    def stage_id(self) -> str:
        """Return stage ID this generator handles."""
        pass

    @abstractmethod
    def generate(
        self,
        task: "Task",
        config: "ChoisorConfig",
        workflow: "WorkflowConfig",
        project_config: "ProjectConfig",
    ) -> str:
        """Generate instruction for a task."""
        pass


class ValidatorPlugin(ABC):
    """Base class for output validator plugins."""

    @property
    @abstractmethod
    def stage_id(self) -> str:
        """Return stage ID this validator handles."""
        pass

    @abstractmethod
    def validate(
        self,
        task: "Task",
        output_path: Path,
        workflow: "WorkflowConfig",
    ) -> "ValidationResult":
        """Validate task output."""
        pass
```

### 3. Plugin Registry

```python
# .claude/skills/choisor/plugins/registry.py

class PluginRegistry:
    """Registry for dynamically loaded plugins."""

    def __init__(self):
        self._task_generators: Dict[str, Type[TaskGeneratorPlugin]] = {}
        self._instruction_generators: Dict[str, Type[InstructionGeneratorPlugin]] = {}
        self._validators: Dict[str, Type[ValidatorPlugin]] = {}

    def register_task_generator(
        self,
        stage_id: str,
        generator_class: Type[TaskGeneratorPlugin]
    ) -> None:
        """Register a task generator for a stage."""
        self._task_generators[stage_id] = generator_class

    def get_task_generator(
        self,
        stage_id: str,
        workflow: "WorkflowConfig",
        project_config: "ProjectConfig",
    ) -> TaskGeneratorPlugin:
        """Get task generator for stage, falling back to default."""
        if stage_id in self._task_generators:
            return self._task_generators[stage_id](workflow, project_config)
        return DefaultTaskGeneratorPlugin(stage_id, workflow, project_config)

    # Similar methods for instruction_generators and validators
```

### 4. Plugin Loader

```python
# .claude/skills/choisor/plugins/loader.py

class PluginLoader:
    """Loads plugins from project directory."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.plugins_dir = project_root / ".choisor" / "plugins"

    def load(self) -> PluginRegistry:
        """Load all plugins and return registry."""
        registry = PluginRegistry()

        if not self.plugins_dir.exists():
            return registry

        # Add plugins dir to Python path
        sys.path.insert(0, str(self.plugins_dir))

        # Load generator plugins
        generators_dir = self.plugins_dir / "generators"
        if generators_dir.exists():
            for plugin_file in generators_dir.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                self._load_generator_plugin(plugin_file, registry)

        # Load validator plugins
        validators_dir = self.plugins_dir / "validators"
        if validators_dir.exists():
            for plugin_file in validators_dir.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                self._load_validator_plugin(plugin_file, registry)

        return registry
```

### 5. Default Plugins

Default implementations that work with workflow.yaml configuration:

```python
# .claude/skills/choisor/plugins/defaults.py

class DefaultTaskGeneratorPlugin(TaskGeneratorPlugin):
    """Default task generator that works from workflow.yaml."""

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

    def generate(self, ...) -> List[Task]:
        stage = self._workflow.get_stage(self._stage_id)
        tasks = []

        for phase in stage.phases:
            phase_type = phase.type  # "system", "domain", or "feature"

            if phase_type == "system":
                # One task total
                tasks.append(self._create_system_task(phase))
            elif phase_type == "domain":
                # One task per domain
                for domain in self._get_domains():
                    tasks.append(self._create_domain_task(phase, domain))
            else:  # feature
                # One task per feature
                for feature in self._get_features():
                    tasks.append(self._create_feature_task(phase, feature))

        return tasks
```

## Migration Path

### Phase 1: Add New Components (Non-Breaking)
1. Create `workflow.yaml` schema
2. Create plugin base classes
3. Create plugin registry
4. Create default plugins

### Phase 2: Refactor Existing Code
1. Wrap existing Stage*Generator classes as plugins
2. Update factories to use plugin registry
3. Keep backward compatibility with hardcoded generators

### Phase 3: Migrate hallain_tft
1. Create `workflow.yaml` for hallain_tft
2. Move Stage1/4/5 generators to plugins directory
3. Test with existing tasks

### Phase 4: Remove Hardcoded Dependencies
1. Remove Stage* classes from core
2. Make workflow.yaml required
3. Update documentation

## Backward Compatibility

During transition:
- If `workflow.yaml` exists: Use plugin architecture
- If `workflow.yaml` absent: Fall back to hardcoded generators (deprecated)

```python
def get_task_generator(stage: int, project_root: Path) -> TaskGenerator:
    workflow_path = project_root / ".choisor" / "workflow.yaml"

    if workflow_path.exists():
        # New plugin-based approach
        workflow = WorkflowLoader(project_root).load()
        plugins = PluginLoader(project_root).load()
        stage_id = workflow.get_stage_id(stage)
        return plugins.get_task_generator(stage_id, workflow, project_config)
    else:
        # Legacy hardcoded approach (deprecated)
        return TaskGeneratorFactory.create(stage, project_config)
```

## Example: Custom Generator Plugin

```python
# .choisor/plugins/generators/code_generation.py

from choisor.plugins.base import TaskGeneratorPlugin

class CodeGenerationTaskGenerator(TaskGeneratorPlugin):
    """Custom task generator for Stage 4 code generation."""

    @property
    def stage_id(self) -> str:
        return "generation"

    def generate(self, project_root, config, workflow, registry, project_config):
        tasks = []

        # Custom logic for code generation tasks
        specs_path = project_root / "work/specs/stage1-outputs/phase3"

        for feature_dir in self._scan_features(specs_path):
            # Skip GAP features
            if project_config.feature.skip_gap_features:
                if project_config.feature.gap_suffix in feature_dir.name:
                    continue

            complexity = self._calculate_complexity(feature_dir)

            task = Task(
                id=f"{feature_dir.name}-codegen",
                stage=workflow.get_stage("generation").number,
                phase=3,
                skill_id="s4-03",
                feature_id=feature_dir.name,
                # ... rest of task creation
            )
            tasks.append(task)

        return tasks
```

## Benefits

1. **Project Independence**: Each project defines its own workflow
2. **Extensibility**: Add custom generators without modifying core
3. **Testability**: Plugins can be unit tested in isolation
4. **Reusability**: Common plugins can be shared across projects
5. **Backward Compatible**: Existing projects continue to work
