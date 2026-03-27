"""Choisor 2.0 Daemon - Task Scheduler

Task scheduler for the daemon:
- Polls for available sessions
- Assigns tasks to sessions
- Processes task completions
- Coordinates parallel execution
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..config import ChoisorConfig, ConfigLoader
from ..core import SkillRegistry, PhaseGate, PriorityEngine
from ..commands import handle_assign_next, handle_process_completion
from .session_pool import SessionPool, SessionState, Session
from .parallel_coordinator import ParallelCoordinator


class Scheduler:
    """Task scheduler for the daemon.

    Manages the scheduling loop that assigns tasks to available
    sessions and processes completions.

    Attributes:
        project_root: Project root directory
        config: Choisor configuration
        registry: Skill registry
        session_pool: Session pool manager
        parallel_coordinator: Parallel task coordinator
    """

    DEFAULT_POLL_INTERVAL = 5.0  # seconds
    CONFIG_RELOAD_INTERVAL = 5.0  # seconds (reload every tick for dynamic config updates)

    def __init__(
        self,
        project_root: Path,
        config: ChoisorConfig,
        registry: SkillRegistry,
        session_pool: SessionPool,
    ):
        """Initialize the scheduler.

        Args:
            project_root: Project root directory
            config: Choisor configuration
            registry: Skill registry
            session_pool: Session pool manager
        """
        self.project_root = project_root
        self.config = config
        self.registry = registry
        self.session_pool = session_pool

        # Initialize parallel coordinator with config pairs
        self.parallel_coordinator = ParallelCoordinator(
            parallel_pairs=config.parallel.pairs,
            registry=registry,
        )

        self._running = False
        self._last_config_reload = datetime.now()
        self._last_assignment_time: Optional[datetime] = None  # Track last task assignment
        self._delay_logged = False  # Track if delay message was logged

    async def run(self) -> None:
        """Main scheduler loop.

        Runs the scheduling tick at regular intervals until stopped.
        """
        self._running = True
        print(f"Scheduler started (poll interval: {self.DEFAULT_POLL_INTERVAL}s)")

        while self._running:
            try:
                await self._schedule_tick()
            except Exception as e:
                print(f"[{self._timestamp()}] Scheduler error: {e}")
                import traceback
                traceback.print_exc()

            await asyncio.sleep(self.DEFAULT_POLL_INTERVAL)

        print("Scheduler stopped")

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False

    async def _schedule_tick(self) -> None:
        """Single scheduling iteration.

        Performs the following in order:
        1. Reload config if needed
        2. Check for stale sessions and recover them
        3. Check and process completed sessions
        4. Trim excess sessions (AFTER completions, so newly-idle sessions are trimmed)
        5. Assign tasks to available sessions
        """
        # Reload config periodically
        await self._maybe_reload_config()

        # Check for stale sessions FIRST (before any other processing)
        await self._check_stale_sessions()

        # Check running sessions for completion (poll process status)
        await self._check_running_sessions()

        # Check if assignment is disabled
        if not self.config.assignment.enabled:
            # Still process completions even when disabled
            await self._process_completed_sessions()
            # Still trim excess sessions
            await self._trim_excess_sessions()
            return

        # Process completed sessions
        await self._process_completed_sessions()

        # Trim excess sessions AFTER completions are processed
        # This ensures newly-idle sessions are trimmed before assignment
        await self._trim_excess_sessions()

        # Check assignment delay
        if not self._can_assign_now():
            return

        # Get available sessions
        available_sessions = self.session_pool.get_available_sessions()

        # Create new session if needed and allowed
        if not available_sessions:
            available_sessions = await self._maybe_create_session()

        if not available_sessions:
            return

        # Try to assign tasks to available sessions (one at a time)
        for session_id in available_sessions[:1]:  # Process one at a time
            assigned = await self._assign_task(session_id)
            if assigned:
                # Update last assignment time on successful assignment
                self._last_assignment_time = datetime.now()
            if not assigned:
                break  # No more tasks to assign

    async def _maybe_create_session(self) -> List[str]:
        """Create a new session if under max_sessions limit.

        Returns:
            List containing new session ID, or empty list if cannot create
        """
        stats = self.session_pool.get_stats()
        total_active = stats.get("idle", 0) + stats.get("assigned", 0) + stats.get("running", 0)
        max_sessions = self.session_pool.max_sessions

        if total_active >= max_sessions:
            return []

        # Create new session
        model = self.config.default_model
        new_session = await self.session_pool.create_session(model=model)
        print(f"[{self._timestamp()}] Created new session {new_session.id[:8]} ({total_active + 1}/{max_sessions})")

        return [new_session.id]

    async def _assign_task(self, session_id: str) -> bool:
        """Assign next task to session.

        Args:
            session_id: Session ID to assign task to

        Returns:
            True if task was assigned, False otherwise
        """
        try:
            # Call assign_next command
            task_dict, instruction, message = handle_assign_next(
                self.project_root,
                request_id=session_id
            )

            if not task_dict:
                # No task available
                if message:
                    print(f"[{self._timestamp()}] {message}")
                return False

            task_id = task_dict.get("id", "unknown")
            model = self.config.default_model

            print(f"[{self._timestamp()}] Assigning task {task_id} to session {session_id[:8]}")

            # Check for parallel task opportunity
            await self._handle_parallel_opportunity(task_dict)

            # Send instruction to session
            success = await self.session_pool.assign_task(
                session_id=session_id,
                task_id=task_id,
                instruction=instruction,
                model=model,
            )

            if success:
                print(f"[{self._timestamp()}] Task {task_id} assigned to session {session_id[:8]}")
                return True
            else:
                print(f"[{self._timestamp()}] Failed to assign task to session {session_id[:8]}")
                return False

        except Exception as e:
            print(f"[{self._timestamp()}] Error assigning task: {e}")
            return False

    async def _handle_parallel_opportunity(self, task_dict: Dict[str, Any]) -> None:
        """Check and handle parallel task opportunity.

        If the current task can run in parallel with another task,
        and there's an available session, try to assign the parallel task.

        Args:
            task_dict: Task dictionary for the primary task
        """
        if not self.config.parallel.enabled:
            return

        # Check if this task can run in parallel
        skill_id = task_dict.get("skill_id", "")
        if not self.parallel_coordinator.can_run_parallel_by_skill_id(skill_id):
            return

        # Get available sessions for parallel task
        available = self.session_pool.get_available_sessions()
        if len(available) < 1:  # Need at least one more available
            return

        # Get the parallel skill ID
        parallel_skill_id = self.parallel_coordinator.get_parallel_skill_id(skill_id)
        if not parallel_skill_id:
            return

        print(f"[{self._timestamp()}] Parallel opportunity detected: {skill_id} <-> {parallel_skill_id}")
        # Note: Parallel task assignment would be handled in the next tick
        # if the corresponding task exists and is ready

    async def _check_running_sessions(self) -> None:
        """Check running sessions and detect completed processes.

        Polls each RUNNING session to check if the underlying process
        has completed, and updates the session state accordingly.
        Also handles orphaned sessions (process not tracked but session still RUNNING).
        """
        running_sessions = self.session_pool.get_running_sessions()

        for session_id in running_sessions:
            session = self.session_pool.get_session(session_id)
            if not session:
                continue

            # Check actual process status
            status = await self.session_pool.check_session_status(session_id)

            if status == SessionState.COMPLETED:
                print(f"[{self._timestamp()}] Session {session_id[:8]} process completed")
            elif status == SessionState.FAILED:
                print(f"[{self._timestamp()}] Session {session_id[:8]} process failed")
            elif status == SessionState.IDLE:
                # Process not found - session was orphaned (daemon restarted or process lost)
                # Check if there was a task and handle completion
                task_id = session.current_task_id
                if task_id:
                    print(f"[{self._timestamp()}] Session {session_id[:8]} orphaned, processing task {task_id}")
                    # Mark as completed so it goes through completion processing
                    await self.session_pool.mark_completed(session_id)
            # RUNNING or ASSIGNED means still running, do nothing

    async def _process_completed_sessions(self) -> None:
        """Process all completed sessions."""
        completed_sessions = self.session_pool.get_completed_sessions()

        for session_id in completed_sessions:
            await self._process_completion(session_id)

    async def _process_completion(self, session_id: str) -> None:
        """Process session completion.

        Args:
            session_id: Completed session ID
        """
        # Get task from session
        task_id = self.session_pool.get_session_task(session_id)
        if not task_id:
            # No task to process, just release session
            await self.session_pool.release_session(session_id)
            return

        print(f"[{self._timestamp()}] Processing completion for task {task_id}")

        try:
            # Process completion
            result = handle_process_completion(
                self.project_root,
                task_id,
                request_id=session_id,
            )

            if result.get("success"):
                print(f"[{self._timestamp()}] Task {task_id} completed successfully")

                # Check for parallel task completion
                self._handle_parallel_completion(task_id)
            else:
                error = result.get("error", "Unknown error")
                print(f"[{self._timestamp()}] Task {task_id} completion failed: {error}")

        except Exception as e:
            print(f"[{self._timestamp()}] Error processing completion: {e}")

        # Archive instruction file before releasing session
        self._cleanup_instruction_file(session_id, task_id)

        # Release session for reuse
        await self.session_pool.release_session(session_id)

    def _handle_parallel_completion(self, task_id: str) -> None:
        """Handle completion of parallel task pair.

        Args:
            task_id: Completed task ID
        """
        # Extract skill_id from task_id
        parts = task_id.split("-")
        if len(parts) >= 2:
            skill_id = f"{parts[0]}-{parts[1]}"
            if self.parallel_coordinator.can_run_parallel_by_skill_id(skill_id):
                self.parallel_coordinator.on_task_complete(skill_id)

    async def _maybe_reload_config(self) -> None:
        """Reload configuration if enough time has passed."""
        now = datetime.now()
        elapsed = (now - self._last_config_reload).total_seconds()

        if elapsed >= self.CONFIG_RELOAD_INTERVAL:
            try:
                loader = ConfigLoader(self.project_root)
                new_config = loader.load()

                # Check for significant changes and log them
                if new_config.assignment.enabled != self.config.assignment.enabled:
                    status = "enabled" if new_config.assignment.enabled else "disabled"
                    print(f"[{self._timestamp()}] ⚙️  Assignment {status}")

                if new_config.assignment.delay != self.config.assignment.delay:
                    delay_str = f"{new_config.assignment.delay} min" if new_config.assignment.delay else "none"
                    print(f"[{self._timestamp()}] ⚙️  Assignment delay: {delay_str}")

                old_max = self.config.parallel.max_parallel_sessions
                new_max = new_config.parallel.max_parallel_sessions
                if new_max != old_max:
                    print(f"[{self._timestamp()}] ⚙️  Max sessions: {old_max} → {new_max}")
                    # Update session pool max sessions
                    # (Excess idle sessions will be trimmed in _schedule_tick after completions)
                    self.session_pool.set_max_sessions(new_max)

                # Check work_scope changes
                old_domains = self.config.work_scope.enabled_domains
                new_domains = new_config.work_scope.enabled_domains
                if old_domains != new_domains:
                    domains_str = ', '.join(new_domains) if new_domains else 'all'
                    print(f"[{self._timestamp()}] ⚙️  Work scope: {domains_str}")

                self.config = new_config
                self._last_config_reload = now

            except Exception as e:
                print(f"[{self._timestamp()}] Config reload failed: {e}")

    def _can_assign_now(self) -> bool:
        """Check if assignment is allowed based on delay configuration.

        Returns:
            True if assignment is allowed, False if still within delay period
        """
        delay_minutes = self.config.assignment.delay
        if not delay_minutes:
            # No delay configured, always allow
            if self._delay_logged:
                self._delay_logged = False
            return True

        if self._last_assignment_time is None:
            # No previous assignment, allow first one
            return True

        # Check if enough time has passed since last assignment
        now = datetime.now()
        elapsed_minutes = (now - self._last_assignment_time).total_seconds() / 60

        if elapsed_minutes < delay_minutes:
            # Still within delay period - log only once when delay starts
            if not self._delay_logged:
                remaining = delay_minutes - elapsed_minutes
                print(f"[{self._timestamp()}] ⏳ Assignment delayed ({remaining:.1f} min remaining)")
                self._delay_logged = True
            return False

        # Delay period ended
        if self._delay_logged:
            print(f"[{self._timestamp()}] ✓ Assignment delay ended")
            self._delay_logged = False

        return True

    def _timestamp(self) -> str:
        """Get formatted timestamp for logging."""
        return datetime.now().strftime("%H:%M:%S")

    async def _trim_excess_sessions(self) -> None:
        """Terminate idle sessions that exceed max_sessions limit.

        Called every tick AFTER completion processing to ensure newly-idle
        sessions are trimmed before assignment. This prevents the race condition
        where sessions complete, become idle, and get reassigned before trim.
        Running/assigned sessions are preserved until they complete.
        """
        excess_sessions = self.session_pool.get_excess_idle_sessions()

        for session_id in excess_sessions:
            print(f"[{self._timestamp()}] 🔻 Terminating excess idle session {session_id[:8]}")
            await self.session_pool.terminate_idle_session(session_id)

        if excess_sessions:
            stats = self.session_pool.get_stats()
            total_active = stats.get("idle", 0) + stats.get("assigned", 0) + stats.get("running", 0)
            print(f"[{self._timestamp()}] ✓ Session pool trimmed to {total_active}/{self.session_pool.max_sessions}")

    async def _check_stale_sessions(self) -> None:
        """Detect and recover stale sessions.

        Checks for sessions in ASSIGNED/RUNNING state without recent activity.
        If a session exceeds the stale_timeout, it will be recovered.
        """
        stale_timeout = self.config.assignment.stale_timeout
        if stale_timeout <= 0:
            return

        for session in self.session_pool.get_all_sessions():
            if session.state not in (SessionState.ASSIGNED, SessionState.RUNNING):
                continue

            if self._is_session_stale(session, stale_timeout):
                await self._recover_stale_session(session)

    def _is_session_stale(self, session: Session, timeout_minutes: int) -> bool:
        """Check if session is stale based on activity timeout.

        Args:
            session: Session to check
            timeout_minutes: Timeout threshold in minutes

        Returns:
            True if session is stale (inactive beyond timeout)
        """
        # Use last_activity_at if available, otherwise fall back to started_at
        activity_time = session.last_activity_at or session.started_at

        if not activity_time:
            # No activity timestamp, consider stale
            return True

        now = datetime.now()
        elapsed_minutes = (now - activity_time).total_seconds() / 60

        return elapsed_minutes > timeout_minutes

    async def _recover_stale_session(self, session: Session) -> None:
        """Recover a stale session and its task.

        Args:
            session: Stale session to recover
        """
        session_id = session.id
        task_id = session.current_task_id

        print(f"[{self._timestamp()}] ⚠️  Stale session detected: {session_id[:8]}")

        if task_id:
            print(f"[{self._timestamp()}] ⚠️  Resetting task {task_id} to pending")
            # Reset task status to pending
            self._reset_task_to_pending(task_id)

            # Archive instruction file
            self._cleanup_instruction_file(session_id, task_id)

        # Release session to idle
        await self.session_pool.recover_stale_session(session_id)
        print(f"[{self._timestamp()}] ✓ Session {session_id[:8]} recovered to idle")

    def _reset_task_to_pending(self, task_id: str) -> None:
        """Reset a task's status to pending.

        Args:
            task_id: Task ID to reset
        """
        tasks_path = self.project_root / ".choisor" / "tasks" / "tasks.json"

        if not tasks_path.exists():
            return

        try:
            with open(tasks_path, "r", encoding="utf-8") as f:
                tasks = json.load(f)

            # Find and update the task
            for task in tasks:
                if task.get("id") == task_id:
                    task["status"] = "pending"
                    task["assigned_session"] = None
                    task["updated_at"] = datetime.now().isoformat()
                    break

            # Save updated tasks
            with open(tasks_path, "w", encoding="utf-8") as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)

        except (json.JSONDecodeError, IOError) as e:
            print(f"[{self._timestamp()}] Error resetting task: {e}")

    def _cleanup_instruction_file(self, session_id: str, task_id: Optional[str] = None) -> None:
        """Archive instruction file for a session to logs directory.

        Args:
            session_id: Session ID
            task_id: Optional task ID for archive naming
        """
        instructions_dir = self.project_root / ".choisor" / "instructions"
        instruction_file = instructions_dir / f"instruction-{session_id}.txt"

        if not instruction_file.exists():
            return

        try:
            # Create logs/instructions directory
            logs_dir = self.project_root / ".choisor" / "logs" / "instructions"
            logs_dir.mkdir(parents=True, exist_ok=True)

            # Generate archive filename with timestamp and task_id
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            if task_id:
                archive_name = f"{timestamp}-{task_id}.txt"
            else:
                archive_name = f"{timestamp}-{session_id[:8]}.txt"

            archive_path = logs_dir / archive_name

            # Move to archive
            instruction_file.rename(archive_path)
            print(f"[{self._timestamp()}] Archived instruction file: {archive_name}")

        except OSError as e:
            print(f"[{self._timestamp()}] Error archiving instruction file: {e}")
