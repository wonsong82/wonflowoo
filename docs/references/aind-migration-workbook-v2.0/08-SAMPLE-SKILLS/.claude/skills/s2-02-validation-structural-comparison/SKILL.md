---
name: s2-02-validation-structural-comparison
description: Use when comparing Stage 1 specs against ground truth inventory, performing bidirectional coverage analysis, or generating coverage metrics for validation (project)
---

# Structural Comparison

> **Skill ID**: S2-02
> **Skill Type**: Validation (양방향 구조 비교)
> **Stage**: 2 - Validation
> **Phase**: 2.2 - Structural Comparison

## 1. Overview

### 1.1 Purpose

Stage 1에서 생성된 Specification과 S2-01에서 생성된 Ground Truth(Source Inventory)를 **양방향으로 비교**하여 Coverage 메트릭을 산출하고 불일치 항목을 식별합니다.

**비교 방향:**
| Direction | Purpose | Identifies |
|-----------|---------|------------|
| **Forward** (Spec → Source) | Spec의 모든 항목이 Source에 있는지 | Over-specification (없는 것 정의) |
| **Backward** (Source → Spec) | Source의 모든 항목이 Spec에 있는지 | Under-specification (누락) |

**목표:**
- Overall Coverage >= 95% 달성
- 모든 불일치 항목 식별 및 문서화
- Gap Analysis (S2-03)를 위한 기초 데이터 생성

### 1.2 Validation Scope

| Dimension | Weight | Match Criteria |
|-----------|--------|----------------|
| endpoint_coverage | 0.30 | URL + HTTP Method 일치 |
| service_coverage | 0.25 | 클래스명 + 메서드명 일치 |
| sql_coverage | 0.25 | namespace + id 일치 |
| entity_coverage | 0.20 | 클래스명 + 주요 필드 일치 |

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **양방향성** | Forward + Backward 모두 수행 | 누락과 과다 모두 탐지 |
| **정규화** | 비교 전 표준 형식 변환 | 형식 차이로 인한 false negative 방지 |
| **정량화** | 모든 결과 수치화 | 객관적 품질 측정 |
| **추적성** | 각 불일치에 원본 위치 기록 | Gap 분석 시 빠른 추적 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S2-02는 Spec과 Ground Truth를 비교하며, **SQL 커버리지가 가중치 0.25로 핵심 검증 차원**

### 1.5 Relationships

**Predecessors:**
| Skill | Input |
|-------|-------|
| `s2-01-validation-source-inventory` | source-inventory.yaml (Ground Truth) |
| `s1-04-discovery-spec-generation` | main.yaml + spec files (Spec) |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s2-03-validation-gap-analysis` | 비교 결과 기반 Gap 분류 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "s2-01-validation-source-inventory"
    relationship: "sequential"
    outputs_used:
      - "source-inventory.yaml"

  - skill_id: "s1-04-discovery-spec-generation"
    relationship: "cross-stage"
    outputs_used:
      - "main.yaml"
      - "api-specs/"
      - "business-logic/"
      - "data-model/"
```

### 2.2 Comparison Sources

```yaml
comparison_sources:
  source_a:
    name: "Stage 1 Specification"
    location: "work/specs/stage1-outputs/phase4/{Priority}/{Domain}/"
    type: "spec"
    format: "YAML"

  source_b:
    name: "Ground Truth (Source Inventory)"
    location: "work/specs/stage2-outputs/phase1/{Priority}/{Domain}/source-inventory.yaml"
    type: "code"
    format: "YAML"
```

### 2.3 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| source_inventory | file | `work/specs/stage2-outputs/phase1/{Priority}/{Domain}/source-inventory.yaml` | YAML | Yes |
| stage1_specs | directory | `work/specs/stage1-outputs/phase4/{Priority}/{Domain}/` | YAML | Yes |

### 2.4 Normalization Rules

| Source | Field | Normalization |
|--------|-------|---------------|
| Spec | endpoint.path | 소문자, trailing slash 제거 |
| Spec | method_name | camelCase 유지 |
| Source | url | 소문자, trailing slash 제거 |
| Source | method_name | camelCase 유지 |
| Both | class_name | 패키지 제외, 클래스명만 |

### 2.5 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Read | - | YAML 파일 읽기 |
| Glob | - | Spec 파일 패턴 매칭 |

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: parallel
  unit: domain
  parallelization:
    max_sessions: 10
    batch_unit: domain
    timeout_minutes: 120
    retry_on_failure: 3
```

### 3.2 Validation Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Load Sources │────▶│ Normalize    │────▶│ Compare      │────▶│ Score &      │
│ (Spec + GT)  │     │ & Align      │     │ Bidirectional│     │ Report       │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 3.3 Comparison Strategy

```yaml
comparison_strategy:
  direction: "bidirectional"

  forward_check:
    name: "Spec → Source"
    purpose: "Spec의 모든 항목이 실제 소스에 존재하는지"
    identifies: "Over-specification (phantom definitions)"
    formula: "spec_items_found_in_source / total_spec_items * 100"

  backward_check:
    name: "Source → Spec"
    purpose: "실제 소스의 모든 항목이 Spec에 문서화되었는지"
    identifies: "Under-specification (missing documentation)"
    formula: "source_items_found_in_spec / total_source_items * 100"
```

### 3.4 Process Steps

#### Step 1: Load Sources

**Description:** Spec 및 Ground Truth 로드

**Sub-steps:**
1. Stage 1 Spec 파일 로드 (main.yaml + subdirectories)
2. Ground Truth (source-inventory) 로드 - **Large File Handling 적용** (v1.2.0)
3. 데이터 구조 파싱 및 검증

**Large File Reading (v1.2.0):**

> **⚠️ Read Tool Limit**: source-inventory는 256KB를 초과할 수 있음. 분할/레거시 파일 모두 지원 필요

```yaml
source_inventory_loading:
  step_1:
    name: "형식 감지"
    actions:
      - "source-inventory/ 디렉토리 존재 확인"
      - "존재하면 → 분할 형식"
      - "없으면 → 단일 파일 형식"

  step_2_chunked:
    name: "분할 형식 로드"
    actions:
      - "source-inventory/_manifest.yaml 읽기"
      - "manifest.chunks[] 순회"
      - "각 청크 파일 읽기 (controllers.yaml, services.yaml 등)"
      - "메모리에 layers 구조 재조립"

  step_2_single:
    name: "단일 파일 로드"
    check: "파일 크기 확인 (Bash: wc -c < source-inventory.yaml)"
    if_small: "전체 Read"
    if_large:
      name: "offset/limit 청크 읽기"
      process: |
        1. total_lines=$(wc -l < source-inventory.yaml)
        2. for offset in 0, 1500, 3000, ...:
             Read(file, offset=offset, limit=1500)
             # YAML 파싱 및 누적
        3. 전체 데이터 조립

  threshold_kb: 200
  chunk_lines: 1500
```

**Validation:** 두 소스 모두 정상 로드 (분할/레거시 파일 모두 지원)

---

#### Step 2: Normalize & Align

**Description:** 비교를 위한 정규화 및 정렬

**Sub-steps:**
1. URL 패턴 정규화 (소문자, trailing slash 제거)
2. 클래스명 정규화 (패키지 제외)
3. 메서드명 정규화 (대소문자 통일 옵션)
4. 비교 키 생성

**Normalization Examples:**
```yaml
# Before
spec_endpoint: "/PA/pa01001/List/"
source_endpoint: "/pa/PA01001/list"

# After (normalized)
spec_normalized: "/pa/pa01001/list"
source_normalized: "/pa/pa01001/list"
# Result: MATCH
```

---

#### Step 3: Forward Check (Spec → Source)

**Description:** Spec에 정의된 항목이 Source에 있는지 확인

**Sub-steps:**
1. Spec의 모든 항목 순회
2. 각 항목을 Source에서 검색
3. 매칭 여부 기록
4. 미매칭 항목 → Over-specification 목록

**Outputs:**
- forward_coverage: 매칭률 (%)
- over_specifications: 소스에 없는 Spec 항목 목록

---

#### Step 4: Backward Check (Source → Spec)

**Description:** Source의 모든 항목이 Spec에 있는지 확인

**Sub-steps:**
1. Source의 모든 항목 순회
2. 각 항목을 Spec에서 검색
3. 매칭 여부 기록
4. 미매칭 항목 → Under-specification 목록

**Outputs:**
- backward_coverage: 매칭률 (%)
- under_specifications: Spec에 없는 Source 항목 목록

---

#### Step 5: Dimension-wise Scoring

**Description:** 각 차원별 Coverage 계산

**Sub-steps:**
1. Endpoint 차원 점수 계산
2. Service 차원 점수 계산
3. SQL 차원 점수 계산
4. Entity 차원 점수 계산
5. 가중치 적용 Overall Score 계산

**Score Formula:**
```
overall_score = Σ(dimension_weight × dimension_coverage)
             = 0.30 × endpoint_coverage
             + 0.25 × service_coverage
             + 0.25 × sql_coverage
             + 0.20 × entity_coverage
```

---

#### Step 6: Report Generation

**Description:** comparison-report.yaml 및 coverage-matrix.yaml 생성

**Sub-steps:**
1. 비교 결과 집계
2. comparison-report.yaml 생성
3. coverage-matrix.yaml 생성
4. YAML 문법 검증

---

#### Step 7: Schema Validation

**Description:** 생성된 comparison-report.yaml 및 coverage-matrix.yaml이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | comparison-report | 필수 키 존재 | ERROR | Yes |
| V002 | coverage-matrix | 필수 키 존재 | ERROR | Yes |
| V003 | metadata.generated_by | 정확히 일치 | ERROR | Yes |
| V004 | summary.result | enum 검증 (PASS/WARNING/FAIL) | ERROR | Yes |
| V005 | matrix.dimensions[].dimension | enum 검증 | ERROR | Yes |
| V006 | matrix.dimensions[].weight | 합계 1.0 검증 | ERROR | Yes |
| V007 | coverage | 0-100 범위 검증 | ERROR | Yes |
| V008 | mismatch | 수치 일관성 검증 | WARNING | No |
| V009 | gate_evaluation.result | threshold 비교 일치 | WARNING | No |

**Sub-steps:**
1. comparison-report.yaml 파일 로드
2. coverage-matrix.yaml 파일 로드
3. 스키마 파일 로드 및 검증 규칙 적용
4. 검증 실패 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재생성 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.5 Matching Rules

#### 3.5.1 기본 매칭 규칙

| Field | Match Type | Tolerance | Notes |
|-------|------------|-----------|-------|
| endpoint.url | fuzzy | case-insensitive, trailing slash | 정규화 후 비교 |
| endpoint.method | exact | - | GET, POST 등 |
| class_name | fuzzy | 패키지 무시 | 클래스명만 비교 |
| method_name | exact | - | 완전 일치 |
| sql.id | exact | - | MyBatis SQL ID |
| field_name | fuzzy | 대소문자 | 필드명 비교 |

#### 3.5.2 시그니처 매칭 규칙 (v1.2.0 추가)

| Field | Match Type | Severity on Mismatch | Notes |
|-------|------------|----------------------|-------|
| service.method.signature | exact | MAJOR | API 호환성 영향 |
| service.method.return_type | exact | MAJOR | 반환 타입 불일치 |
| service.method.parameters | exact | MAJOR | 파라미터 불일치 |

**시그니처 비교 로직:**
```yaml
signature_comparison:
  strategy: "full_signature"
  match_criteria:
    - return_type: "완전 일치 (제네릭 포함)"
    - method_name: "완전 일치"
    - parameter_count: "개수 일치"
    - parameter_types: "순서대로 타입 일치"
  on_mismatch:
    severity: "MAJOR"
    reason: "API 호환성 문제 - 빌드 오류 가능"
```

#### 3.5.3 트랜잭션 어노테이션 매칭 규칙 (v1.2.0 추가)

| Field | Match Type | Severity on Mismatch | Notes |
|-------|------------|----------------------|-------|
| service.class_annotations | set | WARNING | @Transactional(readOnly=true) 등 |
| service.method.annotations | set | WARNING | @Transactional 등 |

**트랜잭션 비교 로직:**
```yaml
transaction_comparison:
  target_annotations:
    - "@Transactional"
    - "@Transactional(readOnly=true)"
    - "@Transactional(propagation=*)"
  strategy: "presence_check"
  on_mismatch:
    severity: "WARNING"
    reason: "트랜잭션 경계 불일치 - 데이터 무결성 위험"
```

#### 3.5.4 Entity 필드 타입 매칭 규칙 (v1.2.0 추가)

| Field | Match Type | Severity on Mismatch | Notes |
|-------|------------|----------------------|-------|
| entity.field.type | exact | MINOR | 간단 타입명 비교 |
| entity.field.java_type | fuzzy | MINOR | FQN, import alias 허용 |

**필드 타입 비교 로직:**
```yaml
field_type_comparison:
  primary: "type"  # 우선 비교
  secondary: "java_type"  # FQN 비교 (있을 경우)
  type_aliases:
    - "String" ↔ "java.lang.String"
    - "Integer" ↔ "java.lang.Integer"
    - "Long" ↔ "java.lang.Long"
  on_mismatch:
    severity: "MINOR"
    reason: "필드 타입 불일치 - 형변환 이슈 가능"
```

### 3.6 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | Coverage >= 95% | PASS 처리 | Gap Analysis 필요 표시 |
| DP-2 | Coverage 90-95% | WARNING + Gap Analysis | Gap Analysis 필요 표시 |
| DP-3 | Coverage < 90% | ERROR + 상세 분석 필요 | - |
| DP-4 | Critical 불일치 발견 | 즉시 보고 | 정상 진행 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage2-outputs/phase2/"
    pattern: "{Priority}/{Domain}/"

  example: "work/specs/stage2-outputs/phase2/P2-Core/PA/"
```

### 4.2 Output Files

| File | Type | Purpose | Required |
|------|------|---------|----------|
| comparison-report.yaml | YAML | 상세 비교 결과 | Yes |
| coverage-matrix.yaml | YAML | 차원별 Coverage 매트릭스 | Yes |

### 4.3 File Header

```yaml
# Generated by: s2-02-validation-structural-comparison
# Stage: 2 - Validation
# Phase: 2.2 - Structural Comparison
# Domain: ${DOMAIN}
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
```

### 4.4 Output Schemas

#### comparison-report.yaml

```yaml
# comparison-report.yaml
metadata:
  generated_by: "s2-02-validation-structural-comparison"
  generated_at: "2026-01-07T11:00:00Z"
  domain: "PA"
  sources:
    spec: "work/specs/stage1-outputs/phase4/P2-Core/PA/"
    ground_truth: "work/specs/stage2-outputs/phase1/P2-Core/PA/source-inventory.yaml"

summary:
  overall_coverage: 96.5
  forward_coverage: 98.2  # Spec → Source
  backward_coverage: 94.8  # Source → Spec
  total_spec_items: 1245
  total_source_items: 1312
  matched_items: 1201
  mismatched_items: 111
  result: "PASS"  # PASS, WARNING, FAIL

forward_check:
  coverage: 98.2
  total_items: 1245
  matched: 1222
  missing_in_source: 23
  over_specifications:
    - item: "PA01099Controller.getArchiveList"
      type: "endpoint"
      spec_location: "api-specs/openapi-spec.yaml:line 234"
      reason: "Controller not found in source"
    # ... more items

backward_check:
  coverage: 94.8
  total_items: 1312
  matched: 1244
  missing_in_spec: 68
  under_specifications:
    - item: "PA01005Controller.getLegacyReport"
      type: "endpoint"
      source_location: "src/main/java/com/hallain/pa/controller/PA01005Controller.java:line 45"
      reason: "Endpoint not documented in spec"
    # ... more items

by_dimension:
  endpoints:
    forward_coverage: 97.5
    backward_coverage: 93.2
    mismatches: 34
  services:
    forward_coverage: 98.0
    backward_coverage: 95.1
    mismatches: 28
  sql:
    forward_coverage: 99.1
    backward_coverage: 96.3
    mismatches: 21
  entities:
    forward_coverage: 98.8
    backward_coverage: 94.2
    mismatches: 28

discrepancies:
  - id: "DISC-001"
    type: "missing_in_spec"
    dimension: "endpoint"
    source_item: "PA01005Controller.getLegacyReport"
    source_file: "PA01005Controller.java"
    source_line: 45
    severity: "major"  # critical, major, minor

  # v1.2.0 추가: 시그니처 불일치
  - id: "DISC-002"
    type: "signature_mismatch"
    dimension: "service"
    source_item: "PA01001Service.getList"
    spec_signature: "List<PA01001VO> getList()"
    source_signature: "List<PA01001VO> getList(PA01001SearchVO)"
    severity: "major"
    reason: "파라미터 불일치 - API 호환성 문제"

  # v1.2.0 추가: 트랜잭션 어노테이션 불일치
  - id: "DISC-003"
    type: "annotation_mismatch"
    dimension: "service"
    source_item: "PA01001ServiceImpl.save"
    spec_annotations: []
    source_annotations: ["@Transactional"]
    severity: "warning"
    reason: "트랜잭션 경계 누락"

  # v1.2.0 추가: 필드 타입 불일치
  - id: "DISC-004"
    type: "field_type_mismatch"
    dimension: "entity"
    source_item: "PA01001VO.planQty"
    spec_type: "String"
    source_type: "Integer"
    severity: "minor"
    reason: "필드 타입 불일치 - 형변환 필요"
  # ... more discrepancies
```

#### coverage-matrix.yaml

```yaml
# coverage-matrix.yaml
metadata:
  generated_by: "s2-02-validation-structural-comparison"
  generated_at: "2026-01-07T11:00:00Z"
  domain: "PA"

matrix:
  dimensions:
    - dimension: "endpoint"
      weight: 0.30
      spec_count: 512
      source_count: 549
      matched_count: 498
      forward_coverage: 97.3
      backward_coverage: 90.7
      weighted_score: 28.2

    - dimension: "service"
      weight: 0.25
      spec_count: 678
      source_count: 698
      matched_count: 665
      forward_coverage: 98.1
      backward_coverage: 95.3
      weighted_score: 24.2

    - dimension: "sql"
      weight: 0.25
      spec_count: 456
      source_count: 478
      matched_count: 452
      forward_coverage: 99.1
      backward_coverage: 94.6
      weighted_score: 24.2

    - dimension: "entity"
      weight: 0.20
      spec_count: 234
      source_count: 256
      matched_count: 228
      forward_coverage: 97.4
      backward_coverage: 89.1
      weighted_score: 18.7

  totals:
    overall_score: 95.3
    forward_average: 98.0
    backward_average: 92.4
    total_mismatches: 111

gate_evaluation:
  threshold: 95.0
  actual_score: 95.3
  result: "PASS"
  margin: 0.3
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| files_exist | structural | 두 파일 모두 존재 | ERROR | Yes |
| yaml_syntax | structural | YAML 파싱 오류 없음 | ERROR | Yes |
| coverage_threshold | metric | overall >= 95% | WARNING/ERROR | Yes |
| no_critical | content | critical 불일치 0개 | ERROR | Yes |

### 5.2 Coverage Requirements

| Metric | Warning | Pass | Excellent |
|--------|---------|------|-----------|
| Overall Coverage | 90-94% | 95-97% | >= 98% |
| Forward Coverage | < 95% | 95-99% | 100% |
| Backward Coverage | < 93% | 93-97% | >= 98% |

### 5.3 Gate Criteria

```yaml
gate_criteria:
  id: "G2.2"
  name: "Comparison Gate"
  tier: "phase_gate"
  threshold: 70
  metrics:
    - metric: "file_exists"
      weight: 0.2
      target: "true"
      formula: "comparison-report.yaml AND coverage-matrix.yaml exist"
    - metric: "coverage_threshold"
      weight: 0.6
      target: ">= 95%"
      formula: "overall_coverage"
    - metric: "no_critical"
      weight: 0.2
      target: "0"
      formula: "count of critical discrepancies"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Source file missing | 로드 실패 | S2-01 미완료 | S2-01 완료 후 재실행 | Yes |
| Spec file missing | 로드 실패 | S1-04 미완료 | S1-04 완료 확인 | Yes |
| Normalization mismatch | false negative | 패턴 불일치 | 정규화 규칙 조정 | Yes |
| Large domain timeout | 120분 초과 | PA 도메인 | 병렬 처리 강화 | Yes |
| **Large input file** (v1.3.0) | Read tool 256KB 초과 | 대형 도메인 source-inventory | 분할 형식 또는 offset/limit 읽기 (Step 1) | Auto |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Coverage < 90% | critical | Phase 중단, 원인 분석 | Tech Lead |
| Coverage 90-95% | major | WARNING 로그, 계속 진행 | Orchestrator |
| Critical 불일치 > 5 | major | 즉시 보고 | Tech Lead |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 부분 실패 | 해당 도메인만 재실행 | Domain |
| 입력 파일 오류 | 선행 Phase 확인 | Phase |
| 비정상 Coverage | 정규화 규칙 검토 후 재실행 | Phase |

---

## 7. Examples

### 7.1 Sample Comparison

**Spec (Stage 1):**
```yaml
endpoints:
  - path: "/pa/PA01001/list"
    method: "POST"
    controller: "PA01001Controller"
  - path: "/pa/PA01001/detail"
    method: "POST"
    controller: "PA01001Controller"
```

**Ground Truth (Source):**
```yaml
controllers:
  - class: "PA01001Controller"
    methods:
      - name: "getList"
        url: "/pa/PA01001/list"
        http_method: "POST"
      - name: "getDetail"
        url: "/pa/PA01001/detail"
        http_method: "POST"
      - name: "exportExcel"
        url: "/pa/PA01001/export"
        http_method: "GET"
```

### 7.2 Sample Output

```yaml
# comparison-report.yaml (simplified)
summary:
  overall_coverage: 66.7
  forward_coverage: 100.0  # 2/2 spec items found
  backward_coverage: 66.7  # 2/3 source items found

forward_check:
  coverage: 100.0
  missing_in_source: []

backward_check:
  coverage: 66.7
  missing_in_spec:
    - item: "PA01001Controller.exportExcel"
      type: "endpoint"
      source_location: "PA01001Controller.java:line 78"

discrepancies:
  - id: "DISC-001"
    type: "missing_in_spec"
    dimension: "endpoint"
    source_item: "PA01001Controller.exportExcel"
    severity: "major"
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| 100% 일치 | Spec = Source | Coverage 100%, discrepancies 0 |
| Spec만 있음 | Source 비어있음 | Forward 0%, Backward N/A |
| Source만 있음 | Spec 비어있음 | Forward N/A, Backward 0% |
| URL 대소문자 차이 | /PA/List vs /pa/list | 정규화 후 MATCH |

---

## Version History

### v1.3.0 (2026-01-13)
- **Large File Reading 추가**
  - Step 1: source-inventory 대용량 파일 읽기 지원
  - 분할 형식 (source-inventory/ 디렉토리) 지원
  - 레거시 단일 파일 offset/limit 읽기 지원
  - Known Issues에 Large input file 추가

### v1.2.0 (2026-01-13)
- 3.5.2: 시그니처 매칭 규칙 추가 (parameters, return_type, signature)
- 3.5.3: 트랜잭션 어노테이션 매칭 규칙 추가 (class_annotations, method annotations)
- 3.5.4: Entity 필드 타입 매칭 규칙 추가 (type, java_type)
- discrepancy 유형 확장: signature_mismatch, annotation_mismatch, field_type_mismatch

### v1.1.0 (2026-01-08)
- Step 7: Schema Validation 추가
- s2-02-comparison-report.schema.yaml 스키마 참조
- 9개 검증 규칙 (V001-V009) 적용
- 수치 일관성 검증 추가

### v1.0.0 (2026-01-07)
- Initial version
- Bidirectional comparison 구현
- 4-Dimension weighted scoring
- Normalization rules 적용
