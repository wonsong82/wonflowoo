"""Choisor 2.0 Plugin System

Provides plugin architecture for project-specific workflow customization:
- TaskGeneratorPlugin: Custom task generation logic
- InstructionGeneratorPlugin: Custom instruction templates
- ValidatorPlugin: Custom output validation

Usage:
    from choisor.plugins import PluginRegistry, PluginLoader

    loader = PluginLoader(project_root)
    registry = loader.load()

    generator = registry.get_task_generator("discovery", workflow, project_config)
    tasks = generator.generate(...)
"""

from .base import (
    TaskGeneratorPlugin,
    InstructionGeneratorPlugin,
    ValidatorPlugin,
    ValidationResult,
)
from .registry import PluginRegistry
from .loader import PluginLoader
from .defaults import (
    DefaultTaskGeneratorPlugin,
    DefaultInstructionGeneratorPlugin,
    DefaultValidatorPlugin,
)

__all__ = [
    # Base classes
    "TaskGeneratorPlugin",
    "InstructionGeneratorPlugin",
    "ValidatorPlugin",
    "ValidationResult",
    # Registry and loader
    "PluginRegistry",
    "PluginLoader",
    # Default implementations
    "DefaultTaskGeneratorPlugin",
    "DefaultInstructionGeneratorPlugin",
    "DefaultValidatorPlugin",
]
