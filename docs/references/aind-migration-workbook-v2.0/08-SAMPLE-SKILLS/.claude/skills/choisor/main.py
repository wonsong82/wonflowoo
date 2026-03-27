#!/usr/bin/env python3
"""Choisor 2.0 - CLI Entry Point

Usage:
    python -m choisor <command> [options]

Commands:
    status              Show current project status
    scan                Scan for tasks
    sync                Sync task status with filesystem
    query               Query tasks with filters
    assign-next         Select and assign next task
    process-completion  Process task completion
    manual-assign       Manually assign feature
    clean-restart       Reset features for rework
    stop                Stop running session and release task
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Handle both module and script execution
if __name__ == "__main__":
    # When run as script, add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        prog="choisor",
        description="Choisor 2.0 - Task Orchestrator for 5-Stage Workflow"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # status command
    subparsers.add_parser("status", help="Show current project status")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for tasks")
    scan_parser.add_argument("--stage", type=int, help="Stage to scan (1-5)")

    # sync command
    subparsers.add_parser("sync", help="Sync task status with filesystem")

    # query command
    query_parser = subparsers.add_parser("query", help="Query tasks")
    query_parser.add_argument(
        "--status",
        choices=["pending", "assigned", "in_progress", "completed", "skip", "failed"],
        help="Filter by task status"
    )
    query_parser.add_argument("--domain", help="Filter by domain")
    query_parser.add_argument("--stage", type=int, help="Filter by stage (1-5)")
    query_parser.add_argument("--phase", type=int, help="Filter by phase (1-5)")
    query_parser.add_argument("--priority", help="Filter by priority")
    query_parser.add_argument("--skip-reason", dest="skip_reason_filter", help="Filter by skip reason")
    query_parser.add_argument("--list", action="store_true", dest="show_list", help="Show task list")
    query_parser.add_argument("--format", choices=["table", "json", "csv"], default="table", help="Output format")
    query_parser.add_argument("--limit", type=int, help="Limit number of results")
    query_parser.add_argument("--no-stats", action="store_true", help="Hide statistics")

    # assign-next command
    assign_parser = subparsers.add_parser("assign-next", help="Assign next task")
    assign_parser.add_argument("--request", help="Request ID")

    # process-completion command
    completion_parser = subparsers.add_parser("process-completion", help="Process task completion")
    completion_parser.add_argument("task_id", help="Task ID")
    completion_parser.add_argument("--request", help="Request ID")

    # manual-assign command
    manual_parser = subparsers.add_parser("manual-assign", help="Manually assign feature")
    manual_parser.add_argument("feature_id", help="Feature ID")
    manual_parser.add_argument("--session", help="Session ID")

    # clean-restart command
    restart_parser = subparsers.add_parser("clean-restart", help="Reset features")
    restart_parser.add_argument("feature_ids", nargs="+", help="Feature IDs")
    restart_parser.add_argument("--target-phase", type=int, default=2, help="Target phase to reset to")

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop running session and release task")
    stop_parser.add_argument("--session", help="Session ID to stop")
    stop_parser.add_argument("--task", help="Task ID to find session")
    stop_parser.add_argument("--feature", help="Feature ID to find session (e.g., FEAT-CM-001)")
    stop_parser.add_argument("--all", action="store_true", dest="stop_all", help="Stop all running sessions")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize project configuration")
    init_parser.add_argument(
        "--template",
        choices=["spring-migration", "custom"],
        default="spring-migration",
        help="Template to use (default: spring-migration)"
    )
    init_parser.add_argument("--name", help="Project name (default: directory name)")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing project.yaml")
    init_parser.add_argument("--list-templates", action="store_true", dest="list_templates", help="List available templates")

    args = parser.parse_args()

    # Import here to avoid circular imports and speed up --help
    try:
        from .config import find_project_root
        from .commands import (
            handle_status,
            handle_scan,
            handle_sync,
            handle_query,
            handle_assign_next,
            handle_process_completion,
            handle_manual_assign,
            handle_clean_restart,
            handle_stop,
            handle_stop_all,
            handle_init,
            handle_show_templates,
        )
    except ImportError:
        # When run as script
        from choisor.config import find_project_root
        from choisor.commands import (
            handle_status,
            handle_scan,
            handle_sync,
            handle_query,
            handle_assign_next,
            handle_process_completion,
            handle_manual_assign,
            handle_clean_restart,
            handle_stop,
            handle_stop_all,
            handle_init,
            handle_show_templates,
        )

    # Find project root
    project_root = find_project_root()
    if not project_root:
        print("Error: Not in a Choisor project (no .choisor/ or .claude/ directory found)")
        return 1

    # Route to command handler
    if args.command == "status":
        handle_status(project_root)

    elif args.command == "scan":
        result = handle_scan(project_root, stage=args.stage)
        print(f"Scan complete: {result.get('total_tasks', 0)} tasks")

    elif args.command == "sync":
        result = handle_sync(project_root)
        print(f"Sync complete: {result.get('updated', 0)} tasks updated")

    elif args.command == "query":
        handle_query(
            project_root,
            status=args.status,
            domain=args.domain,
            stage=args.stage,
            phase=args.phase,
            priority=args.priority,
            skip_reason_filter=args.skip_reason_filter,
            show_list=args.show_list,
            output_format=args.format,
            limit=args.limit,
            no_stats=args.no_stats,
        )

    elif args.command == "assign-next":
        task, instruction, model = handle_assign_next(project_root, request_id=args.request)
        if task:
            task_id = task.get('id', task) if isinstance(task, dict) else task.id
            print(f"Assigned: {task_id}")
            print(f"Model: {model}")
        else:
            print(f"No task assigned: {model}")

    elif args.command == "process-completion":
        result = handle_process_completion(project_root, args.task_id, request_id=args.request)
        if result.get("success"):
            print(f"Task {args.task_id} completed successfully")
        else:
            print(f"Failed: {result.get('error', 'Unknown error')}")

    elif args.command == "manual-assign":
        result = handle_manual_assign(project_root, args.feature_id, session_id=args.session)
        if result.get("success"):
            print(f"Assigned {args.feature_id} to session {result.get('session_id', 'N/A')}")
        else:
            print(f"Failed: {result.get('error', 'Unknown error')}")

    elif args.command == "clean-restart":
        result = handle_clean_restart(
            project_root,
            args.feature_ids,
            target_phase=args.target_phase
        )
        if result.get("success"):
            print(f"Reset {len(args.feature_ids)} features to phase {args.target_phase}")
        else:
            print(f"Failed: {result.get('error', 'Unknown error')}")

    elif args.command == "stop":
        if args.stop_all:
            count, msg = handle_stop_all(project_root)
            print(msg)
        else:
            success, msg = handle_stop(
                project_root,
                session_id=args.session,
                task_id=args.task,
                feature_id=args.feature
            )
            print(msg)
            if not success:
                return 1

    elif args.command == "init":
        if args.list_templates:
            handle_show_templates()
        else:
            result = handle_init(
                project_root,
                template=args.template,
                name=args.name,
                force=args.force
            )
            if not result.get("success"):
                print(f"Failed: {result.get('error', 'Unknown error')}")
                return 1

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
