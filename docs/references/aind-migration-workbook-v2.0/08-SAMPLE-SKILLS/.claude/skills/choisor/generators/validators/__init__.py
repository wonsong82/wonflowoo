"""Choisor 2.0 Validators Module

Output validators for stage progression gates:
- ValidationResult: Structured validation result with errors and warnings
- StageValidator: Abstract base class for stage validators
- Stage-specific validators for checking output completeness and correctness
"""

from .base import ValidationResult, StageValidator
from .stage_validators import (
    ValidatorFactory,
    DefaultValidator,
    Stage1Validator,
    Stage4Validator,
    Stage5Validator,
)

__all__ = [
    # Base classes
    "ValidationResult",
    "StageValidator",
    # Factory
    "ValidatorFactory",
    # Concrete validators
    "DefaultValidator",
    "Stage1Validator",
    "Stage4Validator",
    "Stage5Validator",
]
