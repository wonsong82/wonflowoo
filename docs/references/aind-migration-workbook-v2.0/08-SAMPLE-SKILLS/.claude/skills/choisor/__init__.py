"""Choisor 2.0 - Skill-centric Task Orchestrator

A skill-centric task orchestrator for 5-stage migration workflow.
Replaces choisor_old with key improvements:
- Skill-centric: Uses skill phase numbers (1-5) instead of legacy phase names
- Dynamic Discovery: Discovers skills from .claude/skills/s{stage}-{phase}-*/SKILL.md
- Parallel Support: Native support for s4-03 + s4-04 parallel execution
"""

__version__ = "2.0.0"
__author__ = "Migration Team"

from .core.skill_registry import Skill, SkillRegistry
from .core.task import Task, TaskStatus
from .core.phase_gate import PhaseGate
from .core.priority import PriorityEngine
from .core.contracts import ContractValidator, ContractViolation

__all__ = [
    "Skill",
    "SkillRegistry",
    "Task",
    "TaskStatus",
    "PhaseGate",
    "PriorityEngine",
    "ContractValidator",
    "ContractViolation",
]
