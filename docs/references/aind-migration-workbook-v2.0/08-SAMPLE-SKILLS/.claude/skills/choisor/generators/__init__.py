"""Choisor 2.0 Generators Module

Task and instruction generators for the skill-centric orchestrator:
- TaskGenerator: Base class and factory for creating tasks from source scanning
- InstructionGenerator: Base class and factory for creating Claude session instructions
- Validators: Output validation for stage progression gates
"""

from .base import TaskGenerator, InstructionGenerator
from .task_generator import (
    TaskGeneratorFactory,
    DefaultTaskGenerator,
    Stage1TaskGenerator,
    Stage4TaskGenerator,
    Stage5TaskGenerator,
)
from .instruction_generator import (
    InstructionGeneratorFactory,
    DefaultInstructionGenerator,
    Stage4InstructionGenerator,
    Stage5InstructionGenerator,
)
from .validators import (
    ValidationResult,
    StageValidator,
    ValidatorFactory,
    DefaultValidator,
    Stage1Validator,
    Stage4Validator,
    Stage5Validator,
)
from .unified import (
    UnifiedTaskGenerator,
    UnifiedInstructionGenerator,
    create_task_generator,
    create_instruction_generator,
)

__all__ = [
    # Base classes
    "TaskGenerator",
    "InstructionGenerator",
    # Task generators
    "TaskGeneratorFactory",
    "DefaultTaskGenerator",
    "Stage1TaskGenerator",
    "Stage4TaskGenerator",
    "Stage5TaskGenerator",
    # Instruction generators
    "InstructionGeneratorFactory",
    "DefaultInstructionGenerator",
    "Stage4InstructionGenerator",
    "Stage5InstructionGenerator",
    # Validators
    "ValidationResult",
    "StageValidator",
    "ValidatorFactory",
    "DefaultValidator",
    "Stage1Validator",
    "Stage4Validator",
    "Stage5Validator",
    # Unified generators (auto-detect workflow.yaml)
    "UnifiedTaskGenerator",
    "UnifiedInstructionGenerator",
    "create_task_generator",
    "create_instruction_generator",
]
