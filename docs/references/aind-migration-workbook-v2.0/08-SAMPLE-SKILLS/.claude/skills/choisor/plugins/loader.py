"""Plugin Loader

Dynamically loads plugins from the project's .choisor/plugins directory.
Supports loading task generators, instruction generators, and validators.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Optional, List, Type, TYPE_CHECKING

from .registry import PluginRegistry
from .base import (
    TaskGeneratorPlugin,
    InstructionGeneratorPlugin,
    ValidatorPlugin,
)

if TYPE_CHECKING:
    from ..config import WorkflowConfig


class PluginLoader:
    """Loads plugins from project directory.

    Scans .choisor/plugins/ for Python files and registers any
    plugin classes found. Plugin files should define classes that
    inherit from TaskGeneratorPlugin, InstructionGeneratorPlugin,
    or ValidatorPlugin.

    Example project structure:
        .choisor/
        └── plugins/
            ├── __init__.py
            ├── generators/
            │   ├── __init__.py
            │   └── discovery_generator.py
            └── validators/
                ├── __init__.py
                └── discovery_validator.py

    Example plugin file:
        # discovery_generator.py
        from choisor.plugins import TaskGeneratorPlugin

        class DiscoveryTaskGenerator(TaskGeneratorPlugin):
            @property
            def stage_id(self) -> str:
                return "discovery"

            def generate(self, ...):
                # Custom logic
                pass
    """

    def __init__(self, project_root: Path):
        """Initialize plugin loader.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.plugins_dir = self.project_root / ".choisor" / "plugins"

    def load(self, workflow: Optional["WorkflowConfig"] = None) -> PluginRegistry:
        """Load all plugins and return registry.

        Scans the plugins directory for generator and validator
        implementations, registering them in the returned registry.

        Args:
            workflow: Optional workflow config for validation

        Returns:
            PluginRegistry with loaded plugins
        """
        registry = PluginRegistry()

        if not self.plugins_dir.exists():
            return registry

        # Add plugins dir to Python path temporarily
        plugins_parent = str(self.plugins_dir.parent)
        if plugins_parent not in sys.path:
            sys.path.insert(0, plugins_parent)

        try:
            # Load generator plugins
            self._load_generators(registry)

            # Load validator plugins
            self._load_validators(registry)

            # Load from workflow.yaml generator/validator references
            if workflow:
                self._load_workflow_plugins(registry, workflow)

        finally:
            # Clean up sys.path
            if plugins_parent in sys.path:
                sys.path.remove(plugins_parent)

        return registry

    def _load_generators(self, registry: PluginRegistry) -> None:
        """Load task and instruction generators from plugins/generators/."""
        generators_dir = self.plugins_dir / "generators"
        if not generators_dir.exists():
            return

        for plugin_file in generators_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue

            module = self._load_module(plugin_file)
            if module is None:
                continue

            # Find and register TaskGeneratorPlugin subclasses
            for name in dir(module):
                obj = getattr(module, name)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, TaskGeneratorPlugin)
                    and obj is not TaskGeneratorPlugin
                ):
                    # Instantiate to get stage_id, then register class
                    try:
                        # Create temp instance to get stage_id
                        # Note: This requires a no-arg constructor or we inspect differently
                        stage_id = self._get_stage_id(obj)
                        if stage_id:
                            registry.register_task_generator(stage_id, obj)
                    except Exception:
                        pass

            # Find and register InstructionGeneratorPlugin subclasses
            for name in dir(module):
                obj = getattr(module, name)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, InstructionGeneratorPlugin)
                    and obj is not InstructionGeneratorPlugin
                ):
                    try:
                        stage_id = self._get_stage_id(obj)
                        if stage_id:
                            registry.register_instruction_generator(stage_id, obj)
                    except Exception:
                        pass

    def _load_validators(self, registry: PluginRegistry) -> None:
        """Load validators from plugins/validators/."""
        validators_dir = self.plugins_dir / "validators"
        if not validators_dir.exists():
            return

        for plugin_file in validators_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue

            module = self._load_module(plugin_file)
            if module is None:
                continue

            # Find and register ValidatorPlugin subclasses
            for name in dir(module):
                obj = getattr(module, name)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, ValidatorPlugin)
                    and obj is not ValidatorPlugin
                ):
                    try:
                        stage_id = self._get_stage_id(obj)
                        if stage_id:
                            registry.register_validator(stage_id, obj)
                    except Exception:
                        pass

    def _load_workflow_plugins(
        self, registry: PluginRegistry, workflow: "WorkflowConfig"
    ) -> None:
        """Load plugins referenced in workflow.yaml.

        Workflow can specify custom generator/validator modules:
            stages:
              - id: generation
                generator: "generators.code_gen"  # Module path
                phases:
                  - id: domain-batch
                    generator: "generators.batch_gen"  # Phase-specific
        """
        for stage in workflow.stages:
            # Stage-level generator
            if stage.generator:
                plugin_class = self._load_plugin_by_path(
                    stage.generator, TaskGeneratorPlugin
                )
                if plugin_class:
                    registry.register_task_generator(stage.id, plugin_class)

            # Stage-level validator
            if stage.validator:
                plugin_class = self._load_plugin_by_path(
                    stage.validator, ValidatorPlugin
                )
                if plugin_class:
                    registry.register_validator(stage.id, plugin_class)

    def _load_module(self, plugin_file: Path):
        """Load a Python module from file path."""
        module_name = f"choisor_plugins.{plugin_file.stem}"

        try:
            spec = importlib.util.spec_from_file_location(
                module_name, plugin_file
            )
            if spec is None or spec.loader is None:
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
        except Exception:
            return None

    def _load_plugin_by_path(
        self, module_path: str, base_class: Type
    ) -> Optional[Type]:
        """Load a plugin class by module path.

        Args:
            module_path: Dot-separated module path (e.g., "generators.code_gen")
            base_class: Expected base class

        Returns:
            Plugin class or None
        """
        parts = module_path.split(".")
        if len(parts) < 2:
            return None

        subdir = parts[0]  # "generators" or "validators"
        module_name = parts[1]

        plugin_file = self.plugins_dir / subdir / f"{module_name}.py"
        if not plugin_file.exists():
            return None

        module = self._load_module(plugin_file)
        if module is None:
            return None

        # Find the appropriate plugin class
        for name in dir(module):
            obj = getattr(module, name)
            if (
                isinstance(obj, type)
                and issubclass(obj, base_class)
                and obj is not base_class
            ):
                return obj

        return None

    def _get_stage_id(self, plugin_class: Type) -> Optional[str]:
        """Get stage_id from a plugin class.

        Tries to get stage_id without full instantiation.

        Args:
            plugin_class: Plugin class

        Returns:
            Stage ID or None
        """
        # Check if stage_id is a class attribute
        if hasattr(plugin_class, "STAGE_ID"):
            return plugin_class.STAGE_ID

        # Check if there's a no-arg way to get it
        # For now, return None and require STAGE_ID class attribute
        return None

    def has_plugins(self) -> bool:
        """Check if plugins directory exists and has content.

        Returns:
            True if plugins directory has Python files
        """
        if not self.plugins_dir.exists():
            return False

        generators_dir = self.plugins_dir / "generators"
        validators_dir = self.plugins_dir / "validators"

        has_generators = (
            generators_dir.exists()
            and any(generators_dir.glob("*.py"))
        )
        has_validators = (
            validators_dir.exists()
            and any(validators_dir.glob("*.py"))
        )

        return has_generators or has_validators

    def list_plugins(self) -> dict:
        """List all available plugin files.

        Returns:
            Dict with 'generators' and 'validators' lists
        """
        result = {"generators": [], "validators": []}

        generators_dir = self.plugins_dir / "generators"
        if generators_dir.exists():
            result["generators"] = [
                f.stem for f in generators_dir.glob("*.py")
                if not f.name.startswith("_")
            ]

        validators_dir = self.plugins_dir / "validators"
        if validators_dir.exists():
            result["validators"] = [
                f.stem for f in validators_dir.glob("*.py")
                if not f.name.startswith("_")
            ]

        return result
