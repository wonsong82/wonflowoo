#!/bin/bash
# Choisor 실시간 모니터링 스크립트 (간단한 버전)

# 프로젝트 루트 찾기
find_project_root() {
    local current=$(pwd)
    while [ "$current" != "/" ]; do
        if [ -d "$current/.choisor" ]; then
            echo "$current"
            return 0
        fi
        current=$(dirname "$current")
    done
    return 1
}

PROJECT_ROOT=$(find_project_root)
if [ -z "$PROJECT_ROOT" ]; then
    echo "Error: Choisor 프로젝트를 찾을 수 없습니다"
    exit 1
fi

PROJECT_NAME=$(basename "$PROJECT_ROOT")
LOG_DIR="$PROJECT_ROOT/.choisor/logs/sessions"
DAEMON_PID_FILE="$PROJECT_ROOT/.choisor/daemon.pid"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Daemon 상태 확인
check_daemon() {
    if [ -f "$DAEMON_PID_FILE" ]; then
        local pid=$(cat "$DAEMON_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Daemon 실행 중 (PID: $pid)"
            return 0
        else
            echo -e "${RED}✗${NC} Daemon 프로세스 없음 (stale PID file)"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} Daemon 실행 중 아님"
        return 1
    fi
}

# 세션 로그 파일 목록
list_logs() {
    if [ -d "$LOG_DIR" ]; then
        ls -t "$LOG_DIR"/session-*.log 2>/dev/null | head -10
    fi
}

# 실시간 로그 모니터링
monitor_logs() {
    local session_id=$1
    
    if [ -n "$session_id" ]; then
        # 특정 세션 로그
        local log_file="$LOG_DIR/session-${session_id}.log"
        if [ -f "$log_file" ]; then
            echo -e "${CYAN}Monitoring: $(basename $log_file)${NC}"
            echo "=================================="
            tail -f "$log_file"
        else
            echo "Error: Log file not found: $log_file"
            exit 1
        fi
    else
        # 모든 세션 로그 (multitail 스타일)
        local log_files=$(list_logs)
        if [ -z "$log_files" ]; then
            echo "로그 파일 없음"
            return
        fi
        
        echo -e "${CYAN}모든 세션 로그 모니터링${NC}"
        echo "=================================="
        
        # 각 로그 파일의 마지막 몇 줄 표시
        for log_file in $log_files; do
            echo ""
            echo -e "${YELLOW}========================================${NC}"
            echo -e "${YELLOW}$(basename $log_file)${NC}"
            echo -e "${YELLOW}========================================${NC}"
            tail -n 10 "$log_file" 2>/dev/null || echo "읽기 실패"
        done
        
        echo ""
        echo -e "${CYAN}참고: 특정 세션 로그만 보려면: $0 --logs <session-id>${NC}"
    fi
}

# 간단한 상태 표시
show_status() {
    clear
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}Choisor 모니터링 - $PROJECT_NAME${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    
    check_daemon
    echo ""
    
    # 최근 로그 파일
    local log_files=$(list_logs)
    if [ -n "$log_files" ]; then
        echo "최근 로그 파일:"
        for log_file in $log_files; do
            local size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null)
            local mtime=$(stat -f%Sm "$log_file" 2>/dev/null || stat -c%y "$log_file" 2>/dev/null)
            echo "  $(basename $log_file) ($size bytes, $mtime)"
        done
    fi
    
    echo ""
    echo -e "${CYAN}========================================${NC}"
}

# Watch 모드
watch_mode() {
    local interval=${1:-2}
    while true; do
        show_status
        sleep "$interval"
    done
}

# 메인 로직
case "$1" in
    --logs)
        monitor_logs "$2"
        ;;
    --status)
        show_status
        ;;
    --watch)
        watch_mode "${2:-2}"
        ;;
    *)
        echo "Choisor 모니터링 스크립트"
        echo ""
        echo "사용법:"
        echo "  $0 --status          # 상태 표시"
        echo "  $0 --logs            # 모든 세션 로그 모니터링"
        echo "  $0 --logs <session-id>  # 특정 세션 로그만"
        echo "  $0 --watch [interval]   # watch 모드 (기본 2초)"
        echo ""
        echo "또는 Python 모니터링 도구 사용:"
        echo "  python .claude/skills/choisor/tools/monitor.py"
        ;;
esac

