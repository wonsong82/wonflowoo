# Skill Definition Framework

**Version**: 2.0.0
**Last Updated**: 2026-01-07
**Purpose**: AI-Driven Migration 프로젝트를 위한 범용 Skill 정의 프레임워크

---

## 1. Overview

### 1.1 What is a Skill?

Skill은 AI 에이전트가 특정 작업을 수행하기 위한 **구조화된 지시사항**입니다. Migration 프로젝트에서 Skill은 다음과 같은 계층 구조 내에서 동작합니다.

```
┌────────────────────────────────────────────────────────────────┐
│                         SKILL HIERARCHY                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   Stage (목적 중심)                                             │
│     └─ Phase (작업 단위)                                        │
│          └─ Task (실행 단위)                                    │
│               └─ Skill (AI 지시사항) ◄─── 이 문서의 범위         │
│                                                                │
│   Example:                                                     │
│   Stage 1: Discovery                                           │
│     └─ Phase 1.1: Feature Inventory                            │
│          └─ Task: FEAT-PA-001-INV                              │
│               └─ Skill: s1-01-discovery-feature-inventory      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 1.2 Skill Characteristics

모든 Skill은 다음 세 가지 특성을 가져야 합니다:

| 특성 | 설명 | 구현 방법 |
|------|------|-----------|
| **Deterministic** | 동일 입력 → 일관된 출력 | 명시적 단계, 검증 조건, 출력 형식 정의 |
| **Self-Contained** | 단일 문서로 작업 수행 가능 | 목적, 선행조건, 실행단계, 출력명세, 품질기준 포함 |
| **Composable** | 다른 Skill과 조합 가능 | 공통 템플릿, 표준 입출력 형식 |

### 1.3 Skill Types

```yaml
skill_types:
  analysis:
    purpose: "소스코드/데이터 분석 및 정보 추출"
    characteristics:
      input: "소스코드, 기존 문서, 데이터"
      output: "분석 결과, 구조화된 데이터"
      processing: "읽기 중심 (Read-centric)"
    examples:
      - "Feature inventory extraction"
      - "Dependency analysis"
      - "Protocol analysis"

  generation:
    purpose: "분석 결과 기반 산출물 생성"
    characteristics:
      input: "분석 데이터, 템플릿, 명세"
      output: "문서, 스펙, 코드"
      processing: "쓰기 중심 (Write-centric)"
    examples:
      - "Specification generation"
      - "Code generation"
      - "Test generation"

  validation:
    purpose: "품질 검증 및 일치성 확인"
    characteristics:
      input: "비교 대상 A, 비교 대상 B"
      output: "검증 보고서, 점수, Gap 목록"
      processing: "비교/검증 중심 (Comparison-centric)"
    examples:
      - "Structural comparison"
      - "Functional validation"
      - "Contract testing"

  transformation:
    purpose: "형식 변환 또는 표준화"
    characteristics:
      input: "원본 데이터"
      output: "변환된 데이터 (동일 의미, 다른 형식)"
      processing: "변환 중심 (Conversion-centric)"
    examples:
      - "Spec standardization"
      - "Code formatting"
      - "Schema migration"

  orchestration:
    purpose: "작업 흐름 제어 및 조율"
    characteristics:
      input: "작업 목록, 상태 정보"
      output: "실행 결과, 진행 상황"
      processing: "제어 중심 (Control-centric)"
    examples:
      - "Phase gate validation"
      - "Task dispatching"
      - "Rollback execution"
```

---

## 2. Skill File Structure

### 2.1 Directory Layout

```
.claude/skills/
├── {stage}/                          # Stage별 디렉토리
│   ├── {skill-name}/                 # 개별 Skill 디렉토리
│   │   ├── SKILL.md                  # Main skill document
│   │   ├── templates/                # Output templates
│   │   │   ├── output-template.yaml
│   │   │   └── report-template.md
│   │   ├── examples/                 # Reference examples
│   │   │   └── sample-output.yaml
│   │   └── validation/               # Validation rules
│   │       └── quality-checks.yaml
│   └── ...
├── orchestration/                    # Cross-cutting skills
│   ├── phase-gate/
│   ├── stage-gate/
│   └── ...
├── common/                           # Shared resources
│   ├── templates/
│   └── utilities/
└── templates/                        # Global templates
    └── skill-template.md
```

### 2.2 Naming Conventions

> **권장 명명 규칙**: `s{stage}-{phase}-{workflow}-{action}`
>
> 이 패턴은 알파벳순 정렬 시 Stage→Phase 순서로 나열되며, ID로 빠른 검색이 가능합니다.

| 구분 | 패턴 | 예시 |
|------|------|------|
| **Skill Directory** | `s{stage}-{phase}-{workflow}-{action}/` | `s1-01-discovery-feature-inventory/` |
| **Main File** | `SKILL.md` | 모든 skill의 메인 문서 |
| **Skill Name** | `s{stage}-{phase}-{workflow}-{action}` | `s1-01-discovery-feature-inventory` |
| **Orchestration** | `x-{phase}-orchestration-{action}` | `x-01-orchestration-phase-gate` |

**예시:**
- `s1-01-discovery-feature-inventory` (Stage 1, Phase 1)
- `s1-02-discovery-miplatform-protocol` (Stage 1, Phase 2)
- `s2-01-validation-source-inventory` (Stage 2, Phase 1)
- `x-03-orchestration-task-dispatch` (Cross-cutting, Phase 3)

### 2.3 Frontmatter Schema

모든 SKILL.md는 다음 frontmatter로 시작해야 합니다:

```yaml
---
name: {skill-name-with-hyphens}
description: Use when {specific triggering conditions and symptoms}
---
```

| 필드 | 필수 | 설명 | 규칙 |
|------|------|------|------|
| `name` | Yes | Skill 고유 이름 | 문자, 숫자, 하이픈만 (특수문자 금지) |
| `description` | Yes | 트리거 조건 | "Use when..."으로 시작, 워크플로우 요약 금지 |

> **중요**: Frontmatter는 **최대 1024자**입니다.

### 2.4 CSO (Claude Search Optimization)

`description` 필드는 Claude가 스킬을 발견하고 로드할지 결정하는 핵심 요소입니다.

**규칙:**
1. **"Use when..."으로 시작** - 트리거 조건 명시
2. **워크플로우 요약 금지** - 워크플로우를 요약하면 Claude가 전체 스킬을 읽지 않고 description만 따라감
3. **구체적 증상/상황 포함** - 에러 메시지, 증상, 상황 키워드 포함
4. **3인칭 작성** - 시스템 프롬프트에 주입됨

```yaml
# ❌ 나쁜 예시: 워크플로우 요약 포함
description: Use when executing plans - dispatches subagent per task with code review between tasks

# ❌ 나쁜 예시: 너무 추상적
description: For async testing

# ✅ 좋은 예시: 트리거 조건만
description: Use when executing implementation plans with independent tasks in the current session

# ✅ 좋은 예시: 구체적 증상 포함
description: Use when tests have race conditions, timing dependencies, or pass/fail inconsistently
```

### 2.5 Token Efficiency

스킬은 컨텍스트 윈도우를 소비하므로 토큰 효율성이 중요합니다.

**단어 수 목표:**
| 스킬 유형 | 목표 | 비고 |
|----------|------|------|
| getting-started workflows | <150 words | 모든 대화에 로드됨 |
| 자주 로드되는 스킬 | <200 words | 빈번하게 참조됨 |
| 일반 스킬 | <500 words | 필요 시 로드 |

**압축 기법:**
- 세부사항은 `--help` 참조로 대체
- 다른 스킬 cross-reference 활용
- 예시는 최소화 (1개의 좋은 예시 > 5개의 평범한 예시)
- 중복 제거

---

## 3. SKILL.md Structure

### 3.1 Required Sections (7 Sections)

```markdown
# {Skill Name}

## 1. Overview
[목적, 범위, 핵심 원칙, 관계]

## 2. Prerequisites
[선행 조건, 필수 입력, 의존성]

## 3. Methodology
[단계별 실행 방법, 결정 포인트]

## 4. Outputs
[산출물 명세, 파일 구조, 헤더 형식]

## 5. Quality Checks
[자동 검증, 스키마 검증, 수동 검토, 품질 메트릭]

## 6. Error Handling
[알려진 문제, 에스컬레이션, 복구 절차]

## 7. Examples
[입력 예시, 출력 예시]
```

### 3.2 Section Details

#### Section 1: Overview

```yaml
overview_structure:
  purpose:
    description: "이 Skill이 해결하는 문제 (프로젝트 독립적으로 기술)"
    example: "Legacy 소스코드에서 API 엔드포인트를 추출하고 Feature로 그룹핑"

  scope:
    in_scope:
      - "포함되는 작업"
    out_of_scope:
      - "제외되는 작업 (다른 skill에서 처리)"

  core_principles:
    - principle: "원칙 이름"
      description: "원칙 설명"
      rationale: "이 원칙이 필요한 이유"

  relationships:
    predecessors:
      - skill: "선행 skill"
        reason: "왜 이 skill이 먼저 실행되어야 하는지"
    successors:
      - skill: "후행 skill"
        reason: "이 skill의 출력이 어떻게 사용되는지"
```

#### Section 2: Prerequisites

```yaml
prerequisites_structure:
  skill_dependencies:
    - skill: "skill-name"
      status: "completed"
      outputs:
        - "필요한 출력 파일"

  input_requirements:
    - name: "입력 이름"
      type: "file|directory|data"
      location: "경로 패턴"
      format: "yaml|json|java|..."
      required: true|false

  environment:
    tools:
      - name: "도구 이름"
        version: "최소 버전"
        purpose: "용도"
    access:
      - "필요 접근 권한"
    resources:
      - "필요 리소스 (메모리, 디스크 등)"
```

#### Section 3: Methodology

```yaml
methodology_structure:
  execution_model:
    type: "sequential|parallel|hybrid"
    unit: "feature|domain|batch|none"
    parallelization:
      max_sessions: 10
      batch_size: 50

  steps:
    - step: 1
      name: "단계 이름"
      description: "상세 설명"
      sub_steps:
        - "세부 단계 1"
        - "세부 단계 2"
      validation: "단계 완료 조건"
      outputs:
        - "단계 산출물"
      rollback: "실패 시 복구 방법"

  decision_points:
    - id: "DP-1"
      condition: "조건"
      branches:
        - when: "condition == true"
          action: "수행 작업"
          next: "다음 단계"
        - when: "condition == false"
          action: "대안 작업"
          next: "대안 단계"
```

#### Section 4: Outputs

```yaml
outputs_structure:
  directory:
    base: "${STAGE_OUTPUTS}/phase${CURRENT_PHASE}/"
    pattern: "{priority}/{domain}-domain/{feature-id}/"

  files:
    - name: "파일명.yaml"
      type: "yaml"
      purpose: "용도"
      required: true
      template: "templates/output-template.yaml"
      constraints:
        max_lines: 300
        max_size_kb: 100

  file_header:
    required: true
    format: |
      # Generated by: ${SKILL_NAME}
      # Stage: ${CURRENT_STAGE}
      # Phase: ${CURRENT_PHASE}
      # Feature: ${FEATURE_ID}
      # Generated: ${TIMESTAMP}
      # Model: ${MODEL_NAME}
```

#### Section 5: Quality Checks

```yaml
quality_checks_structure:
  automated_checks:
    - check: "검증 항목"
      type: "structural|content|metric|schema"
      criteria: "통과 기준"
      action_on_fail: "실패 시 조치"
      blocking: true|false

  schema_validation:
    description: "표준 스키마 준수 검증"
    schema_location: ".claude/skills/{skill}/output.schema.yaml"
    common_types: ".claude/skills/common/types.schema.yaml"
    validation_rules:
      - type: "structural"
        description: "필수 키 존재 확인"
      - type: "content"
        description: "패턴 규칙 검증 (FEAT-{DOMAIN}-{NNN} 등)"
      - type: "metric"
        description: "수치 일관성 (합계, 범위)"
    on_failure:
      output: "validation-errors.yaml"
      blocking: true
      retry_eligible: true

  manual_reviews:
    - review: "검토 항목"
      reviewer: "역할 (tech_lead, architect, etc.)"
      criteria: "검토 기준"
      required: true|false

  gate_criteria:
    threshold: 70|90|85  # Phase Gate, Validation Gate, Quality Gate
    metrics:
      - metric: "측정 지표"
        weight: 0.25
        target: "목표 값"
        formula: "계산 방법"
```

#### Section 6: Error Handling

```yaml
error_handling_structure:
  known_issues:
    - issue: "알려진 문제"
      symptom: "증상"
      cause: "원인"
      resolution: "해결 방법"
      retry_eligible: true|false

  escalation:
    - condition: "상황"
      severity: "critical|major|minor"
      action: "조치"
      notify: "알림 대상"

  recovery:
    - scenario: "시나리오"
      procedure:
        - "복구 절차 1"
        - "복구 절차 2"
      rollback_level: "phase|stage|wave"
```

#### Section 7: Examples

```yaml
examples_structure:
  sample_input:
    description: "입력 예시 설명"
    content: |
      # 실제 입력 예시

  sample_output:
    description: "출력 예시 설명"
    content: |
      # 실제 출력 예시

  edge_cases:
    - case: "경계 조건"
      input: "입력"
      expected_output: "예상 출력"
```

---

## 4. Skill Dependencies

### 4.1 Dependency Declaration

```yaml
skill_dependencies:
  explicit:
    description: "SKILL.md의 prerequisites에 명시된 의존성"
    format:
      prerequisites:
        skill_dependencies:
          - skill: "s1-01-discovery-feature-inventory"
            status: "completed"
            outputs:
              - "feature-inventory.yaml"

  implicit:
    description: "입력 파일 경로에서 추론되는 의존성"
    detection: "입력 경로가 다른 skill 출력 경로와 일치하는 경우"
```

### 4.2 Dependency Graph Example

```
┌──────────────────────────────────────────────────────────────────┐
│                   STAGE DEPENDENCY FLOW                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Stage 1: Discovery                                              │
│  ┌───────────┐     ┌───────────┐     ┌───────────┐               │
│  │ Inventory │────▶│ Analysis  │────▶│   Spec    │               │
│  └───────────┘     └───────────┘     └─────┬─────┘               │
│                                            │                     │
│  Stage 2: Validation                       ▼                     │
│  ┌───────────┐     ┌───────────┐     ┌───────────┐               │
│  │ Source    │────▶│ Compare   │────▶│   Gap     │               │
│  │ Inventory │     │           │     │ Analysis  │               │
│  └───────────┘     └───────────┘     └─────┬─────┘               │
│                                            │                     │
│                                            ▼                     │
│                                      ┌───────────┐               │
│                                      │ Complete  │               │
│                                      └───────────┘               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. Execution Context

### 5.1 Context Variables

모든 Skill은 다음 컨텍스트 변수에 접근할 수 있습니다:

| Level | Variable | Description |
|-------|----------|-------------|
| **Project** | `${PROJECT_ROOT}` | 프로젝트 루트 디렉토리 |
| **Project** | `${WORKSPACE}` | 작업 디렉토리 |
| **Project** | `${LEGACY_CODEBASE}` | 레거시 소스코드 경로 |
| **Stage** | `${CURRENT_STAGE}` | 현재 Stage 번호 |
| **Stage** | `${STAGE_OUTPUTS}` | Stage 출력 경로 |
| **Phase** | `${CURRENT_PHASE}` | 현재 Phase 번호 |
| **Phase** | `${PHASE_OUTPUTS}` | Phase 출력 경로 |
| **Task** | `${FEATURE_ID}` | 현재 Feature ID |
| **Task** | `${DOMAIN}` | 현재 도메인 |
| **Task** | `${PRIORITY}` | Feature 우선순위 |
| **Skill** | `${SKILL_NAME}` | 현재 Skill 이름 |
| **Skill** | `${MODEL_NAME}` | AI 모델 이름 |
| **Skill** | `${TIMESTAMP}` | 실행 타임스탬프 |

### 5.2 Variable Substitution

```yaml
# SKILL.md에서 변수 사용
outputs:
  directory:
    base: "${STAGE_OUTPUTS}/phase${CURRENT_PHASE}/"
    pattern: "${PRIORITY}/${DOMAIN}-domain/${FEATURE_ID}/"

# 기본값 지정
input:
  path: "${CUSTOM_PATH:-${PROJECT_ROOT}/default/}"
```

---

## 6. Versioning

### 6.1 Version Schema

```yaml
version_schema:
  format: "MAJOR.MINOR.PATCH"

  rules:
    major: "호환성 깨지는 변경 (출력 형식 변경, 필수 입력 추가)"
    minor: "기능 추가 (하위 호환 유지)"
    patch: "버그 수정, 문서 개선"

  framework_compatibility:
    skill_version: "1.2.3"
    framework_version: "2.0.0"
```

### 6.2 Version History Format

```markdown
## Version History

### v1.2.0 (2026-01-07)
- Added: 새로운 검증 단계 추가
- Changed: 출력 형식 개선
- Fixed: 경계 조건 처리 버그 수정

### v1.1.0 (2026-01-01)
- Added: 병렬 처리 지원
```

---

## 7. Best Practices

### 7.1 Writing Principles

| 원칙 | 설명 | 예시 |
|------|------|------|
| **Clarity** | 모호한 표현 금지 | ❌ "적절히 분석하세요" → ✅ "@RequestMapping 어노테이션을 추출하세요" |
| **Completeness** | 모든 분기 처리 정의 | 모든 if/else, 에러 케이스 명시 |
| **Measurability** | 정량적 기준 제시 | ❌ "충분히 검증" → ✅ "커버리지 95% 이상" |
| **Reproducibility** | 동일 입력 → 동일 출력 | 랜덤 요소 제거, 결정적 알고리즘 사용 |

### 7.2 Anti-Patterns

```yaml
anti_patterns:
  vague_instructions:
    bad: "적절히 분석하세요"
    good: "각 Controller 클래스에서 @RequestMapping 어노테이션을 추출하세요"
    reason: "AI가 '적절히'를 해석하는 방식이 일관되지 않음"

  missing_validation:
    bad: "파일을 생성하세요"
    good: "파일을 생성하고 YAML 문법 오류가 없는지 검증하세요"
    reason: "검증 없이 생성된 파일은 후속 단계에서 오류 발생"

  implicit_knowledge:
    bad: "표준 방식으로 처리하세요"
    good: "MyBatis XML에서 <select> 태그의 id 속성을 추출하세요"
    reason: "AI 세션 간 '표준'의 정의가 다를 수 있음"

  unbounded_scope:
    bad: "모든 문제를 해결하세요"
    good: "Critical severity의 Gap만 이번 Phase에서 해결하세요"
    reason: "무한 루프 또는 과도한 리소스 사용 방지"
```

---

## 8. Quick Reference

### 8.1 Skill Creation Checklist

**Frontmatter (필수):**
- [ ] `name`: 문자, 숫자, 하이픈만 사용
- [ ] `description`: "Use when..."으로 시작, 트리거 조건만 (워크플로우 요약 금지)
- [ ] 총 1024자 이하

**CSO (Claude Search Optimization):**
- [ ] 구체적 증상/상황 키워드 포함
- [ ] 에러 메시지, 도구명 등 검색어 포함
- [ ] 3인칭 작성

**Token Efficiency:**
- [ ] 목표 단어 수 확인 (<150 / <200 / <500)
- [ ] 불필요한 예시 제거
- [ ] cross-reference 활용

**Content:**
- [ ] Overview (purpose, scope, principles)
- [ ] Prerequisites (dependencies, inputs)
- [ ] Methodology (steps, decision points)
- [ ] Outputs (directory, files)
- [ ] Quality Checks
- [ ] Error Handling
- [ ] Examples (최소 1개의 좋은 예시)

### 8.2 Related Documents

| Document | Purpose |
|----------|---------|
| [02-skill-taxonomy.md](02-skill-taxonomy.md) | Skill 분류 체계 |
| [03-skill-authoring-guide.md](03-skill-authoring-guide.md) | Skill 작성 상세 가이드 |
| [04-skill-patterns.md](04-skill-patterns.md) | 재사용 가능한 Skill 패턴 |
| [05-orchestration-patterns.md](05-orchestration-patterns.md) | Orchestration 패턴 |

---

**Next**: [02-skill-taxonomy.md](02-skill-taxonomy.md)
