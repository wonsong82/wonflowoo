"""Choisor 2.0 Workflow Configuration Schema

Defines project-specific workflow structure including stages, phases,
skill mappings, and task generation rules. This enables Choisor to
support different migration workflows without code changes.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum


class PhaseType(str, Enum):
    """Phase execution type determining task granularity.

    - SYSTEM: One task total for the entire phase
    - DOMAIN: One task per domain
    - FEATURE: One task per feature (parallelizable)
    """
    SYSTEM = "system"
    DOMAIN = "domain"
    FEATURE = "feature"


class PhaseConfig(BaseModel):
    """Configuration for a single phase within a stage.

    Attributes:
        id: Unique phase identifier (e.g., "feature-inventory")
        number: Phase number within stage (1-based)
        name: Human-readable phase name
        type: Execution type (system/domain/feature)
        skill: Skill name or ID to execute
        outputs: Expected output file patterns
        generator: Optional custom generator module path
        validator: Optional custom validator module path
        prerequisites: List of phase IDs that must complete first
    """
    id: str
    number: int
    name: str = ""
    type: PhaseType = PhaseType.FEATURE
    skill: str = ""
    outputs: List[str] = Field(default_factory=list)
    generator: Optional[str] = None
    validator: Optional[str] = None
    prerequisites: List[str] = Field(default_factory=list)

    def __post_init__(self):
        if not self.name:
            self.name = self.id.replace("-", " ").title()


class StageConfig(BaseModel):
    """Configuration for a single stage in the workflow.

    Attributes:
        id: Unique stage identifier (e.g., "discovery")
        number: Stage number (1-based)
        name: Human-readable stage name
        description: Stage description
        output_dir: Output directory name (e.g., "stage1-outputs")
        phases: List of phases in this stage
        parallel_pairs: List of phase ID pairs that can run in parallel
        generator: Optional custom generator for entire stage
        validator: Optional custom validator for entire stage
    """
    id: str
    number: int
    name: str = ""
    description: str = ""
    output_dir: str = ""
    phases: List[PhaseConfig] = Field(default_factory=list)
    parallel_pairs: List[List[str]] = Field(default_factory=list)
    generator: Optional[str] = None
    validator: Optional[str] = None

    def __post_init__(self):
        if not self.name:
            self.name = self.id.replace("-", " ").title()
        if not self.output_dir:
            self.output_dir = f"stage{self.number}-outputs"

    def get_phase(self, phase_id: str) -> Optional[PhaseConfig]:
        """Get phase by ID."""
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None

    def get_phase_by_number(self, number: int) -> Optional[PhaseConfig]:
        """Get phase by number."""
        for phase in self.phases:
            if phase.number == number:
                return phase
        return None

    def get_parallel_skill(self, phase_id: str) -> Optional[str]:
        """Get parallel phase ID for a given phase."""
        for pair in self.parallel_pairs:
            if len(pair) == 2:
                if pair[0] == phase_id:
                    return pair[1]
                if pair[1] == phase_id:
                    return pair[0]
        return None


class TaskSourceConfig(BaseModel):
    """Configuration for task source locations.

    Attributes:
        path: Path template with placeholders ({priority}, {domain}, {feature})
        pattern: Glob pattern for discovering files
    """
    path: str = ""
    pattern: str = ""


class WorkflowConfig(BaseModel):
    """Main workflow configuration.

    Defines the complete workflow structure including all stages,
    phases, skill patterns, and task sources.

    Attributes:
        name: Workflow name identifier
        description: Workflow description
        skill_pattern: Pattern for skill directory names
        skill_dir: Root directory for skills
        stages: List of stage configurations
        task_sources: Task source configurations
    """
    name: str = ""
    description: str = ""
    skill_pattern: str = "s{stage}-{phase:02d}-*"
    skill_dir: str = ".claude/skills"
    stages: List[StageConfig] = Field(default_factory=list)
    task_sources: Dict[str, TaskSourceConfig] = Field(default_factory=dict)

    model_config = {"extra": "allow"}

    def get_stage(self, stage_id: str) -> Optional[StageConfig]:
        """Get stage by ID.

        Args:
            stage_id: Stage identifier (e.g., "discovery")

        Returns:
            StageConfig or None if not found
        """
        for stage in self.stages:
            if stage.id == stage_id:
                return stage
        return None

    def get_stage_by_number(self, number: int) -> Optional[StageConfig]:
        """Get stage by number.

        Args:
            number: Stage number (1-based)

        Returns:
            StageConfig or None if not found
        """
        for stage in self.stages:
            if stage.number == number:
                return stage
        return None

    def get_stage_id(self, number: int) -> Optional[str]:
        """Get stage ID from number.

        Args:
            number: Stage number (1-based)

        Returns:
            Stage ID or None if not found
        """
        stage = self.get_stage_by_number(number)
        return stage.id if stage else None

    def get_phase(self, stage_id: str, phase_id: str) -> Optional[PhaseConfig]:
        """Get phase by stage and phase ID.

        Args:
            stage_id: Stage identifier
            phase_id: Phase identifier

        Returns:
            PhaseConfig or None if not found
        """
        stage = self.get_stage(stage_id)
        if stage:
            return stage.get_phase(phase_id)
        return None

    def get_phase_type(self, stage_number: int, phase_number: int) -> PhaseType:
        """Get phase type for a stage/phase combination.

        Args:
            stage_number: Stage number (1-based)
            phase_number: Phase number (1-based)

        Returns:
            PhaseType (defaults to FEATURE if not found)
        """
        stage = self.get_stage_by_number(stage_number)
        if stage:
            phase = stage.get_phase_by_number(phase_number)
            if phase:
                return phase.type
        return PhaseType.FEATURE

    def get_skill_for_phase(
        self, stage_number: int, phase_number: int
    ) -> Optional[str]:
        """Get skill name for a stage/phase combination.

        Args:
            stage_number: Stage number (1-based)
            phase_number: Phase number (1-based)

        Returns:
            Skill name or None if not found
        """
        stage = self.get_stage_by_number(stage_number)
        if stage:
            phase = stage.get_phase_by_number(phase_number)
            if phase:
                return phase.skill
        return None

    def get_parallel_pairs(self) -> List[tuple]:
        """Get all parallel execution pairs across all stages.

        Returns:
            List of (skill_id, skill_id) tuples
        """
        pairs = []
        for stage in self.stages:
            for pair in stage.parallel_pairs:
                if len(pair) == 2:
                    # Convert phase IDs to skill IDs
                    phase1 = stage.get_phase(pair[0])
                    phase2 = stage.get_phase(pair[1])
                    if phase1 and phase2 and phase1.skill and phase2.skill:
                        pairs.append((phase1.skill, phase2.skill))
        return pairs

    def get_output_dir(self, stage_number: int) -> str:
        """Get output directory for a stage.

        Args:
            stage_number: Stage number (1-based)

        Returns:
            Output directory name (defaults to "stage{n}-outputs")
        """
        stage = self.get_stage_by_number(stage_number)
        if stage:
            return stage.output_dir
        return f"stage{stage_number}-outputs"

    def get_expected_outputs(
        self, stage_number: int, phase_number: int
    ) -> List[str]:
        """Get expected output patterns for a phase.

        Args:
            stage_number: Stage number (1-based)
            phase_number: Phase number (1-based)

        Returns:
            List of output file patterns
        """
        stage = self.get_stage_by_number(stage_number)
        if stage:
            phase = stage.get_phase_by_number(phase_number)
            if phase:
                return phase.outputs
        return []

    def get_all_skills(self) -> List[str]:
        """Get all skill names defined in the workflow.

        Returns:
            List of skill names
        """
        skills = []
        for stage in self.stages:
            for phase in stage.phases:
                if phase.skill:
                    skills.append(phase.skill)
        return skills

    def get_stage_count(self) -> int:
        """Get total number of stages."""
        return len(self.stages)

    def get_max_phase(self, stage_number: int) -> int:
        """Get maximum phase number for a stage.

        Args:
            stage_number: Stage number (1-based)

        Returns:
            Maximum phase number or 0 if stage not found
        """
        stage = self.get_stage_by_number(stage_number)
        if stage and stage.phases:
            return max(p.number for p in stage.phases)
        return 0
