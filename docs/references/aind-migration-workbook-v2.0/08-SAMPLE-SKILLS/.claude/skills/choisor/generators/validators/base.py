"""Validator Base Classes - Abstract interfaces for output validation

Provides abstract base classes for stage output validators:
- ValidationResult: Structured validation result
- StageValidator: Abstract validator interface
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional

from ...core import Task
from ...config import ChoisorConfig


@dataclass
class ValidationResult:
    """Result of output validation.

    Captures the outcome of validating stage outputs, including
    any errors, warnings, and additional details.

    Attributes:
        passed: Whether validation passed
        errors: List of error messages (failures)
        warnings: List of warning messages (non-blocking issues)
        details: Additional validation details (metrics, paths checked, etc.)
    """
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        """Allow using ValidationResult directly in boolean context."""
        return self.passed

    def add_error(self, message: str) -> None:
        """Add an error message.

        Args:
            message: Error description
        """
        self.errors.append(message)
        self.passed = False

    def add_warning(self, message: str) -> None:
        """Add a warning message.

        Args:
            message: Warning description
        """
        self.warnings.append(message)

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge another validation result into this one.

        Args:
            other: Another ValidationResult to merge

        Returns:
            Self for chaining
        """
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.details.update(other.details)
        if not other.passed:
            self.passed = False
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "details": self.details,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }

    @classmethod
    def success(cls, details: Optional[Dict[str, Any]] = None) -> "ValidationResult":
        """Create a successful validation result.

        Args:
            details: Optional details dict

        Returns:
            ValidationResult with passed=True
        """
        return cls(passed=True, details=details or {})

    @classmethod
    def failure(
        cls,
        errors: List[str],
        details: Optional[Dict[str, Any]] = None
    ) -> "ValidationResult":
        """Create a failed validation result.

        Args:
            errors: List of error messages
            details: Optional details dict

        Returns:
            ValidationResult with passed=False
        """
        return cls(passed=False, errors=errors, details=details or {})


class StageValidator(ABC):
    """Abstract base class for stage output validators.

    Stage validators verify that the outputs of a stage meet
    the required criteria before allowing progression to the
    next stage or phase.

    Example:
        >>> validator = Stage1Validator()
        >>> result = validator.validate(task, output_path, config)
        >>> if result.passed:
        ...     print("Validation passed!")
    """

    @abstractmethod
    def get_stage(self) -> int:
        """Return stage number this validator handles.

        Returns:
            Stage number (1-5)
        """
        pass

    @abstractmethod
    def validate(
        self,
        task: Task,
        output_path: Path,
        config: ChoisorConfig
    ) -> ValidationResult:
        """Validate stage output.

        Args:
            task: Task that produced the output
            output_path: Path to the output directory
            config: Choisor configuration

        Returns:
            ValidationResult with pass/fail status and details
        """
        pass

    def validate_file_exists(
        self,
        file_path: Path,
        required: bool = True
    ) -> ValidationResult:
        """Validate that a file exists.

        Args:
            file_path: Path to check
            required: Whether file is required (error vs warning)

        Returns:
            ValidationResult
        """
        if file_path.exists():
            return ValidationResult.success({
                "file": str(file_path),
                "exists": True,
            })

        message = f"File not found: {file_path}"
        if required:
            return ValidationResult.failure([message], {"file": str(file_path)})
        else:
            result = ValidationResult.success({"file": str(file_path)})
            result.add_warning(message)
            return result

    def validate_directory_exists(
        self,
        dir_path: Path,
        required: bool = True
    ) -> ValidationResult:
        """Validate that a directory exists.

        Args:
            dir_path: Directory path to check
            required: Whether directory is required

        Returns:
            ValidationResult
        """
        if dir_path.exists() and dir_path.is_dir():
            return ValidationResult.success({
                "directory": str(dir_path),
                "exists": True,
            })

        message = f"Directory not found: {dir_path}"
        if required:
            return ValidationResult.failure([message], {"directory": str(dir_path)})
        else:
            result = ValidationResult.success({"directory": str(dir_path)})
            result.add_warning(message)
            return result

    def validate_yaml_structure(
        self,
        file_path: Path,
        required_keys: Optional[List[str]] = None
    ) -> ValidationResult:
        """Validate YAML file structure.

        Args:
            file_path: Path to YAML file
            required_keys: List of required top-level keys

        Returns:
            ValidationResult
        """
        import yaml

        if not file_path.exists():
            return ValidationResult.failure([f"YAML file not found: {file_path}"])

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return ValidationResult.failure([f"Invalid YAML: {e}"])

        if data is None:
            return ValidationResult.failure(["YAML file is empty"])

        if required_keys:
            missing_keys = [k for k in required_keys if k not in data]
            if missing_keys:
                return ValidationResult.failure(
                    [f"Missing required keys: {', '.join(missing_keys)}"]
                )

        return ValidationResult.success({
            "file": str(file_path),
            "keys": list(data.keys()) if isinstance(data, dict) else [],
        })
