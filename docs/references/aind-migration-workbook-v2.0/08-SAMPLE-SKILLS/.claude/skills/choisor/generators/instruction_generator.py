"""Instruction Generators - Factory pattern for stage-specific instruction generation

Provides instruction generators for creating Claude session instructions:
- DefaultInstructionGenerator: Generic instruction generation
- Stage4InstructionGenerator: Code generation specific instructions
"""

from pathlib import Path
from typing import Dict, Any, Tuple, List, Type, Optional

from .base import InstructionGenerator
from ..core import Task, Skill, SkillRegistry
from ..config import ChoisorConfig, ProjectConfig


class DefaultInstructionGenerator(InstructionGenerator):
    """Default instruction generator for most stages.

    Generates instructions that guide Claude to invoke the appropriate
    skill and produce outputs in the correct directory.
    """

    def generate(
        self,
        task: Task,
        skill: Skill,
        context: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Generate instruction with skill invocation.

        Args:
            task: Task to generate instruction for
            skill: Skill associated with the task
            context: Additional context containing config, paths, etc.

        Returns:
            Tuple of (instruction_text, model_id)
        """
        config: ChoisorConfig = context.get("config")
        project_root: Path = context.get("project_root", Path("."))
        session_id = context.get("session_id", "")
        max_allowed_phase = context.get("max_allowed_phase", task.phase)
        auto_to_max = context.get("auto_to_max", False)
        registry: SkillRegistry = context.get("registry")

        # Check if multi-phase mode
        is_multi_phase = auto_to_max and max_allowed_phase > task.phase

        # Build instruction lines
        lines = self._build_header(task, skill)

        # Skip separate skill section for multi-phase (included in multi-phase section)
        if not is_multi_phase:
            lines.extend(self._build_skill_section(skill))

        lines.extend(self._build_environment_section(task, project_root, config))

        # Build multi-phase section if auto_to_max is enabled
        if is_multi_phase:
            lines.extend(
                self._build_multi_phase_section(
                    task, skill, max_allowed_phase, config, registry, context
                )
            )
        else:
            lines.extend(
                self._build_output_path_section(
                    task, config, max_allowed_phase, auto_to_max
                )
            )
            lines.extend(self._build_commit_section(task, context))

        lines.extend(self._build_important_notes(task, max_allowed_phase, is_multi_phase))

        model_id = config.default_model if config else "claude-opus-4-5-20251101"

        return "\n".join(lines).strip(), model_id

    def _build_multi_phase_section(
        self,
        task: Task,
        skill: Skill,
        max_allowed_phase: int,
        config: ChoisorConfig,
        registry: SkillRegistry,
        context: Dict[str, Any]
    ) -> List[str]:
        """Build multi-phase auto-progression section.

        Args:
            task: Task object
            skill: Current skill
            max_allowed_phase: Maximum phase to progress to
            config: Configuration
            registry: Skill registry
            context: Context dict with session_id etc.

        Returns:
            List of instruction lines
        """
        session_id = context.get("session_id", "")
        stage_output = config.paths.stage_outputs.get(
            task.stage, f"stage{task.stage}-outputs"
        )
        priority_label = self._get_priority_label(task.domain, config)
        base_output = f"{config.paths.specs_root}/{stage_output}"

        # Collect phase info
        phases_info = []
        for phase_num in range(task.phase, max_allowed_phase + 1):
            phase_skill = registry.get_skill(task.stage, phase_num) if registry else None
            output_path = (
                f"{base_output}/phase{phase_num}/{priority_label}/"
                f"{task.domain.upper()}/{task.feature_id}/"
            )
            phases_info.append({
                "phase": phase_num,
                "skill": phase_skill,
                "output_path": output_path,
            })

        # Build header
        phase_range = f"Phase {task.phase} → {max_allowed_phase}"
        lines = [
            f"## Multi-Phase Workflow ({phase_range})",
            "",
            "This task uses **auto-progression mode**. Complete phases sequentially:",
            "",
        ]

        # Phase details
        for info in phases_info:
            phase_num = info["phase"]
            phase_skill = info["skill"]
            output_path = info["output_path"]

            skill_name = phase_skill.name if phase_skill else "(unknown)"
            skill_invocation = phase_skill.invocation if phase_skill else "(not found)"

            lines.extend([
                f"### Phase {phase_num}: {skill_name}",
                f"**Skill**: `{skill_invocation}`",
                f"**Output**: `{output_path}`",
                "",
            ])

        lines.append("---")
        lines.append("")

        # Workflow steps
        lines.extend(self._build_workflow_steps(task, phases_info, session_id))

        # Commit templates
        lines.extend(self._build_multi_commit_section(task, phases_info, session_id))

        return lines

    def _build_workflow_steps(
        self,
        task: Task,
        phases_info: List[Dict[str, Any]],
        session_id: str
    ) -> List[str]:
        """Build numbered workflow steps for multi-phase execution.

        Args:
            task: Task object
            phases_info: List of phase info dicts
            session_id: Session identifier

        Returns:
            List of workflow step lines
        """
        lines = [
            "## Workflow",
            "",
        ]

        step_num = 1
        for info in phases_info:
            phase_num = info["phase"]
            phase_skill = info["skill"]
            skill_invocation = phase_skill.invocation if phase_skill else "(skill not found)"

            lines.append(f"{step_num}. **Invoke Phase {phase_num} skill**: `{skill_invocation}`")
            step_num += 1
            lines.append(f"{step_num}. **Verify outputs** exist in phase{phase_num} output path")
            step_num += 1
            lines.append(
                f"{step_num}. **Commit Phase {phase_num}**: "
                f"`stage{task.stage} phase{phase_num} completion for {task.feature_id}`"
            )
            step_num += 1

        lines.append("")
        return lines

    def _build_multi_commit_section(
        self,
        task: Task,
        phases_info: List[Dict[str, Any]],
        session_id: str
    ) -> List[str]:
        """Build commit templates for multi-phase execution.

        Args:
            task: Task object
            phases_info: List of phase info dicts
            session_id: Session identifier

        Returns:
            List of commit template lines
        """
        lines = [
            "## Commit Templates",
            "",
        ]

        for info in phases_info:
            phase_num = info["phase"]
            phase_skill = info["skill"]
            skill_id = phase_skill.id if phase_skill else "unknown"

            lines.extend([
                f"**Phase {phase_num} commit:**",
                "```",
                f"stage{task.stage} phase{phase_num} completion for {task.feature_id}",
                "",
                f"Session ID: {session_id}",
                f"Domain: {task.domain.upper()}",
                f"Skill: {skill_id}",
                "```",
                "",
            ])

        return lines

    def _build_important_notes(
        self,
        task: Task,
        max_allowed_phase: int,
        is_multi_phase: bool = False
    ) -> List[str]:
        """Build important notes section.

        Args:
            task: Task object
            max_allowed_phase: Maximum allowed phase
            is_multi_phase: Whether this is a multi-phase workflow

        Returns:
            List of instruction lines
        """
        lines = [
            "## IMPORTANT",
            "",
        ]

        if is_multi_phase:
            lines.extend([
                f"- Complete phases **in order**: Phase {task.phase} → {max_allowed_phase}",
                "- **Commit after each phase** (not at the end)",
                f"- Do NOT skip to Phase {max_allowed_phase} without completing prior phases",
                "- Each skill provides detailed work procedures",
            ])
        else:
            lines.extend([
                "- The skill provides detailed work procedures.",
                f"- Do NOT exceed **phase {max_allowed_phase}**.",
                "- Commit changes after completing the task.",
            ])

        lines.append("")
        return lines


class Stage4InstructionGenerator(InstructionGenerator):
    """Stage 4 (Code Generation) instruction generator.

    Generates specialized instructions for code generation tasks,
    including spec input paths, Java output paths, and mapper paths.

    Attributes:
        _project_config: Project-specific configuration for path templates.
    """

    def __init__(self, project_config: Optional[ProjectConfig] = None):
        """Initialize with optional project configuration.

        Args:
            project_config: Project-specific config. If None, uses hallain defaults.
        """
        self._project_config = project_config or ProjectConfig()

    def generate(
        self,
        task: Task,
        skill: Skill,
        context: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Generate code generation instruction.

        Args:
            task: Task to generate instruction for
            skill: Skill associated with the task
            context: Additional context

        Returns:
            Tuple of (instruction_text, model_id)
        """
        config: ChoisorConfig = context.get("config")
        project_root: Path = context.get("project_root", Path("."))
        session_id = context.get("session_id", "")

        # Get paths from task metadata or config
        spec_path = task.metadata.get("spec_path", "")
        if not spec_path and config:
            # Construct spec path from config
            specs_root = config.paths.specs_root
            stage1_output = config.paths.stage_outputs.get(1, "stage1-outputs")
            priority_label = task.metadata.get("priority_label", "P2-Core")
            spec_path = (
                f"{specs_root}/{stage1_output}/phase3/"
                f"{priority_label}/{task.domain.upper()}/{task.feature_id}"
            )

        # Output paths for generated code (use project config)
        paths = self._project_config.paths
        java_output = paths.get_java_output(task.domain)
        mapper_output = paths.get_mapper_output(task.domain)

        # Determine phase-specific instruction
        if task.phase in (3, 4):  # code-gen or compile-verify
            instruction = self._generate_code_gen_instruction(
                task=task,
                skill=skill,
                spec_path=spec_path,
                java_output=java_output,
                mapper_output=mapper_output,
                session_id=session_id,
                project_root=project_root,
                config=config,
            )
        else:
            instruction = self._generate_default_instruction(
                task=task,
                skill=skill,
                session_id=session_id,
                project_root=project_root,
                config=config,
            )

        model_id = config.default_model if config else "claude-opus-4-5-20251101"
        return instruction, model_id

    def _generate_code_gen_instruction(
        self,
        task: Task,
        skill: Skill,
        spec_path: str,
        java_output: str,
        mapper_output: str,
        session_id: str,
        project_root: Path,
        config: ChoisorConfig,
    ) -> str:
        """Generate code generation phase instruction.

        Args:
            task: Task object
            skill: Skill object
            spec_path: Path to specification files
            java_output: Java output directory
            mapper_output: Mapper XML output directory
            session_id: Session identifier
            project_root: Project root path
            config: Configuration

        Returns:
            Instruction text
        """
        complexity = task.metadata.get("complexity_estimate", "MEDIUM")
        endpoint_count = task.metadata.get("endpoint_count", 0)

        return f"""# {task.feature_id} Code Generation

## Task Information
- **Feature ID**: {task.feature_id}
- **Domain**: {task.domain.upper()}
- **Stage**: 4
- **Phase**: {task.phase} (code-generation)
- **Complexity**: {complexity}
- **Endpoints**: {endpoint_count}

## Required Skill

**You MUST invoke the skill:**

```
{skill.invocation}
```

## Input/Output Paths

- **Specification Input**: `{spec_path}/`
- **Java Output**: `{java_output}/`
- **Mapper XML Output**: `{mapper_output}/`

## Project Environment
- **Project Root**: {project_root}
- **Source Base**: {config.paths.source_base if config else 'hallain'}/

## Work Steps

1. Read the feature specification from the input path
2. Generate the following components:
   - Entity classes
   - Repository/Mapper interfaces
   - Service classes
   - Controller (REST API)
   - MyBatis mapper XML
3. Validate generated code compiles
4. Commit changes

## Completion Criteria

1. All components generated according to specification
2. Code compiles without errors
3. Changes committed to git

## Commit Message Template
```
stage4 phase{task.phase} completion for {task.feature_id}

Session ID: {session_id}
Domain: {task.domain.upper()}
Skill: {skill.id}
```

## IMPORTANT

- Follow QUERY-FIRST principle: preserve SQL 100%
- iBatis to MyBatis syntax conversion only
- Do not modify database schema or stored procedures
"""

    def _generate_default_instruction(
        self,
        task: Task,
        skill: Skill,
        session_id: str,
        project_root: Path,
        config: ChoisorConfig,
    ) -> str:
        """Generate default stage 4 instruction.

        Args:
            task: Task object
            skill: Skill object
            session_id: Session identifier
            project_root: Project root path
            config: Configuration

        Returns:
            Instruction text
        """
        return f"""# {task.feature_id} - Stage 4 Phase {task.phase}

## Task Information
- **Feature ID**: {task.feature_id}
- **Domain**: {task.domain.upper()}
- **Stage**: 4
- **Phase**: {task.phase}

## Required Skill

**You MUST invoke the skill:**

```
{skill.invocation}
```

## Project Environment
- **Project Root**: {project_root}

## Commit on Completion

Commit message template:
```
stage4 phase{task.phase} completion for {task.feature_id}

Session ID: {session_id}
Domain: {task.domain.upper()}
Skill: {skill.id}
```
"""


class Stage5InstructionGenerator(DefaultInstructionGenerator):
    """Stage 5 (Assurance) instruction generator.

    Extends DefaultInstructionGenerator with quality assurance
    specific instructions.
    """

    def generate(
        self,
        task: Task,
        skill: Skill,
        context: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Generate assurance instruction.

        Args:
            task: Task object
            skill: Skill object
            context: Context dict

        Returns:
            Tuple of (instruction_text, model_id)
        """
        # Use default generation as base
        instruction, model_id = super().generate(task, skill, context)

        # Add assurance-specific content
        config: ChoisorConfig = context.get("config")
        source_task_id = task.metadata.get("source_task_id", "")

        assurance_section = f"""
## Quality Assurance Focus

- Verify generated code matches specification
- Check coding conventions compliance
- Validate API contracts
- Review performance patterns (N+1 queries, etc.)

**Source Task**: {source_task_id}
"""

        # Insert before IMPORTANT section
        if "## IMPORTANT" in instruction:
            instruction = instruction.replace(
                "## IMPORTANT", assurance_section + "\n## IMPORTANT"
            )
        else:
            instruction += assurance_section

        return instruction, model_id


class InstructionGeneratorFactory:
    """Factory for creating stage-specific instruction generators.

    Example:
        >>> generator = InstructionGeneratorFactory.create(4)
        >>> isinstance(generator, Stage4InstructionGenerator)
        True
    """

    _generators: Dict[int, Type[InstructionGenerator]] = {
        1: DefaultInstructionGenerator,
        2: DefaultInstructionGenerator,
        3: DefaultInstructionGenerator,
        4: Stage4InstructionGenerator,
        5: Stage5InstructionGenerator,
    }

    @classmethod
    def create(
        cls,
        stage: int,
        project_config: Optional[ProjectConfig] = None
    ) -> InstructionGenerator:
        """Create instruction generator for stage.

        Args:
            stage: Stage number (1-5)
            project_config: Optional project-specific configuration

        Returns:
            InstructionGenerator instance
        """
        generator_class = cls._generators.get(stage, DefaultInstructionGenerator)

        # Pass project_config to generators that support it
        if generator_class == Stage4InstructionGenerator:
            return Stage4InstructionGenerator(project_config)

        return generator_class()

    @classmethod
    def register(cls, stage: int, generator_class: Type[InstructionGenerator]) -> None:
        """Register custom generator for stage.

        Args:
            stage: Stage number
            generator_class: InstructionGenerator subclass
        """
        cls._generators[stage] = generator_class

    @classmethod
    def get_available_stages(cls) -> List[int]:
        """Get list of registered stage numbers.

        Returns:
            List of stage numbers
        """
        return sorted(cls._generators.keys())
