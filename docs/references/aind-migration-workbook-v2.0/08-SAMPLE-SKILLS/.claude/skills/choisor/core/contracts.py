"""Contract Validator - Inter-stage contract validation

Validates stage outputs against inter-stage contracts defined in
.claude/skills/common/inter-stage-contracts.yaml
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


@dataclass
class ContractViolation:
    """Represents a contract violation

    Attributes:
        severity: Violation severity (CRITICAL, MAJOR, MINOR)
        rule: Rule that was violated
        message: Human-readable description
        path: Optional path to the violating element
    """
    severity: str  # CRITICAL, MAJOR, MINOR
    rule: str
    message: str
    path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "severity": self.severity,
            "rule": self.rule,
            "message": self.message,
            "path": self.path,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContractViolation":
        """Create from dictionary"""
        return cls(
            severity=data["severity"],
            rule=data["rule"],
            message=data["message"],
            path=data.get("path"),
        )

    def is_blocking(self) -> bool:
        """Check if this violation blocks progression"""
        return self.severity == "CRITICAL"


class ContractValidator:
    """Inter-stage contract validation

    Validates stage outputs against contracts to ensure:
    - Required fields are present
    - Data formats are correct
    - URL/class name normalization rules are followed
    - Summary counts match actual data

    Example:
        >>> validator = ContractValidator(contracts_path)
        >>> validator.load_contracts()
        >>> violations = validator.validate_stage_output(1, 4, output_path)
        >>> if any(v.is_blocking() for v in violations):
        ...     raise ValidationError("Critical violations found")
    """

    # URL extensions to remove during normalization
    URL_EXTENSIONS = [".mi", ".do", ".action"]

    def __init__(self, contracts_path: Path):
        """Initialize contract validator

        Args:
            contracts_path: Path to inter-stage-contracts.yaml
        """
        self.contracts_path = contracts_path
        self._contracts: Dict[str, Any] = {}
        self._normalization_rules: Dict[str, Any] = {}

    def load_contracts(self) -> None:
        """Load contracts from YAML file"""
        if yaml is None:
            raise ImportError("PyYAML is required for contract validation")

        if not self.contracts_path.exists():
            raise FileNotFoundError(f"Contracts file not found: {self.contracts_path}")

        with open(self.contracts_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data:
            self._contracts = data
            self._normalization_rules = data.get("normalization_rules", {})

    def normalize_url(self, url: str) -> str:
        """Normalize URL according to contract rules

        Rules:
        1. Convert to lowercase
        2. Remove trailing slash
        3. Remove extensions (.mi, .do, .action)

        Args:
            url: URL to normalize

        Returns:
            Normalized URL
        """
        if not url:
            return url

        # Step 1: Lowercase
        normalized = url.lower()

        # Step 2: Remove trailing slash
        normalized = normalized.rstrip("/")

        # Step 3: Remove extensions
        for ext in self.URL_EXTENSIONS:
            if normalized.endswith(ext):
                normalized = normalized[:-len(ext)]
                break

        return normalized

    def normalize_class_name(self, class_name: str) -> str:
        """Normalize class name by removing package prefix

        Args:
            class_name: Fully qualified or simple class name

        Returns:
            Simple class name without package
        """
        if not class_name:
            return class_name

        # Remove package prefix (everything before last dot)
        if "." in class_name:
            return class_name.rsplit(".", 1)[-1]

        return class_name

    def validate_stage_output(
        self,
        stage: int,
        phase: int,
        output_path: Path
    ) -> List[ContractViolation]:
        """Validate stage output against contracts

        Args:
            stage: Stage number (1-5)
            phase: Phase number (1-5)
            output_path: Path to output file or directory

        Returns:
            List of contract violations
        """
        violations: List[ContractViolation] = []
        skill_id = f"s{stage}-{phase:02d}"

        # Check if output exists
        if not output_path.exists():
            violations.append(ContractViolation(
                severity="CRITICAL",
                rule="output_exists",
                message=f"Output not found: {output_path}",
                path=str(output_path),
            ))
            return violations

        # If it's a file, validate its contents
        if output_path.is_file():
            violations.extend(self._validate_yaml_file(output_path, skill_id))

        # If it's a directory, validate expected files
        elif output_path.is_dir():
            violations.extend(self._validate_directory(output_path, skill_id))

        return violations

    def _validate_yaml_file(
        self,
        file_path: Path,
        skill_id: str
    ) -> List[ContractViolation]:
        """Validate a YAML output file

        Args:
            file_path: Path to YAML file
            skill_id: Skill ID for context

        Returns:
            List of violations
        """
        violations: List[ContractViolation] = []

        if yaml is None:
            return violations

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            violations.append(ContractViolation(
                severity="CRITICAL",
                rule="yaml_syntax",
                message=f"YAML parsing error: {e}",
                path=str(file_path),
            ))
            return violations

        if data is None:
            violations.append(ContractViolation(
                severity="CRITICAL",
                rule="not_empty",
                message="File is empty",
                path=str(file_path),
            ))
            return violations

        # Validate metadata
        violations.extend(self._validate_metadata(data, file_path))

        # Validate summary counts
        violations.extend(self._validate_summary_counts(data, file_path))

        # Validate URL normalization in endpoints
        violations.extend(self._validate_url_normalization(data, file_path))

        return violations

    def _validate_metadata(
        self,
        data: Dict[str, Any],
        file_path: Path
    ) -> List[ContractViolation]:
        """Validate metadata section

        Args:
            data: Parsed YAML data
            file_path: Source file path

        Returns:
            List of violations
        """
        violations: List[ContractViolation] = []
        metadata = data.get("metadata", {})

        # Check required metadata fields
        required_fields = ["generated_by", "generated_at"]
        for field in required_fields:
            if field not in metadata:
                violations.append(ContractViolation(
                    severity="MAJOR",
                    rule="metadata_required",
                    message=f"Missing required metadata field: {field}",
                    path=f"{file_path}::metadata.{field}",
                ))

        # Validate generated_at format (ISO8601)
        generated_at = metadata.get("generated_at", "")
        if generated_at:
            iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
            if not re.match(iso_pattern, generated_at):
                violations.append(ContractViolation(
                    severity="MINOR",
                    rule="timestamp_format",
                    message=f"Timestamp not in ISO8601 format: {generated_at}",
                    path=f"{file_path}::metadata.generated_at",
                ))

        return violations

    def _validate_summary_counts(
        self,
        data: Dict[str, Any],
        file_path: Path
    ) -> List[ContractViolation]:
        """Validate that summary counts match actual data

        Args:
            data: Parsed YAML data
            file_path: Source file path

        Returns:
            List of violations
        """
        violations: List[ContractViolation] = []
        summary = data.get("summary", {})

        # Check features count
        if "features" in data and "total_features" in summary:
            actual_count = len(data["features"])
            declared_count = summary["total_features"]
            if actual_count != declared_count:
                violations.append(ContractViolation(
                    severity="MAJOR",
                    rule="summary_count_match",
                    message=f"Feature count mismatch: summary={declared_count}, actual={actual_count}",
                    path=f"{file_path}::summary.total_features",
                ))

        # Check endpoints count
        if "features" in data and "total_endpoints" in summary:
            actual_count = sum(
                len(f.get("endpoints", [])) for f in data["features"]
            )
            declared_count = summary["total_endpoints"]
            if actual_count != declared_count:
                violations.append(ContractViolation(
                    severity="MAJOR",
                    rule="summary_count_match",
                    message=f"Endpoint count mismatch: summary={declared_count}, actual={actual_count}",
                    path=f"{file_path}::summary.total_endpoints",
                ))

        return violations

    def _validate_url_normalization(
        self,
        data: Dict[str, Any],
        file_path: Path
    ) -> List[ContractViolation]:
        """Validate URL normalization in endpoint paths

        Args:
            data: Parsed YAML data
            file_path: Source file path

        Returns:
            List of violations
        """
        violations: List[ContractViolation] = []
        features = data.get("features", [])

        for i, feature in enumerate(features):
            endpoints = feature.get("endpoints", [])
            for j, endpoint in enumerate(endpoints):
                path = endpoint.get("path", "")
                normalized = self.normalize_url(path)

                # Check if URL needs normalization
                if path != normalized:
                    # Check for uppercase (should be warning)
                    if path.lower() != path:
                        violations.append(ContractViolation(
                            severity="MINOR",
                            rule="url_lowercase",
                            message=f"URL contains uppercase: {path}",
                            path=f"{file_path}::features[{i}].endpoints[{j}].path",
                        ))

                    # Check for trailing slash
                    if path.endswith("/"):
                        violations.append(ContractViolation(
                            severity="MINOR",
                            rule="url_trailing_slash",
                            message=f"URL has trailing slash: {path}",
                            path=f"{file_path}::features[{i}].endpoints[{j}].path",
                        ))

                    # Check for extensions
                    for ext in self.URL_EXTENSIONS:
                        if path.lower().endswith(ext):
                            violations.append(ContractViolation(
                                severity="MINOR",
                                rule="url_extension",
                                message=f"URL has extension {ext}: {path}",
                                path=f"{file_path}::features[{i}].endpoints[{j}].path",
                            ))
                            break

        return violations

    def _validate_directory(
        self,
        dir_path: Path,
        skill_id: str
    ) -> List[ContractViolation]:
        """Validate a directory of outputs

        Args:
            dir_path: Path to output directory
            skill_id: Skill ID for context

        Returns:
            List of violations
        """
        violations: List[ContractViolation] = []

        # Check for expected files based on skill
        expected_files = self._get_expected_files(skill_id)

        for expected in expected_files:
            file_path = dir_path / expected
            if not file_path.exists():
                violations.append(ContractViolation(
                    severity="MAJOR",
                    rule="expected_file",
                    message=f"Expected file not found: {expected}",
                    path=str(file_path),
                ))
            elif file_path.is_file():
                # Validate the file contents
                violations.extend(self._validate_yaml_file(file_path, skill_id))

        return violations

    def _get_expected_files(self, skill_id: str) -> List[str]:
        """Get expected output files for a skill

        Args:
            skill_id: Skill ID (e.g., "s1-01")

        Returns:
            List of expected file names
        """
        # Map skill IDs to expected outputs
        skill_outputs = {
            "s1-01": ["feature-inventory.yaml"],
            "s1-02": ["miplatform-protocol.yaml"],
            "s1-03": ["summary.yaml"],
            "s1-04": ["main.yaml"],
            "s2-01": ["source-inventory.yaml"],
            "s2-02": ["comparison-report.yaml", "coverage-matrix.yaml"],
            "s2-03": ["gap-analysis.yaml"],
            "s2-04": ["completion-report.yaml"],
        }

        return skill_outputs.get(skill_id, [])

    def get_required_inputs(self, stage: int, phase: int) -> List[str]:
        """Get required input files for a stage/phase

        Args:
            stage: Stage number
            phase: Phase number

        Returns:
            List of required input file patterns
        """
        skill_id = f"s{stage}-{phase:02d}"

        # Look up in contracts
        stage_contracts = self._contracts.get(f"stage{stage}_internal", {})

        for contract_key, contract in stage_contracts.items():
            consumer = contract.get("consumer", {})
            if consumer.get("skill", "").endswith(skill_id):
                producer = contract.get("producer", {})
                output = producer.get("output")
                if output:
                    return [output] if isinstance(output, str) else output
                outputs = producer.get("outputs", [])
                return outputs

        return []

    def get_contract_for_skill(
        self,
        skill_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get contract definition for a skill

        Args:
            skill_id: Skill ID (e.g., "s1-01")

        Returns:
            Contract definition or None
        """
        # Search all stage contracts
        for stage_key in ["stage1_internal", "stage2_internal", "stage1_to_stage2", "stage2_to_stage3"]:
            stage_contracts = self._contracts.get(stage_key, {})
            for contract_key, contract in stage_contracts.items():
                producer = contract.get("producer", {})
                consumer = contract.get("consumer", {})

                # Check if skill is producer or consumer
                if skill_id in str(producer.get("skill", "")) or skill_id in str(consumer.get("skill", "")):
                    return contract

        return None

    def get_violations_summary(
        self,
        violations: List[ContractViolation]
    ) -> Dict[str, int]:
        """Get summary of violations by severity

        Args:
            violations: List of violations

        Returns:
            Dict mapping severity to count
        """
        summary = {"CRITICAL": 0, "MAJOR": 0, "MINOR": 0}

        for v in violations:
            if v.severity in summary:
                summary[v.severity] += 1

        return summary

    def has_blocking_violations(
        self,
        violations: List[ContractViolation]
    ) -> bool:
        """Check if any violations are blocking

        Args:
            violations: List of violations

        Returns:
            True if any CRITICAL violations exist
        """
        return any(v.is_blocking() for v in violations)
