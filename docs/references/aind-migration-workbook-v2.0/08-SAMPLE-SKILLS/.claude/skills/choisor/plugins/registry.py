"""Plugin Registry

Central registry for dynamically loaded plugins. Provides fallback
to default implementations when no custom plugin is registered.
"""

from typing import Dict, Type, Optional, TYPE_CHECKING

from .base import (
    TaskGeneratorPlugin,
    InstructionGeneratorPlugin,
    ValidatorPlugin,
)

if TYPE_CHECKING:
    from ..config import WorkflowConfig, ProjectConfig


class PluginRegistry:
    """Registry for dynamically loaded plugins.

    Manages registration and retrieval of task generators,
    instruction generators, and validators. Falls back to
    default implementations when no custom plugin is registered.

    Example:
        registry = PluginRegistry()
        registry.register_task_generator("discovery", DiscoveryGenerator)

        generator = registry.get_task_generator(
            "discovery", workflow, project_config
        )
        tasks = generator.generate(...)
    """

    def __init__(self):
        """Initialize empty registry."""
        self._task_generators: Dict[str, Type[TaskGeneratorPlugin]] = {}
        self._instruction_generators: Dict[str, Type[InstructionGeneratorPlugin]] = {}
        self._validators: Dict[str, Type[ValidatorPlugin]] = {}

    # Task Generator Methods

    def register_task_generator(
        self,
        stage_id: str,
        generator_class: Type[TaskGeneratorPlugin],
    ) -> None:
        """Register a task generator for a stage.

        Args:
            stage_id: Stage identifier (e.g., "discovery")
            generator_class: TaskGeneratorPlugin subclass
        """
        self._task_generators[stage_id] = generator_class

    def has_task_generator(self, stage_id: str) -> bool:
        """Check if a custom task generator is registered.

        Args:
            stage_id: Stage identifier

        Returns:
            True if custom generator is registered
        """
        return stage_id in self._task_generators

    def get_task_generator(
        self,
        stage_id: str,
        workflow: "WorkflowConfig",
        project_config: "ProjectConfig",
    ) -> TaskGeneratorPlugin:
        """Get task generator for a stage.

        Returns custom generator if registered, otherwise
        returns default generator.

        Args:
            stage_id: Stage identifier
            workflow: Workflow configuration
            project_config: Project configuration

        Returns:
            TaskGeneratorPlugin instance
        """
        if stage_id in self._task_generators:
            return self._task_generators[stage_id](workflow, project_config)

        # Import here to avoid circular imports
        from .defaults import DefaultTaskGeneratorPlugin
        return DefaultTaskGeneratorPlugin(stage_id, workflow, project_config)

    # Instruction Generator Methods

    def register_instruction_generator(
        self,
        stage_id: str,
        generator_class: Type[InstructionGeneratorPlugin],
    ) -> None:
        """Register an instruction generator for a stage.

        Args:
            stage_id: Stage identifier
            generator_class: InstructionGeneratorPlugin subclass
        """
        self._instruction_generators[stage_id] = generator_class

    def has_instruction_generator(self, stage_id: str) -> bool:
        """Check if a custom instruction generator is registered.

        Args:
            stage_id: Stage identifier

        Returns:
            True if custom generator is registered
        """
        return stage_id in self._instruction_generators

    def get_instruction_generator(
        self,
        stage_id: str,
        workflow: "WorkflowConfig",
        project_config: "ProjectConfig",
    ) -> InstructionGeneratorPlugin:
        """Get instruction generator for a stage.

        Returns custom generator if registered, otherwise
        returns default generator.

        Args:
            stage_id: Stage identifier
            workflow: Workflow configuration
            project_config: Project configuration

        Returns:
            InstructionGeneratorPlugin instance
        """
        if stage_id in self._instruction_generators:
            return self._instruction_generators[stage_id](workflow, project_config)

        from .defaults import DefaultInstructionGeneratorPlugin
        return DefaultInstructionGeneratorPlugin(stage_id, workflow, project_config)

    # Validator Methods

    def register_validator(
        self,
        stage_id: str,
        validator_class: Type[ValidatorPlugin],
    ) -> None:
        """Register a validator for a stage.

        Args:
            stage_id: Stage identifier
            validator_class: ValidatorPlugin subclass
        """
        self._validators[stage_id] = validator_class

    def has_validator(self, stage_id: str) -> bool:
        """Check if a custom validator is registered.

        Args:
            stage_id: Stage identifier

        Returns:
            True if custom validator is registered
        """
        return stage_id in self._validators

    def get_validator(
        self,
        stage_id: str,
        workflow: "WorkflowConfig",
        project_config: "ProjectConfig",
    ) -> ValidatorPlugin:
        """Get validator for a stage.

        Returns custom validator if registered, otherwise
        returns default validator.

        Args:
            stage_id: Stage identifier
            workflow: Workflow configuration
            project_config: Project configuration

        Returns:
            ValidatorPlugin instance
        """
        if stage_id in self._validators:
            return self._validators[stage_id](workflow, project_config)

        from .defaults import DefaultValidatorPlugin
        return DefaultValidatorPlugin(stage_id, workflow, project_config)

    # Utility Methods

    def get_registered_stages(self) -> Dict[str, list]:
        """Get all registered stage IDs by plugin type.

        Returns:
            Dict with keys 'task_generators', 'instruction_generators',
            'validators', each containing list of stage IDs
        """
        return {
            "task_generators": list(self._task_generators.keys()),
            "instruction_generators": list(self._instruction_generators.keys()),
            "validators": list(self._validators.keys()),
        }

    def clear(self) -> None:
        """Clear all registered plugins."""
        self._task_generators.clear()
        self._instruction_generators.clear()
        self._validators.clear()
