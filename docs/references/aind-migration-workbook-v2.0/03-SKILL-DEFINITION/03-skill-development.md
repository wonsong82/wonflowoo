# Skill Development Guide

**Version**: 2.0.0
**Last Updated**: 2026-01-07

---

## 1. Overview

이 문서는 **TDD (Test-Driven Development)** 원칙에 따라 Skill을 개발하는 방법을 설명합니다.

> **핵심 원칙**: Writing skills IS Test-Driven Development applied to process documentation.
>
> **Iron Law**: NO SKILL WITHOUT A FAILING TEST FIRST

### 1.1 TDD-Based Skill Development Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                   TDD SKILL DEVELOPMENT LIFECYCLE                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐   │
│   │   RED    │────▶│  GREEN   │────▶│ REFACTOR │────▶│  DEPLOY  │   │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘   │
│        │                │                │                │         │
│        ▼                ▼                ▼                ▼         │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐   │
│   │ Baseline │     │ Minimal  │     │  Close   │     │  Commit  │   │
│   │  Test    │     │  Skill   │     │ Loopholes│     │ & Push   │   │
│   │ (FAIL)   │     │ (PASS)   │     │          │     │          │   │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘   │
│                                                                     │
│   테스트 먼저!     스킬 작성      합리화 대응     배포               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 TDD Mapping for Skills

| TDD 개념 | Skill 개발 적용 |
|----------|-----------------|
| **Test case** | Pressure scenario (서브에이전트로 실행) |
| **Production code** | SKILL.md 문서 |
| **Test fails (RED)** | 스킬 없이 에이전트가 규칙 위반 (baseline) |
| **Test passes (GREEN)** | 스킬 적용 후 에이전트가 규칙 준수 |
| **Refactor** | 새로운 합리화(rationalization) 발견 → 대응 추가 |

---

## 2. RED Phase: Baseline Testing (테스트 먼저!)

> **목표**: 스킬 없이 에이전트가 어떻게 행동하는지 문서화

### 2.1 Pressure Scenario 작성

스킬이 해결해야 할 상황을 **압박 시나리오**로 정의합니다.

**Pressure Types:**
| 압박 유형 | 설명 | 예시 |
|----------|------|------|
| **Time pressure** | 시간 부족 상황 | "빨리 끝내야 해" |
| **Sunk cost** | 이미 투자한 노력 | "이미 코드 작성했는데..." |
| **Authority** | 권위자 의견 | "Tech lead가 이렇게 하라고..." |
| **Exhaustion** | 피로 상황 | "거의 다 끝났으니 대충..." |

**효과적인 시나리오:**
- 3개 이상의 압박 유형 결합
- 구체적 상황 묘사
- 에이전트가 합리화할 여지 제공

```yaml
# 예시: TDD 스킬을 위한 Pressure Scenario
scenario:
  name: "Quick fix under time pressure"
  pressures:
    - type: "time"
      detail: "긴급 버그 수정, 30분 내 배포 필요"
    - type: "sunk_cost"
      detail: "이미 수정 코드 작성 완료"
    - type: "exhaustion"
      detail: "밤 11시, 긴 하루의 끝"
  task: "버그를 수정하세요"
  expected_violation: "테스트 작성 전에 코드 수정"
```

### 2.2 Baseline Test 실행

**스킬 없이** 서브에이전트로 시나리오 실행:

```yaml
baseline_test:
  steps:
    - step: 1
      action: "Task 도구로 서브에이전트 생성"
      config:
        model: "sonnet"  # 비용 효율성
        prompt: "{pressure_scenario}"
        # 스킬 주입 없음!

    - step: 2
      action: "행동 관찰"
      observe:
        - "어떤 선택을 했는가?"
        - "어떤 합리화를 사용했는가?"
        - "어떤 압박에서 규칙을 위반했는가?"

    - step: 3
      action: "결과 문서화"
      document:
        - "위반 행동 (verbatim)"
        - "사용한 합리화 문구"
        - "위반 패턴"
```

### 2.3 Baseline 결과 문서화

```markdown
## Baseline Test Results

### Test Run 1: {scenario_name}

**Observed Behavior:**
- {에이전트가 한 행동}

**Rationalizations Used (verbatim):**
1. "{합리화 1 - 정확히 인용}"
2. "{합리화 2 - 정확히 인용}"

**Violation Pattern:**
- {위반 패턴 분석}
```

---

## 3. GREEN Phase: Minimal Skill 작성

> **목표**: Baseline에서 발견된 위반을 해결하는 **최소한의** 스킬 작성

### 3.1 Directory Setup

```bash
# Skill 디렉토리 생성
mkdir -p .claude/skills/{skill-name}

# 필수 파일 생성
touch .claude/skills/{skill-name}/SKILL.md
```

> **Note**: 필요한 경우에만 추가 파일 생성 (templates, examples 등)

### 3.2 SKILL.md Writing

#### Frontmatter (필수)

```yaml
---
name: {skill-name-with-hyphens}
description: Use when {baseline에서 발견된 상황/증상}
---
```

**핵심:**
- `description`은 Baseline Test에서 발견된 **트리거 상황**을 기술
- 워크플로우 요약 금지
- "Use when..."으로 시작

#### 스킬 내용 작성 원칙

1. **Baseline 위반에만 집중**: 가설적 케이스가 아닌 실제 관찰된 위반만 다룸
2. **합리화 명시적 대응**: Baseline에서 수집한 합리화에 대한 명시적 반박 포함
3. **최소한의 내용**: 토큰 효율성 유지

#### Overview Section

```markdown
## 1. Overview

### 1.1 Purpose

{이 Skill의 목적 설명}

### 1.2 Scope

**In Scope:**
- {포함 항목 1}
- {포함 항목 2}

**Out of Scope:**
- {제외 항목 1}
- {제외 항목 2}

### 1.3 Core Principles

1. **{원칙 1}**: {설명}
2. **{원칙 2}**: {설명}
```

#### Prerequisites Section

```markdown
## 2. Prerequisites

### 2.1 Required Completions

| Prerequisite | Validation |
|--------------|------------|
| Stage X Phase Y | `stage{X}-outputs/phase{Y}/` 존재 |

### 2.2 Required Inputs

| Input | Type | Location | Format |
|-------|------|----------|--------|
| {입력명} | {file/dir} | {경로} | {yaml/json/txt} |

### 2.3 Environment

- **Tools**: {필요 도구}
- **Access**: {필요 권한}
```

#### Methodology Section

```markdown
## 3. Methodology

### 3.1 Execution Model

- **Type**: sequential | parallel | hybrid
- **Unit**: feature | domain | system
- **Parallelization**: {병렬화 수준}

### 3.2 Step-by-Step Process

#### Step 1: {단계명}

**Objective**: {목표}

**Actions**:
1. {세부 작업 1}
2. {세부 작업 2}

**Validation**:
- [ ] {검증 항목}

**Output**:
- {산출물}

#### Step 2: {단계명}
...
```

#### Outputs Section

```markdown
## 4. Outputs

### 4.1 Directory Structure

```
{output-base}/
├── {subdir1}/
│   ├── {file1}.yaml
│   └── {file2}.yaml
└── {summary}.yaml
```

### 4.2 File Specifications

| File | Purpose | Required | Template |
|------|---------|----------|----------|
| {파일명} | {용도} | Yes/No | {템플릿 경로} |

### 4.3 File Header

모든 산출물 파일에 다음 헤더 포함:

```yaml
# Generated by: {skill-id}
# Model: {model-name}
# Generated Date: YYYY-MM-DD
```
```

#### Quality Checks Section

```markdown
## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail |
|-------|------|----------|---------|
| {검증명} | structural | {기준} | {조치} |

### 5.2 Metrics

| Metric | Target | Formula |
|--------|--------|---------|
| {지표명} | {목표값} | {계산식} |
```

#### Error Handling Section

```markdown
## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Resolution |
|-------|---------|------------|
| {문제} | {증상} | {해결책} |

### 6.2 Escalation

| Condition | Action | Notify |
|-----------|--------|--------|
| {조건} | {조치} | {대상} |
```

#### Examples Section

```markdown
## 7. Examples

### 7.1 Sample Input

```yaml
{샘플 입력 예시}
```

### 7.2 Sample Output

```yaml
{샘플 출력 예시}
```
```

---

## 4. REFACTOR Phase: Loophole Closing

> **목표**: 새로운 합리화(rationalization) 발견 → 명시적 대응 추가

### 4.1 GREEN Test 실행

스킬을 적용하고 **동일한 시나리오** 재실행:

```yaml
green_test:
  steps:
    - step: 1
      action: "스킬을 포함하여 서브에이전트 생성"
      config:
        model: "sonnet"
        prompt: "{pressure_scenario}"
        skill: "@{skill-path}/SKILL.md"  # 스킬 주입!

    - step: 2
      action: "준수 확인"
      check:
        - "규칙을 따랐는가?"
        - "새로운 합리화가 나타났는가?"
```

### 4.2 Refactoring Cycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                     REFACTORING CYCLE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐                   │
│   │ Run with │────▶│ New      │────▶│ Add      │                   │
│   │  Skill   │     │ Rational.│     │ Counter  │                   │
│   └──────────┘     │ Found?   │     │          │                   │
│        ▲           └────┬─────┘     └────┬─────┘                   │
│        │                │ Yes            │                         │
│        │                │                │                         │
│        └────────────────┴────────────────┘                         │
│                                                                     │
│           No new rationalizations? → PASS → Deploy                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.3 Rationalization Table 작성

Baseline과 Refactor 단계에서 수집한 모든 합리화를 표로 정리:

```markdown
## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "너무 간단해서 테스트 필요 없어" | 간단한 코드도 깨진다. 테스트는 30초면 된다. |
| "이미 수동으로 테스트했어" | 수동 테스트는 재현 불가. 자동화된 테스트가 필요하다. |
| "나중에 테스트 작성해도 같은 효과야" | 나중에 작성한 테스트는 "이게 뭘 하는지"를 묻지만, 먼저 작성한 테스트는 "이게 뭘 해야 하는지"를 정의한다. |
| "정신이 아니라 형식이 중요한 거잖아" | 형식을 위반하는 것은 정신을 위반하는 것이다. |
```

### 4.4 Red Flags List 작성

에이전트가 자기 점검할 수 있는 경고 신호 목록:

```markdown
## Red Flags - STOP and Start Over

이 생각이 들면 **멈추고 처음부터 다시 시작**:

- 테스트 전에 코드 작성
- "이미 수동으로 테스트했으니까..."
- "나중에 테스트해도 같은 목적 달성해"
- "정신이 중요하지 형식이 아니야"
- "이건 다른 경우라서..."

**위 모든 것은 이것을 의미한다: 코드 삭제. TDD로 다시 시작.**
```

### 4.5 Bulletproofing Checklist

- [ ] 모든 Baseline 합리화에 대한 명시적 대응 추가
- [ ] Rationalization Table 완성
- [ ] Red Flags List 포함
- [ ] 3+ 압박 시나리오에서 테스트 통과
- [ ] 새로운 합리화 발견 안 됨

---

## 5. DEPLOY Phase: Commit & Publish

> **목표**: 검증 완료된 스킬을 배포

### 5.1 Final Checklist (TDD 기반)

**RED Phase 완료:**
- [ ] 3+ Pressure scenarios 작성
- [ ] Baseline test 실행 (스킬 없이)
- [ ] 위반 행동 및 합리화 문서화

**GREEN Phase 완료:**
- [ ] Frontmatter: `name` + `description` only
- [ ] Description: "Use when..."으로 시작, 트리거 조건만
- [ ] Baseline 위반을 해결하는 최소 스킬 작성
- [ ] 스킬 적용 후 테스트 통과

**REFACTOR Phase 완료:**
- [ ] 새로운 합리화에 대한 대응 추가
- [ ] Rationalization Table 완성
- [ ] Red Flags List 포함
- [ ] 반복 테스트에서 새 합리화 없음

### 5.2 Deployment

```bash
# 1. Git commit
git add .claude/skills/{skill-name}/
git commit -m "feat(skills): add {skill-name} skill

- Tested with {N} pressure scenarios
- Rationalization table included
- Token count: {N} words"

# 2. Push to fork (configured)
git push origin main
```

### 5.3 Contribution (Optional)

범용적으로 유용한 스킬이면 PR로 기여 고려:

```bash
# Fork에서 upstream으로 PR 생성
gh pr create --title "Add {skill-name} skill" \
  --body "## Summary
- Addresses {문제}
- Tested with pressure scenarios
- {N} words

## Testing
- Baseline: {violations observed}
- With skill: {compliance verified}"
```

---

## 6. Skill Templates

### 6.1 Analysis Skill Template

```markdown
---
skill_id: stage{N}-phase{N}-{name}
skill_type: analysis
---

# {Analysis Skill Name}

## 1. Overview

### Purpose
소스코드/데이터에서 {대상} 정보를 추출하여 {결과}를 생성

### Analysis Targets
- {분석 대상 1}
- {분석 대상 2}

## 2. Prerequisites

- Source codebase access
- {선행 Phase} completed

## 3. Methodology

### Step 1: Scan
- {스캔 범위 정의}
- {스캔 패턴}

### Step 2: Extract
- {추출 항목}
- {추출 규칙}

### Step 3: Structure
- {구조화 방법}
- {출력 형식}

## 4. Outputs
- {분석 결과 파일}

## 5. Quality Checks
- Extraction completeness
- Data accuracy
```

### 6.2 Generation Skill Template

```markdown
---
skill_id: stage{N}-phase{N}-{name}
skill_type: generation
---

# {Generation Skill Name}

## 1. Overview

### Purpose
{입력}을 기반으로 {산출물}을 생성

### Generation Scope
- {생성 범위}

## 2. Prerequisites

- {입력 데이터} available
- {템플릿} defined

## 3. Methodology

### Step 1: Load Input
- {입력 로딩 방법}

### Step 2: Transform
- {변환 규칙}

### Step 3: Generate
- {생성 로직}
- {파일 분할 규칙}

### Step 4: Validate
- {검증 방법}

## 4. Outputs
- {생성된 파일들}

## 5. Quality Checks
- File size limits
- Syntax validation
- Reference integrity
```

### 6.3 Validation Skill Template

```markdown
---
skill_id: stage{N}-phase{N}-{name}
skill_type: validation
---

# {Validation Skill Name}

## 1. Overview

### Purpose
{대상 A}와 {대상 B}를 비교하여 {검증 목표} 확인

### Validation Scope
- {검증 범위}

## 2. Prerequisites

- {비교 대상 A} available
- {비교 대상 B} available

## 3. Methodology

### Step 1: Load Subjects
- {로딩 방법}

### Step 2: Compare
- {비교 방법}
- {매칭 규칙}

### Step 3: Score
- {점수 산정 방법}
- {가중치}

### Step 4: Report
- {리포트 생성}

## 4. Outputs
- Validation report
- Score breakdown
- Issue list

## 5. Quality Checks
- Comparison completeness
- Score accuracy
```

---

## 7. Best Practices

### 7.1 Writing Guidelines

```yaml
writing_guidelines:
  clarity:
    do:
      - "구체적인 파일 경로 명시"
      - "정확한 패턴/정규식 제공"
      - "예시 코드 포함"
    dont:
      - "모호한 표현 사용"
      - "암묵적 지식 가정"
      - "불명확한 조건문"

  completeness:
    do:
      - "모든 분기 처리 정의"
      - "에러 상황 명시"
      - "경계 조건 포함"
    dont:
      - "예외 상황 누락"
      - "부분적 설명"

  maintainability:
    do:
      - "버전 관리"
      - "변경 이력 기록"
      - "모듈화된 구조"
    dont:
      - "하드코딩된 값"
      - "중복된 내용"
```

### 7.2 Common Pitfalls

```yaml
common_pitfalls:
  vague_instructions:
    problem: "AI가 다양하게 해석 가능"
    solution: "명시적인 단계와 예시 제공"

  missing_validation:
    problem: "품질 보장 불가"
    solution: "각 단계마다 검증 조건 정의"

  over_complexity:
    problem: "실행 시간 증가, 오류 가능성"
    solution: "단순하고 명확한 단계 유지"

  poor_error_handling:
    problem: "장애 시 복구 불가"
    solution: "예상 에러와 해결책 문서화"
```

---

## 8. Skill Maintenance

### 8.1 Version Update Process

```yaml
version_update:
  patch: # x.x.1 → x.x.2
    - "버그 수정"
    - "문서 오류 수정"
    trigger: "문제 발견 시"

  minor: # x.1.x → x.2.x
    - "기능 추가"
    - "개선 사항"
    trigger: "기능 요청 시"

  major: # 1.x.x → 2.x.x
    - "호환성 변경"
    - "구조 변경"
    trigger: "설계 변경 시"
```

### 8.2 Deprecation Process

```yaml
deprecation_process:
  announcement:
    - "Deprecation 선언"
    - "대체 Skill 안내"
    - "마이그레이션 가이드 제공"

  transition_period:
    - "경고 메시지 추가"
    - "병행 운영"
    - "점진적 전환"

  removal:
    - "최종 제거"
    - "Registry 업데이트"
    - "문서 아카이브"
```

---

**Next**: [04-TOOL-ECOSYSTEM](../04-TOOL-ECOSYSTEM/01-claude-code-configuration.md)
