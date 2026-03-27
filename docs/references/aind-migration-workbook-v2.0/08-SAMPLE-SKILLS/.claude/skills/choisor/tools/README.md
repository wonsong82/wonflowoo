# Choisor 모니터링 도구

choisor daemon의 백그라운드 작업을 실시간으로 모니터링하는 도구들입니다.

## 빠른 시작

### Python 모니터링 도구 (권장)

```bash
# 프로젝트 디렉토리에서 실행
cd /path/to/your/project

# 실시간 대시보드 (기본)
python .claude/skills/choisor/tools/monitor.py

# 세션 상태만 한 번 표시
python .claude/skills/choisor/tools/monitor.py --sessions

# 모든 세션 로그 보기
python .claude/skills/choisor/tools/monitor.py --logs

# 특정 세션 로그만 모니터링
python .claude/skills/choisor/tools/monitor.py --logs <session-id>

# 갱신 간격 변경 (기본: 10초)
python .claude/skills/choisor/tools/monitor.py --interval 5
```

### Daemon 관리

```bash
# Daemon 시작
python .claude/skills/choisor/daemon/main.py

# Daemon 상태 확인
python .claude/skills/choisor/daemon/main.py --status

# Daemon 중지
python .claude/skills/choisor/daemon/main.py --stop
```

## 대시보드 정보

### 표시 항목

- **Daemon 상태**: 실행 중 여부, PID
- **Phase Gate**: 현재 허용된 최대 Phase
- **Work Scope**: 활성화된 도메인 필터
- **활성 세션**: 총 세션 수, 작업 중/유휴/에러 세션
- **작업 중인 세션 상세**: Feature ID, Domain, Phase, 마지막 활동 시간
- **작업 진행 상황**: 완료/작업 중/대기/스킵 통계
- **대기 중인 작업**: 우선순위 순 정렬 (최대 10개)
- **최근 로그 파일**: 세션 로그 목록

### 세션 상태

| 상태 | 설명 |
|------|------|
| idle | 유휴 상태 (작업 대기 중) |
| busy | 작업 실행 중 |
| error | 에러 발생 |
| terminated | 종료됨 |

## 고급 사용법

### tail로 로그 직접 모니터링

```bash
# 모든 세션 로그
tail -f .choisor/logs/sessions/session-*.log

# 특정 세션 로그
tail -f .choisor/logs/sessions/session-<session-id>.log
```

### Daemon 상태 직접 확인

```bash
# PID 확인
cat .choisor/daemon.pid

# 프로세스 상태
ps -p $(cat .choisor/daemon.pid)
```

## 파일 위치

| 파일 | 경로 |
|------|------|
| 세션 로그 | `.choisor/logs/sessions/session-<session-id>.log` |
| 작업지시서 아카이브 | `.choisor/logs/instructions/instruction-<task-id>-<timestamp>.txt` |
| Daemon PID | `.choisor/daemon.pid` |
| 세션 풀 | `.choisor/sessions/sessions.json` |
| 작업 목록 | `.choisor/tasks/tasks.json` |
| 설정 | `.choisor/config.yaml` |
