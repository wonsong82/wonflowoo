# Claude Code Agent Teams

> **출처**: [Claude Code 공식 문서](https://code.claude.com/docs/en/agent-teams) | [Anthropic 엔지니어링 블로그](https://www.anthropic.com/engineering/building-c-compiler)  

---

## 핵심 요약

Claude Code Agent Teams는 **여러 Claude 인스턴스가 독립적으로 작업하면서 서로 협력할 수 있는 시스템**이다. 한 세션이 팀 리드로서 작업을 조율하고, 각 팀원은 독립적인 컨텍스트 윈도우에서 작업하며 서로 직접 메시지를 주고받는다. 병렬 탐색, 리뷰, 디버깅, 크로스 레이어 개발 등 병렬 작업이 가치를 더하는 복잡한 작업에 최적화되어 있다.

Anthropic 연구원은 이 시스템을 사용해 **16개 에이전트가 2주간 협력**하여, Linux 커널을 컴파일할 수 있는 10만 줄 규모의 Rust 기반 C 컴파일러를 완전 자율적으로 작성했다 ($20,000 API 비용).

---

## Agent Teams란?

### 핵심 개념

**Agent Teams = 여러 Claude Code 인스턴스가 팀으로 협력하는 시스템**

- **팀 리드 (Team Lead)**: 팀을 생성하고, 팀원을 관리하며, 작업을 조율하는 메인 Claude Code 세션
- **팀원 (Teammates)**: 각자 독립적인 컨텍스트 윈도우를 가지고 작업하는 별도의 Claude Code 인스턴스
- **공유 태스크 리스트 (Task List)**: 팀원들이 클레임하고 완료하는 공유 작업 목록
- **메일박스 (Mailbox)**: 에이전트 간 직접 메시지 전달 시스템

### Subagents와 비교

| 구분 | Subagents | Agent Teams |
|------|-----------|-------------|
| **컨텍스트** | 자체 컨텍스트 윈도우; 결과만 호출자에게 반환 | 독립적인 컨텍스트 윈도우; 완전 독립적 |
| **커뮤니케이션** | 메인 에이전트에게만 보고 | 팀원끼리 직접 메시지 주고받기 |
| **조율** | 메인 에이전트가 모든 작업 관리 | 공유 태스크 리스트로 자율 조정 |
| **적합한 용도** | 결과만 중요한 집중 작업 | 토론과 협력이 필요한 복잡한 작업 |
| **토큰 비용** | 낮음: 결과만 메인 컨텍스트로 요약 | 높음: 각 팀원이 별도 Claude 인스턴스 |

**선택 기준:**
- **Subagents**: 빠르고 집중된 작업자가 필요하고 결과만 중요할 때
- **Agent Teams**: 팀원들이 발견 사항을 공유하고, 서로 도전하며, 자율적으로 조정해야 할 때

---

## 언제 사용하는가?

### 최적 사용 사례

1. **리서치와 리뷰**
   - 여러 팀원이 문제의 다른 측면을 동시에 조사
   - 발견 사항을 공유하고 서로의 이론에 도전

2. **새로운 모듈/기능 개발**
   - 각 팀원이 서로 겹치지 않는 별도 영역 담당
   - 독립적으로 작업 가능한 컴포넌트

3. **경쟁 가설로 디버깅**
   - 여러 팀원이 서로 다른 이론을 병렬로 테스트
   - 더 빠르게 답을 찾음

4. **크로스 레이어 조정**
   - 프론트엔드, 백엔드, 테스트에 걸친 변경
   - 각 레이어를 다른 팀원이 담당

### 적합하지 않은 경우

- 순차적 작업
- 같은 파일을 편집해야 하는 작업
- 의존성이 많은 작업
- 조정 오버헤드가 이득보다 큰 간단한 작업

이런 경우엔 **단일 세션 또는 Subagents**가 더 효과적이다.

---

## 설정 및 시작

### 1. Agent Teams 활성화

기본적으로 비활성화되어 있으며, 환경 변수로 활성화:

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

또는 `settings.json`에서:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### 2. 첫 팀 시작

자연어로 팀 생성 요청:

```
I'm designing a CLI tool that helps developers track TODO comments across
their codebase. Create an agent team to explore this from different angles: one
teammate on UX, one on technical architecture, one playing devil's advocate.
```

Claude가 자동으로:
1. 팀 생성
2. 각 역할에 맞는 팀원 생성
3. 작업 조율
4. 발견 사항 종합
5. 완료 시 팀 정리

### 3. 디스플레이 모드 선택

**In-process 모드** (기본):
- 모든 팀원이 메인 터미널 안에서 실행
- `Shift+Up/Down`으로 팀원 선택 및 메시지 전송
- 별도 설정 불필요

**Split panes 모드**:
- 각 팀원이 독립적인 패널에서 실행
- 모든 팀원의 출력을 동시에 확인 가능
- tmux 또는 iTerm2 필요

```json
{
  "teammateMode": "in-process"  // 또는 "tmux" / "auto"
}
```

```bash
# 단일 세션에서 모드 지정
claude --teammate-mode in-process
```

---

## 팀 제어 방법

### 팀원 및 모델 지정

```
Create a team with 4 teammates to refactor these modules in parallel.
Use Sonnet for each teammate.
```

### Plan 승인 요구

복잡하거나 위험한 작업에서:

```
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```

- 팀원이 계획 완료 시 리드에게 승인 요청
- 리드가 승인/거부 결정 (자율적)
- 거부 시 팀원은 피드백 기반으로 수정 후 재제출

### Delegate 모드

리드가 코드 작성 없이 **오케스트레이션만** 담당하도록 제한:
- `Shift+Tab`으로 Delegate 모드 전환
- 리드는 팀원 생성, 메시징, 태스크 관리만 수행
- 직접 구현하지 않음

### 팀원과 직접 대화

각 팀원은 완전히 독립적인 Claude Code 세션:

- **In-process 모드**: `Shift+Up/Down`으로 팀원 선택 후 메시지 입력
- **Split panes 모드**: 팀원의 패널 클릭해서 직접 상호작용

### 태스크 할당 및 클레임

공유 태스크 리스트를 통한 조정:

- **태스크 상태**: pending → in progress → completed
- **의존성 관리**: 태스크 A가 완료되기 전까지 태스크 B는 블록됨
- **할당 방식**:
  - 리드가 명시적 할당: "이 태스크를 X 팀원에게 할당"
  - 자율 클레임: 팀원이 자동으로 다음 가능한 태스크 선택

파일 락킹으로 **경쟁 조건 방지** (여러 팀원이 동시에 같은 태스크 클레임 시도 시).

### 팀원 종료 및 정리

```
Ask the researcher teammate to shut down
```

팀원은 승인/거부 가능.

팀 전체 정리:

```
Clean up the team
```

- 공유 팀 리소스 제거
- 활성 팀원이 있으면 실패 (먼저 종료 필요)

---

## 아키텍처

### 구성 요소

| 컴포넌트 | 역할 |
|----------|------|
| **Team Lead** | 팀을 생성하고 팀원을 생성하며 작업을 조율하는 메인 Claude Code 세션 |
| **Teammates** | 각자 할당된 태스크를 수행하는 별도 Claude Code 인스턴스 |
| **Task List** | 팀원들이 클레임하고 완료하는 공유 작업 항목 리스트 |
| **Mailbox** | 에이전트 간 메시지 전달 시스템 |

### 파일 저장 위치

- **팀 설정**: `~/.claude/teams/{team-name}/config.json`
- **태스크 리스트**: `~/.claude/tasks/{team-name}/`

### 권한 설정

- 팀원은 리드의 권한 설정을 상속
- 리드가 `--dangerously-skip-permissions`로 실행하면 모든 팀원도 동일
- 생성 후 개별 팀원 모드 변경 가능 (단, 생성 시점에 개별 설정 불가)

### 컨텍스트 및 커뮤니케이션

**각 팀원은 독립적인 컨텍스트 윈도우**:
- 생성 시 리드와 동일한 프로젝트 컨텍스트 로드 (CLAUDE.md, MCP 서버, 스킬)
- 리드의 대화 히스토리는 **상속되지 않음**
- 리드의 spawn 프롬프트만 수신

**정보 공유 방식**:
- **자동 메시지 전달**: 팀원이 메시지를 보내면 수신자에게 자동 전달
- **아이들 알림**: 팀원이 작업 완료 후 자동으로 리드에게 알림
- **공유 태스크 리스트**: 모든 에이전트가 태스크 상태 확인 및 클레임 가능

**팀원 메시징**:
- `message`: 특정 팀원 1명에게 메시지
- `broadcast`: 모든 팀원에게 동시 전송 (비용이 팀 크기에 비례하므로 신중히 사용)

### 토큰 사용량

Agent Teams는 **단일 세션보다 훨씬 많은 토큰 사용**:
- 각 팀원이 독립적인 컨텍스트 윈도우
- 토큰 사용량은 활성 팀원 수에 비례
- 리서치, 리뷰, 새 기능 개발엔 추가 토큰이 가치 있음
- 일상적인 작업엔 단일 세션이 비용 효율적

---

## 실제 사용 사례

### 1. 병렬 코드 리뷰

단일 리뷰어는 한 번에 한 가지 이슈에 집중하는 경향이 있다. 리뷰 기준을 독립적인 도메인으로 분리하면 **보안, 성능, 테스트 커버리지가 모두 동시에 철저히 검토**된다.

```
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

각 리뷰어가 같은 PR을 보지만 **다른 필터를 적용**. 리드가 모든 발견 사항을 종합.

### 2. 경쟁 가설로 조사

근본 원인이 불명확할 때, 단일 에이전트는 그럴듯한 설명 하나를 찾으면 멈춘다. 프롬프트가 팀원들을 명시적으로 **적대적으로 만듦**: 각자 자신의 이론을 조사하고 **다른 팀원의 이론을 반박**하는 것이 목표.

```
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk to
each other to try to disprove each other's theories, like a scientific
debate. Update the findings doc with whatever consensus emerges.
```

**토론 구조가 핵심**. 순차 조사는 고정 편향(anchoring)에 취약: 한 이론이 탐색되면 이후 조사가 그쪽으로 편향됨. 여러 독립 조사자가 **서로를 반박하려 노력**하면, 살아남은 이론이 실제 원인일 가능성이 훨씬 높다.

### 3. C 컴파일러 구축 (Anthropic 실제 사례)

**프로젝트 개요:**
- **목표**: Linux 커널을 컴파일할 수 있는 Rust 기반 C 컴파일러를 처음부터 작성
- **팀 규모**: 16개 에이전트
- **기간**: 약 2주 (거의 2,000 Claude Code 세션)
- **비용**: $20,000 API 비용
- **결과**: 100,000줄의 컴파일러

**성능:**
- Linux 6.9를 x86, ARM, RISC-V에서 부팅 가능
- QEMU, FFmpeg, SQLite, postgres, redis 컴파일 가능
- GCC torture test suite 99% 통과율
- Doom 컴파일 및 실행 가능

**작동 방식:**

1. **무한 루프 하네스**:
   ```bash
   while true; do
     claude --dangerously-skip-permissions \
       -p "$(cat AGENT_PROMPT.md)" \
       --model claude-opus-X-Y &> "$LOGFILE"
   done
   ```

2. **병렬 실행**:
   - 각 에이전트는 Docker 컨테이너에서 실행
   - bare git repo를 `/upstream`에 마운트
   - 각 에이전트가 로컬 복사본 클론 → 작업 → upstream에 푸시

3. **동기화 알고리즘**:
   - 태스크 "락": `current_tasks/parse_if_statement.txt` 같은 텍스트 파일 생성
   - Git의 동기화로 두 에이전트가 같은 태스크 클레임 방지
   - 작업 완료 → upstream에서 pull → 머지 → 푸시 → 락 제거

4. **팀원 역할 분담**:
   - 일부: 컴파일러 기능 구현
   - 일부: 중복 코드 제거
   - 일부: 컴파일러 자체 성능 개선
   - 일부: 생성 코드 효율성 향상
   - 일부: Rust 코드 품질 향상
   - 일부: 문서화

**교훈:**

- **고품질 테스트 작성**: Claude가 자율적으로 올바른 문제를 해결하도록 테스트 검증기 완벽하게 설계
- **Claude 입장에서 생각**: 컨텍스트 윈도우 오염 최소화, 시간 맹점 해결 (--fast 옵션)
- **병렬화 용이성**: GCC를 온라인 오라클로 사용해 각 에이전트가 다른 파일 작업 가능하도록
- **역할 전문화**: 병렬화가 전문화를 가능하게 함

---

## 베스트 프랙티스

### 1. 팀원에게 충분한 컨텍스트 제공

팀원은 프로젝트 컨텍스트(CLAUDE.md, MCP 서버, 스킬)를 자동 로드하지만, **리드의 대화 히스토리는 상속하지 않음**. Spawn 프롬프트에 태스크별 세부 사항 포함:

```
Spawn a security reviewer teammate with the prompt: "Review the authentication module
at src/auth/ for security vulnerabilities. Focus on token handling, session
management, and input validation. The app uses JWT tokens stored in
httpOnly cookies. Report any issues with severity ratings."
```

### 2. 태스크 크기 적절하게 조절

- **너무 작음**: 조정 오버헤드가 이득을 초과
- **너무 큼**: 팀원이 체크인 없이 너무 오래 작업 → 낭비 위험 증가
- **적절함**: 함수, 테스트 파일, 리뷰 같은 명확한 결과물을 내는 자기 완결적 단위

### 3. 팀원 완료 대기

때때로 리드가 팀원을 기다리지 않고 직접 태스크를 구현하기 시작할 수 있음:

```
Wait for your teammates to complete their tasks before proceeding
```

### 4. 리서치와 리뷰부터 시작

Agent Teams가 처음이라면 **명확한 경계가 있고 코드 작성이 필요 없는** 작업부터 시작:
- PR 리뷰
- 라이브러리 조사
- 버그 조사

병렬 탐색의 가치를 병렬 구현의 조정 문제 없이 경험 가능.

### 5. 파일 충돌 방지

두 팀원이 같은 파일을 편집하면 덮어쓰기 발생. **각 팀원이 다른 파일 세트를 담당**하도록 작업 분할.

### 6. 모니터링 및 조정

팀원의 진행 상황 확인, 효과 없는 접근 방식 수정, 발견 사항을 받는 대로 종합. **팀을 너무 오래 무인 실행**하면 낭비 위험 증가.

### 7. 훅으로 품질 게이트 강제

[Hooks](https://code.claude.com/docs/en/hooks)로 팀원 완료 시 또는 태스크 완료 시 규칙 강제:

- **TeammateIdle**: 팀원이 아이들 상태가 되려 할 때 실행. 코드 2로 종료하면 피드백 전송 및 작업 계속
- **TaskCompleted**: 태스크가 완료 표시되려 할 때 실행. 코드 2로 종료하면 완료 방지 및 피드백 전송

---

## 한계점

Agent Teams는 **실험적(experimental)** 기능:

### 현재 제약 사항

1. **In-process 팀원의 세션 재개 불가**
   - `/resume`, `/rewind`가 in-process 팀원 복원하지 않음
   - 재개 후 리드가 존재하지 않는 팀원에게 메시지 시도 가능
   - 해결: 새 팀원 생성 지시

2. **태스크 상태 지연**
   - 팀원이 완료 표시를 못하는 경우 발생
   - 의존 태스크가 블록됨
   - 해결: 작업 실제 완료 여부 확인 후 수동 업데이트 또는 팀원 독촉

3. **종료가 느릴 수 있음**
   - 팀원이 현재 요청/도구 호출 완료 후 종료
   - 시간이 걸릴 수 있음

4. **세션당 하나의 팀**
   - 리드는 한 번에 하나의 팀만 관리 가능
   - 새 팀 시작 전 현재 팀 정리 필요

5. **중첩 팀 불가**
   - 팀원이 자신의 팀/팀원 생성 불가
   - 리드만 팀 관리 가능

6. **리드 고정**
   - 팀을 생성한 세션이 평생 리드
   - 팀원을 리드로 승격 불가

7. **생성 시 권한 설정**
   - 모든 팀원이 리드의 권한 모드로 시작
   - 생성 후 개별 팀원 모드 변경 가능
   - 생성 시점에 팀원별 권한 설정 불가

8. **Split panes는 tmux 또는 iTerm2 필요**
   - 기본 in-process 모드는 모든 터미널에서 작동
   - VS Code 통합 터미널, Windows Terminal, Ghostty에서 split-pane 미지원

---

## 사용 예시

### 병렬 코드 리뷰

```
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

### 가설 검증 디버깅

```
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk to
each other to try to disprove each other's theories, like a scientific
debate. Update the findings doc with whatever consensus emerges.
```

### 모듈별 병렬 개발

```
Create a team with 4 teammates to refactor these modules in parallel.
Use Sonnet for each teammate.
```

---

## 다음 단계

관련 병렬 작업 및 위임 접근법:

- **경량 위임**: [Subagents](https://code.claude.com/docs/en/sub-agents) - 세션 내에서 리서치/검증용 헬퍼 에이전트 생성 (에이전트 간 조정 불필요한 작업에 적합)
- **수동 병렬 세션**: [Git worktrees](https://code.claude.com/docs/en/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees) - 자동 팀 조정 없이 직접 여러 Claude Code 세션 실행
- **기능 비교**: [Subagent vs Agent Team 비교](https://code.claude.com/docs/en/features-overview#compare-similar-features)

---

## 결론

Claude Code Agent Teams는 AI 에이전트 협업의 새로운 패러다임을 제시한다. 단일 에이전트의 한계를 넘어 **여러 전문가가 협력**하듯 복잡한 문제를 병렬로 탐색하고, 서로 도전하며, 자율적으로 조정할 수 있다.

**언제 사용하는가:**
- 병렬 탐색이 가치를 더하는 복잡한 작업
- 리서치, 리뷰, 디버깅, 크로스 레이어 개발
- 팀원 간 토론과 협력이 필요한 경우

**주의사항:**
- 토큰 비용이 높음 (팀원 수에 비례)
- 조정 오버헤드 존재
- 실험적 기능으로 제약 사항 있음

Nicholas Carlini의 C 컴파일러 프로젝트는 Agent Teams의 잠재력을 보여주는 동시에, **완전 자율 개발의 리스크**도 제시한다. 테스트 통과가 완료를 의미하지 않으며, 인간 검증 없이 소프트웨어를 배포하는 것은 실질적인 우려 사항이다.

2026년 초, 이런 수준의 자율 협업이 가능해진 것은 놀랍고도 불안하다. LLM과 상호작용 스캐폴드의 빠른 발전이 엄청난 양의 새 코드 작성을 가능하게 하며, 긍정적 적용이 부정적 사용을 능가할 것으로 기대되지만, **안전하게 탐색하려면 새로운 전략이 필요**하다.

---

