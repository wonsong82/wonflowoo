"""Skill Registry - Dynamic skill discovery and management

Discovers skills from .claude/skills/s{stage}-{phase}-*/SKILL.md files
and provides lookup by stage, phase, ID, or name.

Supports dynamic skill patterns via workflow.yaml configuration:
- skill_pattern: Pattern for matching skill directories
- parallel_pairs: Phase pairs that can run concurrently
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import re
import yaml

if TYPE_CHECKING:
    from ..config import WorkflowConfig


@dataclass
class Skill:
    """Represents a discovered skill from SKILL.md

    Attributes:
        id: Short identifier (e.g., "s1-01")
        name: Full skill name (e.g., "s1-01-discovery-feature-inventory")
        stage: Stage number (1-5)
        phase: Phase number within stage (1-5)
        description: Skill description from frontmatter
        skill_path: Path to the skill directory
        prerequisites: List of prerequisite skill IDs
        outputs: List of output file patterns
        parallel_with: Skill ID that can run in parallel (e.g., s4-03 <-> s4-04)
        invocation: CLI invocation string (e.g., "/s1-01-discovery-feature-inventory")
    """
    id: str
    name: str
    stage: int
    phase: int
    description: str
    skill_path: Path
    prerequisites: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    parallel_with: Optional[str] = None
    invocation: str = ""

    def __post_init__(self) -> None:
        """Set default invocation if not provided"""
        if not self.invocation:
            self.invocation = f"/{self.name}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "stage": self.stage,
            "phase": self.phase,
            "description": self.description,
            "skill_path": str(self.skill_path),
            "prerequisites": self.prerequisites,
            "outputs": self.outputs,
            "parallel_with": self.parallel_with,
            "invocation": self.invocation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        """Create Skill from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            stage=data["stage"],
            phase=data["phase"],
            description=data["description"],
            skill_path=Path(data["skill_path"]),
            prerequisites=data.get("prerequisites", []),
            outputs=data.get("outputs", []),
            parallel_with=data.get("parallel_with"),
            invocation=data.get("invocation", ""),
        )


class SkillRegistry:
    """Dynamic skill discovery and registry

    Discovers skills by globbing for SKILL.md files matching the pattern
    s{stage}-{phase}-*/SKILL.md and parses their frontmatter.

    Supports workflow.yaml configuration for:
    - Custom skill patterns (skill_pattern field)
    - Dynamic parallel pairs (parallel_pairs field on stages)

    Example:
        >>> registry = SkillRegistry(Path(".claude/skills"))
        >>> registry.discover()
        >>> skill = registry.get_skill(1, 1)
        >>> print(skill.name)  # "s1-01-discovery-feature-inventory"

        # With workflow config:
        >>> registry = SkillRegistry(Path(".claude/skills"))
        >>> registry.discover(workflow=workflow_config)
    """

    # Default pattern to parse skill directory names: s{stage}-{phase}-{name}
    DEFAULT_SKILL_PATTERN = r"^s(\d+)-(\d{2})-(.+)$"

    # Default parallel pairs (fallback when no workflow.yaml)
    DEFAULT_PARALLEL_PAIRS = {
        "s4-03": "s4-04",
        "s4-04": "s4-03",
    }

    def __init__(self, skills_root: Path):
        """Initialize registry with skills root directory

        Args:
            skills_root: Root directory containing skill directories
        """
        self.skills_root = skills_root
        self._skills: Dict[str, Skill] = {}  # Keyed by skill ID (e.g., "s1-01")
        self._skills_by_name: Dict[str, Skill] = {}  # Keyed by full name
        self._skill_pattern: re.Pattern = re.compile(self.DEFAULT_SKILL_PATTERN)
        self._parallel_pairs: Dict[str, str] = dict(self.DEFAULT_PARALLEL_PAIRS)
        self._workflow: Optional["WorkflowConfig"] = None

    def discover(
        self,
        workflow: Optional["WorkflowConfig"] = None
    ) -> None:
        """Discover all skills by globbing for SKILL.md files

        Searches for s*-*-*/SKILL.md patterns, parses frontmatter,
        and registers each skill.

        Args:
            workflow: Optional workflow config for dynamic patterns
        """
        self._skills.clear()
        self._skills_by_name.clear()
        self._workflow = workflow

        # Configure from workflow if provided
        if workflow:
            self._configure_from_workflow(workflow)
        else:
            # Reset to defaults
            self._skill_pattern = re.compile(self.DEFAULT_SKILL_PATTERN)
            self._parallel_pairs = dict(self.DEFAULT_PARALLEL_PAIRS)

        # Glob for SKILL.md files
        skill_files = self.skills_root.glob("s*-*-*/SKILL.md")

        for skill_file in skill_files:
            skill = self._parse_skill_file(skill_file)
            if skill:
                self._skills[skill.id] = skill
                self._skills_by_name[skill.name] = skill

    def _configure_from_workflow(self, workflow: "WorkflowConfig") -> None:
        """Configure registry from workflow configuration.

        Extracts skill pattern and parallel pairs from workflow.yaml.

        Args:
            workflow: Workflow configuration
        """
        # Build skill pattern from workflow.skill_pattern
        # workflow.skill_pattern format: "s{stage}-{phase:02d}-*"
        # Convert to regex: "^s(\d+)-(\d{2})-(.+)$"
        if workflow.skill_pattern:
            pattern = self._convert_pattern_to_regex(workflow.skill_pattern)
            self._skill_pattern = re.compile(pattern)
        else:
            self._skill_pattern = re.compile(self.DEFAULT_SKILL_PATTERN)

        # Build parallel pairs from workflow stages
        self._parallel_pairs = {}
        for stage in workflow.stages:
            if stage.parallel_pairs:
                for pair in stage.parallel_pairs:
                    if len(pair) == 2:
                        phase1_id, phase2_id = pair
                        # Get phase numbers from phase IDs
                        phase1 = self._find_phase_number(stage, phase1_id)
                        phase2 = self._find_phase_number(stage, phase2_id)
                        if phase1 and phase2:
                            skill1_id = f"s{stage.number}-{phase1:02d}"
                            skill2_id = f"s{stage.number}-{phase2:02d}"
                            self._parallel_pairs[skill1_id] = skill2_id
                            self._parallel_pairs[skill2_id] = skill1_id

    def _convert_pattern_to_regex(self, skill_pattern: str) -> str:
        """Convert workflow skill pattern to regex.

        Converts format strings like "s{stage}-{phase:02d}-*"
        to regex patterns like "^s(\d+)-(\d{2})-(.+)$"

        Args:
            skill_pattern: Workflow skill pattern string

        Returns:
            Regex pattern string
        """
        # Common format: "s{stage}-{phase:02d}-*"
        # Replace {stage} with (\d+)
        # Replace {phase:02d} or {phase} with (\d{2})
        # Replace * with (.+)
        pattern = skill_pattern
        pattern = re.sub(r'\{stage\}', r'(\\d+)', pattern)
        pattern = re.sub(r'\{phase:?\d*d?\}', r'(\\d{2})', pattern)
        pattern = pattern.replace('*', '(.+)')
        return f"^{pattern}$"

    def _find_phase_number(self, stage, phase_id: str) -> Optional[int]:
        """Find phase number by phase ID within a stage.

        Args:
            stage: Stage configuration
            phase_id: Phase ID to find

        Returns:
            Phase number or None
        """
        for phase in stage.phases:
            if phase.id == phase_id:
                return phase.number
        return None

    def _parse_skill_file(self, skill_file: Path) -> Optional[Skill]:
        """Parse a SKILL.md file and extract skill metadata

        Args:
            skill_file: Path to SKILL.md file

        Returns:
            Skill object or None if parsing fails
        """
        skill_dir = skill_file.parent
        dir_name = skill_dir.name

        # Parse directory name to extract stage and phase using instance pattern
        match = self._skill_pattern.match(dir_name)
        if not match:
            return None

        stage = int(match.group(1))
        phase = int(match.group(2))
        skill_id = f"s{stage}-{phase:02d}"

        # Read and parse frontmatter from SKILL.md
        try:
            content = skill_file.read_text(encoding="utf-8")
            frontmatter = self._parse_frontmatter(content)
        except Exception:
            frontmatter = {}

        # Extract metadata
        name = frontmatter.get("name", dir_name)
        description = frontmatter.get("description", "")

        # Parse prerequisites from content if available
        prerequisites = self._extract_prerequisites(content) if content else []

        # Parse outputs from content if available
        outputs = self._extract_outputs(content) if content else []

        # Check for parallel execution capability using instance pairs
        parallel_with = self._parallel_pairs.get(skill_id)

        return Skill(
            id=skill_id,
            name=name,
            stage=stage,
            phase=phase,
            description=description,
            skill_path=skill_dir,
            prerequisites=prerequisites,
            outputs=outputs,
            parallel_with=parallel_with,
        )

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from markdown content

        Args:
            content: Markdown content with optional YAML frontmatter

        Returns:
            Dictionary of frontmatter fields
        """
        if not content.startswith("---"):
            return {}

        # Find the closing ---
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return {}

        frontmatter_str = content[3:end_idx].strip()

        try:
            return yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError:
            return {}

    def _extract_prerequisites(self, content: str) -> List[str]:
        """Extract prerequisite skill IDs from SKILL.md content

        Looks for patterns like:
        - skill_id: "S4-02" or skill_id: "s4-02"
        - Predecessors table entries

        Args:
            content: SKILL.md content

        Returns:
            List of prerequisite skill IDs (normalized to lowercase)
        """
        prerequisites = []

        # Pattern for skill_dependencies section
        skill_id_pattern = re.compile(r'skill_id:\s*["\']?[Ss](\d+)-(\d{2})["\']?')

        for match in skill_id_pattern.finditer(content):
            stage = int(match.group(1))
            phase = int(match.group(2))
            prerequisites.append(f"s{stage}-{phase:02d}")

        return list(set(prerequisites))  # Remove duplicates

    def _extract_outputs(self, content: str) -> List[str]:
        """Extract output file patterns from SKILL.md content

        Args:
            content: SKILL.md content

        Returns:
            List of output file patterns
        """
        outputs = []

        # Look for common output patterns
        output_patterns = [
            r'output:\s*["\']([^"\']+)["\']',
            r'outputs:\s*\n\s*-\s*["\']?([^"\'\n]+)["\']?',
        ]

        for pattern in output_patterns:
            for match in re.finditer(pattern, content):
                outputs.append(match.group(1).strip())

        return outputs

    def get_skill(self, stage: int, phase: int) -> Optional[Skill]:
        """Get skill by stage and phase number

        Args:
            stage: Stage number (1-5)
            phase: Phase number (1-5)

        Returns:
            Skill object or None if not found
        """
        skill_id = f"s{stage}-{phase:02d}"
        return self._skills.get(skill_id)

    def get_skills_for_stage(self, stage: int) -> List[Skill]:
        """Get all skills for a given stage

        Args:
            stage: Stage number (1-5)

        Returns:
            List of skills in the stage, sorted by phase
        """
        skills = [s for s in self._skills.values() if s.stage == stage]
        return sorted(skills, key=lambda s: s.phase)

    def get_skill_by_id(self, skill_id: str) -> Optional[Skill]:
        """Get skill by ID

        Args:
            skill_id: Skill ID (e.g., "s1-01" or "S1-01")

        Returns:
            Skill object or None if not found
        """
        # Normalize to lowercase
        normalized_id = skill_id.lower()
        return self._skills.get(normalized_id)

    def get_skill_by_name(self, name: str) -> Optional[Skill]:
        """Get skill by full name

        Args:
            name: Full skill name (e.g., "s1-01-discovery-feature-inventory")

        Returns:
            Skill object or None if not found
        """
        return self._skills_by_name.get(name)

    def get_all_skills(self) -> List[Skill]:
        """Get all discovered skills

        Returns:
            List of all skills, sorted by stage and phase
        """
        return sorted(self._skills.values(), key=lambda s: (s.stage, s.phase))

    def get_parallel_skills(self) -> List[tuple[Skill, Skill]]:
        """Get pairs of skills that can run in parallel

        Returns:
            List of (skill1, skill2) tuples for parallel execution
        """
        pairs = []
        seen = set()

        for skill_id, parallel_id in self._parallel_pairs.items():
            if skill_id in seen or parallel_id in seen:
                continue

            skill1 = self._skills.get(skill_id)
            skill2 = self._skills.get(parallel_id)

            if skill1 and skill2:
                pairs.append((skill1, skill2))
                seen.add(skill_id)
                seen.add(parallel_id)

        return pairs

    @property
    def parallel_pairs(self) -> Dict[str, str]:
        """Get current parallel pairs configuration.

        Returns:
            Dictionary mapping skill IDs to their parallel partner
        """
        return dict(self._parallel_pairs)

    @property
    def workflow(self) -> Optional["WorkflowConfig"]:
        """Get current workflow configuration.

        Returns:
            WorkflowConfig or None if not using workflow mode
        """
        return self._workflow

    def __len__(self) -> int:
        """Return number of discovered skills"""
        return len(self._skills)

    def __iter__(self):
        """Iterate over all skills"""
        return iter(self.get_all_skills())
