"""Choisor 2.0 Configuration Module

Configuration management for the orchestrator including:
- Workflow settings
- Phase gate policies
- Priority weights
- Session pool settings
"""

from .schema import (
    ChoisorConfig,
    PhaseGateConfig,
    ParallelConfig,
    PathsConfig,
    StageConfig,
    AutoCommitConfig,
    WorkScopeConfig,
)
from .project_schema import (
    ProjectConfig,
    FeaturePatternConfig,
    DomainConfig,
    PathTemplateConfig,
    PhaseTypesConfig,
)
from .workflow_schema import (
    WorkflowConfig,
    StageConfig as WorkflowStageConfig,
    PhaseConfig,
    PhaseType,
    TaskSourceConfig,
)
from .loader import ConfigLoader, load_config, load_project_config, find_project_root

__all__ = [
    # Schema classes
    "ChoisorConfig",
    "PhaseGateConfig",
    "ParallelConfig",
    "PathsConfig",
    "StageConfig",
    "AutoCommitConfig",
    "WorkScopeConfig",
    # Project schema classes
    "ProjectConfig",
    "FeaturePatternConfig",
    "DomainConfig",
    "PathTemplateConfig",
    "PhaseTypesConfig",
    # Workflow schema classes
    "WorkflowConfig",
    "WorkflowStageConfig",
    "PhaseConfig",
    "PhaseType",
    "TaskSourceConfig",
    # Loader classes and functions
    "ConfigLoader",
    "load_config",
    "load_project_config",
    "find_project_root",
]
