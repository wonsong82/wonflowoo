"""Choisor 2.0 Daemon - Communication Module

File-based IPC between daemon and CLI commands:
- Command queue (pending/executing/completed)
- Request/response protocol
- Session-to-daemon communication
"""

import glob
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any


class DaemonCommunication:
    """Handles communication between daemon and CLI commands.

    Uses file-based IPC with command directories for
    pending, executing, and completed commands.

    Attributes:
        project_root: Project root directory
        commands_dir: Base directory for command files
    """

    def __init__(self, project_root: Path):
        """Initialize communication handler.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.commands_dir = project_root / ".choisor" / "commands"
        self.pending_dir = self.commands_dir / "pending"
        self.executing_dir = self.commands_dir / "executing"
        self.completed_dir = self.commands_dir / "completed"

    def ensure_dirs(self) -> None:
        """Ensure communication directories exist."""
        for dir_path in [self.pending_dir, self.executing_dir, self.completed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def send_command(self, command: str, params: Dict[str, Any]) -> str:
        """Send a command to the daemon.

        Args:
            command: Command name (e.g., "assign-next", "process-completion")
            params: Command parameters

        Returns:
            Request ID for tracking
        """
        self.ensure_dirs()

        request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        request = {
            "id": request_id,
            "command": command,
            "params": params,
            "created_at": datetime.now().isoformat(),
        }

        request_path = self.pending_dir / f"{request_id}.json"

        with open(request_path, "w", encoding="utf-8") as f:
            json.dump(request, f, indent=2)

        return request_id

    def get_pending_commands(self) -> List[Dict[str, Any]]:
        """Get all pending commands.

        Returns:
            List of pending command dictionaries, sorted by creation time
        """
        commands = []

        for path in self.pending_dir.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    commands.append(json.load(f))
            except (json.JSONDecodeError, IOError):
                continue

        return sorted(commands, key=lambda x: x.get("created_at", ""))

    def mark_executing(self, request_id: str) -> bool:
        """Move command to executing state.

        Args:
            request_id: Request ID to mark

        Returns:
            True if command was moved successfully
        """
        src = self.pending_dir / f"{request_id}.json"
        dst = self.executing_dir / f"{request_id}.json"

        if src.exists():
            try:
                src.rename(dst)
                return True
            except OSError:
                pass

        return False

    def mark_completed(
        self,
        request_id: str,
        result: Dict[str, Any],
    ) -> bool:
        """Move command to completed state with result.

        Args:
            request_id: Request ID to complete
            result: Result dictionary to include

        Returns:
            True if command was completed successfully
        """
        src = self.executing_dir / f"{request_id}.json"

        if not src.exists():
            # Try pending directory
            src = self.pending_dir / f"{request_id}.json"

        if not src.exists():
            return False

        try:
            with open(src, "r", encoding="utf-8") as f:
                data = json.load(f)

            data["result"] = result
            data["completed_at"] = datetime.now().isoformat()

            dst = self.completed_dir / f"{request_id}.json"

            with open(dst, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            src.unlink()
            return True

        except (json.JSONDecodeError, IOError):
            return False

    def wait_for_result(
        self,
        request_id: str,
        timeout: float = 60.0,
    ) -> Optional[Dict[str, Any]]:
        """Wait for command result.

        Args:
            request_id: Request ID to wait for
            timeout: Timeout in seconds

        Returns:
            Result dictionary or None if timeout
        """
        result_path = self.completed_dir / f"{request_id}.json"
        start_time = time.time()

        while time.time() - start_time < timeout:
            if result_path.exists():
                try:
                    with open(result_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return data.get("result")
                except (json.JSONDecodeError, IOError):
                    pass

            time.sleep(0.5)

        return None

    def cleanup_old_commands(self, max_age_seconds: int = 3600) -> int:
        """Clean up old completed commands.

        Args:
            max_age_seconds: Maximum age in seconds (default: 1 hour)

        Returns:
            Number of commands cleaned up
        """
        cleaned = 0
        now = time.time()

        for path in self.completed_dir.glob("*.json"):
            try:
                file_age = now - path.stat().st_mtime
                if file_age > max_age_seconds:
                    path.unlink()
                    cleaned += 1
            except OSError:
                continue

        return cleaned


class IPCHandler:
    """Handles file-based IPC between daemon and sessions.

    Sessions can make requests (e.g., read source files, report progress)
    and the daemon responds.

    Protocol:
    - Request: .choisor/communication/requests/{session_id}-{seq}.json
    - Response: .choisor/communication/responses/{session_id}-{seq}.json
    """

    POLL_INTERVAL = 2  # seconds
    REQUEST_TIMEOUT = 60  # seconds

    def __init__(self, project_root: Path):
        """Initialize IPC handler.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.request_dir = project_root / ".choisor" / "communication" / "requests"
        self.response_dir = project_root / ".choisor" / "communication" / "responses"

        # Request handlers registry
        self.handlers: Dict[str, Callable] = {}

        # Ensure directories exist
        self.request_dir.mkdir(parents=True, exist_ok=True)
        self.response_dir.mkdir(parents=True, exist_ok=True)

    def register_handler(
        self,
        request_type: str,
        handler: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        """Register a handler for a request type.

        Args:
            request_type: Type of request (e.g., "read_source", "report_progress")
            handler: Function that takes request dict and returns response dict
        """
        self.handlers[request_type] = handler

    def poll_requests(self) -> List[Dict[str, Any]]:
        """Poll for new request files.

        Returns:
            List of request dictionaries
        """
        request_files = sorted(glob.glob(str(self.request_dir / "*.json")))
        requests = []

        for req_file in request_files:
            try:
                with open(req_file, "r", encoding="utf-8") as f:
                    req = json.load(f)

                # Validate request structure
                if not all(k in req for k in ["session_id", "sequence", "type"]):
                    print(f"Warning: Invalid request structure in {req_file}")
                    Path(req_file).unlink()
                    continue

                requests.append(req)

                # Remove consumed request
                Path(req_file).unlink()

            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading request {req_file}: {e}")
                # Don't remove on error - might be incomplete write

        return requests

    def send_response(
        self,
        session_id: str,
        sequence: int,
        response: Dict[str, Any],
    ) -> None:
        """Send a response to a session.

        Args:
            session_id: Session ID
            sequence: Request sequence number
            response: Response dict (must include "status")
        """
        response_data = {
            "session_id": session_id,
            "sequence": sequence,
            "timestamp": datetime.now().isoformat(),
            **response,
        }

        resp_file = self.response_dir / f"{session_id}-{sequence}.json"

        try:
            with open(resp_file, "w", encoding="utf-8") as f:
                json.dump(response_data, f, indent=2)
        except IOError as e:
            print(f"Error writing response {resp_file}: {e}")

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request and generate response.

        Args:
            request: Request dictionary

        Returns:
            Response dictionary
        """
        req_type = request.get("type")
        handler = self.handlers.get(req_type)

        if not handler:
            return {
                "status": "error",
                "error": f"Unknown request type: {req_type}",
            }

        try:
            return handler(request)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def process_all_requests(self) -> int:
        """Poll and process all pending requests.

        Returns:
            Number of requests processed
        """
        requests = self.poll_requests()

        for req in requests:
            response = self.handle_request(req)
            self.send_response(req["session_id"], req["sequence"], response)

        return len(requests)

    def cleanup_old_responses(self, max_age_seconds: int = 300) -> int:
        """Clean up old response files.

        Args:
            max_age_seconds: Maximum age in seconds (default: 5 minutes)

        Returns:
            Number of responses cleaned up
        """
        cleaned = 0
        now = time.time()

        for resp_file in self.response_dir.glob("*.json"):
            try:
                file_age = now - resp_file.stat().st_mtime
                if file_age > max_age_seconds:
                    resp_file.unlink()
                    cleaned += 1
            except OSError:
                continue

        return cleaned


class SessionIPCClient:
    """Client-side IPC helper for sessions.

    This class can be used by sessions to make requests to the daemon.

    Attributes:
        project_root: Project root directory
        session_id: Session identifier
        sequence: Request sequence counter
    """

    def __init__(self, project_root: Path, session_id: str):
        """Initialize session IPC client.

        Args:
            project_root: Project root directory
            session_id: Session identifier
        """
        self.project_root = project_root
        self.session_id = session_id
        self.request_dir = project_root / ".choisor" / "communication" / "requests"
        self.response_dir = project_root / ".choisor" / "communication" / "responses"
        self.sequence = 0

        # Ensure directories exist
        self.request_dir.mkdir(parents=True, exist_ok=True)
        self.response_dir.mkdir(parents=True, exist_ok=True)

    def send_request(
        self,
        request_type: str,
        payload: Dict[str, Any],
        timeout: float = 60.0,
    ) -> Optional[Dict[str, Any]]:
        """Send a request and wait for response.

        Args:
            request_type: Type of request (e.g., "read_source")
            payload: Request payload
            timeout: Timeout in seconds

        Returns:
            Response dictionary or None if timeout
        """
        self.sequence += 1
        seq = self.sequence

        request = {
            "session_id": self.session_id,
            "sequence": seq,
            "timestamp": datetime.now().isoformat(),
            "type": request_type,
            "payload": payload,
        }

        # Write request file
        req_file = self.request_dir / f"{self.session_id}-{seq}.json"
        with open(req_file, "w", encoding="utf-8") as f:
            json.dump(request, f, indent=2)

        # Wait for response
        resp_file = self.response_dir / f"{self.session_id}-{seq}.json"
        start_time = time.time()

        while time.time() - start_time < timeout:
            if resp_file.exists():
                try:
                    with open(resp_file, "r", encoding="utf-8") as f:
                        response = json.load(f)
                    resp_file.unlink()  # Consume response
                    return response
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error reading response: {e}")
                    return None

            time.sleep(0.5)

        # Timeout
        return None

    def read_source(self, file_path: str) -> Optional[str]:
        """Request to read a source file.

        Args:
            file_path: Relative path to source file

        Returns:
            File content or None if failed
        """
        response = self.send_request("read_source", {"file_path": file_path})

        if response and response.get("status") == "ok":
            return response.get("payload", {}).get("content")

        return None

    def report_progress(self, progress_data: Dict[str, Any]) -> bool:
        """Report progress to daemon.

        Args:
            progress_data: Progress information

        Returns:
            True if acknowledged, False otherwise
        """
        response = self.send_request("report_progress", progress_data)
        return response is not None and response.get("status") == "ok"
