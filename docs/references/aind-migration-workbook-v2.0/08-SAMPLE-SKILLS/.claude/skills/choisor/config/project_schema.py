"""Choisor 2.0 Project Configuration Schema

Provides project-specific configuration for generalizing Choisor
across different migration projects. When project.yaml is absent,
defaults to hallain project settings for backward compatibility.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class FeaturePatternConfig(BaseModel):
    """Feature identification patterns.

    Attributes:
        id_prefix: Prefix for feature IDs (e.g., "FEAT-")
        gap_suffix: Suffix identifying GAP features (e.g., "GAP")
        skip_gap_features: If True, skip GAP features in task generation
    """
    id_prefix: str = "FEAT-"
    gap_suffix: str = "GAP"
    skip_gap_features: bool = True


class DomainConfig(BaseModel):
    """Domain-specific configuration.

    Attributes:
        skip_domains: List of domain codes to skip (e.g., ["CM"])
        priority_map: Mapping of priority tier to domain list
    """
    skip_domains: List[str] = Field(default_factory=list)
    priority_map: Dict[str, List[str]] = Field(default_factory=lambda: {
        "P0-Foundation": [],
        "P1-Hub": [],
        "P2-Core": [],
        "P3-Supporting": [],
    })


class PhaseTypesConfig(BaseModel):
    """Phase type configuration per stage.

    Defines whether each phase operates at system, domain, or feature level:
    - system: One task total (e.g., project scaffold)
    - domain: One task per domain (e.g., feature inventory)
    - feature: One task per feature (parallelizable)

    Attributes:
        stage1: Phase types for Stage 1
        stage2: Phase types for Stage 2
        stage3: Phase types for Stage 3
        stage4: Phase types for Stage 4
        stage5: Phase types for Stage 5
    """
    stage1: Dict[str, str] = Field(default_factory=lambda: {
        "phase1": "domain",   # Feature Inventory
        "phase2": "domain",   # MiPlatform Protocol
        "phase3": "feature",  # Deep Analysis
        "phase4": "feature",  # Spec Generation
    })
    stage4: Dict[str, str] = Field(default_factory=lambda: {
        "phase1": "system",   # Project Scaffold
        "phase2": "system",   # Mini-pilot
        "phase3": "feature",  # Domain Batch
        "phase4": "feature",  # Test Generation
        "phase5": "system",   # Integration Build
    })

    def get_phase_type(self, stage: int, phase: int) -> str:
        """Get phase type for a stage/phase combination.

        Args:
            stage: Stage number (1-5)
            phase: Phase number (1-5)

        Returns:
            Phase type: "system", "domain", or "feature"
        """
        stage_key = f"stage{stage}"
        phase_key = f"phase{phase}"
        stage_config = getattr(self, stage_key, None)
        if stage_config and phase_key in stage_config:
            return stage_config[phase_key]
        return "feature"  # Default to feature-level


class PathTemplateConfig(BaseModel):
    """Path templates for code generation.

    Attributes:
        source_base: Base directory for legacy source code
        target_base: Base directory for generated target code
        java_src_path: Java source path relative to target_base
        mapper_path: Mapper XML path relative to target_base
        java_package: Java package path (e.g., "com/example")
        specs_root: Root directory for specifications (e.g., "work/specs")
    """
    source_base: str = ""
    target_base: str = ""
    java_src_path: str = "src/main/java"
    mapper_path: str = "src/main/resources/mapper"
    java_package: str = ""
    specs_root: str = "work/specs"

    def get_java_base(self) -> str:
        """Get full Java source base path.

        Returns:
            Path like "next-hallain/src/main/java"
        """
        return f"{self.target_base}/{self.java_src_path}"

    def get_mapper_base(self) -> str:
        """Get full mapper XML base path.

        Returns:
            Path like "next-hallain/src/main/resources/mapper"
        """
        return f"{self.target_base}/{self.mapper_path}"

    def get_java_output(self, domain: str) -> str:
        """Get Java output directory for a domain.

        Args:
            domain: Domain code (e.g., "PA", "MM")

        Returns:
            Full path like "next-hallain/src/main/java/com/halla/pa"
        """
        return f"{self.get_java_base()}/{self.java_package}/{domain.lower()}"

    def get_mapper_output(self, domain: str) -> str:
        """Get mapper XML output directory for a domain.

        Args:
            domain: Domain code (e.g., "PA", "MM")

        Returns:
            Full path like "next-hallain/src/main/resources/mapper/pa"
        """
        return f"{self.get_mapper_base()}/{domain.lower()}"


class StageDefinitionConfig(BaseModel):
    """Stage definition for project workflow.

    Attributes:
        name: Human-readable stage name
        phases: List of phase identifiers (e.g., ["phase1", "phase2"])
        skills: Mapping of phase to skill name
    """
    name: str
    phases: List[str] = Field(default_factory=list)
    skills: Dict[str, str] = Field(default_factory=dict)


class TaskSourcesConfig(BaseModel):
    """Task source locations for the project.

    Attributes:
        feature_inventory_base: Base path for feature inventory files
        feature_inventory_pattern: Pattern for finding feature inventory files
        stage1_specs: Path to Stage 1 Phase 3 specs (deep analysis results)
        stage4_specs: Path to Stage 4 generation specs
    """
    feature_inventory_base: str = "work/specs/stage1-outputs/phase1"
    feature_inventory_pattern: str = "work/specs/stage1-outputs/phase1/{priority}/{domain}/feature-inventory.yaml"
    stage1_specs: str = "work/specs/stage1-outputs/phase3"
    stage4_specs: str = "work/specs/stage1-outputs/phase3"


class ProjectConfig(BaseModel):
    """Main project configuration.

    This configuration defines project-specific settings that allow
    Choisor to work with different migration projects.

    IMPORTANT: project.yaml is required for project-specific values.
    Generic defaults are used only as fallback.

    Attributes:
        name: Project name identifier
        description: Optional project description
        feature: Feature identification patterns
        domain: Domain-specific configuration
        paths: Path templates for code generation
        phase_types: Phase type configuration (system/domain/feature per phase)
        stages: Stage definitions with skill mappings
        task_sources: Task source locations
    """
    name: str = ""
    description: str = ""
    feature: FeaturePatternConfig = Field(default_factory=FeaturePatternConfig)
    domain: DomainConfig = Field(default_factory=DomainConfig)
    paths: PathTemplateConfig = Field(default_factory=PathTemplateConfig)
    phase_types: PhaseTypesConfig = Field(default_factory=PhaseTypesConfig)
    stages: Dict[str, StageDefinitionConfig] = Field(default_factory=dict)
    task_sources: TaskSourcesConfig = Field(default_factory=TaskSourcesConfig)

    model_config = {"extra": "allow"}  # Allow additional fields
