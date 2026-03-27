"""Phase Gate Manager - Skill-aligned Phase progression control

Controls phase progression ensuring all features complete a phase
before advancing to the next. Uses integer phase numbers (1-5)
instead of legacy string phase names.
"""

from typing import Dict, List, Optional, Any


class PhaseGate:
    """Skill-aligned Phase Gate manager

    Ensures orderly phase progression across all features:
    - All features must complete phase N before any can proceed to phase N+1
    - Supports override for manual phase advancement
    - Provides phase status reporting

    Example:
        >>> gate = PhaseGate(max_phases=5)
        >>> max_phase = gate.get_max_allowed_phase(tasks)
        >>> if gate.can_proceed_to_phase(3, max_phase):
        ...     # Safe to execute phase 3 tasks
    """

    def __init__(self, max_phases: int = 5):
        """Initialize Phase Gate manager

        Args:
            max_phases: Maximum number of phases (default: 5)
        """
        self.max_phases = max_phases
        self.phases = list(range(1, max_phases + 1))  # [1, 2, 3, 4, 5]

    def get_max_allowed_phase(
        self,
        tasks: List[Dict[str, Any]],
        override: Optional[int] = None
    ) -> int:
        """Return maximum allowed phase number

        Args:
            tasks: List of task dictionaries
            override: Manual phase override (if provided, used directly)

        Returns:
            Maximum allowed phase number (1-5)
        """
        # Manual override takes precedence
        if override is not None and 1 <= override <= self.max_phases:
            return override

        # Filter to feature tasks only
        feature_tasks = [
            t for t in tasks
            if t.get("task_unit_type") == "feature"
        ]

        if not feature_tasks:
            return 1  # Start with phase 1 if no tasks

        # Check phases in reverse order to find highest completed
        for phase in reversed(self.phases):
            if self._is_phase_complete(phase, feature_tasks):
                # Phase is complete, allow next phase
                if phase < self.max_phases:
                    return phase + 1
                else:
                    return phase  # At max phase

        # No phase complete, start with phase 1
        return 1

    def _is_phase_complete(
        self,
        phase: int,
        feature_tasks: List[Dict[str, Any]]
    ) -> bool:
        """Check if phase is complete for all features

        A phase is complete when all features have completed tasks
        for that phase.

        Args:
            phase: Phase number to check
            feature_tasks: List of feature task dictionaries

        Returns:
            True if phase is complete for all features
        """
        if not feature_tasks:
            return False

        # Group tasks by feature
        features_by_id = self._group_by_feature(feature_tasks)

        if not features_by_id:
            return False

        # Check each feature for phase completion
        for feature_id, tasks in features_by_id.items():
            if not self._is_feature_phase_complete(feature_id, phase, tasks):
                return False

        return True

    def _group_by_feature(
        self,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group tasks by feature ID

        Args:
            tasks: List of task dictionaries

        Returns:
            Dictionary mapping feature_id to list of tasks
        """
        features_by_id: Dict[str, List[Dict[str, Any]]] = {}

        for task in tasks:
            # Try metadata.feature_id first, then category
            metadata = task.get("metadata", {})
            feature_id = metadata.get("feature_id") or task.get("category")
            if not feature_id:
                continue

            if feature_id not in features_by_id:
                features_by_id[feature_id] = []
            features_by_id[feature_id].append(task)

        return features_by_id

    def _is_feature_phase_complete(
        self,
        feature_id: str,
        phase: int,
        tasks: List[Dict[str, Any]]
    ) -> bool:
        """Check if a specific feature's phase is complete

        Args:
            feature_id: Feature identifier
            phase: Phase number to check
            tasks: List of tasks for this feature

        Returns:
            True if the feature has completed this phase
        """
        # Find tasks for this phase
        phase_tasks = []
        for t in tasks:
            metadata = t.get("metadata", {})
            # Support both integer phase and skill_id-based phase
            task_phase = metadata.get("phase")
            if task_phase is None:
                # Try to extract phase from skill_id (e.g., "s1-03" -> 3)
                skill_id = t.get("skill_id") or metadata.get("skill_id", "")
                if skill_id:
                    import re
                    match = re.match(r"s\d+-(\d{2})", skill_id.lower())
                    if match:
                        task_phase = int(match.group(1))

            # Match phase or default to phase 1 for unspecified
            if task_phase == phase or (phase == 1 and task_phase is None):
                phase_tasks.append(t)

        if not phase_tasks:
            # No tasks for this phase
            # Phase 1 with no tasks is considered complete
            if phase == 1:
                return True
            return False

        # Check all phase tasks are completed
        for task in phase_tasks:
            if task.get("status") != "completed":
                return False

        return True

    def can_proceed_to_phase(
        self,
        target_phase: int,
        max_allowed_phase: int
    ) -> bool:
        """Check if can proceed to target phase

        Args:
            target_phase: Phase to proceed to
            max_allowed_phase: Maximum allowed phase

        Returns:
            True if target_phase <= max_allowed_phase
        """
        return 1 <= target_phase <= max_allowed_phase

    def get_phase_status(
        self,
        tasks: List[Dict[str, Any]],
        max_allowed_phase: int
    ) -> Dict[int, Dict[str, Any]]:
        """Get status summary for all phases

        Args:
            tasks: List of task dictionaries
            max_allowed_phase: Maximum allowed phase number

        Returns:
            Dictionary mapping phase number to status info
        """
        feature_tasks = [
            t for t in tasks
            if t.get("task_unit_type") == "feature"
        ]

        # Group by feature
        features_by_id = self._group_by_feature(feature_tasks)

        # Track each feature's current highest phase
        feature_current_phase: Dict[str, int] = {}
        for feature_id, ftasks in features_by_id.items():
            max_phase = 0
            for task in ftasks:
                metadata = task.get("metadata", {})
                task_phase = metadata.get("phase")
                if task_phase is None:
                    skill_id = task.get("skill_id") or metadata.get("skill_id", "")
                    if skill_id:
                        import re
                        match = re.match(r"s\d+-(\d{2})", skill_id.lower())
                        if match:
                            task_phase = int(match.group(1))

                if task_phase and 1 <= task_phase <= self.max_phases:
                    max_phase = max(max_phase, task_phase)

            if max_phase > 0:
                feature_current_phase[feature_id] = max_phase

        status: Dict[int, Dict[str, Any]] = {}

        for phase in self.phases:
            # Count phase tasks
            phase_tasks = []
            for t in feature_tasks:
                metadata = t.get("metadata", {})
                task_phase = metadata.get("phase")
                if task_phase is None:
                    skill_id = t.get("skill_id") or metadata.get("skill_id", "")
                    if skill_id:
                        import re
                        match = re.match(r"s\d+-(\d{2})", skill_id.lower())
                        if match:
                            task_phase = int(match.group(1))

                if task_phase == phase or (phase == 1 and task_phase is None):
                    phase_tasks.append(t)

            # Count completed features
            completed_features = 0
            in_phase_count = 0
            advanced_count = 0

            for feature_id, ftasks in features_by_id.items():
                current_phase = feature_current_phase.get(feature_id, 0)

                if current_phase > phase:
                    # Feature has advanced past this phase
                    completed_features += 1
                    advanced_count += 1
                elif current_phase == phase:
                    in_phase_count += 1
                    if self._is_feature_phase_complete(feature_id, phase, ftasks):
                        completed_features += 1

            total_features = len(features_by_id)
            completed_tasks = sum(1 for t in phase_tasks if t.get("status") == "completed")
            total_tasks = len(phase_tasks)

            # Progress display
            if advanced_count > 0:
                progress_detail = f"{completed_features}/{total_features} ({in_phase_count} in phase, {advanced_count} advanced)"
            else:
                progress_detail = f"{completed_features}/{total_features}"

            status[phase] = {
                "allowed": phase <= max_allowed_phase,
                "completed": self._is_phase_complete(phase, feature_tasks),
                "progress": progress_detail,
                "task_progress": f"{completed_tasks}/{total_tasks}" if total_tasks > 0 else "0/0",
                "total_features": total_features,
                "completed_features": completed_features,
                "in_phase_features": in_phase_count,
                "advanced_features": advanced_count,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
            }

        return status

    def validate_phase_transition(
        self,
        from_phase: int,
        to_phase: int,
        tasks: List[Dict[str, Any]]
    ) -> tuple[bool, str]:
        """Validate a phase transition

        Args:
            from_phase: Current phase
            to_phase: Target phase
            tasks: List of task dictionaries

        Returns:
            Tuple of (is_valid, message)
        """
        if to_phase < 1 or to_phase > self.max_phases:
            return False, f"Invalid target phase: {to_phase}. Must be 1-{self.max_phases}"

        if to_phase <= from_phase:
            return True, f"Backward/same phase transition allowed: {from_phase} -> {to_phase}"

        # Check if previous phases are complete
        for phase in range(1, to_phase):
            feature_tasks = [
                t for t in tasks
                if t.get("task_unit_type") == "feature"
            ]
            if not self._is_phase_complete(phase, feature_tasks):
                return False, f"Phase {phase} is not complete. Cannot proceed to phase {to_phase}"

        return True, f"Phase transition valid: {from_phase} -> {to_phase}"
