#!/usr/bin/env python3
"""Choisor 실시간 모니터링 도구

사용법:
    python monitor.py                      # 통합 대시보드 (자동 갱신)
    python monitor.py --logs               # 모든 세션 로그 실시간 모니터링
    python monitor.py --logs <session-id>  # 특정 세션 로그만 모니터링
    python monitor.py --sessions           # 세션 상태만 표시 (한 번만)
    python monitor.py --interval 5         # 갱신 간격 변경 (기본: 10초)
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Handle direct script execution
if __name__ == "__main__" or not __package__:
    _this_file = Path(__file__).resolve()
    _choisor_root = _this_file.parent.parent.parent  # .claude/skills
    if str(_choisor_root) not in sys.path:
        sys.path.insert(0, str(_choisor_root))

    from choisor.config import find_project_root, ConfigLoader
    from choisor.core.priority import PriorityEngine
else:
    from ..config import find_project_root, ConfigLoader
    from ..core.priority import PriorityEngine


# ANSI 색상 코드
COLORS = {
    'reset': '\033[0m',
    'bold': '\033[1m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
}


def load_sessions(project_root: str) -> List[Dict]:
    """프로젝트별 세션 목록 로드"""
    sessions_file = os.path.join(project_root, ".choisor", "sessions", "sessions.json")

    if not os.path.exists(sessions_file):
        return []

    try:
        with open(sessions_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"{COLORS['yellow']}Warning: Failed to load sessions: {e}{COLORS['reset']}")
        return []


def load_config(project_root: str) -> Dict:
    """프로젝트 설정 로드"""
    try:
        loader = ConfigLoader(Path(project_root))
        config = loader.load()
        return config.model_dump()
    except Exception:
        return {}


def load_tasks(project_root: str) -> List[Dict]:
    """프로젝트 작업 목록 로드"""
    tasks_path = os.path.join(project_root, ".choisor", "tasks", "tasks.json")
    if not os.path.exists(tasks_path):
        return []

    max_retries = 3
    for attempt in range(max_retries):
        try:
            with open(tasks_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return json.loads(content)
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
                continue
            else:
                print(f"{COLORS['red']}Error: Invalid JSON in tasks.json{COLORS['reset']}")
                return []
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
                continue
            else:
                print(f"{COLORS['red']}Error loading tasks.json: {e}{COLORS['reset']}")
                return []

    return []


def get_daemon_status(project_root: str) -> Optional[Dict]:
    """Daemon 상태 확인"""
    pid_file = os.path.join(project_root, ".choisor", "daemon.pid")
    if not os.path.exists(pid_file):
        return None

    try:
        with open(pid_file, 'r') as f:
            pid_str = f.read().strip()
            if not pid_str:
                return None
            pid = int(pid_str)
    except (ValueError, IOError):
        return None

    try:
        os.kill(pid, 0)
        return {"pid": pid, "running": True}
    except OSError:
        return {"pid": pid, "running": False}


def get_log_files(project_root: str) -> List[str]:
    """로그 파일 목록 가져오기"""
    log_dir = os.path.join(project_root, ".choisor", "logs", "sessions")
    if not os.path.exists(log_dir):
        return []

    log_files = []
    for f in os.listdir(log_dir):
        if f.startswith("session-") and f.endswith(".log"):
            log_files.append(os.path.join(log_dir, f))

    return sorted(log_files, key=os.path.getmtime, reverse=True)


def format_status(status: str) -> str:
    """상태에 색상 적용"""
    colors = {
        "idle": COLORS['green'],
        "assigned": COLORS['yellow'],
        "running": COLORS['yellow'],
        "completed": COLORS['green'],
        "failed": COLORS['red'],
        "terminated": COLORS['white'],
        # Legacy support
        "busy": COLORS['yellow'],
        "error": COLORS['red'],
    }
    color = colors.get(status, COLORS['white'])
    return f"{color}{status:12}{COLORS['reset']}"


def format_time(iso_str: str) -> str:
    """ISO 시간 문자열을 읽기 쉬운 형식으로 변환"""
    try:
        dt = datetime.fromisoformat(iso_str)
        now = datetime.now()
        diff = now - dt

        if diff.total_seconds() < 60:
            return f"{int(diff.total_seconds())}초 전"
        elif diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() / 60)}분 전"
        else:
            return f"{int(diff.total_seconds() / 3600)}시간 전"
    except:
        return iso_str


def show_dashboard(project_root: str, project_name: str, clear_screen: bool = True):
    """통합 대시보드 표시"""
    if clear_screen:
        sys.stdout.flush()
        sys.stderr.flush()
        os.system('clear' if os.name != 'nt' else 'cls')
        sys.stdout.flush()

    print(f"{COLORS['bold']}{COLORS['cyan']}{'='*80}{COLORS['reset']}")
    print(f"{COLORS['bold']}Choisor 실시간 모니터링 - {project_name}{COLORS['reset']}")
    print(f"{COLORS['cyan']}{'='*80}{COLORS['reset']}\n")

    # Daemon 상태
    daemon = get_daemon_status(project_root)
    if daemon:
        status_icon = "✓" if daemon["running"] else "✗"
        status_color = COLORS['green'] if daemon["running"] else COLORS['red']
        print(f"{COLORS['bold']}Daemon:{COLORS['reset']} {status_color}{status_icon}{COLORS['reset']} PID: {daemon['pid']}")
    else:
        print(f"{COLORS['bold']}Daemon:{COLORS['reset']} {COLORS['red']}✗ Not running{COLORS['reset']}")

    # Config 로드
    config = load_config(project_root)

    # 작업 목록 로드 (early load for assignment delay calculation)
    tasks = load_tasks(project_root)

    # Assignment 상태
    assignment_config = config.get("assignment", {})
    assignment_enabled = assignment_config.get("enabled", True)
    assignment_delay = assignment_config.get("delay")

    if not assignment_enabled:
        print(f"{COLORS['bold']}Assignment:{COLORS['reset']} {COLORS['red']}✗ Disabled{COLORS['reset']}")
    elif assignment_delay:
        # Calculate remaining delay time from last assigned task
        last_assigned_time = None
        for task in tasks:
            if task.get("status") in ("assigned", "completed"):
                updated_at = task.get("updated_at")
                if updated_at:
                    try:
                        task_time = datetime.fromisoformat(updated_at)
                        if last_assigned_time is None or task_time > last_assigned_time:
                            last_assigned_time = task_time
                    except (ValueError, TypeError):
                        pass

        if last_assigned_time:
            elapsed = (datetime.now() - last_assigned_time).total_seconds() / 60
            remaining = assignment_delay - elapsed
            if remaining > 0:
                print(f"{COLORS['bold']}Assignment:{COLORS['reset']} {COLORS['yellow']}⏳ Delayed ({remaining:.1f} min remaining){COLORS['reset']}")
            else:
                print(f"{COLORS['bold']}Assignment:{COLORS['reset']} {COLORS['green']}✓ Ready (delay: {assignment_delay} min){COLORS['reset']}")
        else:
            print(f"{COLORS['bold']}Assignment:{COLORS['reset']} {COLORS['green']}✓ Ready (delay: {assignment_delay} min){COLORS['reset']}")
    else:
        print(f"{COLORS['bold']}Assignment:{COLORS['reset']} {COLORS['green']}✓ Enabled{COLORS['reset']}")

    # Phase Gate
    phase_gate = config.get("phase_gate", {})
    max_allowed_phase = phase_gate.get("max_allowed_phase", "phase1")
    print(f"{COLORS['bold']}Phase Gate:{COLORS['reset']} {max_allowed_phase}")

    # Work Scope
    work_scope = config.get("work_scope", {})
    enabled_domains = work_scope.get("enabled_domains")
    if enabled_domains:
        domains_str = ', '.join([d.upper() for d in enabled_domains])
        print(f"{COLORS['bold']}Work Scope:{COLORS['reset']} {domains_str}")
    else:
        print(f"{COLORS['bold']}Work Scope:{COLORS['reset']} All domains")

    print()

    # tasks already loaded above
    tasks_by_id = {t["id"]: t for t in tasks if "id" in t}

    # 세션 상태
    sessions = load_sessions(project_root)

    if sessions:
        # Support both old "status" and new "state" field names
        def get_state(s):
            return s.get("state") or s.get("status", "unknown")

        busy_sessions = [s for s in sessions if get_state(s) in ("assigned", "running", "busy")]
        idle_sessions = [s for s in sessions if get_state(s) == "idle"]
        error_sessions = [s for s in sessions if get_state(s) in ("failed", "error")]

        print(f"{COLORS['bold']}활성 세션: {len(sessions)} (작업 중: {len(busy_sessions)}, 유휴: {len(idle_sessions)}, 에러: {len(error_sessions)}){COLORS['reset']}\n")

        # Get default model from config
        claude_code_config = config.get("claude_code", {})
        default_model = claude_code_config.get("default_model", "unknown")

        print(f"{'Session ID':<12} {'PID':<8} {'Model':<30} {'Status':<10}")
        print("-" * 65)

        for session in sorted(sessions, key=lambda x: get_state(x), reverse=False):
            session_id = session["id"][:8]
            status = get_state(session)
            process_id = session.get("process_id")
            pid_str = str(process_id) if process_id else "-"

            # Get model from session (last_model in new schema, current_model/last_used_model in old)
            current_model = session.get("last_model") or session.get("current_model") or session.get("last_used_model") or default_model
            # Truncate model name if too long
            if len(current_model) > 28:
                current_model = current_model[:25] + "..."

            status_color = COLORS['yellow'] if status in ("assigned", "running", "busy") else COLORS['green'] if status == "idle" else COLORS['red']
            print(f"{COLORS['cyan']}{session_id:<12}{COLORS['reset']} {pid_str:<8} {current_model:<30} {status_color}{status:<10}{COLORS['reset']}")

        print()

        # 작업 중인 세션 상세 정보
        if busy_sessions:
            print(f"{COLORS['bold']}{COLORS['yellow']}작업 중인 세션:{COLORS['reset']}\n")
            print(f"{'Session ID':<12} {'Domain':<8} {'Feature ID':<20} {'Phase':<10} {'Started':<15}")
            print("-" * 70)

            # Support both old "last_activity_at" and new "started_at" field names
            def get_activity_time(s):
                return s.get("started_at") or s.get("last_activity_at", "")

            for session in sorted(busy_sessions, key=lambda x: get_activity_time(x), reverse=True):
                session_id = session["id"][:8]
                task_id = session.get("current_task_id")
                last_activity = format_time(get_activity_time(session))

                if task_id and task_id in tasks_by_id:
                    task = tasks_by_id[task_id]
                    metadata = task.get("metadata", {})
                    # Check task directly first, then metadata
                    feature_id = task.get("feature_id") or metadata.get("feature_id") or task.get("category", "N/A")
                    stage = task.get("stage", "")
                    phase = task.get("phase") or metadata.get("phase", "N/A")
                    domain = task.get("domain") or metadata.get("domain", "")
                    domain = domain.upper() if domain else "N/A"

                    # Format phase with stage
                    if stage and phase != "N/A":
                        phase_str = f"S{stage}P{phase}"
                    else:
                        phase_str = str(phase)

                    if len(feature_id) > 18:
                        feature_id = feature_id[:15] + "..."

                    print(f"{COLORS['cyan']}{session_id:<12}{COLORS['reset']} {domain:<8} {feature_id:<20} {phase_str:<10} {last_activity:<15}")
                else:
                    print(f"{COLORS['cyan']}{session_id:<12}{COLORS['reset']} {'-':<8} {COLORS['yellow']}Task 정보 없음{COLORS['reset']:<20} {'-':<10} {last_activity:<15}")

            print()
    else:
        print(f"{COLORS['yellow']}활성 세션 없음{COLORS['reset']}\n")

    # 작업 진행 상황 요약 (항상 표시)
    if tasks:
        status_counts = {}
        for task in tasks:
            status = task.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        print(f"{COLORS['bold']}작업 진행 상황:{COLORS['reset']}")
        print(f"  총 작업: {len(tasks)}")
        print(f"  {COLORS['green']}완료: {status_counts.get('completed', 0)}{COLORS['reset']}, "
              f"{COLORS['yellow']}작업 중: {status_counts.get('assigned', 0) + status_counts.get('in_progress', 0)}{COLORS['reset']}, "
              f"{COLORS['white']}대기: {status_counts.get('pending', 0)}{COLORS['reset']}, "
              f"{COLORS['magenta']}스킵: {status_counts.get('skip', 0)}{COLORS['reset']}")

        print()

        # 대기 중인 작업 목록
        pending_tasks = [task for task in tasks if task.get("status") in ["pending", "skip"]]

        # 도메인 필터링
        def get_domain(task):
            """Get domain from metadata or extract from feature_id."""
            domain = task.get('metadata', {}).get('domain')
            if domain:
                return domain.lower()
            # Extract from feature_id: FEAT-CM-xxx -> cm
            feature_id = task.get('feature_id', '')
            if feature_id and '-' in feature_id:
                parts = feature_id.split('-')
                if len(parts) >= 2:
                    return parts[1].lower()
            return ''

        if enabled_domains:
            enabled_lower = [d.lower() for d in enabled_domains]
            pending_tasks = [
                t for t in pending_tasks
                if get_domain(t) in enabled_lower
            ]

        if pending_tasks:
            # 우선순위 정렬
            try:
                priority_config = config.get("priority", {})
                algorithm = priority_config.get("algorithm", "weighted_score")
                weights = priority_config.get("weights")

                engine = PriorityEngine(algorithm=algorithm, weights=weights)

                scored_tasks = [
                    (task, engine.calculate_score(task, tasks))
                    for task in pending_tasks
                ]
                scored_tasks.sort(key=lambda x: x[1], reverse=True)
                pending_tasks_sorted = [task for task, _ in scored_tasks]
                task_scores = {task.get("id"): score for task, score in scored_tasks}
            except Exception as e:
                pending_tasks_sorted = pending_tasks
                task_scores = {}

            print(f"{COLORS['bold']}{COLORS['white']}대기 중인 작업 (최대 10개):{COLORS['reset']}\n")
            print(f"{'Domain':<8} {'Feature ID':<20} {'Phase':<10} {'Score':<8} {'Status':<10}")
            print("-" * 60)

            for task in pending_tasks_sorted[:10]:
                metadata = task.get("metadata", {})
                # Get domain from metadata or extract from feature_id
                domain = metadata.get("domain")
                feature_id = task.get("feature_id") or metadata.get("feature_id") or task.get("category", "N/A")
                if not domain and feature_id and '-' in feature_id:
                    parts = feature_id.split('-')
                    if len(parts) >= 2:
                        domain = parts[1]
                domain = domain.upper() if domain else "N/A"
                # Get phase from task directly, fallback to metadata
                phase = task.get("phase") or metadata.get("phase", "N/A")
                stage = task.get("stage", "")
                if stage and phase != "N/A":
                    phase = f"S{stage}P{phase}"
                task_status = task.get("status", "pending")

                if len(feature_id) > 18:
                    feature_id = feature_id[:15] + "..."

                task_id = task.get("id")
                score_str = f"{task_scores.get(task_id, 0):.3f}" if task_id in task_scores else "N/A"

                status_color = COLORS['magenta'] if task_status == "skip" else COLORS['white']

                print(f"{domain:<8} {feature_id:<20} {phase:<10} {score_str:<8} {status_color}{task_status:<10}{COLORS['reset']}")

            if len(pending_tasks_sorted) > 10:
                print(f"\n  {COLORS['yellow']}... 및 {len(pending_tasks_sorted) - 10}개 더{COLORS['reset']}")

            print()
    else:
        print(f"{COLORS['yellow']}작업 목록 없음{COLORS['reset']}\n")

    # 최근 로그 파일
    log_files = get_log_files(project_root)
    if log_files:
        print(f"{COLORS['bold']}최근 로그 파일 (최대 5개):{COLORS['reset']}\n")
        for log_file in log_files[:5]:
            filename = os.path.basename(log_file)
            size = os.path.getsize(log_file)
            mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
            age = format_time(mtime.isoformat())

            print(f"  {COLORS['cyan']}{filename}{COLORS['reset']} ({size} bytes, {age})")

    print(f"\n{COLORS['cyan']}{'='*80}{COLORS['reset']}")
    print(f"업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Ctrl+C로 종료")


def monitor_logs(project_root: str, session_id: Optional[str] = None):
    """로그 파일 실시간 모니터링"""
    log_dir = os.path.join(project_root, ".choisor", "logs", "sessions")

    if session_id:
        log_file = os.path.join(log_dir, f"session-{session_id}.log")
        if not os.path.exists(log_file):
            print(f"Error: Log file not found: {log_file}")
            sys.exit(1)

        print(f"{COLORS['bold']}{COLORS['cyan']}Monitoring: {os.path.basename(log_file)}{COLORS['reset']}\n")

        try:
            subprocess.run(["tail", "-f", log_file])
        except KeyboardInterrupt:
            print(f"\n{COLORS['yellow']}모니터링 종료{COLORS['reset']}")
    else:
        log_files = get_log_files(project_root)

        if not log_files:
            print(f"{COLORS['yellow']}로그 파일 없음{COLORS['reset']}")
            return

        print(f"{COLORS['bold']}{COLORS['cyan']}모든 세션 로그 ({len(log_files)}개 파일){COLORS['reset']}\n")

        for log_file in log_files[:10]:
            filename = os.path.basename(log_file)
            print(f"\n{COLORS['bold']}{COLORS['yellow']}{'='*60}{COLORS['reset']}")
            print(f"{COLORS['bold']}{COLORS['yellow']}{filename}{COLORS['reset']}")
            print(f"{COLORS['yellow']}{'='*60}{COLORS['reset']}\n")

            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for line in lines[-10:]:
                        print(line.rstrip())
            except Exception as e:
                print(f"{COLORS['red']}Error reading {log_file}: {e}{COLORS['reset']}")


def show_sessions(project_root: str, project_name: str):
    """세션 상태만 표시"""
    sessions = load_sessions(project_root)

    if not sessions:
        print(f"{COLORS['yellow']}활성 세션 없음{COLORS['reset']}")
        return

    # Support both old "status" and new "state" field names
    def get_state(s):
        return s.get("state") or s.get("status", "unknown")

    def get_activity_time(s):
        return s.get("started_at") or s.get("last_activity_at", "")

    # Load config for default model
    config = load_config(project_root)
    claude_code_config = config.get("claude_code", {})
    default_model = claude_code_config.get("default_model", "unknown")

    print(f"{COLORS['bold']}{COLORS['cyan']}세션 상태{COLORS['reset']}\n")

    stats = {}
    for session in sessions:
        status = get_state(session)
        stats[status] = stats.get(status, 0) + 1

    print(f"총 세션: {len(sessions)}")
    for status, count in sorted(stats.items()):
        print(f"  {format_status(status)}: {count}")

    print()
    print(f"{'Session ID':<12} {'PID':<8} {'Model':<30} {'Status':<12} {'Task ID':<30}")
    print("-" * 95)

    for session in sorted(sessions, key=lambda x: get_activity_time(x), reverse=True):
        session_id = session["id"][:8]
        status = format_status(get_state(session))
        task_id = session.get("current_task_id") or "-"
        if len(task_id) > 28:
            task_id = task_id[:25] + "..."

        process_id = session.get("process_id")
        pid_str = str(process_id) if process_id else "-"

        # Get model from session
        current_model = session.get("last_model") or session.get("current_model") or session.get("last_used_model") or default_model
        if len(current_model) > 28:
            current_model = current_model[:25] + "..."

        print(f"{COLORS['cyan']}{session_id:<12}{COLORS['reset']} {pid_str:<8} {current_model:<30} {status:<12} {task_id:<30}")


def watch_mode(project_root: str, project_name: str, interval: int = 10):
    """watch 모드 (주기적으로 갱신)"""
    try:
        if os.name != 'nt':
            sys.stdout.write('\033[?25l')  # 커서 숨기기
            sys.stdout.flush()

        while True:
            sys.stdout.flush()
            sys.stderr.flush()

            if os.name != 'nt':
                sys.stdout.write('\033[2J\033[H\033[3J')
                sys.stdout.flush()
            os.system('clear' if os.name != 'nt' else 'cls')

            show_dashboard(project_root, project_name, clear_screen=False)

            sys.stdout.flush()
            time.sleep(interval)
    except KeyboardInterrupt:
        if os.name != 'nt':
            sys.stdout.write('\033[?25h')  # 커서 보이기
            sys.stdout.flush()
        print(f"\n{COLORS['yellow']}모니터링 종료{COLORS['reset']}")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Choisor 실시간 모니터링 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python monitor.py                      # 실시간 대시보드
    python monitor.py --sessions           # 세션 상태만 (한 번)
    python monitor.py --logs               # 모든 로그 보기
    python monitor.py --logs <session-id>  # 특정 세션 로그
    python monitor.py --interval 5         # 5초마다 갱신
"""
    )
    parser.add_argument("--logs", nargs="?", const=True, help="로그 모니터링 (특정 세션 ID 지정 가능)")
    parser.add_argument("--sessions", action="store_true", help="세션 상태만 표시")
    parser.add_argument("--interval", type=int, default=10, help="갱신 간격 (초, 기본: 10)")
    parser.add_argument("--project-root", type=str, help="프로젝트 루트 경로")

    args = parser.parse_args()

    # 프로젝트 루트 찾기
    if args.project_root:
        project_root = Path(args.project_root).resolve()
        if not (project_root / '.choisor').is_dir():
            print(f"{COLORS['red']}Error: .choisor/ 디렉토리가 없습니다: {project_root}{COLORS['reset']}")
            sys.exit(1)
    else:
        project_root = find_project_root()
        if not project_root:
            print(f"{COLORS['red']}Error: Choisor 프로젝트를 찾을 수 없습니다{COLORS['reset']}")
            print(f"{COLORS['yellow']}힌트: --project-root 옵션으로 프로젝트 루트를 지정하세요{COLORS['reset']}")
            sys.exit(1)

    project_name = project_root.name if isinstance(project_root, Path) else os.path.basename(project_root)
    project_root_str = str(project_root)

    # 모드별 실행
    if args.logs:
        session_id = args.logs if isinstance(args.logs, str) else None
        monitor_logs(project_root_str, session_id)
    elif args.sessions:
        show_sessions(project_root_str, project_name)
    else:
        print(f"{COLORS['yellow']}실시간 모니터링 모드 (Ctrl+C로 종료){COLORS['reset']}")
        print(f"{COLORS['yellow']}갱신 간격: {args.interval}초{COLORS['reset']}\n")
        time.sleep(1)
        watch_mode(project_root_str, project_name, args.interval)


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(line_buffering=True)
        except (ValueError, OSError):
            pass
    main()
