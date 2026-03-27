"""Choisor 2.0 Configuration Schema

Pydantic-based configuration schema for the Choisor orchestrator.
Supports the 5-stage migration workflow with skill mappings,
phase gates, and parallel execution settings.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class AssignmentConfig(BaseModel):
    """Assignment control settings.

    Attributes:
        enabled: If True, allow task assignment; if False, stop new assignments
        delay: Delay in minutes before assigning tasks (0 or None = no delay)
        stale_timeout: Minutes before considering a task stale (default 10)
    """
    enabled: bool = True
    delay: Optional[int] = None
    stale_timeout: int = 10


class PhaseGateConfig(BaseModel):
    """Phase Gate settings for controlling workflow progression.

    Attributes:
        enabled: Whether phase gates are active
        strict_mode: If True, fail immediately on phase gate violation
        auto_to_max: If True, auto-advance to max allowed phase
        max_allowed_phase: Maximum phase that can be executed (1-5)
    """
    enabled: bool = True
    strict_mode: bool = True
    auto_to_max: bool = True
    max_allowed_phase: Optional[int] = None  # None = calculate from task status


class ParallelConfig(BaseModel):
    """Parallel execution settings for concurrent skill execution.

    Attributes:
        enabled: Whether parallel execution is allowed
        pairs: List of skill pairs that can run in parallel
        max_parallel_sessions: Maximum concurrent sessions
    """
    enabled: bool = True
    pairs: List[List[str]] = Field(
        default_factory=lambda: [["s4-03", "s4-04"]]
    )
    max_parallel_sessions: int = 10


class PathsConfig(BaseModel):
    """Path configurations for project resources.

    Attributes:
        skills_root: Root directory for skill definitions
        specs_root: Root directory for stage specifications
        source_base: Base directory for legacy source code (configure in project.yaml)
        contracts_path: Path to inter-stage contracts YAML
        stage_outputs: Mapping of stage number to output directory name
    """
    skills_root: str = ".claude/skills"
    specs_root: str = "work/specs"
    source_base: str = ""  # Project-specific, configure in project.yaml
    contracts_path: str = ".claude/skills/common/inter-stage-contracts.yaml"

    stage_outputs: Dict[int, str] = Field(default_factory=lambda: {
        1: "stage1-outputs",
        2: "stage2-outputs",
        3: "stage3-outputs",
        4: "stage4-outputs",
        5: "stage5-outputs",
    })


class StageConfig(BaseModel):
    """Stage-specific configuration.

    Attributes:
        name: Human-readable stage name
        description: Stage description
        phases: List of phase numbers in this stage
        skills: Mapping of phase number to skill name
    """
    name: str
    description: str = ""
    phases: List[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5])
    skills: Dict[int, str] = Field(default_factory=dict)


class AutoCommitConfig(BaseModel):
    """Auto-commit settings for version control integration.

    Attributes:
        enabled: Whether auto-commit is active
        commit_on_completion: If True, commit after each phase completion
    """
    enabled: bool = True
    commit_on_completion: bool = True


class WorkScopeConfig(BaseModel):
    """Work scope filtering to limit processing to specific domains/stages.

    Attributes:
        enabled_domains: List of domains to process (None = all)
        enabled_stages: List of stage numbers to process (None = all)
    """
    enabled_domains: Optional[List[str]] = None
    enabled_stages: Optional[List[int]] = None


class TaskSourcesConfig(BaseModel):
    """Task source locations configuration.

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


class ChoisorConfig(BaseModel):
    """Main Choisor configuration.

    This is the root configuration object that contains all settings
    for the Choisor orchestrator, including workflow control, provider
    settings, and sub-configurations.

    Attributes:
        assignment: Assignment control settings
        current_stage: Current active stage (1-5)
        current_phase: Current active phase within stage (1-5)
        provider: LLM provider name
        default_model: Default model ID for LLM calls
        phase_gate: Phase gate configuration
        parallel: Parallel execution configuration
        paths: Path configurations
        auto_commit: Auto-commit configuration
        work_scope: Work scope filtering configuration
        stages: Per-stage configurations (1-5, loaded from project.yaml)
        domain_priority_map: Domain groupings by priority tier (from project.yaml)
        task_sources: Task source locations (from project.yaml)
    """
    # Assignment control
    assignment: AssignmentConfig = Field(default_factory=AssignmentConfig)

    # Current position in workflow
    current_stage: int = 1
    current_phase: int = 1

    # Provider settings
    provider: str = "anthropic"
    default_model: str = "claude-opus-4-5-20251101"

    # Sub-configurations
    phase_gate: PhaseGateConfig = Field(default_factory=PhaseGateConfig)
    parallel: ParallelConfig = Field(default_factory=ParallelConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    auto_commit: AutoCommitConfig = Field(default_factory=AutoCommitConfig)
    work_scope: WorkScopeConfig = Field(default_factory=WorkScopeConfig)

    # Stage configurations (1-5, loaded from project.yaml if not in config.yaml)
    stages: Dict[int, StageConfig] = Field(default_factory=dict)

    # Domain priority mapping (project-specific, loaded from project.yaml)
    domain_priority_map: Dict[str, List[str]] = Field(default_factory=lambda: {
        "P0-Foundation": [],
        "P1-Hub": [],
        "P2-Core": [],
        "P3-Supporting": [],
    })

    # Task sources (project-specific, loaded from project.yaml)
    task_sources: TaskSourcesConfig = Field(default_factory=TaskSourcesConfig)

    model_config = {"extra": "allow"}  # Allow additional fields
