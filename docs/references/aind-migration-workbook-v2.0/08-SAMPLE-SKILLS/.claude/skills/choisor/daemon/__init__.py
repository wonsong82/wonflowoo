"""Choisor 2.0 Daemon Module

Background orchestration daemon for parallel task execution:
- ChoisorDaemon: Main daemon process
- Scheduler: Task assignment and completion processing
- SessionPool: Claude Code session management
- ParallelCoordinator: s4-03 + s4-04 parallel execution
- ClaudeCodeClient: Claude Code process lifecycle
- Communication: File-based IPC between daemon and sessions
"""

from .main import ChoisorDaemon, main, check_existing_daemon, stop_daemon
from .scheduler import Scheduler
from .session_pool import SessionPool, Session, SessionState
from .parallel_coordinator import ParallelCoordinator, ParallelPairState
from .claude_code_client import ClaudeCodeClient
from .communication import DaemonCommunication, IPCHandler, SessionIPCClient

__all__ = [
    # Main daemon
    "ChoisorDaemon",
    "main",
    "check_existing_daemon",
    "stop_daemon",
    # Scheduler
    "Scheduler",
    # Session pool
    "SessionPool",
    "Session",
    "SessionState",
    # Parallel coordination
    "ParallelCoordinator",
    "ParallelPairState",
    # Claude Code client
    "ClaudeCodeClient",
    # Communication
    "DaemonCommunication",
    "IPCHandler",
    "SessionIPCClient",
]
