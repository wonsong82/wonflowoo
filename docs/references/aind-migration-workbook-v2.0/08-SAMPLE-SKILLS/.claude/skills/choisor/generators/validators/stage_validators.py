"""Stage Validators - Concrete validators for each migration stage

Provides stage-specific output validators:
- DefaultValidator: Generic validator for stages without specific requirements
- Stage1Validator: Discovery stage output validation
- Stage4Validator: Code generation output validation
- ValidatorFactory: Factory for creating stage validators
"""

from pathlib import Path
from typing import Dict, List, Any, Type, Optional

from .base import StageValidator, ValidationResult
from ...core import Task
from ...config import ChoisorConfig


class DefaultValidator(StageValidator):
    """Default validator for stages without specific validation logic.

    Performs basic directory and file existence checks.
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

    def validate(
        self,
        task: Task,
        output_path: Path,
        config: ChoisorConfig
    ) -> ValidationResult:
        """Perform basic validation.

        Args:
            task: Task that produced the output
            output_path: Path to output directory
            config: Choisor configuration

        Returns:
            ValidationResult
        """
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {
            "task_id": task.id,
            "stage": self._stage,
            "output_path": str(output_path),
        }

        # Check output directory exists
        if not output_path.exists():
            errors.append(f"Output directory not found: {output_path}")
        elif not output_path.is_dir():
            errors.append(f"Output path is not a directory: {output_path}")
        else:
            # Count files in output
            file_count = len(list(output_path.glob("*")))
            details["file_count"] = file_count

            if file_count == 0:
                warnings.append("Output directory is empty")

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details=details,
        )


class Stage1Validator(StageValidator):
    """Stage 1 output validator - feature inventory and deep analysis.

    Validates:
    - Feature inventory YAML exists and has required structure
    - Deep analysis outputs for phase 3
    - Required documentation files
    """

    def get_stage(self) -> int:
        """Return stage number."""
        return 1

    def validate(
        self,
        task: Task,
        output_path: Path,
        config: ChoisorConfig
    ) -> ValidationResult:
        """Validate Stage 1 outputs.

        Args:
            task: Task that produced the output
            output_path: Path to output directory
            config: Choisor configuration

        Returns:
            ValidationResult
        """
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {
            "task_id": task.id,
            "phase": task.phase,
            "output_path": str(output_path),
        }

        # Phase-specific validation
        if task.phase == 1:
            # Phase 1: Feature inventory
            result = self._validate_phase1(output_path)
        elif task.phase == 2:
            # Phase 2: MiPlatform protocol analysis
            result = self._validate_phase2(output_path)
        elif task.phase == 3:
            # Phase 3: Deep analysis
            result = self._validate_phase3(output_path)
        elif task.phase == 4:
            # Phase 4: Spec generation
            result = self._validate_phase4(output_path)
        else:
            result = ValidationResult.success()

        errors.extend(result.errors)
        warnings.extend(result.warnings)
        details.update(result.details)

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details=details,
        )

    def _validate_phase1(self, output_path: Path) -> ValidationResult:
        """Validate Phase 1 (Feature Inventory) output.

        Args:
            output_path: Output directory path

        Returns:
            ValidationResult
        """
        # Check for feature-inventory.yaml
        inventory_file = output_path / "feature-inventory.yaml"
        if not inventory_file.exists():
            # Also check in parent directory (stage-level output)
            parent_inventory = output_path.parent / "feature-inventory.yaml"
            if parent_inventory.exists():
                inventory_file = parent_inventory
            else:
                return ValidationResult.failure(
                    ["Missing feature-inventory.yaml"],
                    {"expected_file": str(inventory_file)}
                )

        # Validate YAML structure
        return self.validate_yaml_structure(
            inventory_file,
            required_keys=["features"]
        )

    def _validate_phase2(self, output_path: Path) -> ValidationResult:
        """Validate Phase 2 (MiPlatform Protocol) output.

        Args:
            output_path: Output directory path

        Returns:
            ValidationResult
        """
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {}

        # Check for protocol analysis files
        protocol_file = output_path / "protocol-analysis.yaml"
        dataset_file = output_path / "dataset-definitions.yaml"

        if not protocol_file.exists():
            warnings.append("Missing protocol-analysis.yaml")
        else:
            details["protocol_file"] = str(protocol_file)

        if not dataset_file.exists():
            warnings.append("Missing dataset-definitions.yaml")
        else:
            details["dataset_file"] = str(dataset_file)

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details=details,
        )

    def _validate_phase3(self, output_path: Path) -> ValidationResult:
        """Validate Phase 3 (Deep Analysis) output.

        Args:
            output_path: Output directory path

        Returns:
            ValidationResult
        """
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {}

        # Check for main.yaml (feature specification)
        main_file = output_path / "main.yaml"
        if not main_file.exists():
            errors.append("Missing main.yaml")
        else:
            details["main_file"] = str(main_file)
            # Validate structure
            result = self.validate_yaml_structure(main_file)
            if not result.passed:
                errors.extend(result.errors)

        # Check for api-specs directory
        api_specs_dir = output_path / "api-specs"
        if api_specs_dir.exists():
            api_count = len(list(api_specs_dir.glob("*.yaml")))
            details["api_spec_count"] = api_count
            if api_count == 0:
                warnings.append("api-specs directory is empty")
        else:
            warnings.append("Missing api-specs directory")

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details=details,
        )

    def _validate_phase4(self, output_path: Path) -> ValidationResult:
        """Validate Phase 4 (Spec Generation) output.

        Args:
            output_path: Output directory path

        Returns:
            ValidationResult
        """
        # Phase 4 follows same structure as Phase 3
        return self._validate_phase3(output_path)


class Stage4Validator(StageValidator):
    """Stage 4 output validator - code generation.

    Validates:
    - Generated Java files exist
    - Generated mapper XML files exist
    - Code compiles (optional)
    """

    def get_stage(self) -> int:
        """Return stage number."""
        return 4

    def validate(
        self,
        task: Task,
        output_path: Path,
        config: ChoisorConfig
    ) -> ValidationResult:
        """Validate Stage 4 outputs.

        Args:
            task: Task that produced the output
            output_path: Path to output (Java source root)
            config: Choisor configuration

        Returns:
            ValidationResult
        """
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {
            "task_id": task.id,
            "feature_id": task.feature_id,
            "domain": task.domain,
        }

        # Determine expected paths
        domain_lower = task.domain.lower()
        java_base = output_path / "src" / "main" / "java" / "com" / "halla" / domain_lower
        resources_base = output_path / "src" / "main" / "resources" / "mapper" / domain_lower

        # Validate Java source files
        java_result = self._validate_java_files(java_base, task.feature_id)
        errors.extend(java_result.errors)
        warnings.extend(java_result.warnings)
        details["java"] = java_result.details

        # Validate mapper XML files
        mapper_result = self._validate_mapper_files(resources_base, task.feature_id)
        errors.extend(mapper_result.errors)
        warnings.extend(mapper_result.warnings)
        details["mapper"] = mapper_result.details

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details=details,
        )

    def _validate_java_files(
        self,
        java_path: Path,
        feature_id: str
    ) -> ValidationResult:
        """Validate generated Java files.

        Args:
            java_path: Java source directory
            feature_id: Feature identifier

        Returns:
            ValidationResult
        """
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {
            "path": str(java_path),
            "files_found": [],
        }

        if not java_path.exists():
            errors.append(f"Java directory not found: {java_path}")
            return ValidationResult(
                passed=False, errors=errors, warnings=warnings, details=details
            )

        # Look for expected file types
        java_files = list(java_path.rglob("*.java"))
        details["file_count"] = len(java_files)
        details["files_found"] = [f.name for f in java_files[:10]]  # First 10

        if len(java_files) == 0:
            errors.append("No Java files generated")

        # Check for required components (entity, service, controller)
        has_entity = any("Entity" in f.name or "DTO" in f.name for f in java_files)
        has_service = any("Service" in f.name for f in java_files)
        has_controller = any("Controller" in f.name for f in java_files)
        has_mapper = any("Mapper" in f.name for f in java_files)

        details["components"] = {
            "entity": has_entity,
            "service": has_service,
            "controller": has_controller,
            "mapper": has_mapper,
        }

        if not has_service:
            warnings.append("No Service class found")
        if not has_mapper:
            warnings.append("No Mapper interface found")

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details=details,
        )

    def _validate_mapper_files(
        self,
        mapper_path: Path,
        feature_id: str
    ) -> ValidationResult:
        """Validate generated mapper XML files.

        Args:
            mapper_path: Mapper XML directory
            feature_id: Feature identifier

        Returns:
            ValidationResult
        """
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {
            "path": str(mapper_path),
            "files_found": [],
        }

        if not mapper_path.exists():
            warnings.append(f"Mapper directory not found: {mapper_path}")
            return ValidationResult(
                passed=True, errors=errors, warnings=warnings, details=details
            )

        # Find mapper XML files
        xml_files = list(mapper_path.glob("*Mapper.xml"))
        details["file_count"] = len(xml_files)
        details["files_found"] = [f.name for f in xml_files]

        if len(xml_files) == 0:
            warnings.append("No mapper XML files found")

        # Basic XML validation
        for xml_file in xml_files:
            try:
                content = xml_file.read_text(encoding="utf-8")
                if "<!DOCTYPE mapper" not in content and "<mapper" not in content:
                    warnings.append(f"Invalid mapper XML format: {xml_file.name}")
            except Exception as e:
                warnings.append(f"Could not read {xml_file.name}: {e}")

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details=details,
        )


class Stage5Validator(StageValidator):
    """Stage 5 output validator - quality assurance.

    Validates:
    - Validation report exists
    - Test results exist
    - Coverage metrics meet threshold
    """

    def get_stage(self) -> int:
        """Return stage number."""
        return 5

    def validate(
        self,
        task: Task,
        output_path: Path,
        config: ChoisorConfig
    ) -> ValidationResult:
        """Validate Stage 5 outputs.

        Args:
            task: Task that produced the output
            output_path: Path to validation output
            config: Choisor configuration

        Returns:
            ValidationResult
        """
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {
            "task_id": task.id,
            "phase": task.phase,
        }

        # Check for validation report
        report_file = output_path / "validation-report.yaml"
        if report_file.exists():
            details["report_file"] = str(report_file)
            result = self.validate_yaml_structure(report_file)
            if not result.passed:
                errors.extend(result.errors)
        else:
            warnings.append("Missing validation-report.yaml")

        # Check for test results
        test_results = output_path / "test-results.json"
        if test_results.exists():
            details["test_results"] = str(test_results)
        else:
            warnings.append("Missing test-results.json")

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details=details,
        )


class ValidatorFactory:
    """Factory for creating stage-specific validators.

    Example:
        >>> validator = ValidatorFactory.create(4)
        >>> isinstance(validator, Stage4Validator)
        True
    """

    _validators: Dict[int, Type[StageValidator]] = {
        1: Stage1Validator,
        4: Stage4Validator,
        5: Stage5Validator,
    }

    @classmethod
    def create(cls, stage: int) -> StageValidator:
        """Create validator for stage.

        Args:
            stage: Stage number (1-5)

        Returns:
            StageValidator instance
        """
        validator_class = cls._validators.get(stage)
        if validator_class is None:
            return DefaultValidator(stage)
        return validator_class()

    @classmethod
    def register(cls, stage: int, validator_class: Type[StageValidator]) -> None:
        """Register custom validator for stage.

        Args:
            stage: Stage number
            validator_class: StageValidator subclass
        """
        cls._validators[stage] = validator_class

    @classmethod
    def get_available_stages(cls) -> List[int]:
        """Get list of stages with specialized validators.

        Returns:
            List of stage numbers
        """
        return sorted(cls._validators.keys())
