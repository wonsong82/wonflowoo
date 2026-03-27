"""Choisor 2.0 Daemon - Claude Code Client

Client for launching and communicating with Claude Code processes:
- Process lifecycle management
- Instruction file handling
- Output logging
- Status monitoring
"""

import asyncio
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

import yaml


class ClaudeCodeClient:
    """Client for launching and communicating with Claude Code processes.

    Manages the lifecycle of Claude Code subprocess executions,
    including instruction delivery, logging, and status monitoring.

    Attributes:
        project_root: Project root directory
        default_model: Default model ID from configuration
    """

    def __init__(self, project_root: Path):
        """Initialize the client.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.default_model: Optional[str] = None

        # Process tracking: session_id -> subprocess
        self._processes: Dict[str, asyncio.subprocess.Process] = {}

        # Log file handles
        self._log_handles: Dict[str, Any] = {}

        # Load default model from config
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration to get default model."""
        config_path = self.project_root / ".choisor" / "config.yaml"

        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    self.default_model = config.get("default_model")
            except (yaml.YAMLError, IOError):
                pass

    async def launch_session(
        self,
        session_id: str,
        task_id: str,
        instruction: str,
        model: Optional[str] = None,
    ) -> Optional[int]:
        """Launch a new Claude Code session.

        Creates instruction file and starts Claude Code process
        with the instruction piped to stdin.

        Args:
            session_id: Session identifier
            task_id: Task identifier
            instruction: Instruction text
            model: Model to use (falls back to default)

        Returns:
            Process PID if launched successfully, None otherwise
        """
        # Create instruction file
        instruction_path = self._create_instruction_file(
            session_id, task_id, instruction
        )

        # Determine model
        selected_model = model or self.default_model

        # Build command
        # Use --dangerously-skip-permissions for background/unattended execution
        # This delegates all permissions to avoid interactive prompts
        shell = os.getenv("SHELL", "/bin/zsh")
        skip_permissions_flag = "--dangerously-skip-permissions"

        if selected_model:
            cmd_str = f"source ~/.zshrc 2>/dev/null; cat {instruction_path} | claude {skip_permissions_flag} --model {selected_model}"
        else:
            cmd_str = f"source ~/.zshrc 2>/dev/null; cat {instruction_path} | claude {skip_permissions_flag}"

        # Set up logging
        log_dir = self.project_root / ".choisor" / "logs" / "sessions"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"session-{session_id}.log"

        try:
            # Open log file
            log_handle = open(log_path, "a")
            self._log_handles[session_id] = log_handle

            # Write session header
            log_handle.write(f"\n{'='*80}\n")
            log_handle.write(f"[{datetime.now().isoformat()}] Starting Task: {task_id}\n")
            log_handle.write(f"Model: {selected_model or 'default'}\n")
            log_handle.write(f"{'='*80}\n\n")
            log_handle.flush()

            # Launch process
            process = await asyncio.create_subprocess_shell(
                cmd_str,
                stdout=log_handle,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(self.project_root),
            )

            self._processes[session_id] = process
            return process.pid  # Return PID for tracking

        except Exception as e:
            print(f"Failed to launch session {session_id}: {e}")
            if session_id in self._log_handles:
                try:
                    self._log_handles[session_id].close()
                except Exception:
                    pass
                del self._log_handles[session_id]
            return None

    def _create_instruction_file(
        self,
        session_id: str,
        task_id: str,
        instruction: str,
    ) -> Path:
        """Create instruction file for the session.

        Args:
            session_id: Session identifier
            task_id: Task identifier
            instruction: Instruction text

        Returns:
            Path to the created instruction file
        """
        instructions_dir = self.project_root / ".choisor" / "instructions"
        instructions_dir.mkdir(parents=True, exist_ok=True)

        instruction_path = instructions_dir / f"instruction-{session_id}.txt"

        # Build header
        header = f"""# Session ID: {session_id}
# Task ID: {task_id}
# Created: {datetime.now().isoformat()}
{'='*80}

"""

        with open(instruction_path, "w", encoding="utf-8") as f:
            f.write(header + instruction)

        return instruction_path

    async def check_session(self, session_id: str) -> str:
        """Check session status.

        Args:
            session_id: Session identifier

        Returns:
            Status string: "running", "completed", "failed", "not_found"
        """
        process = self._processes.get(session_id)

        if not process:
            return "not_found"

        # Check if process has exited
        if process.returncode is None:
            # Process still running - check with poll
            try:
                # Non-blocking wait with timeout of 0
                await asyncio.wait_for(
                    asyncio.shield(process.wait()),
                    timeout=0.01
                )
            except asyncio.TimeoutError:
                return "running"

        # Process has exited
        if process.returncode == 0:
            return "completed"
        else:
            return "failed"

    async def terminate_session(self, session_id: str) -> bool:
        """Terminate a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was terminated
        """
        process = self._processes.get(session_id)

        if process and process.returncode is None:
            try:
                process.terminate()
                # Wait for termination with timeout
                try:
                    await asyncio.wait_for(process.wait(), timeout=10.0)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
            except Exception as e:
                print(f"Error terminating session {session_id}: {e}")

        # Clean up log handle
        if session_id in self._log_handles:
            try:
                self._log_handles[session_id].close()
            except Exception:
                pass
            del self._log_handles[session_id]

        # Remove from tracking
        if session_id in self._processes:
            del self._processes[session_id]

        return True

    async def get_session_output(self, session_id: str) -> Optional[str]:
        """Get session log output.

        Args:
            session_id: Session identifier

        Returns:
            Log content or None if not found
        """
        log_path = self.project_root / ".choisor" / "logs" / "sessions" / f"session-{session_id}.log"

        if not log_path.exists():
            return None

        try:
            with open(log_path, "r", encoding="utf-8") as f:
                return f.read()
        except IOError:
            return None

    def log_task_completion(
        self,
        session_id: str,
        task_id: str,
        status: str,
    ) -> None:
        """Log task completion to session log.

        Args:
            session_id: Session identifier
            task_id: Task identifier
            status: Completion status ("completed" or "failed")
        """
        log_path = self.project_root / ".choisor" / "logs" / "sessions" / f"session-{session_id}.log"

        try:
            with open(log_path, "a") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"[{datetime.now().isoformat()}] Task {status.upper()}: {task_id}\n")
                f.write(f"{'='*80}\n\n")
        except IOError:
            pass

    def cleanup_instruction_file(self, session_id: str, task_id: Optional[str] = None) -> bool:
        """Archive instruction file to logs after task completion.

        Moves instruction file to logs/instructions/ directory for record keeping,
        renaming it with timestamp and task_id for easy identification.

        Args:
            session_id: Session identifier
            task_id: Optional task identifier for naming

        Returns:
            True if file was archived successfully
        """
        instruction_path = (
            self.project_root / ".choisor" / "instructions" / f"instruction-{session_id}.txt"
        )

        if not instruction_path.exists():
            return False

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
            instruction_path.rename(archive_path)
            return True

        except OSError as e:
            print(f"Warning: Failed to archive instruction file: {e}")
            # Fallback: try to delete if archive fails
            try:
                instruction_path.unlink()
            except OSError:
                pass
            return False

    async def wait_for_session(
        self,
        session_id: str,
        timeout: Optional[float] = None,
    ) -> Tuple[str, Optional[int]]:
        """Wait for session to complete.

        Args:
            session_id: Session identifier
            timeout: Optional timeout in seconds

        Returns:
            Tuple of (status, return_code)
        """
        process = self._processes.get(session_id)

        if not process:
            return ("not_found", None)

        try:
            if timeout:
                await asyncio.wait_for(process.wait(), timeout=timeout)
            else:
                await process.wait()

            status = "completed" if process.returncode == 0 else "failed"
            return (status, process.returncode)

        except asyncio.TimeoutError:
            return ("timeout", None)

    def get_active_sessions(self) -> Dict[str, int]:
        """Get all active sessions with their PIDs.

        Returns:
            Dictionary of session_id -> PID
        """
        active = {}
        for session_id, process in self._processes.items():
            if process.returncode is None:
                active[session_id] = process.pid
        return active

    async def cleanup_all(self) -> None:
        """Clean up all sessions and resources."""
        for session_id in list(self._processes.keys()):
            await self.terminate_session(session_id)

        # Close all remaining log handles
        for handle in self._log_handles.values():
            try:
                handle.close()
            except Exception:
                pass
        self._log_handles.clear()
