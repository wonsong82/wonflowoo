"""Choisor 2.0 Core Modules

Core components for the skill-centric task orchestrator:
- SkillRegistry: Dynamic skill discovery and management
- Task: Task representation with skill alignment
- PhaseGate: Phase progression control (1-5 phases)
- PriorityEngine: Task prioritization
- ContractValidator: Inter-stage contract validation
"""

from .skill_registry import Skill, SkillRegistry
from .task import Task, TaskStatus
from .phase_gate import PhaseGate
from .priority import PriorityEngine
from .contracts import ContractValidator, ContractViolation

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
