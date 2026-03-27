"""Priority Engine - Task prioritization

Calculates task priority scores using configurable algorithms
and weights. Supports weighted scoring and FIFO ordering.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional


# Default weights for weighted score algorithm
DEFAULT_WEIGHTS = {
    "dependency_ready": 0.4,
    "priority_score": 0.4,
    "estimated_duration": 0.2,
}


class PriorityEngine:
    """Task priority calculation engine

    Supports multiple prioritization algorithms:
    - weighted_score: Combines dependency, priority, and duration factors
    - fifo: First-in-first-out based on creation time

    Example:
        >>> engine = PriorityEngine(algorithm="weighted_score")
        >>> score = engine.calculate_score(task, all_tasks)
        >>> sorted_tasks = engine.sort_by_priority(tasks)
    """

    def __init__(
        self,
        algorithm: str = "weighted_score",
        weights: Optional[Dict[str, float]] = None
    ):
        """Initialize priority engine

        Args:
            algorithm: Prioritization algorithm ("weighted_score" | "fifo")
            weights: Custom weights for weighted_score algorithm
        """
        self.algorithm = algorithm
        self.weights = weights or DEFAULT_WEIGHTS.copy()

    def calculate_score(
        self,
        task: Dict[str, Any],
        all_tasks: List[Dict[str, Any]]
    ) -> float:
        """Calculate priority score for a task

        Args:
            task: Task to calculate score for
            all_tasks: All tasks (for dependency checking)

        Returns:
            Priority score (higher = higher priority)
        """
        if self.algorithm == "weighted_score":
            return self._weighted_score(task, all_tasks)
        elif self.algorithm == "fifo":
            return self._fifo_score(task)
        else:
            return self._weighted_score(task, all_tasks)

    def _weighted_score(
        self,
        task: Dict[str, Any],
        all_tasks: List[Dict[str, Any]]
    ) -> float:
        """Calculate weighted score

        Combines:
        - dependency_ready: 1.0 if all dependencies complete, 0.0 otherwise
        - priority_score: Normalized priority (1-10 -> 0.1-1.0)
        - duration_score: Inverse of duration (shorter = higher score)

        Args:
            task: Task to score
            all_tasks: All tasks for dependency lookup

        Returns:
            Weighted score (0.0-1.0)
        """
        # Dependency readiness check
        dependency_ready = 1.0
        dependencies = task.get("dependencies", [])
        if dependencies:
            for dep_id in dependencies:
                dep_task = next((t for t in all_tasks if t.get("id") == dep_id), None)
                if dep_task and dep_task.get("status") != "completed":
                    dependency_ready = 0.0
                    break

        # Explicit priority (1-10, normalized to 0.1-1.0)
        priority = task.get("priority", 5)
        priority_score = priority / 10.0

        # Estimated duration (shorter tasks preferred)
        # Default to 0.5, max 120 minutes baseline
        duration_score = 0.5
        estimated_duration = task.get("estimated_duration")
        if estimated_duration:
            duration_score = 1.0 - min(estimated_duration / 120.0, 1.0)

        # Apply weights
        score = (
            dependency_ready * self.weights["dependency_ready"] +
            priority_score * self.weights["priority_score"] +
            duration_score * self.weights["estimated_duration"]
        )

        return score

    def _fifo_score(self, task: Dict[str, Any]) -> float:
        """Calculate FIFO score (older tasks = higher score)

        Args:
            task: Task to score

        Returns:
            FIFO score based on age
        """
        created_at = task.get("created_at")
        if not created_at:
            return 0.0

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        # Older tasks get higher scores
        now = datetime.now(created_at.tzinfo)
        age_seconds = (now - created_at).total_seconds()

        # Normalize to max 1 year
        max_age = 365 * 24 * 3600
        return min(age_seconds / max_age, 1.0)

    def sort_by_priority(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Sort tasks by priority (highest first)

        Args:
            tasks: Tasks to sort

        Returns:
            Sorted tasks list (highest priority first)
        """
        scored_tasks = [
            (task, self.calculate_score(task, tasks))
            for task in tasks
        ]

        # Sort by score descending
        scored_tasks.sort(key=lambda x: x[1], reverse=True)

        return [task for task, _ in scored_tasks]

    def select_next_task(
        self,
        tasks: List[Dict[str, Any]],
        max_allowed_phase: int,
        enabled_domains: Optional[List[str]] = None,
        target_phase: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Select next task to execute

        Filters by:
        1. Phase gate (must be <= max_allowed_phase)
        2. Target phase (if specified, must match exactly)
        3. Status (pending or skip for retry)
        4. Domain (if enabled_domains specified)

        Then sorts by priority and returns highest.

        Args:
            tasks: All tasks
            max_allowed_phase: Maximum allowed phase number
            enabled_domains: Optional list of allowed domains
            target_phase: If specified, only select tasks with this exact phase

        Returns:
            Highest priority eligible task or None
        """
        # Filter eligible tasks
        eligible = []
        for t in tasks:
            status = t.get("status")

            # Only pending or skip (retry) status
            if status not in ["pending", "skip"]:
                continue

            # Phase gate check
            task_phase = t.get("phase")
            metadata = t.get("metadata", {})

            # Try to extract phase from skill_id if not in task or metadata
            if task_phase is None:
                task_phase = metadata.get("phase")

            if task_phase is None:
                skill_id = t.get("skill_id") or metadata.get("skill_id", "")
                if skill_id:
                    import re
                    match = re.match(r"s\d+-(\d{2})", skill_id.lower())
                    if match:
                        task_phase = int(match.group(1))

            # Default to phase 1
            if task_phase is None:
                task_phase = 1

            # If target_phase specified, must match exactly
            if target_phase is not None:
                if task_phase != target_phase:
                    continue
            else:
                # Otherwise, must be <= max_allowed_phase
                if task_phase > max_allowed_phase:
                    continue

            eligible.append(t)

        if not eligible:
            return None

        # Domain filter (case-insensitive)
        if enabled_domains is not None:
            enabled_domains_upper = [d.upper() for d in enabled_domains]
            eligible = [
                t for t in eligible
                if t.get("metadata", {}).get("domain", "").upper() in enabled_domains_upper
                or t.get("domain", "").upper() in enabled_domains_upper
            ]

        if not eligible:
            return None

        # Sort by priority and return top
        sorted_tasks = self.sort_by_priority(eligible)
        return sorted_tasks[0] if sorted_tasks else None

    def _build_completed_phases_index(
        self,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, set]:
        """Build index of completed phases by feature.

        Args:
            tasks: All tasks

        Returns:
            Dict mapping "feature_id:stage" to set of completed phases
        """
        completed = {}
        for t in tasks:
            if t.get("status") != "completed":
                continue

            feature_id = (
                t.get("feature_id")
                or t.get("metadata", {}).get("feature_id")
                or t.get("category")
            )
            if not feature_id:
                continue

            stage = t.get("stage", 1)
            phase = t.get("phase") or t.get("metadata", {}).get("phase", 1)

            key = f"{feature_id}:{stage}"
            if key not in completed:
                completed[key] = set()
            completed[key].add(phase)

        return completed

    def get_next_tasks(
        self,
        tasks: List[Dict[str, Any]],
        max_allowed_phase: int,
        count: int = 10,
        enabled_domains: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get multiple next tasks to execute

        Useful for parallel execution planning.

        Args:
            tasks: All tasks
            max_allowed_phase: Maximum allowed phase number
            count: Number of tasks to return
            enabled_domains: Optional list of allowed domains

        Returns:
            List of highest priority eligible tasks
        """
        # Filter eligible tasks
        eligible = []
        for t in tasks:
            status = t.get("status")

            if status not in ["pending", "skip"]:
                continue

            metadata = t.get("metadata", {})
            task_phase = metadata.get("phase")

            if task_phase is None:
                skill_id = t.get("skill_id") or metadata.get("skill_id", "")
                if skill_id:
                    import re
                    match = re.match(r"s\d+-(\d{2})", skill_id.lower())
                    if match:
                        task_phase = int(match.group(1))

            if task_phase is None:
                task_phase = 1

            if task_phase <= max_allowed_phase:
                eligible.append(t)

        if not eligible:
            return []

        # Domain filter
        if enabled_domains is not None:
            enabled_domains_upper = [d.upper() for d in enabled_domains]
            eligible = [
                t for t in eligible
                if t.get("metadata", {}).get("domain", "").upper() in enabled_domains_upper
                or t.get("domain", "").upper() in enabled_domains_upper
            ]

        # Sort and return top N
        sorted_tasks = self.sort_by_priority(eligible)
        return sorted_tasks[:count]

    def set_weights(self, weights: Dict[str, float]) -> None:
        """Update priority weights

        Args:
            weights: New weights dictionary
        """
        self.weights.update(weights)

    def set_algorithm(self, algorithm: str) -> None:
        """Change prioritization algorithm

        Args:
            algorithm: Algorithm name ("weighted_score" or "fifo")
        """
        self.algorithm = algorithm
