# Skill Patterns

**Version**: 1.1.0
**Last Updated**: 2026-01-12
**Purpose**: AI-Driven Migration에서 재사용 가능한 Skill 패턴 라이브러리

---

## 1. Overview

이 문서는 AI-Driven Migration 프로젝트에서 반복적으로 나타나는 Skill 패턴을 정의합니다. 각 패턴은 검증된 접근 방식을 제공하여 새로운 Skill 개발 시 참조할 수 있습니다.

### 1.1 Pattern Categories

| Category | Purpose | Typical Stage |
|----------|---------|---------------|
| **Inventory Pattern** | 대상 시스템 목록화 | S1, S2 |
| **Multi-Layer Trace Pattern** | N-계층 코드 추적 | S1, S3 |
| **Bidirectional Validation Pattern** | 양방향 검증 | S2, S5 |
| **Gap-Fill Pattern** | Gap 식별 및 보완 | S2 |
| **Batch Execution Pattern** | 병렬 배치 처리 | S1, S4, S5 |
| **Quality Gate Pattern** | 임계값 기반 판정 | All |
| **Template-Based Generation Pattern** | 템플릿 기반 생성 | S1, S4 |
| **Truncation Handling Pattern** | 대형 도메인 출력 분할/병합 | S1, S4 |

---

## 2. Inventory Pattern

### 2.1 Intent

대상 시스템의 구성 요소를 체계적으로 스캔하여 구조화된 목록을 생성합니다.

### 2.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    INVENTORY PATTERN                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐            │
│  │  Source  │────▶│   Scan   │────▶│  Filter  │            │
│  │  System  │     │  Engine  │     │  Rules   │            │
│  └──────────┘     └──────────┘     └────┬─────┘            │
│                                         │                   │
│                                         ▼                   │
│                   ┌──────────┐     ┌──────────┐            │
│                   │  Group   │◀────│ Classify │            │
│                   │  & Sort  │     │          │            │
│                   └────┬─────┘     └──────────┘            │
│                        │                                    │
│                        ▼                                    │
│                   ┌──────────┐                              │
│                   │ Inventory│                              │
│                   │   YAML   │                              │
│                   └──────────┘                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Participants

| Component | Role | Example |
|-----------|------|---------|
| **Source System** | 스캔 대상 | Legacy codebase, Database |
| **Scan Engine** | 정보 추출 | Regex, AST parser, SQL parser |
| **Filter Rules** | 대상 필터링 | Include/exclude patterns |
| **Classify** | 항목 분류 | By domain, by type, by priority |
| **Group & Sort** | 그룹화 및 정렬 | Feature grouping, priority ordering |
| **Inventory** | 최종 산출물 | YAML/JSON 목록 |

### 2.4 Implementation

```yaml
inventory_pattern:
  steps:
    - step: 1
      name: "Source Identification"
      description: "스캔 대상 소스 식별"
      outputs:
        - "source_paths.yaml"

    - step: 2
      name: "Scan Execution"
      description: "패턴 기반 정보 추출"
      techniques:
        - "File glob patterns"
        - "Regex extraction"
        - "AST traversal"

    - step: 3
      name: "Classification"
      description: "추출 항목 분류"
      dimensions:
        - "Type (controller, service, entity)"
        - "Domain (PA, MM, SC, ...)"
        - "Priority (P0, P1, P2, P3)"

    - step: 4
      name: "Output Generation"
      description: "구조화된 목록 생성"
      format: "YAML with headers"

  quality_checks:
    - "Coverage >= 90%"
    - "No duplicate entries"
    - "Valid classification for all items"

  applicable_skills:
    - "discovery:feature-inventory"
    - "validation:source-inventory"
```

### 2.5 Example

```yaml
# Input: Java source files
# Output: feature-inventory.yaml

feature_inventory:
  generated_by: "discovery:feature-inventory"
  generated_at: "2026-01-07T10:00:00Z"
  coverage: 95.3%

  summary:
    total_endpoints: 5600
    total_features: 450
    domains: 12

  features:
    - id: "FEAT-PA-001"
      name: "생산계획 조회"
      domain: "PA"
      priority: "P2"
      endpoints:
        - path: "/api/pa/plan/list"
          method: "POST"
          controller: "PA01Controller"
```

---

## 3. Multi-Layer Trace Pattern

### 3.1 Intent

코드의 호출 흐름을 N개 계층에 걸쳐 추적하여 완전한 실행 경로를 문서화합니다.

### 3.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│                 MULTI-LAYER TRACE PATTERN                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Entry Point                                       │
│  ┌─────────────────────────────────────────┐               │
│  │ Controller / API Endpoint               │               │
│  │ @RequestMapping, URL, Method            │               │
│  └──────────────────┬──────────────────────┘               │
│                     │ calls                                 │
│                     ▼                                       │
│  Layer 2: Business Logic                                    │
│  ┌─────────────────────────────────────────┐               │
│  │ Service / Business Component            │               │
│  │ @Service, @Transactional                │               │
│  └──────────────────┬──────────────────────┘               │
│                     │ calls                                 │
│                     ▼                                       │
│  Layer 3: Data Access                                       │
│  ┌─────────────────────────────────────────┐               │
│  │ DAO / Repository                        │               │
│  │ @Repository, Mapper interface           │               │
│  └──────────────────┬──────────────────────┘               │
│                     │ executes                              │
│                     ▼                                       │
│  Layer 4: SQL/Query                                         │
│  ┌─────────────────────────────────────────┐               │
│  │ SQL Statement / Stored Procedure        │               │
│  │ SELECT, INSERT, CALL                    │               │
│  └──────────────────┬──────────────────────┘               │
│                     │ accesses                              │
│                     ▼                                       │
│  Layer 5: Data Model                                        │
│  ┌─────────────────────────────────────────┐               │
│  │ Entity / VO / DTO                       │               │
│  │ Table mapping, Field definitions        │               │
│  └─────────────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Implementation

```yaml
multi_layer_trace:
  layers:
    - layer: 1
      name: "Controller Layer"
      artifacts:
        - "Entry point (URL, method)"
        - "Request parameters"
        - "Response type"
      trace_method: "Annotation scan (@RequestMapping)"

    - layer: 2
      name: "Service Layer"
      artifacts:
        - "Business method"
        - "Transaction boundary"
        - "Dependencies"
      trace_method: "Method call analysis"

    - layer: 3
      name: "Repository Layer"
      artifacts:
        - "DAO/Repository method"
        - "Mapper interface"
      trace_method: "Interface/implementation mapping"

    - layer: 4
      name: "SQL Layer"
      artifacts:
        - "SQL statement ID"
        - "SQL type (SELECT, INSERT, ...)"
        - "Parameter mapping"
      trace_method: "MyBatis XML parsing"

    - layer: 5
      name: "Data Model Layer"
      artifacts:
        - "Entity class"
        - "Field mappings"
        - "Table relationships"
      trace_method: "VO/DTO analysis"

  output_structure:
    per_feature:
      - "summary.yaml"
      - "api-endpoints/"
      - "business-logic/"
      - "data-access/"
      - "data-model/"

  applicable_skills:
    - "discovery:deep-analysis"
    - "preparation:dependency-graph"
```

### 3.4 Variations

| Variation | Layers | Use Case |
|-----------|--------|----------|
| **3-Layer** | Controller → Service → Repository | Simple CRUD applications |
| **5-Layer** | Full stack trace | Enterprise applications |
| **7-Layer** | + Cache + Message Queue | Distributed systems |

---

## 4. Bidirectional Validation Pattern

### 4.1 Intent

두 대상 간의 일치성을 양방향으로 검증하여 누락과 불일치를 모두 탐지합니다.

### 4.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│              BIDIRECTIONAL VALIDATION PATTERN               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│     Source A                           Source B             │
│  ┌───────────┐                      ┌───────────┐          │
│  │   Spec    │                      │  Ground   │          │
│  │ (Stage 1) │                      │   Truth   │          │
│  └─────┬─────┘                      └─────┬─────┘          │
│        │                                  │                 │
│        │    ┌──────────────────────┐     │                 │
│        └───▶│   Forward Check      │◀────┘                 │
│             │   A → B              │                        │
│             │   "Is A in B?"       │                        │
│             └──────────┬───────────┘                        │
│                        │                                    │
│             ┌──────────▼───────────┐                        │
│             │   Backward Check     │                        │
│             │   B → A              │                        │
│             │   "Is B in A?"       │                        │
│             └──────────┬───────────┘                        │
│                        │                                    │
│             ┌──────────▼───────────┐                        │
│             │   Gap Analysis       │                        │
│             │   - Missing in A     │                        │
│             │   - Missing in B     │                        │
│             │   - Mismatches       │                        │
│             └──────────┬───────────┘                        │
│                        │                                    │
│             ┌──────────▼───────────┐                        │
│             │   Validation Report  │                        │
│             │   + Coverage Score   │                        │
│             └──────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Implementation

```yaml
bidirectional_validation:
  directions:
    forward:
      name: "A → B"
      purpose: "Spec이 Ground Truth에 있는지 확인"
      identifies: "Over-specification (있어야 할 것이 없음)"

    backward:
      name: "B → A"
      purpose: "Ground Truth가 Spec에 있는지 확인"
      identifies: "Under-specification (있는 것이 문서화 안됨)"

  comparison_dimensions:
    - dimension: "Endpoint Coverage"
      weight: 0.30
      match_criteria: "URL + Method"

    - dimension: "Service Coverage"
      weight: 0.25
      match_criteria: "Class + Method signature"

    - dimension: "SQL Coverage"
      weight: 0.25
      match_criteria: "Statement ID"

    - dimension: "Entity Coverage"
      weight: 0.20
      match_criteria: "Class name + Fields"

  scoring:
    formula: "Σ(dimension_weight × dimension_coverage)"
    thresholds:
      excellent: ">= 99%"
      good: "95-98%"
      acceptable: "90-94%"
      warning: "< 90%"

  applicable_skills:
    - "validation:structural-comparison"
    - "assurance:functional-validation"
```

### 4.4 Example Output

```yaml
validation_report:
  forward_check:
    total_items: 5600
    matched: 5400
    missing: 200
    coverage: 96.4%

  backward_check:
    total_items: 5650
    matched: 5400
    missing: 250
    coverage: 95.6%

  combined_score: 96.0%

  gaps:
    missing_in_spec:
      - endpoint: "/api/hidden/legacy"
        reason: "Legacy endpoint not documented"
    missing_in_source:
      - endpoint: "/api/new/feature"
        reason: "Planned but not implemented"
```

---

## 5. Gap-Fill Pattern

### 5.1 Intent

식별된 Gap을 분류하고 우선순위에 따라 체계적으로 보완합니다.

### 5.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    GAP-FILL PATTERN                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐            │
│  │   Gap    │────▶│ Classify │────▶│Prioritize│            │
│  │  List    │     │ by Type  │     │ by Impact│            │
│  └──────────┘     └──────────┘     └────┬─────┘            │
│                                         │                   │
│                                         ▼                   │
│                   ┌───────────────────────────┐             │
│                   │    Remediation Strategy   │             │
│                   ├───────────────────────────┤             │
│                   │ Critical → Immediate fix  │             │
│                   │ Major    → Phase fix      │             │
│                   │ Minor    → Backlog        │             │
│                   │ False+   → Mark & skip    │             │
│                   └─────────────┬─────────────┘             │
│                                 │                           │
│                                 ▼                           │
│                   ┌──────────────────────────┐              │
│                   │      Execute Fix         │              │
│                   │   (Generate/Update)      │              │
│                   └─────────────┬────────────┘              │
│                                 │                           │
│                                 ▼                           │
│                   ┌──────────────────────────┐              │
│                   │      Validate Fix        │              │
│                   │   (Re-run comparison)    │              │
│                   └──────────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Implementation

```yaml
gap_fill_pattern:
  classification:
    - type: "missing_endpoint"
      severity_factors:
        - "Business criticality"
        - "User impact"
        - "Dependency count"

    - type: "incomplete_spec"
      severity_factors:
        - "Missing fields"
        - "Partial trace"

    - type: "outdated_spec"
      severity_factors:
        - "Version mismatch"
        - "Deprecated elements"

  severity_scoring:
    critical: 100  # Must fix before proceed
    major: 70      # Should fix in this phase
    minor: 30      # Can defer to later
    false_positive: 0  # Not a real gap

  remediation_strategies:
    critical:
      action: "Immediate deep analysis and spec generation"
      timeline: "Same phase"
      validation: "Re-run comparison"

    major:
      action: "Scheduled fix with review"
      timeline: "Before stage completion"
      validation: "Batch re-validation"

    minor:
      action: "Add to technical debt backlog"
      timeline: "Future iteration"
      validation: "Periodic review"

  merge_rules:
    - "Never modify existing spec files"
    - "Use NEW_ prefix for additions"
    - "Document merge decisions"

  applicable_skills:
    - "validation:gap-analysis"
    - "validation:spec-completion"
```

---

## 6. Batch Execution Pattern

### 6.1 Intent

대량의 작업을 병렬로 처리하면서 체크포인트와 재시도 메커니즘을 제공합니다.

### 6.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│                 BATCH EXECUTION PATTERN                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐                                               │
│  │  Task    │                                               │
│  │  Queue   │                                               │
│  └────┬─────┘                                               │
│       │                                                     │
│       ▼                                                     │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Batch Dispatcher                     │      │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐          │      │
│  │  │ Batch 1 │  │ Batch 2 │  │ Batch N │          │      │
│  │  │ (50)    │  │ (50)    │  │ (<=50)  │          │      │
│  │  └────┬────┘  └────┬────┘  └────┬────┘          │      │
│  └───────┼───────────┼───────────┼──────────────────┘      │
│          │           │           │                          │
│          ▼           ▼           ▼                          │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐                 │
│  │ Session 1 │ │ Session 2 │ │ Session N │  (max 10)       │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘                 │
│        │             │             │                        │
│        ▼             ▼             ▼                        │
│  ┌───────────────────────────────────────┐                 │
│  │           Checkpoint Manager           │                 │
│  │  - Save state per task completion     │                 │
│  │  - Enable resume on failure           │                 │
│  └───────────────────────────────────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Implementation

```yaml
batch_execution_pattern:
  configuration:
    max_sessions: 10
    batch_size: 50
    session_timeout_minutes: 60
    checkpoint_frequency: "per_task"

  task_states:
    - PENDING      # 대기 중
    - ASSIGNED     # 세션에 배정됨
    - IN_PROGRESS  # 실행 중
    - VALIDATING   # 검증 중
    - COMPLETED    # 완료
    - FAILED       # 실패
    - REJECTED     # 검증 실패
    - ESCALATED    # 에스컬레이션 필요

  retry_policy:
    default:
      max_attempts: 3
      backoff: "exponential"
      initial_delay_seconds: 30

    rate_limit:
      max_attempts: 5
      backoff: "exponential"
      initial_delay_seconds: 60

    timeout:
      max_attempts: 3
      backoff: "linear"
      delay_increment_seconds: 30

  checkpoint_management:
    save_on:
      - "Task completion"
      - "Batch completion"
      - "Error occurrence"
    restore_on:
      - "Session restart"
      - "Failure recovery"

  applicable_skills:
    - "discovery:deep-analysis"
    - "generation:domain-batch"
    - "assurance:functional-validation"
```

---

## 7. Quality Gate Pattern

### 7.1 Intent

정량적 임계값을 기반으로 진행/중단/조건부 통과 여부를 판정합니다.

### 7.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│                  QUALITY GATE PATTERN                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐                                               │
│  │  Input   │                                               │
│  │ Metrics  │                                               │
│  └────┬─────┘                                               │
│       │                                                     │
│       ▼                                                     │
│  ┌──────────────────────────────────────────┐              │
│  │         Metric Calculation               │              │
│  │  - Coverage score                        │              │
│  │  - Quality score                         │              │
│  │  - Blocker/Critical count                │              │
│  └──────────────────┬───────────────────────┘              │
│                     │                                       │
│                     ▼                                       │
│  ┌──────────────────────────────────────────┐              │
│  │         Threshold Comparison             │              │
│  └──────────────────┬───────────────────────┘              │
│                     │                                       │
│     ┌───────────────┼───────────────┐                      │
│     │               │               │                      │
│     ▼               ▼               ▼                      │
│  ┌──────┐       ┌──────┐       ┌──────┐                   │
│  │ PASS │       │COND. │       │ FAIL │                   │
│  │      │       │ PASS │       │      │                   │
│  └──┬───┘       └──┬───┘       └──┬───┘                   │
│     │              │              │                        │
│     ▼              ▼              ▼                        │
│  Proceed      Proceed +      Rollback                      │
│              Remediation                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 Implementation

```yaml
quality_gate_pattern:
  gate_types:
    phase_gate:
      threshold: 70
      purpose: "Phase 완료 기본 조건"
      blocking: true

    validation_gate:
      threshold: 90
      purpose: "명세 정확도 검증"
      blocking: true
      applies_to:
        - "S2-P2.4 (Spec Completion)"
        - "S5-P5.2 (Functional Validation)"

    quality_gate:
      threshold: 85
      purpose: "배포 준비 상태 판정"
      blocking: true
      requires_human_approval: true
      applies_to:
        - "S5-P5.5 (Quality Gate)"

  decision_matrix:
    approved:
      conditions:
        - "blocker_count == 0"
        - "critical_count < 5"
        - "score >= threshold"
      action: "Proceed to next phase/stage"

    conditional:
      conditions:
        - "blocker_count == 0"
        - "critical_count >= 5 AND critical_count < 15"
        - "score >= (threshold - 15) AND score < threshold"
      action: "Proceed with remediation plan"
      remediation_timeline: "1 week"

    rejected:
      conditions:
        - "blocker_count >= 1"
        - "OR critical_count >= 15"
        - "OR score < (threshold - 15)"
      action: "Rollback and fix"

  metrics_template:
    - metric: "coverage_score"
      weight: 0.30
      calculation: "matched / total * 100"

    - metric: "quality_score"
      weight: 0.40
      calculation: "weighted_average(dimensions)"

    - metric: "blocker_count"
      weight: 0.20
      calculation: "count(severity == 'blocker')"

    - metric: "critical_count"
      weight: 0.10
      calculation: "count(severity == 'critical')"

  applicable_skills:
    - "orchestration:phase-gate"
    - "orchestration:stage-gate"
    - "assurance:quality-gate"
```

---

## 8. Template-Based Generation Pattern

### 8.1 Intent

템플릿과 데이터를 결합하여 일관된 산출물을 생성합니다.

### 8.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│            TEMPLATE-BASED GENERATION PATTERN                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐     ┌──────────┐                             │
│  │ Template │     │   Data   │                             │
│  │ Library  │     │  Source  │                             │
│  └────┬─────┘     └────┬─────┘                             │
│       │                │                                    │
│       └───────┬────────┘                                    │
│               │                                             │
│               ▼                                             │
│       ┌──────────────────┐                                  │
│       │ Template Engine  │                                  │
│       │ - Variable subst │                                  │
│       │ - Conditional    │                                  │
│       │ - Loop expansion │                                  │
│       └────────┬─────────┘                                  │
│                │                                            │
│                ▼                                            │
│       ┌──────────────────┐                                  │
│       │    Validator     │                                  │
│       │ - Syntax check   │                                  │
│       │ - Schema valid   │                                  │
│       └────────┬─────────┘                                  │
│                │                                            │
│                ▼                                            │
│       ┌──────────────────┐                                  │
│       │  Output Files    │                                  │
│       │ - YAML/JSON      │                                  │
│       │ - Code files     │                                  │
│       │ - Documents      │                                  │
│       └──────────────────┘                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.3 Implementation

```yaml
template_generation_pattern:
  template_types:
    - type: "spec_template"
      format: "YAML"
      variables:
        - "${FEATURE_ID}"
        - "${DOMAIN}"
        - "${ENDPOINTS[]}"
      output: "main.yaml"

    - type: "code_template"
      format: "Java"
      variables:
        - "${CLASS_NAME}"
        - "${PACKAGE}"
        - "${METHODS[]}"
      output: "*.java"

    - type: "test_template"
      format: "Java"
      variables:
        - "${TEST_CLASS}"
        - "${TEST_METHODS[]}"
      output: "*Test.java"

  generation_rules:
    - rule: "file_size_limit"
      max_lines: 300
      action_on_exceed: "split_file"

    - rule: "naming_convention"
      pattern: "{domain}/{feature}/{layer}"
      validation: "regex_match"

  validation_steps:
    - step: "Syntax validation"
      tools: ["yaml-lint", "checkstyle"]

    - step: "Schema validation"
      tools: ["json-schema", "xsd"]

    - step: "Compilation check"
      tools: ["javac", "gradle"]

  applicable_skills:
    - "discovery:spec-generation"
    - "generation:domain-batch"
    - "generation:test-generation"
```

---

## 9. Truncation Handling Pattern (v1.1.0)

### 9.1 Intent

AI 출력 토큰 제한으로 인한 데이터 손실을 방지하고, 대형 도메인 처리 시 자동으로 분할/병합합니다.

### 9.2 Context

| Factor | Description |
|--------|-------------|
| **Root Cause** | LLM Output Token Limit (~25-30K tokens) |
| **Symptom** | Summary 정상 생성, 데이터 배열 중간에서 잘림 |
| **Impact** | 95%+ 데이터 손실 가능 (PA: 1.7%, EB: 2.1% 문서화) |

### 9.3 Structure

```
┌─────────────────────────────────────────────────────────────┐
│              TRUNCATION HANDLING PATTERN                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Step 0: Size Assessment              │      │
│  │  controller_count > 100? endpoint_estimate > 200? │      │
│  └──────────────────────┬───────────────────────────┘      │
│                         │                                   │
│         ┌───────────────┴───────────────┐                  │
│         │                               │                  │
│         ▼ small                         ▼ large            │
│  ┌──────────────┐               ┌──────────────┐           │
│  │ Single Pass  │               │  Sub-Wave    │           │
│  │   Execute    │               │  Division    │           │
│  └──────┬───────┘               └──────┬───────┘           │
│         │                              │                   │
│         │                   ┌──────────┴──────────┐        │
│         │                   ▼                     ▼        │
│         │            ┌──────────┐          ┌──────────┐    │
│         │            │ Wave 1   │   ...    │ Wave N   │    │
│         │            │ (30-50)  │          │ (30-50)  │    │
│         │            └────┬─────┘          └────┬─────┘    │
│         │                 │                     │          │
│         │                 └──────────┬──────────┘          │
│         │                            ▼                     │
│         │                 ┌──────────────────┐             │
│         │                 │   Merge Results  │             │
│         │                 │   (Deduplicate)  │             │
│         │                 └────────┬─────────┘             │
│         │                          │                       │
│         └───────────┬──────────────┘                       │
│                     ▼                                      │
│         ┌──────────────────────────┐                       │
│         │  Truncation Detection    │                       │
│         │  summary.count == actual │                       │
│         └──────────────┬───────────┘                       │
│                        │                                   │
│         ┌──────────────┴──────────────┐                   │
│         │ PASS                   FAIL │                   │
│         ▼                             ▼                   │
│  ┌──────────────┐            ┌──────────────┐             │
│  │   Complete   │            │  Re-execute  │             │
│  │              │            │  Sub-Wave    │             │
│  └──────────────┘            └──────────────┘             │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### 9.4 Implementation

```yaml
truncation_handling_pattern:
  step_0_assessment:
    thresholds:
      small:
        max_controllers: 100
        max_endpoints: 200
        strategy: single_pass
      large:
        min_controllers: 100
        min_endpoints: 200
        strategy: sub_wave_division

  sub_wave_division:
    method: prefix_grouping
    target_size: "30-50 controllers per wave"

    examples:
      PA_domain:  # 462 controllers → 6 waves
        - "PA01, PA02 → 26 controllers"
        - "PA03 → 55 controllers"
        - "PA04 → 118 controllers"
        - "PA05 → 80 controllers"
        - "PA06 → 139 controllers"
        - "PA07, PA08+ → 44 controllers"

      EB_domain:  # 116 controllers → 3 waves
        - "EB01-03 → 47 controllers"
        - "EB04-06 → 33 controllers"
        - "EB07-12+ → 36 controllers"

  output_optimization:
    lean_format:
      description: "Sub-wave 출력 시 compact format 사용"
      size_reduction: "60-70%"
      omit:
        - "detailed column definitions"
      preserve:
        - "essential identifiers"
        - "standard response variables"

  merge_strategy:
    tool: "Python YAML parser"
    handle_format_variations: true  # 다양한 YAML 형식 지원
    deduplication: "by primary key (endpoint_path)"

  truncation_detection:
    checks:
      - id: TC-001
        name: "Summary-Data Consistency"
        rule: "summary.total_count == len(data_array)"
        action_on_fail: "Re-execute with sub-wave"

      - id: TC-002
        name: "Coverage Threshold"
        rule: "coverage >= 95%"
        action_on_fail: "Investigate and supplement"

  applicable_skills:
    - "s1-02-discovery-miplatform-protocol"
    - "s1-03-discovery-deep-analysis"
    - "s4-01-generation-domain-batch"
```

### 9.5 Validated Results

| Domain | Before | After | Improvement |
|--------|--------|-------|-------------|
| PA | 34 endpoints (1.7%) | 1,225 endpoints (61%) | **36x** |
| EB | 13 endpoints (2.1%) | 402 endpoints (65%) | **31x** |
| BS | 71 (100%) | 71 (100%) | Already optimal |
| QM | 57 (100%) | 57 (100%) | Already optimal |

### 9.6 Key Learnings

1. **Token Limit is Primary Cause**: Timeout (120min) 아님, Output token limit (~25-30K)
2. **Size Threshold**: 100 controllers 또는 200 endpoints 기준
3. **Wave Size**: 30-50 controllers가 안전한 범위
4. **Format Variations**: Sub-wave 병합 시 다양한 YAML 형식 처리 필요
5. **Proactive Division**: 사후 감지보다 사전 분할이 효율적

---

## 10. Pattern Selection Guide

### 10.1 Decision Matrix

| Situation | Recommended Pattern |
|-----------|---------------------|
| 대상 시스템 목록화 필요 | Inventory Pattern |
| 코드 호출 흐름 추적 필요 | Multi-Layer Trace Pattern |
| 두 소스 간 일치성 검증 | Bidirectional Validation Pattern |
| 누락 항목 보완 필요 | Gap-Fill Pattern |
| 대량 작업 병렬 처리 | Batch Execution Pattern |
| 진행/중단 판정 필요 | Quality Gate Pattern |
| 일관된 산출물 생성 | Template-Based Generation Pattern |
| **대형 도메인 출력 truncation 방지** | **Truncation Handling Pattern** |

### 10.2 Pattern Combinations

```yaml
common_combinations:
  - name: "Discovery Pipeline"
    patterns:
      - "Inventory Pattern"
      - "Multi-Layer Trace Pattern"
      - "Template-Based Generation Pattern"

  - name: "Validation Pipeline"
    patterns:
      - "Inventory Pattern"
      - "Bidirectional Validation Pattern"
      - "Gap-Fill Pattern"
      - "Quality Gate Pattern"

  - name: "Generation Pipeline"
    patterns:
      - "Batch Execution Pattern"
      - "Template-Based Generation Pattern"
      - "Quality Gate Pattern"
```

---

**Previous**: [03-skill-authoring-guide.md](03-skill-authoring-guide.md)
**Next**: [05-orchestration-patterns.md](05-orchestration-patterns.md)
