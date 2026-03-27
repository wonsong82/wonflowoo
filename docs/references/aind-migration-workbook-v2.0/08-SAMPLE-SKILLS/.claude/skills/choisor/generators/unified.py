"""Unified Generator Interface

Provides a unified interface that automatically selects between:
- Plugin-based generators (when workflow.yaml exists)
- Legacy hardcoded generators (when workflow.yaml is absent)

This ensures backward compatibility while enabling the new plugin architecture.
"""

from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import ChoisorConfig, ProjectConfig, WorkflowConfig
    from ..core import Task, SkillRegistry


class UnifiedTaskGenerator:
    """Unified task generator that bridges legacy and plugin systems.

    Automatically detects workflow.yaml and uses the appropriate
    task generation strategy:
    - With workflow.yaml: Uses plugin-based DefaultTaskGeneratorPlugin
    - Without workflow.yaml: Uses legacy Stage*TaskGenerator classes

    Example:
        generator = UnifiedTaskGenerator(project_root)
        tasks = generator.generate(stage=1, config=config, registry=registry)
    """

    def __init__(self, project_root: Path):
        """Initialize unified generator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self._workflow: Optional["WorkflowConfig"] = None
        self._use_plugins: bool = False
        self._initialized: bool = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization to detect workflow mode."""
        if self._initialized:
            return

        from ..config import ConfigLoader

        loader = ConfigLoader(self.project_root)

        if loader.has_workflow():
            self._workflow = loader.load_workflow()
            self._use_plugins = True
        else:
            self._use_plugins = False

        self._initialized = True

    @property
    def use_plugins(self) -> bool:
        """Check if plugin mode is active."""
        self._ensure_initialized()
        return self._use_plugins

    @property
    def workflow(self) -> Optional["WorkflowConfig"]:
        """Get loaded workflow config."""
        self._ensure_initialized()
        return self._workflow

    def generate(
        self,
        stage: int,
        config: "ChoisorConfig",
        registry: "SkillRegistry",
        project_config: Optional["ProjectConfig"] = None,
    ) -> List["Task"]:
        """Generate tasks for a stage.

        Automatically selects the appropriate generator based on
        whether workflow.yaml exists.

        Args:
            stage: Stage number (1-5)
            config: Choisor configuration
            registry: Skill registry
            project_config: Optional project configuration

        Returns:
            List of Task objects
        """
        self._ensure_initialized()

        if project_config is None:
            from ..config import ConfigLoader
            loader = ConfigLoader(self.project_root)
            project_config = loader.load_project()

        if self._use_plugins and self._workflow:
            return self._generate_with_plugins(
                stage, config, registry, project_config
            )
        else:
            return self._generate_legacy(
                stage, config, registry, project_config
            )

    def _generate_with_plugins(
        self,
        stage: int,
        config: "ChoisorConfig",
        registry: "SkillRegistry",
        project_config: "ProjectConfig",
    ) -> List["Task"]:
        """Generate tasks using plugin system.

        Args:
            stage: Stage number
            config: Choisor configuration
            registry: Skill registry
            project_config: Project configuration

        Returns:
            List of Task objects
        """
        from ..plugins import PluginLoader

        # Get stage_id from workflow
        stage_id = self._workflow.get_stage_id(stage)
        if not stage_id:
            return []

        # Load plugins and get generator
        plugin_loader = PluginLoader(self.project_root)
        plugins = plugin_loader.load(self._workflow)

        generator = plugins.get_task_generator(
            stage_id, self._workflow, project_config
        )

        return generator.generate(
            self.project_root,
            config,
            self._workflow,
            registry,
            project_config,
        )

    def _generate_legacy(
        self,
        stage: int,
        config: "ChoisorConfig",
        registry: "SkillRegistry",
        project_config: "ProjectConfig",
    ) -> List["Task"]:
        """Generate tasks using legacy generators.

        Args:
            stage: Stage number
            config: Choisor configuration
            registry: Skill registry
            project_config: Project configuration

        Returns:
            List of Task objects
        """
        from .task_generator import TaskGeneratorFactory

        generator = TaskGeneratorFactory.create(stage, project_config)
        return generator.generate(self.project_root, config, registry)


class UnifiedInstructionGenerator:
    """Unified instruction generator that bridges legacy and plugin systems."""

    def __init__(self, project_root: Path):
        """Initialize unified instruction generator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self._workflow: Optional["WorkflowConfig"] = None
        self._use_plugins: bool = False
        self._initialized: bool = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization to detect workflow mode."""
        if self._initialized:
            return

        from ..config import ConfigLoader

        loader = ConfigLoader(self.project_root)

        if loader.has_workflow():
            self._workflow = loader.load_workflow()
            self._use_plugins = True
        else:
            self._use_plugins = False

        self._initialized = True

    def generate(
        self,
        task: "Task",
        config: "ChoisorConfig",
        project_config: Optional["ProjectConfig"] = None,
    ) -> str:
        """Generate instruction for a task.

        Args:
            task: Task to generate instructions for
            config: Choisor configuration
            project_config: Optional project configuration

        Returns:
            Instruction text
        """
        self._ensure_initialized()

        if project_config is None:
            from ..config import ConfigLoader
            loader = ConfigLoader(self.project_root)
            project_config = loader.load_project()

        if self._use_plugins and self._workflow:
            return self._generate_with_plugins(task, config, project_config)
        else:
            return self._generate_legacy(task, config, project_config)

    def _generate_with_plugins(
        self,
        task: "Task",
        config: "ChoisorConfig",
        project_config: "ProjectConfig",
    ) -> str:
        """Generate instruction using plugin system."""
        from ..plugins import PluginLoader

        stage_id = self._workflow.get_stage_id(task.stage)
        if not stage_id:
            return f"Execute task: {task.title}"

        plugin_loader = PluginLoader(self.project_root)
        plugins = plugin_loader.load(self._workflow)

        generator = plugins.get_instruction_generator(
            stage_id, self._workflow, project_config
        )

        return generator.generate(task, config, self._workflow, project_config)

    def _generate_legacy(
        self,
        task: "Task",
        config: "ChoisorConfig",
        project_config: "ProjectConfig",
    ) -> str:
        """Generate instruction using legacy generators."""
        from .instruction_generator import InstructionGeneratorFactory

        generator = InstructionGeneratorFactory.create(task.stage, project_config)
        return generator.generate(task, config)


def create_task_generator(project_root: Path) -> UnifiedTaskGenerator:
    """Factory function to create a unified task generator.

    Args:
        project_root: Root directory of the project

    Returns:
        UnifiedTaskGenerator instance
    """
    return UnifiedTaskGenerator(project_root)


def create_instruction_generator(project_root: Path) -> UnifiedInstructionGenerator:
    """Factory function to create a unified instruction generator.

    Args:
        project_root: Root directory of the project

    Returns:
        UnifiedInstructionGenerator instance
    """
    return UnifiedInstructionGenerator(project_root)
