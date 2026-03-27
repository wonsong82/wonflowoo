# Claude Code 활용 방식: 계획과 실행의 분리

> **출처**: [GeekNews](https://news.hada.io/topic?id=26907)

---

## 핵심 요약

9개월간 Claude Code를 사용하며 정립한 워크플로우. 핵심 원칙은 **"계획 승인 전에는 코드를 쓰게 하지 않는다"**. AI의 실행력과 인간의 판단력을 분리해 복잡한 시스템에서도 안정적이고 일관된 결과를 얻는다.

---

## 전체 워크플로우

**Research → Plan → Annotation → Todo List → Implementation → Feedback**

---

## Phase 1: Research

- Claude에게 코드베이스를 "깊이 읽고(detailed, intricacies)" 분석하도록 지시
- 결과를 반드시 `research.md`로 기록
- 이 문서는 Claude의 이해도를 검증하는 리뷰 표면 역할
- 잘못된 리서치 = 잘못된 계획 + 구현 → 가장 비용이 큰 실패 요인을 사전에 차단
- 예방 가능한 문제: 캐싱 레이어 무시, ORM 규칙 미반영, 중복 로직 생성 등

---

## Phase 2: Planning

- `plan.md` 작성: 실제 코드 스니펫, 수정 파일 경로, 트레이드오프 포함
- 내장 plan 모드 대신 직접 관리 가능한 markdown 파일 사용
- 오픈소스 참조 구현을 함께 제공하면 계획 품질이 크게 향상
- 계획 문서보다 중요한 것은 이후의 Annotation 사이클

---

## Annotation Cycle (핵심)

- `plan.md`를 열어 직접 인라인 주석 추가
  - "이건 PATCH여야 함", "캐싱 불필요", "visibility 필드는 리스트 단위로 이동" 등
- Claude에게: "주석 반영해서 문서 갱신해, **아직 구현하지 마**"
- 이 사이클을 **1~6회 반복**
- `"don't implement yet"` 명령으로 조기 실행 방지
- markdown 문서 = 공유 가능한 상태(state), 대화형 지시보다 명확하고 구조적
- 반복을 통해 일반적 계획 → 실제 시스템에 맞는 정밀한 사양으로 진화

### Todo List 생성
- 구현 전 세부 작업 목록 추가
- Claude가 완료 항목을 표시 → 장시간 세션에서도 상태 파악 용이

---

## Phase 3: Implementation

- 모든 결정 완료 후 표준화된 프롬프트로 실행:
  - "모든 태스크를 완료할 때까지 멈추지 말 것"
  - "불필요한 주석 금지"
  - "any/unknown 타입 금지"
  - "지속적 타입체크 수행"
- 이 단계는 순수한 기계적 실행, 창의적 판단은 이미 완료
- "don't implement yet" 규칙이 핵심 안전장치

---

## Feedback During Implementation

- 피드백은 짧고 명확하게: "이 함수 누락됨", "admin 앱으로 이동"
- 프론트엔드 수정 시 단문 지시나 스크린샷 활용: "wider", "2px gap"
- 기존 코드 참조로 일관된 UI/UX 유지
- 잘못된 방향 → `git revert` 후 범위 축소 재시도 (점진적 수정보다 효과적)

---

## Staying in the Driver's Seat

- Claude에게 완전한 자율권을 주지 않음, 최종 결정은 항상 사람
- 제안 중 일부만 선택, 수정, 삭제, 기술 선택 재정의 가능
  - "첫 번째는 Promise.all 사용", "네 번째, 다섯 번째는 무시"
- Claude = 기계적 실행 / 사람 = 판단과 우선순위

---

## Single Long Sessions

- 리서치부터 구현까지 하나의 긴 세션에서 연속 수행
- auto-compaction으로 충분한 문맥 유지
- `plan.md`는 세션 내내 완전한 형태로 보존

---

## 핵심 원칙 요약

> **"깊이 읽고, 계획을 쓰고, 주석으로 다듬은 뒤, 한 번에 실행하라."**

- **Research** → 무지한 변경을 막는다
- **Plan** → 잘못된 변경을 막는다
- **Annotation** → 인간의 판단을 주입한다
- **Implementation** → 모든 결정이 확정된 후 자동화된 절차로 수행

---

