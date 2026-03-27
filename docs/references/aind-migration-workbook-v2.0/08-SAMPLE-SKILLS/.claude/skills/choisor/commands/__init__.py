"""Choisor 2.0 Commands Module

CLI command handlers for the orchestrator:
- status: Show workflow status
- scan: Scan for tasks and update tasks.json
- sync: Synchronize task state with filesystem
- query: Query tasks with filters
- assign_next: Select and assign next task
- process_completion: Process task completion
- manual_assign: Manually assign a specific feature
- clean_restart: Reset features to clean state
- stop: Stop running session and release task
- init: Initialize project configuration
"""

from .status import handle_status
from .scan import handle_scan
from .sync import handle_sync
from .query import handle_query
from .assign_next import handle_assign_next
from .process_completion import handle_process_completion
from .manual_assign import handle_manual_assign
from .clean_restart import handle_clean_restart
from .stop import handle_stop, handle_stop_all
from .init import handle_init, handle_show_templates, handle_validate_project

__all__ = [
    "handle_status",
    "handle_scan",
    "handle_sync",
    "handle_query",
    "handle_assign_next",
    "handle_process_completion",
    "handle_manual_assign",
    "handle_clean_restart",
    "handle_stop",
    "handle_stop_all",
    "handle_init",
    "handle_show_templates",
    "handle_validate_project",
]
