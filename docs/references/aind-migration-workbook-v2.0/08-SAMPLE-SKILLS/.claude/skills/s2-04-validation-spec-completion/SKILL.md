---
name: s2-04-validation-spec-completion
description: Use when remediating specification gaps, completing missing spec entries from source analysis, or achieving 99% coverage for validation gate (project)
---

# Spec Completion

> **Skill ID**: S2-04
> **Skill Type**: Validation (Gap 해소 및 Spec 완성)
> **Stage**: 2 - Validation
> **Phase**: 2.4 - Spec Completion

## 1. Overview

### 1.1 Purpose

S2-03에서 분류된 Gap들을 해결하여 **Coverage 99% 이상**, **Critical Gap 0개**, **Validation Score 90점 이상**을 달성합니다. 이 Phase가 완료되면 Stage 3로 진행할 수 있습니다.

**주요 활동:**
| Activity | Description |
|----------|-------------|
| **Gap Remediation** | 각 Gap에 대한 remediation 전략 실행 |
| **Spec Update** | main.yaml 및 관련 spec 파일 보완 |
| **Validation** | 수정 후 Coverage 재계산 |
| **Documentation** | 모든 수정 사항 로깅 |

### 1.2 Success Criteria

| Metric | Target | Blocking |
|--------|--------|----------|
| Coverage | >= 99% | Yes |
| Critical Gaps | == 0 | Yes |
| Validation Score | >= 90 | Yes |
| Remediation Logged | 100% | Yes |

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **완전성** | 모든 major 이상 Gap 해결 | 99% coverage 달성 |
| **정확성** | 소스코드 기반 정확한 보완 | 잘못된 spec 방지 |
| **추적성** | 모든 수정 사항 로깅 | 감사 및 롤백 가능 |
| **일관성** | S1-04 출력 형식 준수 | 통일된 spec 구조 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S2-04는 Gap을 Remediation하며, **SQL 커버리지 99% 달성이 Gate 2.4 통과 조건**

### 1.5 Relationships

**Predecessors:**
| Skill | Input |
|-------|-------|
| `s2-03-validation-gap-analysis` | gap-analysis.yaml, gap-by-feature.yaml |
| `s1-04-discovery-spec-generation` | Original specs (main.yaml + subdirs) |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s3-01-preparation-dependency-graph` | 완성된 Spec 기반 의존성 분석 |
| `s4-03-generation-domain-batch` | 완성된 Spec 기반 코드 생성 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "s2-03-validation-gap-analysis"
    relationship: "sequential"
    outputs_used:
      - "gap-analysis.yaml"
      - "gap-by-feature.yaml"

  - skill_id: "s1-04-discovery-spec-generation"
    relationship: "cross-stage"
    outputs_used:
      - "main.yaml"
      - "api-specs/"
      - "business-logic/"
      - "data-model/"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| gap_analysis | file | `work/specs/stage2-outputs/phase3/{Priority}/{Domain}/gap-analysis.yaml` | YAML | Yes |
| gap_by_feature | file | `work/specs/stage2-outputs/phase3/{Priority}/{Domain}/gap-by-feature.yaml` | YAML | Yes |
| original_specs | directory | `work/specs/stage1-outputs/phase4/{Priority}/{Domain}/` | YAML | Yes |
| legacy_source | directory | `${LEGACY_CODEBASE}/src/main/java/` | Java | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Read | - | YAML/Java 파일 읽기 |
| Write | - | Spec 파일 생성/수정 |
| Grep | - | 소스코드 패턴 검색 |
| Glob | - | 파일 패턴 매칭 |

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: parallel
  unit: feature
  parallelization:
    max_sessions: 10
    batch_size: 50
    batch_unit: features
    timeout_minutes: 120
    retry_on_failure: 3
```

### 3.2 Completion Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Load Gaps &  │────▶│ Execute      │────▶│ Validate     │────▶│ Generate     │
│ Original Spec│     │ Remediation  │     │ Completion   │     │ Outputs      │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 3.3 Process Steps

#### Step 1: Load Inputs

**Description:** Gap 분석 결과 및 원본 Spec 로드

**Large File Reading (v1.2.0):**

> **⚠️ Read Tool Limit**: Claude Code Read 도구는 256KB 제한. 대형 도메인의 gap-analysis.yaml은 이 제한을 초과할 수 있음

```yaml
gap_analysis_loading:
  step_1:
    name: "파일 크기 확인"
    action: "Bash: wc -c < gap-analysis.yaml"

  step_2:
    name: "크기 기반 로딩"
    if_small: "전체 Read (< 200KB)"
    if_large:
      name: "offset/limit 청크 읽기"
      chunk_lines: 1500
      process: |
        total_lines=$(wc -l < gap-analysis.yaml)
        for offset in 0 1500 3000 ...; do
          Read(gap-analysis.yaml, offset=offset, limit=1500)
          # YAML 파싱 및 gaps[] 누적
        done
      note: "YAML 구조상 gap 항목 경계에서 분할 주의"

gap_by_feature_loading:
  step_1:
    name: "파일 크기 확인"
    action: "Bash: wc -c < gap-by-feature.yaml"

  step_2:
    name: "크기 기반 로딩"
    if_small: "전체 Read"
    if_large: "offset/limit 청크 읽기 (동일 전략)"
```

**Sub-steps:**
1. gap-analysis.yaml 로드 (크기 확인 후 적절한 방법 선택)
2. gap-by-feature.yaml 로드 (크기 확인 후 적절한 방법 선택)
3. Original specs (S1-04 output) 로드
4. Remediation 필요 항목 필터링

**Validation:** 모든 입력 정상 로드

---

#### Step 2: Prioritize Remediation

**Description:** Gap 해결 우선순위 결정

**Priority Order:**
1. **Critical gaps** (있다면 즉시 처리)
2. **Major gaps by feature** (feature별 그룹 처리)
3. **Minor gaps** (optional, 시간 허용 시)

**Sub-steps:**
1. gap-by-feature.yaml에서 priority_order 참조
2. Critical gap 존재 여부 확인
3. Feature별 작업 순서 결정

---

#### Step 3: Execute Remediation

**Description:** 각 Gap에 대한 remediation 전략 실행

**Remediation Actions:**

##### add_to_spec
```yaml
action: "add_to_spec"
procedure:
  1. 소스코드에서 누락된 항목 상세 분석
  2. S1-04 출력 형식에 맞게 spec 작성
  3. main.yaml 또는 해당 subdirectory 파일에 추가
  4. remediation-log에 기록
```

##### correct_spec
```yaml
action: "correct_spec"
procedure:
  1. 오류 항목 식별
  2. 소스코드에서 정확한 정보 확인
  3. 기존 spec 수정
  4. remediation-log에 수정 내역 기록
```

##### normalize_spec
```yaml
action: "normalize_spec"
procedure:
  1. 정규화 불일치 항목 식별
  2. 표준 형식으로 변환
  3. spec 업데이트
  4. remediation-log에 기록
```

##### remove_from_spec
```yaml
action: "remove_from_spec"
procedure:
  1. 제거 대상 항목 확인
  2. 제거 근거 문서화
  3. spec에서 항목 제거
  4. remediation-log에 기록
```

##### defer
```yaml
action: "defer"
procedure:
  1. 연기 사유 문서화
  2. remediation-log에 deferred로 기록
  3. 향후 처리 목록에 추가
```

---

#### Step 4: Update Spec Files

**Description:** Spec 파일 업데이트

**Output Structure (S1-04와 동일):**
```
FEAT-{DOMAIN}-{NNN}/
├── main.yaml              # Feature 메인 스펙
├── api-specs/
│   ├── openapi-spec.yaml
│   ├── dto-definitions.yaml
│   └── error-responses.yaml
├── business-logic/
│   ├── service-spec.yaml
│   ├── validation-spec.yaml
│   └── business-rules.yaml
└── data-model/
    ├── entity-spec.yaml
    └── mybatis-mapper-spec.yaml
```

**Sub-steps:**
1. 수정된 내용을 해당 파일에 반영
2. YAML 문법 검증
3. S1-04 스키마 준수 확인

---

#### Step 5: Log Remediation

**Description:** 모든 수정 사항 로깅

**Log Structure:**
```yaml
remediation_log:
  - gap_id: "GAP-PA-001"
    action: "add_to_spec"
    timestamp: "2026-01-07T13:00:00Z"
    files_modified:
      - "api-specs/openapi-spec.yaml"
    changes:
      - type: "addition"
        path: "paths./pa/PA01005/legacyReport.get"
        content: "{endpoint spec}"
    verified: true
```

---

#### Step 6: Validate Completion

**Description:** Remediation 후 Coverage 재계산

**Validation Steps:**
1. 수정된 Spec과 Ground Truth 재비교
2. Coverage 재계산
3. Critical gap 0 확인
4. Validation score 계산

**Score Formula:**
```yaml
validation_score:
  formula: "coverage * 0.7 + completeness * 0.2 + accuracy * 0.1"
  components:
    coverage: "spec_source_match_rate"
    completeness: "all_gaps_addressed_rate"
    accuracy: "no_new_errors_introduced"
```

---

#### Step 7: Generate Outputs

**Description:** 최종 산출물 생성

**Sub-steps:**
1. Completed main.yaml 저장 (S2 output 경로)
2. remediation-log.yaml 생성
3. validation-result.yaml 생성
4. 최종 검증

---

#### Step 8: Schema Validation (강화됨)

**Description:** Remediation 후 모든 산출물이 스키마를 준수하고 회귀 오류가 없는지 검증

**Schema Reference:**
- `output.schema.yaml` (이 skill 디렉토리 내)
- `../s1-04-discovery-spec-generation/output.schema.yaml` (Spec 스키마)

**3단계 검증 프로세스:**

**Step 8.1: Remediation Log/Result 스키마 검증**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | remediation-log | 필수 키 존재 | ERROR | Yes |
| V002 | validation-result | 필수 키 존재 | ERROR | Yes |
| V003 | metadata.generated_by | 정확히 일치 | ERROR | Yes |
| V004 | remediation_entries[].action | enum 검증 | ERROR | Yes |
| V005 | validation_summary.result | enum 검증 | ERROR | Yes |
| V006 | gate_evaluation.gate_id | G2.4 일치 | ERROR | Yes |
| V007 | validation_summary.coverage | 0-100 범위 | ERROR | Yes |
| V008 | validation_summary.validation_score | 0-100 범위 | ERROR | Yes |
| V009 | PASS 조건 | coverage >= 99% | ERROR | Yes |
| V010 | PASS 조건 | critical_gaps == 0 | ERROR | Yes |
| V011 | remediation_entries | 모든 entry verified | WARNING | No |

**Step 8.2: Remediated Spec 스키마 검증 (추가됨)**

> **목적:** Remediation으로 수정된 Spec 파일이 여전히 S1-04 출력 스키마를 준수하는지 확인

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V012 | main.yaml | S1-04 스키마 준수 | ERROR | Yes |
| V013 | api-specs/*.yaml | OpenAPI 3.0 유효성 | ERROR | Yes |
| V014 | business-logic/*.yaml | 필수 키 존재 | ERROR | Yes |
| V015 | data-model/*.yaml | Entity/VO 스키마 준수 | ERROR | Yes |
| V016 | sql-mybatis/*.yaml | SQL/Mapper 스키마 준수 | ERROR | Yes |

**Step 8.3: Before/After Diff 생성 및 회귀 검증 (추가됨)**

> **목적:** Remediation 전후 변경사항을 문서화하고 의도치 않은 변경(회귀)이 없는지 확인

**Sub-steps:**
1. Before spec 로드 (S1-04 출력)
2. After spec 로드 (Remediated)
3. Diff 생성: `spec-diff.yaml`
4. 회귀 검증:
   - 기존 항목 삭제 여부 확인 → WARNING
   - SQL 쿼리 변경 여부 확인 → ERROR (QUERY-FIRST 원칙 위반)
   - 필드 타입 변경 여부 확인 → WARNING

**spec-diff.yaml 스키마:**
```yaml
spec_diff:
  feature_id: "FEAT-PA-001"
  before_path: "stage1-outputs/phase4/.../main.yaml"
  after_path: "stage2-outputs/phase4/.../main.yaml"
  summary:
    added_items: 5
    modified_items: 2
    removed_items: 0  # 0이어야 함
    sql_changes: 0    # 0이어야 함 (QUERY-FIRST)
  changes:
    - type: "added"
      path: "endpoints[3]"
      description: "누락된 /save.mi 엔드포인트 추가"
    - type: "modified"
      path: "services[0].methods[2].signature"
      before: "void update(PA01001VO)"
      after: "int update(PA01001VO)"
      reason: "반환 타입 수정 (affected rows)"
  regression_check:
    status: "PASS"  # PASS/FAIL
    warnings: []
    errors: []
```

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재생성 필요
- blocking=false 오류: WARNING 로그, 계속 진행
- SQL 변경 감지: **즉시 중단**, Tech Lead 확인 필요 (QUERY-FIRST 위반)

---

### 3.4 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | Critical gap 존재 | 즉시 처리, 다른 작업 중단 | 정상 진행 |
| DP-2 | Coverage >= 99% | Gate PASS 가능 | 추가 remediation 필요 |
| DP-3 | Score 80-89 | Conditional pass 검토 | 정상 진행 |
| DP-4 | 소스 해석 불가 | Tech lead 확인 요청 | 정상 분석 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage2-outputs/phase4/"
    pattern: "{Priority}/{Domain}/FEAT-{DOMAIN}-{NNN}/"

  example: "work/specs/stage2-outputs/phase4/P2-Core/PA/FEAT-PA-001/"
```

### 4.2 Output Files

| File | Type | Purpose | Required |
|------|------|---------|----------|
| main.yaml | YAML | 완성된 Feature spec | Yes |
| api-specs/* | YAML | API 스펙 (S1-04 구조) | Yes |
| business-logic/* | YAML | 비즈니스 로직 스펙 | Yes |
| data-model/* | YAML | 데이터 모델 스펙 | Yes |
| remediation-log.yaml | YAML | 수정 이력 | Yes |
| validation-result.yaml | YAML | 검증 결과 | Yes |

### 4.3 File Header

```yaml
# Generated by: s2-04-validation-spec-completion
# Stage: 2 - Validation
# Phase: 2.4 - Spec Completion
# Domain: ${DOMAIN}
# Feature: ${FEATURE_ID}
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
# Status: COMPLETED (remediated from S1-04 output)
```

### 4.4 Output Schemas

#### main.yaml (Completed)

```yaml
# main.yaml - Completed spec
metadata:
  feature_id: "FEAT-PA-001"
  screen_id: "PA01001"
  domain: "PA"
  version: "2.0"  # S2 완료 버전
  generated_by: "s2-04-validation-spec-completion"
  generated_at: "2026-01-07T13:30:00Z"
  base_version: "1.0"  # S1-04 원본 버전
  status: "completed"

validation:
  coverage: 99.2
  validation_score: 92
  critical_gaps: 0
  remediated_gaps: 3
  deferred_gaps: 1

feature:
  name: "생산계획 조회"
  description: "생산계획 목록 및 상세 조회 기능"
  complexity: "medium"

endpoints:
  # S1-04 내용 + remediated additions
  - path: "/pa/PA01001/list"
    method: "POST"
    # ... (S1-04 구조와 동일)

# ... rest of spec (S1-04 구조와 동일)
```

#### remediation-log.yaml

```yaml
# remediation-log.yaml
metadata:
  generated_by: "s2-04-validation-spec-completion"
  generated_at: "2026-01-07T13:30:00Z"
  feature_id: "FEAT-PA-001"
  domain: "PA"

summary:
  total_gaps_processed: 4
  actions_taken:
    add_to_spec: 2
    correct_spec: 1
    defer: 1
  files_modified: 3
  validation_passed: true

remediation_entries:
  - id: "REM-001"
    gap_id: "GAP-PA-001"
    timestamp: "2026-01-07T13:00:00Z"
    action: "add_to_spec"
    severity: "major"

    before:
      state: "missing"

    after:
      state: "added"
      location: "api-specs/openapi-spec.yaml:line 45"

    changes:
      - file: "api-specs/openapi-spec.yaml"
        type: "addition"
        path: "paths./pa/PA01001/export"
        content_summary: "GET endpoint for Excel export"

    source_reference:
      file: "PA01001Controller.java"
      line: 78
      method: "exportExcel"

    verified: true
    verified_at: "2026-01-07T13:15:00Z"

  - id: "REM-002"
    gap_id: "GAP-PA-008"
    timestamp: "2026-01-07T13:05:00Z"
    action: "correct_spec"
    severity: "major"

    before:
      state: "incorrect"
      value: "method: GET"

    after:
      state: "corrected"
      value: "method: POST"

    changes:
      - file: "api-specs/openapi-spec.yaml"
        type: "modification"
        path: "paths./pa/PA01001/detail.method"
        old_value: "GET"
        new_value: "POST"

    verified: true

  - id: "REM-003"
    gap_id: "GAP-PA-015"
    timestamp: "2026-01-07T13:10:00Z"
    action: "defer"
    severity: "minor"

    reason: "Legacy utility method - low impact"
    deferred_to: "post-migration cleanup"

    verified: true
```

#### validation-result.yaml

```yaml
# validation-result.yaml
metadata:
  generated_by: "s2-04-validation-spec-completion"
  generated_at: "2026-01-07T13:30:00Z"
  feature_id: "FEAT-PA-001"
  domain: "PA"

validation_summary:
  coverage: 99.2
  validation_score: 92
  result: "PASS"

metrics:
  before_remediation:
    coverage: 94.8
    critical_gaps: 0
    major_gaps: 2
    minor_gaps: 2

  after_remediation:
    coverage: 99.2
    critical_gaps: 0
    major_gaps: 0
    minor_gaps: 1  # deferred

  improvement:
    coverage_delta: 4.4
    gaps_resolved: 3
    gaps_deferred: 1

score_breakdown:
  coverage_component: 69.4  # 99.2 * 0.7
  completeness_component: 18.0  # 90% * 0.2
  accuracy_component: 10.0  # 100% * 0.1
  total: 97.4

gate_evaluation:
  gate_id: "G2.4"
  tier: "validation_gate"
  criteria:
    - check: "coverage >= 99%"
      actual: 99.2
      result: "PASS"
    - check: "critical_gaps == 0"
      actual: 0
      result: "PASS"
    - check: "validation_score >= 90"
      actual: 92
      result: "PASS"
  overall_result: "PASS"

advance_to: "Stage 3"
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| files_exist | structural | 모든 필수 파일 존재 | ERROR | Yes |
| yaml_syntax | structural | YAML 파싱 오류 없음 | ERROR | Yes |
| coverage | metric | >= 99% | ERROR | Yes |
| critical_gaps | metric | == 0 | ERROR | Yes |
| validation_score | metric | >= 90 | ERROR | Yes |
| remediation_logged | completeness | 100% 기록 | ERROR | Yes |

### 5.2 Gate Criteria

```yaml
gate_criteria:
  id: "G2.4"
  name: "Spec Completion Gate"
  tier: "validation_gate"  # Higher threshold (90)
  threshold: 90
  metrics:
    - metric: "coverage"
      weight: 0.4
      target: ">= 99%"
      formula: "final_coverage"
      blocking: true
    - metric: "critical_gaps"
      weight: 0.3
      target: "== 0"
      formula: "count of critical gaps"
      blocking: true
    - metric: "validation_score"
      weight: 0.3
      target: ">= 90"
      formula: "coverage * 0.7 + completeness * 0.2 + accuracy * 0.1"
      blocking: true
```

### 5.3 Conditional Pass (per ADR-014)

```yaml
conditional_pass:
  enabled: true
  conditions:
    score_range: "80-89"
    critical_gaps: 0

  requirements:
    - "Remediation plan documented for remaining gaps"
    - "Timeline agreed (1 week max)"
    - "Tech lead sign-off obtained"

  tracking:
    deadline: "+7 days"
    escalation: "If not resolved, escalate to architect"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Missing input | 로드 실패 | S2-03 미완료 | S2-03 완료 후 재실행 | Yes |
| Source parse error | 분석 불가 | 복잡한 코드 | 수동 분석 요청 | No |
| Coverage not reaching | < 99% | 해결 불가 gap | Conditional pass 검토 | Yes |
| Timeout | 120분 초과 | 대규모 feature | batch 분할 | Yes |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Critical gap 해결 불가 | critical | 즉시 보고, Gate FAIL | Tech Lead |
| Coverage < 95% | major | 원인 분석, 추가 작업 | Orchestrator |
| Conditional pass 필요 | major | Tech lead 승인 요청 | Tech Lead |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 부분 실패 | 해당 Feature만 재실행 | Feature |
| 잘못된 수정 | remediation-log 기반 롤백 | Feature |
| 전체 실패 | S2-03 결과 확인 후 재실행 | Phase |

---

## 7. Examples

### 7.1 Sample Remediation

**Gap Input:**
```yaml
- id: "GAP-PA-001"
  type: "under_specification"
  dimension: "endpoint"
  severity: "major"
  source_item: "PA01001Controller.exportExcel"
  remediation:
    strategy: "add_to_spec"
```

**Source Analysis:**
```java
// PA01001Controller.java
@GetMapping("/export")
public ResponseEntity<Resource> exportExcel(
    @RequestParam String startDate,
    @RequestParam String endDate) {
    // Excel 다운로드 로직
}
```

**Spec Addition:**
```yaml
# api-specs/openapi-spec.yaml (added)
paths:
  /pa/PA01001/export:
    get:
      operationId: exportExcel
      summary: "생산계획 Excel 다운로드"
      parameters:
        - name: startDate
          in: query
          required: true
          schema:
            type: string
            format: date
        - name: endDate
          in: query
          required: true
          schema:
            type: string
            format: date
      responses:
        200:
          description: "Excel 파일"
          content:
            application/vnd.openxmlformats-officedocument.spreadsheetml.sheet:
              schema:
                type: string
                format: binary
```

### 7.2 Sample Output Summary

```yaml
# validation-result.yaml (summary)
validation_summary:
  coverage: 99.2
  validation_score: 92
  result: "PASS"

metrics:
  before_remediation:
    coverage: 94.8
    major_gaps: 2
  after_remediation:
    coverage: 99.2
    major_gaps: 0

gate_evaluation:
  overall_result: "PASS"
  advance_to: "Stage 3"
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| 0 gaps | 이미 완벽한 spec | 그대로 복사, coverage 100% |
| All deferred | minor만 존재, 모두 defer | coverage 계산에서 제외, PASS 가능 |
| Coverage stuck at 98% | 해결 불가 gap | Conditional pass 또는 FAIL |
| Critical 해결 불가 | 소스 해석 불가 | Gate FAIL, escalation |

---

## Version History

### v1.2.0 (2026-01-13)
- Step 1: Large File Reading 섹션 추가
- gap-analysis.yaml, gap-by-feature.yaml 대용량 파일 처리 지원
- offset/limit 기반 청크 읽기 전략 추가

### v1.1.0 (2026-01-08)
- Step 8: Schema Validation 추가
- s2-04-spec-completion.schema.yaml 스키마 참조
- 11개 검증 규칙 적용 (V001-V011)

### v1.0.0 (2026-01-07)
- Initial version
- Gap remediation execution
- Validation gate (90 threshold)
- Conditional pass support (ADR-014)
