# AIND Migration 강사용 강의안

**Version**: 1.0.0
**기준 커리큘럼**: CURRICULUM_v0.6-draft.md

---

## 교육 핵심 메시지

```
"一騎當千(일기당천)" - Agentic Odyssey

한 명의 개발자가 AI와 협업하여
천 명이 할 일을 해낼 수 있는 역량을 기른다.
```

**3가지 핵심 태도 변화 유도**:
1. 코드 직접 변환 → **명세 우선 사고**
2. 수작업 분석 → **AI 활용 자동화**
3. 사후 테스트 → **내장된 품질 게이트**

---

## Module 1: 방법론 전체 소개 + 환경 설정

### Session 1.1: 레거시 마이그레이션의 도전과제

**핵심 전달 포인트**:
- 레거시 마이그레이션 실패율 70% 이상 (업계 통계 인용)
- 실패 원인 3대 요소: 암묵적 지식, 누락된 기능, 테스트 부족
- "예전에 되던 게 안 된다" = 비즈니스 신뢰 상실

**강조할 질문**:
> "여러분의 레거시 시스템에서 '이건 왜 이렇게 되어 있지?'라고
> 물었을 때 대답할 수 있는 사람이 몇 명인가요?"

**토론 유도**:
- 참가자 경험 공유 시 "가장 힘들었던 점" 집중
- Pain Point를 화이트보드에 정리 → 교육 중 해결책 연결

---

### Session 1.2: AIND Migration 방법론 철학

**핵심 전달 포인트**:

| 원칙 | 키워드 | 강조 포인트 |
|------|--------|------------|
| Specification-First | **명세가 먼저** | 코드 변환 X, 명세 추출 후 생성 |
| Bidirectional Validation | **양방향 검증** | 정방향만으론 누락 발생 |
| AI + Human | **AI가 리드, Human이 검증** | AI 맹신 X, 협업 모델 |
| Quality Over Speed | **품질 우선** | 빠른 것보다 정확한 것 |

**핵심 다이어그램** (칠판에 그리기):
```
Legacy Code → [Spec 추출] → Specification → [코드 생성] → New Code
                                 ↑                          ↓
                                 └────── [검증] ────────────┘
```

**예상 질문**:
- Q: "명세 추출하는 데 시간이 더 걸리지 않나요?"
- A: "명세 없이 변환하면 나중에 누락 찾느라 10배 시간 소요"

---

### Session 1.3: 5-Stage 모델 상세 이해

**핵심 전달 포인트** - 각 Stage의 핵심 질문:

| Stage | 핵심 질문 | 한 줄 설명 |
|-------|----------|-----------|
| 1. Discovery | What exists? | 있는 것 다 찾기 |
| 2. Validation | Is it complete? | 빠진 것 없나 확인 |
| 3. Preparation | How to build? | 어떻게 만들지 설계 |
| 4. Generation | Build it! | 실제로 만들기 |
| 5. Assurance | Does it work? | 제대로 되나 검증 |

**강조 포인트**:
- Stage 1-2가 전체의 **60% 노력** 차지
- "준비 없이 생성하면 실패한다"
- Phase Gate = 품질 관문, 통과 못하면 다음 단계 진입 불가

**워크샵 가이드**:
- 팀별로 5-Stage 다이어그램 직접 그리게 하기
- "우리 프로젝트에 적용하면?" 토론

---

### Session 1.4: 실습 환경 설정

**체크포인트**:
- [ ] Claude Code 설치 완료
- [ ] `claude --version` 정상 출력
- [ ] API 키 설정 확인
- [ ] 레거시 코드베이스 클론 완료
- [ ] 기본 명령어 테스트 (`claude "hello"`)

**자주 발생하는 문제**:
| 문제 | 해결 |
|------|------|
| npm 권한 오류 | `sudo` 또는 nvm 사용 |
| API 키 오류 | 환경변수 설정 확인 |
| 네트워크 차단 | 방화벽 HTTPS 443 확인 |

---

### Session 1.5: 워크북 구조 안내

**7개 섹션 한 줄 요약**:

| 섹션 | 핵심 역할 |
|------|----------|
| 01-ASSESSMENT | 할 수 있나? (Go/No-Go) |
| 02-WORKFLOW-DESIGN | 어떻게 할까? (설계) |
| 03-SKILL-DEFINITION | AI한테 뭐라고 시킬까? (지시) |
| 04-TOOL-ECOSYSTEM | 뭘로 할까? (도구) |
| 05-EXECUTION-PATTERNS | 어떻게 돌릴까? (실행) |
| 06-QUALITY-ASSURANCE | 잘 됐나? (검증) |
| 07-CASE-STUDIES | 남들은 어떻게 했나? (사례) |

---

## Module 2: Assessment (1) - 레거시 분석 기초

### Session 2.1: Assessment 개요

**핵심 전달 포인트**:
- Assessment = **"할 수 있나?" 판단**
- 14개 Task는 체크리스트, 빠뜨리면 나중에 문제
- **"모르면 못 바꾼다"** - 현황 파악이 첫걸음

**14개 Assessment Task 분류**:
```
[Codebase Profiling]     ASSESS-001~003
[Domain Decomposition]   ASSESS-004~006
[Component Analysis]     ASSESS-007~010
[Technical Debt]         ASSESS-011~012
[External Dependencies]  ASSESS-013~014
```

---

### Session 2.2: Codebase Profiling 실습

**데모 스크립트**:
```bash
# 파일 수
find . -name "*.java" | wc -l

# LOC
cloc --yaml src/

# 패키지 구조
find . -name "*.java" -exec dirname {} \; | sort -u | head -20
```

**실습 체크포인트**:
- [ ] 총 파일 수 확인
- [ ] LOC 측정 완료
- [ ] 아키텍처 패턴 식별 (MVC? Layered?)
- [ ] 프레임워크 목록 작성

---

### Session 2.3: Domain Decomposition

**핵심 전달 포인트**:
- 도메인 = 독립적으로 마이그레이션 가능한 단위
- 패키지 구조에서 도메인 추출 (보통 2-3레벨)
- **P0-P3 우선순위**: P0 먼저 해야 P1 가능

**우선순위 분류 기준**:

| Priority | 기준 | 예시 |
|----------|------|------|
| P0-Foundation | 모두가 의존 | common, framework |
| P1-Hub | 많이 참조됨 | CM (공통코드) |
| P2-Core | 핵심 업무 | PA, MM, SC |
| P3-Supporting | 보조 기능 | QM, BS |

---

### Session 2.4: Component Analysis

**핵심 전달 포인트**:
- 4개 레이어 분석: Controller → Service → Mapper → VO
- **엔드포인트 수 = 작업량 추정의 기초**
- 복잡한 Service = 주의 대상

**분석 명령어 예시**:
```bash
# 엔드포인트 추출
grep -rn "@RequestMapping" --include="*.java" | wc -l

# 서비스 클래스 수
find . -name "*Service.java" | wc -l

# Mapper XML 수
find . -name "*Mapper.xml" | wc -l
```

---

## Module 3: Assessment (2) - 복잡도 및 실현 가능성

### Session 3.1: Technical Debt

**핵심 전달 포인트**:
- Dead Code = 분석 시간 낭비 요소
- 복잡도 높은 코드 = 마이그레이션 리스크
- **"부채가 많으면 이사비용도 비싸다"**

**주의 대상 패턴**:
| 패턴 | 위험도 | 이유 |
|------|--------|------|
| Stored Procedure | HIGH | DB 종속, 로직 숨김 |
| Dynamic SQL | HIGH | 분석 어려움 |
| Custom Framework | HIGH | 문서 부족 |
| 순환 의존성 | MEDIUM | 순서 결정 어려움 |

---

### Session 3.2: Complexity Estimation

**복잡도 점수 계산 공식** (예시):
```
Score = (SP비율 × 30) + (동적SQL비율 × 25) +
        (외부연동수 × 3) + (커스텀FW의존도 × 20)

HIGH:   Score > 70
MEDIUM: 40 < Score <= 70
LOW:    Score <= 40
```

**워크샵 가이드**:
- 실습 시스템 점수 직접 산출
- 팀별 결과 비교 → 왜 다른지 토론

---

### Session 3.3: Feasibility Matrix

**Go/No-Go 결정 프레임워크**:

| 조건 | Go | No-Go |
|------|-----|-------|
| 기술적 실현 가능 | O | X |
| 리소스 확보 | O | X |
| 리스크 수용 가능 | O | X |
| ROI 양호 | O | X |

**강조 포인트**:
- **No-Go도 좋은 결정** - 무모한 진행보다 낫다
- 부분 마이그레이션 옵션 검토

---

### Session 3.4: Assessment Report 작성

**보고서 필수 섹션**:
1. Executive Summary (1페이지)
2. Codebase Profile
3. Domain Analysis
4. Complexity Assessment
5. Risk Analysis
6. **Recommendation** (Go/No-Go + 근거)

---

## Module 4: Workflow Design (1) - Stage-Phase 모델

### Session 4.1: Stage-Phase 계층 구조

**4-Level 계층 암기법**:
```
Project → Stage → Phase → Task → Skill
(프로젝트) (목적)  (작업)  (실행)  (지시)

"프스피태스" 또는 "큰 → 작은"
```

**Sequencing Rules 핵심**:
1. Phase는 순차 (Phase 1 → Phase 2 → ...)
2. Stage 사이에 Gate
3. Task는 병렬 가능
4. Phase Gate 통과해야 진행

---

### Session 4.2: 5-Stage 모델 심화

**Stage별 Phase 수**:
| Stage | Phase 수 | 핵심 산출물 |
|-------|----------|------------|
| Discovery | 3 | Feature Specs |
| Validation | 4 | Validated Specs |
| Preparation | 6 | Architecture |
| Generation | 4 | Source Code |
| Assurance | 5 | Quality Report |

---

### Session 4.3: Phase Design Patterns

**5가지 Phase 유형 암기**:
```
I-A-G-V-I
Inventory → Analysis → Generation → Validation → Integration
(수집)      (분석)     (생성)       (검증)       (통합)
```

---

### Session 4.4: Task Lifecycle & Phase Gate

**Task 상태 전이**:
```
PENDING → ASSIGNED → IN_PROGRESS → VALIDATING → COMPLETED
                          ↓              ↓
                       FAILED        REJECTED
                          ↓              ↓
                       RETRYING ←────────┘
```

**Phase Gate 핵심**:
- Gate 조건 미충족 → 다음 Phase 진입 불가
- **자동 커밋** → 품질 보장
- 엄격 모드: 하나라도 실패 시 전체 중단

---

### Session 4.5: Output Structure 설계

**디렉토리 구조 패턴**:
```
{specs_root}/
├── stage1-outputs/
│   ├── phase1/
│   ├── phase2/
│   └── phase3/
│       └── {Priority}/{Domain}/FEAT-XX-NNN/
```

---

## Module 5: Workflow Design (2) - 커스터마이제이션

### Session 5.1: Workflow Customization

**커스터마이제이션 포인트**:

| 무엇을 | 언제 |
|--------|------|
| Stage 스킵 | Rehosting (Stage 4 불필요) |
| Stage 병합 | 소규모 프로젝트 |
| Phase 추가 | 보안 검토, 성능 테스트 |
| Gate 기준 변경 | 프로젝트 특성에 맞춤 |

---

### Session 5.2: Decision Trees

**주요 결정 포인트**:
1. "이 Stage를 할까?" → 프로젝트 유형에 따라
2. "이 Phase를 스킵할까?" → 이미 있는 산출물에 따라
3. "병렬로 돌릴까?" → 의존성에 따라
4. "실패 시 어떻게?" → Remediation 전략

---

### Session 5.4: config.yaml 작성

**config.yaml 핵심 섹션**:
```yaml
project:
  name: "my-migration"
  specs_root: "work/specs"

stages:
  enabled: [1, 2, 3, 4, 5]

phase_gates:
  enabled: true
  strict_mode: true

execution:
  max_parallel_tasks: 10
  retry_on_failure: 3
```

---

## Module 6: Skill Definition (1) - 스킬 구조

### Session 6.1: Skill 개요

**Skill = AI에게 주는 구조화된 지시서**

**3가지 특성**:
| 특성 | 의미 |
|------|------|
| Deterministic | 같은 입력 → 같은 출력 |
| Self-contained | 하나의 문서로 완결 |
| Composable | 다른 Skill과 조합 가능 |

**SKILL.md 7개 필수 섹션**:
```
1. Overview       - 뭘 하는 Skill인가
2. Prerequisites  - 뭐가 있어야 하나
3. Methodology    - 어떻게 하나
4. Outputs        - 뭘 만드나
5. Quality Checks - 어떻게 검증하나
6. Error Handling - 문제 시 어떻게
7. Examples       - 예시
```

---

### Session 6.2-6.4: Skill 섹션 상세

**Overview 작성 팁**:
- Purpose: "이 Skill은 ~를 수행한다"
- Scope: In/Out 명확히
- 모호함 금지

**Methodology 작성 팁**:
- Step-by-Step으로 명확하게
- Decision Point 명시
- "적절히", "필요시" 같은 모호한 표현 금지

**Anti-pattern 예시**:
| Bad | Good |
|-----|------|
| "적절히 분석하세요" | "각 Controller의 @RequestMapping을 추출하세요" |
| "필요하면 검증하세요" | "YAML 문법 오류 검증 후 통과 시 진행" |

---

## Module 7: Skill Definition (2) - 스킬 개발 실습

### Session 7.2: Skill Development Best Practices

**3대 원칙**:
1. **Clarity** - 모호함 제거
2. **Completeness** - 모든 분기 처리
3. **Maintainability** - 버전 관리

**체크리스트**:
- [ ] 모든 Step에 완료 조건이 있는가?
- [ ] 예외 상황이 모두 정의되어 있는가?
- [ ] 출력 형식이 명확한가?

---

### Session 7.3-7.4: Skill 작성 실습

**실습 가이드**:
- 팀당 1개 Skill 완성 목표
- 7개 섹션 모두 작성
- 실제 테스트까지 수행

**리뷰 포인트**:
- 모호한 표현 있는지
- Step 누락 없는지
- 에러 처리 충분한지

---

## Module 8: Tool Ecosystem + Execution Patterns

### Session 8.1: Claude Code 고급 설정

**모델 선택 가이드**:
| 모델 | 용도 | 비용 |
|------|------|------|
| Opus | 복잡한 분석, 코드 생성 | 높음 |
| Sonnet | 일반 작업, 균형 | 중간 |
| Haiku | 단순 작업, 빠른 응답 | 낮음 |

**CLAUDE.md 핵심 설정**:
```markdown
# Project Context
이 프로젝트는 레거시 마이그레이션입니다.

# Skill Location
.claude/skills/ 디렉토리의 Skill을 참조하세요.
```

---

### Session 8.3-8.4: Batch & Parallel Execution

**배치 처리 핵심**:
- 체크포인팅 = 중단 시 재시작 가능
- 진행률 추적 필수

**병렬 실행 핵심**:
- 의존성 없는 Task만 병렬화
- 리소스 한도 설정 (max_parallel_tasks)
- 동기화 포인트 = Phase Gate

---

## Module 9: Quality Assurance + Case Studies

### Session 9.1: Validation Framework

**4-Layer 검증 가중치**:
```
SQL Equivalence:   40%  ← 가장 중요
API Equivalence:   25%
Business Logic:    20%
Data Model:        15%
```

**통과 기준**:
- 총점 70점 이상
- Critical 이슈 0건

---

### Session 9.3: Case Study - hallain_tft

**규모 강조**:
| 항목 | 수치 |
|------|------|
| Java 파일 | 8,377개 |
| API 엔드포인트 | 5,864개 |
| Features | 912개 |
| 도메인 | 11개 |

**성공 요인**:
1. Assessment 철저히 수행
2. Stage-Phase 엄격 준수
3. Phase Gate 통과율 모니터링
4. 병렬 실행으로 속도 확보

**교훈**:
- "명세 없이 시작했으면 3배 걸렸을 것"
- "Phase Gate 덕분에 품질 유지"

---

## Module 10: Mini Project + 발표

### Session 10.1: Mini Project 가이드

**최소 요구사항**:
- [ ] Assessment Report (축소 버전)
- [ ] config.yaml 작성
- [ ] Skill 1개 이상 적용
- [ ] Stage 1 Feature 1개 완료

**평가 기준**:
| 항목 | 배점 |
|------|------|
| Assessment 품질 | 25% |
| Workflow 설계 | 25% |
| Skill 작성 | 25% |
| 발표 | 25% |

---

### Session 10.3: 발표 가이드

**발표 구조 제안**:
1. 대상 레거시 소개 (2분)
2. Assessment 결과 (3분)
3. Workflow 설계 (3분)
4. Skill 적용 (3분)
5. 결과 및 교훈 (4분)
6. Q&A (5분)

---

## 강사 체크리스트

### 교육 시작 전
- [ ] 실습 환경 테스트 완료
- [ ] API 키 동작 확인
- [ ] 네트워크 연결 확인
- [ ] 백업 자료 준비

### 각 모듈 종료 시
- [ ] 핵심 개념 요약
- [ ] 질문 시간 확보
- [ ] 산출물 제출 확인
- [ ] 다음 모듈 예고

### 교육 종료 시
- [ ] 전체 내용 복습
- [ ] 실무 적용 가이드
- [ ] 추가 학습 자료 안내
- [ ] 피드백 수집

---

## 예상 질문 & 답변

### 방법론 관련

**Q: AI가 실수하면 어떡하나요?**
A: 그래서 Phase Gate가 있습니다. AI 결과를 무조건 믿지 않고,
   각 Phase마다 검증합니다. Human Review도 포함됩니다.

**Q: 작은 프로젝트에도 이 방법론이 필요한가요?**
A: 규모에 따라 Stage를 병합하거나 스킵할 수 있습니다.
   하지만 Assessment와 Validation은 규모와 관계없이 권장합니다.

**Q: 기존에 문서화가 안 되어 있으면요?**
A: 그래서 Stage 1 Discovery가 존재합니다.
   AI가 코드에서 명세를 추출합니다.

### 실무 적용 관련

**Q: 우리 회사에 바로 적용할 수 있나요?**
A: 이 교육 후 Mini Project 수준은 바로 가능합니다.
   대규모 적용은 파일럿 프로젝트로 시작하세요.

**Q: 어느 정도 효과가 있나요?**
A: hallain_tft 사례에서 수작업 대비 60% 시간 절감,
   누락률 5% 미만을 달성했습니다.

---

**Document Version**: 1.0.0
**Created**: 2025-12-18
**Author**: Choi | Build Center