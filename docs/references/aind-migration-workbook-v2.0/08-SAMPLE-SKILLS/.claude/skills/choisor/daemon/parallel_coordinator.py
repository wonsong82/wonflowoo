"""Choisor 2.0 Daemon - Parallel Task Coordinator

Coordinates parallel task execution for skill pairs that can run concurrently:
- s4-03 (domain-batch) + s4-04 (test-generation)

Enables code generation and test generation to run in parallel for the same
feature, maximizing throughput while maintaining correctness.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set

from ..core import Task, SkillRegistry


@dataclass
class ParallelPairState:
    """State of a parallel task pair execution.

    Attributes:
        primary_skill_id: Primary skill ID (e.g., "s4-03")
        parallel_skill_id: Parallel skill ID (e.g., "s4-04")
        feature_id: Feature being processed
        primary_started: When primary task started
        parallel_started: When parallel task started
        primary_completed: When primary task completed
        parallel_completed: When parallel task completed
    """
    primary_skill_id: str
    parallel_skill_id: str
    feature_id: str
    primary_started: Optional[datetime] = None
    parallel_started: Optional[datetime] = None
    primary_completed: Optional[datetime] = None
    parallel_completed: Optional[datetime] = None

    @property
    def is_complete(self) -> bool:
        """Check if both tasks are complete."""
        return self.primary_completed is not None and self.parallel_completed is not None

    @property
    def is_in_progress(self) -> bool:
        """Check if either task is in progress."""
        return (
            (self.primary_started is not None and self.primary_completed is None) or
            (self.parallel_started is not None and self.parallel_completed is None)
        )


class ParallelCoordinator:
    """Coordinates parallel task execution (e.g., s4-03 + s4-04).

    Manages the pairing and state tracking of parallel skill executions,
    enabling code generation and test generation to run concurrently.

    Attributes:
        parallel_pairs: List of skill ID pairs that can run in parallel
        registry: Skill registry for lookups
    """

    # Default parallel pairs: code generation + test generation
    DEFAULT_PARALLEL_PAIRS: List[Tuple[str, str]] = [
        ("s4-03", "s4-04"),  # domain-batch + test-generation
    ]

    def __init__(
        self,
        parallel_pairs: Optional[List[List[str]]] = None,
        registry: Optional[SkillRegistry] = None,
    ):
        """Initialize parallel coordinator.

        Args:
            parallel_pairs: List of [skill_id, skill_id] pairs that can run in parallel
            registry: Optional skill registry for lookups
        """
        # Convert list-of-lists to list-of-tuples
        if parallel_pairs:
            self.parallel_pairs = [tuple(pair) for pair in parallel_pairs]
        else:
            self.parallel_pairs = self.DEFAULT_PARALLEL_PAIRS

        self.registry = registry

        # Build lookup maps for quick access
        self._pair_map: Dict[str, str] = {}
        for pair in self.parallel_pairs:
            if len(pair) == 2:
                self._pair_map[pair[0]] = pair[1]
                self._pair_map[pair[1]] = pair[0]

        # Track active parallel executions by feature
        self._active_pairs: Dict[str, ParallelPairState] = {}

        # Track pending parallel tasks
        self._pending_parallels: Dict[str, str] = {}  # task_id -> parallel_skill_id

    def can_run_parallel(self, task: Task) -> bool:
        """Check if a task can run in parallel with another.

        Args:
            task: Task to check

        Returns:
            True if task's skill supports parallel execution
        """
        skill_id = f"s{task.stage}-{task.phase:02d}"
        return skill_id in self._pair_map

    def can_run_parallel_by_skill_id(self, skill_id: str) -> bool:
        """Check if a skill ID supports parallel execution.

        Args:
            skill_id: Skill ID (e.g., "s4-03")

        Returns:
            True if skill supports parallel execution
        """
        return skill_id.lower() in self._pair_map

    def get_parallel_skill_id(self, skill_id: str) -> Optional[str]:
        """Get the parallel skill ID for a given skill.

        Args:
            skill_id: Skill ID (e.g., "s4-03")

        Returns:
            Parallel skill ID (e.g., "s4-04") or None
        """
        return self._pair_map.get(skill_id.lower())

    def create_parallel_task(
        self,
        task: Task,
        all_tasks: List[Dict],
    ) -> Optional[Task]:
        """Create a parallel task for the given task if applicable.

        Looks for a matching task with the parallel skill ID and same
        feature ID that is ready to execute.

        Args:
            task: Primary task
            all_tasks: List of all task dictionaries

        Returns:
            Parallel Task object if found and ready, None otherwise
        """
        if not self.can_run_parallel(task):
            return None

        skill_id = f"s{task.stage}-{task.phase:02d}"
        parallel_skill_id = self.get_parallel_skill_id(skill_id)

        if not parallel_skill_id:
            return None

        # Parse parallel skill ID to get stage and phase
        parts = parallel_skill_id.split("-")
        if len(parts) != 2:
            return None

        parallel_stage = int(parts[0][1:])  # "s4" -> 4
        parallel_phase = int(parts[1])       # "03" -> 3

        # Look for matching pending task with same feature ID
        for task_dict in all_tasks:
            if (
                task_dict.get("feature_id") == task.feature_id and
                task_dict.get("stage") == parallel_stage and
                task_dict.get("phase") == parallel_phase and
                task_dict.get("status") == "pending"
            ):
                # Found a matching parallel task
                return Task.from_dict(task_dict)

        return None

    def register_parallel_start(
        self,
        skill_id: str,
        feature_id: str,
        is_primary: bool = True,
    ) -> None:
        """Register the start of a parallel task.

        Args:
            skill_id: Skill ID starting
            feature_id: Feature being processed
            is_primary: Whether this is the primary or secondary task
        """
        parallel_id = self.get_parallel_skill_id(skill_id)
        if not parallel_id:
            return

        key = f"{feature_id}"

        if key not in self._active_pairs:
            self._active_pairs[key] = ParallelPairState(
                primary_skill_id=skill_id if is_primary else parallel_id,
                parallel_skill_id=parallel_id if is_primary else skill_id,
                feature_id=feature_id,
            )

        state = self._active_pairs[key]
        if is_primary:
            state.primary_started = datetime.now()
        else:
            state.parallel_started = datetime.now()

    def on_task_complete(self, skill_id: str, feature_id: Optional[str] = None) -> Optional[str]:
        """Called when a task completes.

        Updates parallel pair state and returns queued parallel task if any.

        Args:
            skill_id: Completed skill ID
            feature_id: Optional feature ID

        Returns:
            Parallel skill ID if a parallel task should be triggered
        """
        # Find active pair for this skill/feature
        for key, state in list(self._active_pairs.items()):
            if feature_id and not key.endswith(feature_id):
                continue

            now = datetime.now()

            if state.primary_skill_id == skill_id:
                state.primary_completed = now
            elif state.parallel_skill_id == skill_id:
                state.parallel_completed = now

            # Clean up if both complete
            if state.is_complete:
                del self._active_pairs[key]

        return None

    def get_parallel_opportunity(
        self,
        task_dict: Dict,
        available_sessions: int,
    ) -> Optional[str]:
        """Check if there's an opportunity to run a parallel task.

        Args:
            task_dict: Task that was just assigned
            available_sessions: Number of available sessions

        Returns:
            Parallel skill ID if a parallel task should be assigned
        """
        if available_sessions < 1:
            return None

        skill_id = task_dict.get("skill_id", "")
        if not self.can_run_parallel_by_skill_id(skill_id):
            return None

        return self.get_parallel_skill_id(skill_id)

    def get_active_parallel_features(self, skill_id: str) -> Set[str]:
        """Get features currently running in parallel for a skill.

        Args:
            skill_id: Skill ID to check

        Returns:
            Set of feature IDs running in parallel
        """
        features = set()
        for key, state in self._active_pairs.items():
            if state.primary_skill_id == skill_id or state.parallel_skill_id == skill_id:
                if state.is_in_progress:
                    features.add(state.feature_id)
        return features

    def get_stats(self) -> Dict[str, int]:
        """Get parallel execution statistics.

        Returns:
            Dictionary with parallel execution stats
        """
        active_count = sum(1 for s in self._active_pairs.values() if s.is_in_progress)
        completed_count = len(self._pending_parallels)

        return {
            "active_pairs": active_count,
            "pending_parallels": completed_count,
            "total_pairs_tracked": len(self._active_pairs),
        }

    def is_parallel_pair(self, skill_id_1: str, skill_id_2: str) -> bool:
        """Check if two skill IDs form a parallel pair.

        Args:
            skill_id_1: First skill ID
            skill_id_2: Second skill ID

        Returns:
            True if the skills form a parallel pair
        """
        parallel = self.get_parallel_skill_id(skill_id_1.lower())
        return parallel is not None and parallel == skill_id_2.lower()

    def to_dict(self) -> Dict:
        """Serialize coordinator state to dictionary.

        Returns:
            Dictionary representation of state
        """
        return {
            "parallel_pairs": [list(pair) for pair in self.parallel_pairs],
            "active_pairs": {
                k: {
                    "primary_skill_id": v.primary_skill_id,
                    "parallel_skill_id": v.parallel_skill_id,
                    "feature_id": v.feature_id,
                    "primary_started": v.primary_started.isoformat() if v.primary_started else None,
                    "parallel_started": v.parallel_started.isoformat() if v.parallel_started else None,
                    "primary_completed": v.primary_completed.isoformat() if v.primary_completed else None,
                    "parallel_completed": v.parallel_completed.isoformat() if v.parallel_completed else None,
                }
                for k, v in self._active_pairs.items()
            },
            "stats": self.get_stats(),
        }
