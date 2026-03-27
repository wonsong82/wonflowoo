"""Choisor 2.0 Daemon - Session Pool

Manages a pool of Claude Code sessions:
- Session lifecycle management (create, assign, release, terminate)
- State tracking (idle, assigned, running, completed, failed)
- Model affinity for session reuse
- Persistence to JSON for recovery
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

from .claude_code_client import ClaudeCodeClient


class SessionState(Enum):
    """Session execution state."""
    IDLE = "idle"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


@dataclass
class Session:
    """Represents a Claude Code session.

    Attributes:
        id: Unique session identifier
        state: Current session state
        current_task_id: ID of currently assigned task
        last_model: Last used model ID
        started_at: Timestamp when session was started
        completed_at: Timestamp when session completed
        last_activity_at: Timestamp of last activity (for stale detection)
        task_history: List of completed task IDs
        error_count: Number of errors encountered
        process_id: OS process ID if running
    """
    id: str
    state: SessionState = SessionState.IDLE
    current_task_id: Optional[str] = None
    last_model: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    task_history: List[str] = field(default_factory=list)
    error_count: int = 0
    process_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "state": self.state.value,
            "current_task_id": self.current_task_id,
            "last_model": self.last_model,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "task_history": self.task_history,
            "error_count": self.error_count,
            "process_id": self.process_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create Session from dictionary."""
        started_at = None
        if data.get("started_at"):
            try:
                started_at = datetime.fromisoformat(data["started_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        completed_at = None
        if data.get("completed_at"):
            try:
                completed_at = datetime.fromisoformat(data["completed_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        last_activity_at = None
        if data.get("last_activity_at"):
            try:
                last_activity_at = datetime.fromisoformat(data["last_activity_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return cls(
            id=data["id"],
            state=SessionState(data.get("state", "idle")),
            current_task_id=data.get("current_task_id"),
            last_model=data.get("last_model"),
            started_at=started_at,
            completed_at=completed_at,
            last_activity_at=last_activity_at,
            task_history=data.get("task_history", []),
            error_count=data.get("error_count", 0),
            process_id=data.get("process_id"),
        )


class SessionPool:
    """Manages pool of Claude Code sessions.

    Handles session lifecycle, state transitions, and persistence.

    Attributes:
        max_sessions: Maximum number of concurrent sessions
        project_root: Project root directory
    """

    def __init__(
        self,
        max_sessions: int = 10,
        project_root: Optional[Path] = None,
    ):
        """Initialize session pool.

        Args:
            max_sessions: Maximum number of concurrent sessions
            project_root: Project root directory for persistence
        """
        self.max_sessions = max_sessions
        self.project_root = project_root

        self._sessions: Dict[str, Session] = {}
        self._lock = asyncio.Lock()
        self._client: Optional[ClaudeCodeClient] = None

        # Persistence path
        if project_root:
            self._sessions_file = project_root / ".choisor" / "sessions" / "sessions.json"
        else:
            self._sessions_file = None

    def set_max_sessions(self, new_max: int) -> None:
        """Update maximum sessions limit.

        Args:
            new_max: New maximum sessions value
        """
        self.max_sessions = new_max

    def get_excess_idle_sessions(self) -> List[str]:
        """Get idle sessions that exceed max_sessions limit.

        Returns idle sessions that should be terminated when
        total active sessions exceed max_sessions.

        Returns:
            List of excess idle session IDs to terminate
        """
        stats = self.get_stats()
        total_active = stats.get("idle", 0) + stats.get("assigned", 0) + stats.get("running", 0)

        if total_active <= self.max_sessions:
            return []

        # Calculate how many idle sessions to remove
        excess_count = total_active - self.max_sessions
        idle_sessions = self.get_available_sessions()

        # Return up to excess_count idle sessions for removal
        return idle_sessions[:excess_count]

    async def terminate_idle_session(self, session_id: str) -> bool:
        """Terminate and remove an idle session.

        Only terminates sessions in IDLE state to protect running tasks.

        Args:
            session_id: Session ID to terminate

        Returns:
            True if session was terminated successfully,
            False if session not found or not in IDLE state
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            # Safety check: only terminate IDLE sessions
            if session.state != SessionState.IDLE:
                print(f"Warning: Refusing to terminate non-idle session {session_id[:8]} (state: {session.state.value})")
                return False

            # Remove session from pool (IDLE sessions have no running process)
            del self._sessions[session_id]
            self._save_sessions()
            return True

    async def initialize(self) -> None:
        """Initialize the session pool.

        Loads existing sessions from disk and initializes the Claude client.
        """
        # Initialize Claude client
        if self.project_root:
            self._client = ClaudeCodeClient(self.project_root)

        # Load existing sessions
        self._load_sessions()

        # Ensure sessions directory exists
        if self._sessions_file:
            self._sessions_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"Session pool initialized with {len(self._sessions)} existing session(s)")

    def _load_sessions(self) -> None:
        """Load sessions from JSON file."""
        if not self._sessions_file or not self._sessions_file.exists():
            return

        try:
            with open(self._sessions_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for session_data in data:
                session = Session.from_dict(session_data)
                # Only load active sessions
                if session.state in (SessionState.IDLE, SessionState.ASSIGNED, SessionState.RUNNING):
                    self._sessions[session.id] = session

        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load sessions: {e}")

    def _save_sessions(self) -> None:
        """Save sessions to JSON file."""
        if not self._sessions_file:
            return

        try:
            self._sessions_file.parent.mkdir(parents=True, exist_ok=True)

            sessions_data = [
                session.to_dict()
                for session in self._sessions.values()
            ]

            with open(self._sessions_file, "w", encoding="utf-8") as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)

        except IOError as e:
            print(f"Warning: Failed to save sessions: {e}")

    def get_available_sessions(self) -> List[str]:
        """Get list of available (idle) session IDs.

        Returns:
            List of session IDs that are available for task assignment
        """
        return [
            sid for sid, session in self._sessions.items()
            if session.state == SessionState.IDLE
        ]

    def get_completed_sessions(self) -> List[str]:
        """Get list of completed session IDs.

        Returns:
            List of session IDs that have completed their tasks
        """
        return [
            sid for sid, session in self._sessions.items()
            if session.state == SessionState.COMPLETED
        ]

    def get_running_sessions(self) -> List[str]:
        """Get list of running session IDs.

        Returns:
            List of session IDs that are currently running
        """
        return [
            sid for sid, session in self._sessions.items()
            if session.state in (SessionState.ASSIGNED, SessionState.RUNNING)
        ]

    async def create_session(self, model: Optional[str] = None) -> Session:
        """Create a new session.

        Args:
            model: Initial model preference

        Returns:
            New Session object
        """
        async with self._lock:
            session_id = str(uuid.uuid4())
            session = Session(
                id=session_id,
                state=SessionState.IDLE,
                last_model=model,
            )
            self._sessions[session_id] = session
            self._save_sessions()
            return session

    async def assign_task(
        self,
        session_id: str,
        task_id: str,
        instruction: str,
        model: str,
    ) -> bool:
        """Assign a task to a session.

        Args:
            session_id: Session ID
            task_id: Task ID to assign
            instruction: Instruction text for the task
            model: Model to use for the task

        Returns:
            True if task was assigned successfully
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                # Create session if it doesn't exist
                session = Session(id=session_id, state=SessionState.IDLE)
                self._sessions[session_id] = session

            if session.state != SessionState.IDLE:
                return False

            session.state = SessionState.ASSIGNED
            session.current_task_id = task_id
            session.last_model = model
            session.started_at = datetime.now()
            session.last_activity_at = datetime.now()

            self._save_sessions()

        # Launch Claude process
        if self._client:
            pid = await self._client.launch_session(
                session_id=session_id,
                task_id=task_id,
                instruction=instruction,
                model=model,
            )

            if pid is not None:
                async with self._lock:
                    session.state = SessionState.RUNNING
                    session.process_id = pid  # Save PID for tracking
                    self._save_sessions()
                return True
            else:
                async with self._lock:
                    session.state = SessionState.FAILED
                    session.error_count += 1
                    self._save_sessions()
                return False

        return True

    async def release_session(self, session_id: str) -> bool:
        """Release a session back to idle state.

        Args:
            session_id: Session ID to release

        Returns:
            True if session was released successfully
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            # Add completed task to history
            if session.current_task_id:
                session.task_history.append(session.current_task_id)

            session.state = SessionState.IDLE
            session.current_task_id = None
            session.completed_at = datetime.now()
            session.process_id = None

            self._save_sessions()
            return True

    async def mark_completed(self, session_id: str) -> bool:
        """Mark a session as completed.

        Args:
            session_id: Session ID

        Returns:
            True if state was updated
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.state = SessionState.COMPLETED
            session.completed_at = datetime.now()
            self._save_sessions()
            return True

    async def mark_failed(self, session_id: str) -> bool:
        """Mark a session as failed.

        Args:
            session_id: Session ID

        Returns:
            True if state was updated
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.state = SessionState.FAILED
            session.error_count += 1
            session.completed_at = datetime.now()
            self._save_sessions()
            return True

    def get_session_task(self, session_id: str) -> Optional[str]:
        """Get current task for a session.

        Args:
            session_id: Session ID

        Returns:
            Task ID or None if no task assigned
        """
        session = self._sessions.get(session_id)
        return session.current_task_id if session else None

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session object or None
        """
        return self._sessions.get(session_id)

    def get_all_sessions(self) -> List[Session]:
        """Get all sessions.

        Returns:
            List of all Session objects
        """
        return list(self._sessions.values())

    async def recover_stale_session(self, session_id: str) -> bool:
        """Recover a stale session by resetting it to idle.

        Args:
            session_id: Session ID to recover

        Returns:
            True if session was recovered successfully
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            # Clear session state
            session.state = SessionState.IDLE
            session.current_task_id = None
            session.last_activity_at = None
            session.process_id = None

            self._save_sessions()
            return True

    def get_idle_sessions_by_model(self, model: str) -> List[str]:
        """Get idle sessions that last used a specific model.

        Useful for model affinity optimization.

        Args:
            model: Model ID to match

        Returns:
            List of matching session IDs
        """
        return [
            sid for sid, session in self._sessions.items()
            if session.state == SessionState.IDLE and session.last_model == model
        ]

    async def close_all(self) -> None:
        """Close all sessions and clean up."""
        async with self._lock:
            for session_id, session in self._sessions.items():
                if session.state in (SessionState.RUNNING, SessionState.ASSIGNED):
                    # Terminate running processes
                    if self._client and session.process_id:
                        await self._client.terminate_session(session_id)

                session.state = SessionState.TERMINATED

            self._save_sessions()
            self._sessions.clear()

    async def check_session_status(self, session_id: str) -> SessionState:
        """Check actual status of a session.

        Polls the underlying process to determine real state.

        Args:
            session_id: Session ID

        Returns:
            Current session state
        """
        session = self._sessions.get(session_id)
        if not session:
            return SessionState.TERMINATED

        if session.state not in (SessionState.RUNNING, SessionState.ASSIGNED):
            return session.state

        # Check actual process status
        if self._client:
            status = await self._client.check_session(session_id)

            if status == "completed":
                async with self._lock:
                    session.state = SessionState.COMPLETED
                    self._save_sessions()
            elif status == "failed":
                async with self._lock:
                    session.state = SessionState.FAILED
                    self._save_sessions()
            elif status == "not_found":
                async with self._lock:
                    session.state = SessionState.IDLE
                    self._save_sessions()

        return session.state

    def get_stats(self) -> Dict[str, int]:
        """Get session pool statistics.

        Returns:
            Dictionary with counts by state
        """
        stats = {
            "idle": 0,
            "assigned": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "terminated": 0,
            "total": len(self._sessions),
        }

        for session in self._sessions.values():
            state_name = session.state.value
            if state_name in stats:
                stats[state_name] += 1

        return stats

    def to_dict(self) -> Dict[str, Any]:
        """Serialize pool state to dictionary.

        Returns:
            Dictionary representation of pool state
        """
        return {
            "max_sessions": self.max_sessions,
            "sessions": {
                sid: session.to_dict()
                for sid, session in self._sessions.items()
            },
            "stats": self.get_stats(),
        }
