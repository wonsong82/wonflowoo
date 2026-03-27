#!/usr/bin/env python3
"""Choisor 2.0 Daemon - Main Entry Point

Main daemon process for Choisor orchestration:
- Initializes configuration and components
- Manages session pool lifecycle
- Coordinates task scheduling
- Handles graceful shutdown

Usage:
    # From project root
    python .claude/skills/choisor/daemon/main.py [--stop] [--status]

    # Or via module (with PYTHONPATH)
    PYTHONPATH=.claude/skills python -m choisor.daemon.main
"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

# Handle direct script execution
if __name__ == "__main__" or not __package__:
    # Add choisor parent directory to path
    _this_file = Path(__file__).resolve()
    _choisor_root = _this_file.parent.parent.parent  # .claude/skills
    if str(_choisor_root) not in sys.path:
        sys.path.insert(0, str(_choisor_root))

    from choisor.config import ConfigLoader, find_project_root
    from choisor.core import SkillRegistry
    from choisor.daemon.scheduler import Scheduler
    from choisor.daemon.session_pool import SessionPool
else:
    from ..config import ConfigLoader, find_project_root
    from ..core import SkillRegistry
    from .scheduler import Scheduler
    from .session_pool import SessionPool


class ChoisorDaemon:
    """Main daemon process for Choisor orchestration.

    Coordinates the session pool, scheduler, and skill registry
    to execute migration tasks in parallel.

    Attributes:
        project_root: Root directory of the project
        config: Loaded Choisor configuration
        registry: Skill registry with discovered skills
        session_pool: Pool of managed Claude Code sessions
        scheduler: Task scheduler for assignment and completion
    """

    def __init__(self, project_root: Path):
        """Initialize the daemon with project root.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.loader = ConfigLoader(project_root)
        self.config = self.loader.load()

        # Load workflow if available
        self.workflow = self.loader.load_workflow() if self.loader.has_workflow() else None

        # Initialize skill registry (resolve relative path against project_root)
        skills_root = Path(self.config.paths.skills_root)
        if not skills_root.is_absolute():
            skills_root = self.project_root / skills_root
        self.registry = SkillRegistry(skills_root)
        self.registry.discover(workflow=self.workflow)

        # Initialize session pool
        self.session_pool = SessionPool(
            max_sessions=self.config.parallel.max_parallel_sessions,
            project_root=project_root,
        )

        # Initialize scheduler
        self.scheduler = Scheduler(
            project_root=project_root,
            config=self.config,
            registry=self.registry,
            session_pool=self.session_pool,
        )

        self._running = False
        self._shutdown_event: Optional[asyncio.Event] = None

    async def start(self) -> None:
        """Start the daemon.

        Initializes the session pool and begins the scheduler loop.
        Runs until stop() is called or a shutdown signal is received.
        """
        self._running = True
        self._shutdown_event = asyncio.Event()

        print(f"Choisor Daemon starting...")
        print(f"  Project: {self.project_root}")
        print(f"  Max sessions: {self.config.parallel.max_parallel_sessions}")
        print(f"  Skills discovered: {len(self.registry)}")
        print()

        # Write PID file
        self._write_pid_file()

        try:
            # Initialize instruction directory (clean old files)
            print("Initializing instruction directory...")
            self._initialize_instruction_dir()
            print()

            # Initialize session pool
            print("Initializing session pool...")
            await self.session_pool.initialize()

            # Create initial sessions if needed
            await self._initialize_sessions()

            # Start scheduler loop
            await self.scheduler.run()

        except asyncio.CancelledError:
            print("\nDaemon cancelled")
        finally:
            await self._cleanup()

    async def stop(self) -> None:
        """Stop the daemon gracefully.

        Signals the scheduler to stop and closes all sessions.
        """
        print("\nStopping Choisor Daemon...")
        self._running = False

        # Stop scheduler
        await self.scheduler.stop()

        # Close all sessions
        await self.session_pool.close_all()

        # Set shutdown event
        if self._shutdown_event:
            self._shutdown_event.set()

        print("Choisor Daemon stopped")

    def _initialize_instruction_dir(self) -> None:
        """Initialize instruction directory.

        Creates instruction directory if needed and removes old instruction files.
        Preserves logs subdirectory.
        """
        instruction_dir = self.project_root / ".choisor" / "instructions"
        logs_dir = instruction_dir / "logs"

        # Create directories if needed
        if not instruction_dir.exists():
            instruction_dir.mkdir(parents=True, exist_ok=True)
            logs_dir.mkdir(exist_ok=True)
            print("  Created instruction directory")
            return

        # Clean up old instruction files (preserve logs)
        deleted_count = 0
        for filepath in instruction_dir.iterdir():
            if filepath.name == "logs":
                continue
            if filepath.name.startswith("instruction-") and filepath.suffix == ".txt":
                try:
                    filepath.unlink()
                    deleted_count += 1
                except OSError as e:
                    print(f"  Warning: Failed to delete {filepath}: {e}")

        if deleted_count > 0:
            print(f"  Initialized instruction directory (removed {deleted_count} old file(s))")
        else:
            print("  Instruction directory is clean")

    async def _initialize_sessions(self) -> None:
        """Initialize session pool with required sessions.

        Creates new sessions if the pool has fewer than the target count.
        Target is min(3, max_sessions) to ensure reasonable initial capacity.
        """
        # Get existing active sessions
        active_count = len(self.session_pool.get_available_sessions()) + \
                       len(self.session_pool.get_running_sessions())

        if active_count > 0:
            print(f"  Found {active_count} existing active session(s)")

        # Calculate target session count
        target_count = min(3, self.session_pool.max_sessions)
        needed_count = max(0, target_count - active_count)

        if needed_count > 0:
            print(f"  Creating {needed_count} new session(s)...")
            created_count = 0

            for i in range(needed_count):
                session = await self.session_pool.create_session()
                if session:
                    created_count += 1
                    print(f"    Created session {created_count}/{needed_count}: {session.id[:8]}")
                else:
                    print(f"    Failed to create session {i+1}")

            if created_count == 0 and needed_count > 0:
                print(f"    Warning: No new sessions created")
        else:
            print(f"  No new sessions needed (current: {active_count}, target: {target_count}, max: {self.session_pool.max_sessions})")

        print()

    async def _cleanup(self) -> None:
        """Clean up resources on shutdown."""
        self._remove_pid_file()
        await self.session_pool.close_all()

    def _write_pid_file(self) -> None:
        """Write daemon PID file for process tracking."""
        pid_file = self.project_root / ".choisor" / "daemon.pid"
        pid_file.parent.mkdir(parents=True, exist_ok=True)

        with open(pid_file, "w") as f:
            f.write(str(asyncio.current_task().get_loop()._thread_id if hasattr(asyncio.current_task().get_loop(), '_thread_id') else 0))

        # Actually write the process ID
        import os
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))

    def _remove_pid_file(self) -> None:
        """Remove daemon PID file."""
        pid_file = self.project_root / ".choisor" / "daemon.pid"
        if pid_file.exists():
            try:
                pid_file.unlink()
            except OSError:
                pass

    @property
    def is_running(self) -> bool:
        """Check if daemon is running."""
        return self._running


def check_existing_daemon(project_root: Path) -> Optional[int]:
    """Check if a daemon is already running.

    Args:
        project_root: Project root directory

    Returns:
        PID of existing daemon if running, None otherwise
    """
    import os

    pid_file = project_root / ".choisor" / "daemon.pid"

    if not pid_file.exists():
        return None

    try:
        with open(pid_file, "r") as f:
            pid_str = f.read().strip()
            if not pid_str:
                pid_file.unlink()
                return None
            pid = int(pid_str)
    except (ValueError, IOError):
        try:
            pid_file.unlink()
        except OSError:
            pass
        return None

    # Check if process is actually running
    try:
        os.kill(pid, 0)
        return pid  # Process exists
    except OSError:
        # Process doesn't exist, remove stale PID file
        try:
            pid_file.unlink()
        except OSError:
            pass
        return None


def stop_daemon(project_root: Path) -> bool:
    """Stop running daemon.

    Args:
        project_root: Project root directory

    Returns:
        True if daemon was stopped, False if not running
    """
    import os

    pid = check_existing_daemon(project_root)
    if pid is None:
        print("Daemon is not running")
        return False

    print(f"Stopping daemon (PID: {pid})...")
    try:
        os.kill(pid, signal.SIGTERM)
        print("Daemon stopped")
        return True
    except OSError as e:
        print(f"Error stopping daemon: {e}")
        return False


def daemon_status(project_root: Path) -> int:
    """Show daemon status.

    Args:
        project_root: Project root directory

    Returns:
        Exit code (0 if running, 1 if not)
    """
    pid = check_existing_daemon(project_root)
    if pid:
        print(f"Daemon is running (PID: {pid})")
        return 0
    else:
        print("Daemon is not running")
        return 1


def main() -> int:
    """Entry point for daemon.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Choisor Daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python daemon/main.py              # Start daemon
    python daemon/main.py --status     # Check status
    python daemon/main.py --stop       # Stop daemon
"""
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Stop running daemon"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Check daemon status"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Scheduling interval in seconds (default: 30)"
    )
    args = parser.parse_args()

    # Find project root
    project_root = find_project_root()
    if not project_root:
        print("Error: Not in a Choisor project (no .choisor/ or .claude/ found)")
        return 1

    # Handle status command
    if args.status:
        return daemon_status(project_root)

    # Handle stop command
    if args.stop:
        return 0 if stop_daemon(project_root) else 1

    # Check if already running
    existing_pid = check_existing_daemon(project_root)
    if existing_pid:
        print(f"Error: Daemon already running (PID: {existing_pid})")
        print("Use '--stop' to stop it first")
        return 1

    # Create and run daemon
    daemon = ChoisorDaemon(project_root)

    # Set up event loop with signal handlers
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def signal_handler() -> None:
        """Handle shutdown signals."""
        loop.create_task(daemon.stop())

    # Register signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            signal.signal(sig, lambda s, f: signal_handler())

    try:
        loop.run_until_complete(daemon.start())
        return 0
    except KeyboardInterrupt:
        loop.run_until_complete(daemon.stop())
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        loop.close()


if __name__ == "__main__":
    sys.exit(main())
