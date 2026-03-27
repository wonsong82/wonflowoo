"""Plugin Base Classes

Abstract base classes for Choisor plugins. Implement these to create
custom task generators, instruction generators, or validators.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import ChoisorConfig, ProjectConfig, WorkflowConfig
    from ..core import Task, SkillRegistry


@dataclass
class ValidationResult:
    """Result of output validation.

    Attributes:
        valid: Whether validation passed
        errors: List of error messages
        warnings: List of warning messages
        metadata: Additional validation metadata
    """
    valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        """Add an error and mark as invalid."""
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning (doesn't affect validity)."""
        self.warnings.append(message)

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge another result into this one."""
        return ValidationResult(
            valid=self.valid and other.valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            metadata={**self.metadata, **other.metadata},
        )


class TaskGeneratorPlugin(ABC):
    """Base class for task generator plugins.

    Implement this class to create custom task generation logic
    for a specific stage or workflow pattern.

    Example:
        class DiscoveryTaskGenerator(TaskGeneratorPlugin):
            @property
            def stage_id(self) -> str:
                return "discovery"

            def generate(self, ...) -> List[Task]:
                # Custom discovery task generation
                pass
    """

    @property
    @abstractmethod
    def stage_id(self) -> str:
        """Return the stage ID this generator handles.

        Returns:
            Stage identifier (e.g., "discovery", "generation")
        """
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
        """Generate tasks for this stage.

        Args:
            project_root: Root directory of the project
            config: Choisor orchestrator configuration
            workflow: Workflow definition
            registry: Skill registry for skill lookups
            project_config: Project-specific configuration

        Returns:
            List of Task objects
        """
        pass

    def supports_phase(self, phase_id: str) -> bool:
        """Check if this generator supports a specific phase.

        Override this to limit which phases the generator handles.
        Default implementation supports all phases in the stage.

        Args:
            phase_id: Phase identifier

        Returns:
            True if phase is supported
        """
        return True


class InstructionGeneratorPlugin(ABC):
    """Base class for instruction generator plugins.

    Implement this class to create custom instruction templates
    for task execution.

    Example:
        class CodeGenInstructionGenerator(InstructionGeneratorPlugin):
            @property
            def stage_id(self) -> str:
                return "generation"

            def generate(self, ...) -> str:
                return f"Generate code for {task.feature_id}..."
    """

    @property
    @abstractmethod
    def stage_id(self) -> str:
        """Return the stage ID this generator handles.

        Returns:
            Stage identifier
        """
        pass

    @abstractmethod
    def generate(
        self,
        task: "Task",
        config: "ChoisorConfig",
        workflow: "WorkflowConfig",
        project_config: "ProjectConfig",
    ) -> str:
        """Generate instruction text for a task.

        Args:
            task: Task to generate instructions for
            config: Choisor configuration
            workflow: Workflow definition
            project_config: Project-specific configuration

        Returns:
            Instruction text string
        """
        pass

    def get_context(
        self,
        task: "Task",
        project_root: Path,
    ) -> dict:
        """Get additional context for instruction generation.

        Override this to provide custom context data.

        Args:
            task: Task being processed
            project_root: Project root directory

        Returns:
            Context dictionary
        """
        return {}


class ValidatorPlugin(ABC):
    """Base class for output validator plugins.

    Implement this class to create custom validation logic
    for task outputs.

    Example:
        class SpecValidator(ValidatorPlugin):
            @property
            def stage_id(self) -> str:
                return "discovery"

            def validate(self, ...) -> ValidationResult:
                result = ValidationResult()
                if not (output_path / "main.yaml").exists():
                    result.add_error("Missing main.yaml")
                return result
    """

    @property
    @abstractmethod
    def stage_id(self) -> str:
        """Return the stage ID this validator handles.

        Returns:
            Stage identifier
        """
        pass

    @abstractmethod
    def validate(
        self,
        task: "Task",
        output_path: Path,
        workflow: "WorkflowConfig",
    ) -> ValidationResult:
        """Validate task output.

        Args:
            task: Completed task
            output_path: Path to task outputs
            workflow: Workflow definition

        Returns:
            ValidationResult with errors/warnings
        """
        pass

    def get_expected_outputs(
        self,
        task: "Task",
        workflow: "WorkflowConfig",
    ) -> List[str]:
        """Get expected output file patterns for a task.

        Override this for custom output expectations.
        Default implementation uses workflow definition.

        Args:
            task: Task being validated
            workflow: Workflow definition

        Returns:
            List of expected output patterns
        """
        return workflow.get_expected_outputs(task.stage, task.phase)
