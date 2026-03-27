"""Task - Skill-aligned task representation

Tasks are aligned with skills using stage (1-5) and phase (1-5) numbers
instead of legacy string phase names.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"       # Task not yet started
    ASSIGNED = "assigned"     # Task assigned to a session
    IN_PROGRESS = "in_progress"  # Task currently being executed
    COMPLETED = "completed"   # Task finished successfully
    SKIP = "skip"             # Task skipped (e.g., empty folder)
    FAILED = "failed"         # Task failed with error


@dataclass
class Task:
    """Represents a migration task aligned with skill phases

    Attributes:
        id: Unique task identifier
        stage: Stage number (1-5), aligned with skill stages
        phase: Phase number (1-5), aligned with skill phases
        skill_id: Associated skill ID (e.g., "s1-01")
        feature_id: Feature identifier (e.g., "FEAT-PA-001")
        domain: Domain code (e.g., "PA", "CM", "SM")
        status: Current task status
        title: Human-readable task title
        priority: Priority score (1-10, higher = more important)
        created_at: Task creation timestamp
        updated_at: Last update timestamp
        metadata: Additional task metadata
        assigned_session: Session ID if assigned
        skip_reason: Reason for skipping if status is SKIP
    """
    id: str
    stage: int
    phase: int
    skill_id: str
    feature_id: str
    domain: str
    status: TaskStatus = TaskStatus.PENDING
    title: str = ""
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    assigned_session: Optional[str] = None
    skip_reason: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: Optional[int] = None  # minutes

    def __post_init__(self) -> None:
        """Generate default title if not provided"""
        if not self.title:
            self.title = f"[{self.skill_id}] {self.feature_id}"

    @property
    def is_terminal(self) -> bool:
        """Check if task is in a terminal state"""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.SKIP, TaskStatus.FAILED)

    @property
    def is_active(self) -> bool:
        """Check if task is currently active"""
        return self.status in (TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS)

    @property
    def can_start(self) -> bool:
        """Check if task can be started"""
        return self.status in (TaskStatus.PENDING, TaskStatus.SKIP)

    @property
    def phase_key(self) -> str:
        """Get phase key for grouping (e.g., 's1-01')"""
        return self.skill_id

    def mark_assigned(self, session_id: str) -> None:
        """Mark task as assigned to a session

        Args:
            session_id: Session identifier
        """
        self.status = TaskStatus.ASSIGNED
        self.assigned_session = session_id
        self.updated_at = datetime.now()

    def mark_in_progress(self) -> None:
        """Mark task as in progress"""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def mark_completed(self) -> None:
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.updated_at = datetime.now()

    def mark_failed(self, error_message: Optional[str] = None) -> None:
        """Mark task as failed

        Args:
            error_message: Optional error description
        """
        self.status = TaskStatus.FAILED
        self.updated_at = datetime.now()
        if error_message:
            self.metadata["error_message"] = error_message

    def mark_skipped(self, reason: str) -> None:
        """Mark task as skipped

        Args:
            reason: Reason for skipping
        """
        self.status = TaskStatus.SKIP
        self.skip_reason = reason
        self.updated_at = datetime.now()

    def reset(self) -> None:
        """Reset task to pending state"""
        self.status = TaskStatus.PENDING
        self.assigned_session = None
        self.skip_reason = None
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization

        Returns:
            Dictionary representation of the task
        """
        return {
            "id": self.id,
            "stage": self.stage,
            "phase": self.phase,
            "skill_id": self.skill_id,
            "feature_id": self.feature_id,
            "domain": self.domain,
            "status": self.status.value,
            "title": self.title,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "assigned_session": self.assigned_session,
            "skip_reason": self.skip_reason,
            "dependencies": self.dependencies,
            "estimated_duration": self.estimated_duration,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create Task from dictionary

        Args:
            data: Dictionary with task data

        Returns:
            Task instance
        """
        # Parse datetime fields
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        elif created_at is None:
            created_at = datetime.now()

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        elif updated_at is None:
            updated_at = datetime.now()

        # Parse status
        status_value = data.get("status", "pending")
        if isinstance(status_value, str):
            status = TaskStatus(status_value)
        else:
            status = status_value

        return cls(
            id=data["id"],
            stage=data["stage"],
            phase=data["phase"],
            skill_id=data["skill_id"],
            feature_id=data["feature_id"],
            domain=data["domain"],
            status=status,
            title=data.get("title", ""),
            priority=data.get("priority", 5),
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get("metadata", {}),
            assigned_session=data.get("assigned_session"),
            skip_reason=data.get("skip_reason"),
            dependencies=data.get("dependencies", []),
            estimated_duration=data.get("estimated_duration"),
        )

    @classmethod
    def create_for_skill(
        cls,
        skill_id: str,
        feature_id: str,
        domain: str,
        **kwargs: Any
    ) -> "Task":
        """Factory method to create a task for a skill

        Args:
            skill_id: Skill ID (e.g., "s1-01")
            feature_id: Feature ID
            domain: Domain code
            **kwargs: Additional task attributes

        Returns:
            Task instance

        Raises:
            ValueError: If skill_id format is invalid
        """
        import re

        # Parse skill_id to extract stage and phase
        match = re.match(r"s(\d+)-(\d{2})", skill_id.lower())
        if not match:
            raise ValueError(f"Invalid skill_id format: {skill_id}")

        stage = int(match.group(1))
        phase = int(match.group(2))

        # Generate task ID
        task_id = kwargs.pop("id", f"{skill_id}-{feature_id}")

        return cls(
            id=task_id,
            stage=stage,
            phase=phase,
            skill_id=skill_id.lower(),
            feature_id=feature_id,
            domain=domain,
            **kwargs
        )

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id!r}, skill_id={self.skill_id!r}, "
            f"feature_id={self.feature_id!r}, status={self.status.value!r})"
        )
