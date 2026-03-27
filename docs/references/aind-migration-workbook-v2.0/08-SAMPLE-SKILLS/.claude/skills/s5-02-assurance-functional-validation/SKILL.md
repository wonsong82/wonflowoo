---
name: s5-02-assurance-functional-validation
description: Use when validating generated code matches feature specifications, performing bidirectional Spec-to-Code comparison, or measuring functional coverage for migration validation (project)
---

# Functional Validation

> **Skill ID**: S5-02
> **Skill Type**: Validation (Feature-Level Parallel)
> **Stage**: 5 - Assurance
> **Phase**: 5.2 - Functional Validation
> **Parallelization**: Feature-level (max 10 sessions, batch 50 features)
> **Validation Type**: Bidirectional (Spec -> Code, Code -> Spec)

## 1. Overview

### 1.1 Purpose

생성된 코드가 **Feature 명세(Stage 2 Output)와 기능적으로 일치**하는지 양방향으로 검증합니다. 명세에 정의된 API가 코드에 구현되었는지(Forward), 코드에 구현된 기능이 명세에 있는지(Backward) 모두 확인합니다.

**검증 대상:**
- API Endpoint 일치성
- Business Logic 구현 여부
- Data Access 패턴 일치
- Integration Points 검증

**검증 방향:**
- **Forward (Spec -> Code)**: 명세의 모든 항목이 코드에 있는가?
- **Backward (Code -> Spec)**: 코드의 모든 기능이 명세에 있는가?

### 1.2 Scope

**In Scope:**
- Endpoint 존재 및 시그니처 검증
- Service 메서드 구현 검증
- Mapper/Repository 쿼리 검증
- Request/Response DTO 일치 검증

**Out of Scope:**
- 구조적 표준 검증 (-> S5-01)
- API 계약 테스트 (-> S5-03)
- 성능 분석 (-> S5-04)

### 1.3 Validation Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Endpoint Match** | 25% | URL, HTTP Method, Parameter 일치 |
| **Business Logic** | 30% | Service 로직 구현 완전성 |
| **Data Access** | 25% | Mapper 쿼리, SP 호출 일치 |
| **Integration** | 20% | Cross-domain 호출, 외부 연동 |

### 1.4 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Bidirectional** | 양방향 검증 필수 | Over/Under-specification 탐지 |
| **Feature-Centric** | Feature 단위 검증 | 병렬 처리 효율성 |
| **Weighted Scoring** | 차원별 가중 점수 | 중요도 반영 |
| **Threshold-Based** | 임계값 기반 판정 | 일관된 품질 기준 |
| **QUERY-FIRST** | SQL 보존 100% 필수 | Legacy 호환성 보장 |

### 1.5 SQL Fidelity Gate (MANDATORY)

> **CRITICAL**: Query 이관이 어떤 Task보다 우선한다. SQL Fidelity 검증이 다른 모든 검증보다 먼저 수행되어야 한다.

```yaml
SQL_Fidelity_Gate:
  name: "SQL Fidelity Validation Gate"
  type: "Blocking"
  priority: P0  # 다른 검증보다 우선

  inputs:
    legacy_sqlmap: "hallain/src/main/resources/com/halla/{domain}/sqlmap/"
    generated_mapper: "next-hallain/src/main/resources/mapper/{domain}/"

  validation_scope:
    priority_domains:
      - MM: 126  # 케이스 발생 도메인 - 전수 검사
      - PA: 456  # 최대 도메인
      - SC: 131  # 복잡 도메인
    total_features: 713

  per_feature_checks:
    - check: "테이블명 100% 일치"
      example: "FROM EMM_PRCH_APRV_DTL EE, EMM_PRCH_APRV FF"
      on_mismatch: "BLOCK"

    - check: "컬럼명 100% 일치"
      example: "EE.MAT_ORD_NO, FF.ORD_PRG_STAT_CD"
      on_mismatch: "BLOCK"

    - check: "JOIN 조건 100% 일치"
      example: "EE.MAT_ORD_NO = FF.MAT_ORD_NO"
      prohibited: "A.ORD_NO = B.ORD_NO 와 같은 축약/추측"
      on_mismatch: "BLOCK"

    - check: "WHERE 절 조건값 100% 일치"
      example: "ORD_PRG_STAT_CD IN (10,20,30)"
      prohibited: "IN ('20', '30', '40', '50') 와 같은 값 변경"
      on_mismatch: "BLOCK"

    - check: "리터럴 값 100% 일치"
      example: "INOUT_FLAG_CD = 'INPRCH'"
      prohibited: "INOUT_FLAG_CD = '1' 와 같은 값 변경"
      on_mismatch: "BLOCK"

    - check: "GROUP BY/ORDER BY 100% 일치"
      example: "GROUP BY ROLLUP((MAT_CD3, GOODS_NM3), (MAT_CD2, GOODS_NM2))"
      on_mismatch: "BLOCK"

    - check: "DECODE/CASE 로직 100% 일치"
      example: "DECODE(ORD_CANC_FLAG_CD, 'N', 1, 'C', -1)"
      prohibited: "NVL(...) != 'Y' 와 같은 로직 간소화"
      on_mismatch: "BLOCK"

  pass_criteria:
    match_rate: 100%  # 99%도 불가

  allowed_changes:
    - "#var# → #{var} 파라미터 바인딩"
    - "$var$ → ${var} 변수 치환"
    - "<isNotEmpty> → <if test> 동적 SQL 태그"
    - "parameterClass → parameterType 속성"
    - "namespace 변경 (MyBatis 형식)"

  on_fail:
    actions:
      - generate_mismatch_report()
      - block_stage_progression()
      - require_human_review()
    output: "work/specs/stage5-outputs/phase2/sql-fidelity-report.yaml"

  verification_procedure:
    per_statement:
      1. "Legacy sqlmap 열기"
      2. "Generated Mapper XML 열기"
      3. "Statement별 Line-by-Line 비교"
      4. "Checklist 항목별 검증"
      5. "미스매치 발견 시 BLOCK"
```

**Case Study Reference (MM0101051M):**
```yaml
# 케이스 분석: MM0101051M (자재발주 대 실적현황)
root_cause: "Stage 1 스펙 기반 SQL 재생성 (Legacy sqlmap 직접 복사 안함)"

mismatch_examples:
  - location: "EMM_PRCH_APRV 조인"
    legacy: "EE.MAT_ORD_NO = FF.MAT_ORD_NO"
    generated: "A.ORD_NO = B.ORD_NO"
    issue: "컬럼명 축약 추측"

  - location: "INOUT_FLAG_CD 값"
    legacy: "= 'INPRCH'"
    generated: "= '1'"
    issue: "값 임의 변경"

  - location: "ORD_PRG_STAT_CD"
    legacy: "IN ('10', '20', '30')"
    generated: "IN ('20', '30', '40', '50')"
    issue: "비즈니스 로직 변조"

resolution: "Legacy 쿼리 기반 전체 재작성"
```

### 1.6 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s5-01-assurance-structural-check` | 구조 검증 완료 필요 |
| `s2-04-validation-spec-completion` | 완성된 명세 필요 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s5-03-assurance-api-contract-test` | 기능 검증 후 계약 테스트 |
| `s5-05-assurance-quality-gate` | 검증 결과 종합 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S5-01"
    skill_name: "s5-01-assurance-structural-check"
    status: "completed"
    artifacts:
      - "structural-report.yaml"
      - "result: PASS"

  - skill_id: "S2-04"
    skill_name: "s2-04-validation-spec-completion"
    status: "completed"
    artifacts:
      - "Completed feature specs"
      - "coverage >= 99%"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| generated_code | directory | `next-hallain/src/main/java/` | Java | Yes |
| feature_specs | directory | `work/specs/stage2-outputs/phase4/` | YAML | Yes |
| structural_report | file | `work/specs/stage5-outputs/phase1/structural-report.yaml` | YAML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Task | - | 병렬 Feature 검증 |
| Read | - | Spec/Code 읽기 |
| Grep | - | 코드 패턴 검색 |
| Glob | - | 파일 탐색 |

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: parallel
  unit: feature
  parallelization:
    enabled: true
    max_sessions: 10
    batch_size: 50
    session_timeout_minutes: 60
    retry_on_failure: 2

task:
  naming_pattern: "FVAL-{FEAT_ID}"
  granularity: feature
```

### 3.2 Bidirectional Validation Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  BIDIRECTIONAL VALIDATION PIPELINE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    FORWARD CHECK (Spec → Code)                   │   │
│   │                                                                   │   │
│   │   Feature Spec ──▶ For each item ──▶ Find in Code ──▶ Match?    │   │
│   │                                                                   │   │
│   │   Missing in Code = Under-implementation                          │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    BACKWARD CHECK (Code → Spec)                  │   │
│   │                                                                   │   │
│   │   Generated Code ──▶ For each item ──▶ Find in Spec ──▶ Match?  │   │
│   │                                                                   │   │
│   │   Missing in Spec = Over-implementation                           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│                              ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      SCORE CALCULATION                           │   │
│   │                                                                   │   │
│   │   final_score = Σ(dimension_weight × dimension_score)            │   │
│   │   Result = final_score >= 85 ? PASS :                            │   │
│   │            final_score >= 50 ? CONDITIONAL : FAIL                │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   NOTE: "final_score" = per-feature score                               │
│         "average_score" = aggregate across all features (Gate G5.2)     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Dimension Validation Details

#### 3.3.1 Endpoint Match (Weight: 25%)

```yaml
endpoint_validation:
  checks:
    - url_path: "exact match"
    - http_method: "exact match"
    - request_params: "name and type match"
    - response_type: "structure match"

  scoring:
    full_match: 100
    path_match_only: 50
    partial_match: 25
    no_match: 0

  example:
    spec:
      path: "/api/pa/pa01001/list"
      method: "POST"
      request: "PA01001SearchRequest"
      response: "List<PA01001Response>"
    code:
      controller: "PA01001Controller"
      mapping: "@PostMapping(\"/list\")"
      class_mapping: "@RequestMapping(\"/api/pa/pa01001\")"
```

#### 3.3.2 Business Logic (Weight: 30%)

```yaml
business_logic_validation:
  checks:
    - service_method_exists: "Method signature match"
    - logic_implementation: "Core logic presence"
    - validation_rules: "Input validation"
    - exception_handling: "Error cases covered"

  scoring:
    full_implementation: 100
    method_exists_only: 60
    partial_logic: 40
    missing: 0

  verification_approach:
    - "Service method presence check"
    - "Mapper call verification"
    - "Transaction annotation check"
```

#### 3.3.3 Data Access (Weight: 25%)

```yaml
data_access_validation:
  checks:
    - mapper_method_exists: "Method signature"
    - sql_operation_match: "SELECT/INSERT/UPDATE/DELETE"
    - parameter_binding: "Parameter names match"
    - sp_call_match: "Stored procedure calls"

  scoring:
    full_match: 100
    method_exists_only: 50
    different_operation: 25
    missing: 0

  verification_approach:
    - "Mapper interface method check"
    - "MyBatis XML query presence"
    - "Parameter type verification"
```

#### 3.3.4 Integration (Weight: 20%)

```yaml
integration_validation:
  checks:
    - cross_domain_calls: "Service-to-service calls"
    - external_apis: "External system integration"
    - event_publishing: "Event-driven patterns"

  scoring:
    all_integrations_present: 100
    partial_integration: 50
    missing_critical: 0

  verification_approach:
    - "Dependency injection check"
    - "External client usage"
    - "Event publisher usage"
```

### 3.4 Process Steps

#### Step 1: Load Feature Spec

**Description:** Feature 명세 로드 및 파싱

**Sub-steps:**
1. Feature spec YAML 로드
2. API endpoints 추출
3. Business logic 요구사항 추출
4. Data access 요구사항 추출

**Spec Structure Expected:**
```yaml
# FEAT-PA-001/main.yaml
feature:
  id: "FEAT-PA-001"
  domain: "PA"
  screen: "PA01001"

api_endpoints:
  - path: "/api/pa/pa01001/list"
    method: "POST"
    request_type: "PA01001SearchRequest"
    response_type: "List<PA01001Response>"
    description: "목록 조회"

  - path: "/api/pa/pa01001/save"
    method: "POST"
    request_type: "List<PA01001SaveRequest>"
    response_type: "void"
    description: "저장"

business_logic:
  service: "PA01001Service"
  methods:
    - name: "getList"
      input: "PA01001SearchRequest"
      output: "List<PA01001Response>"
      logic: "Mapper 조회 후 Response 변환"

data_access:
  mapper: "PA01001Mapper"
  operations:
    - name: "selectList"
      type: "SELECT"
      parameters: ["siteCd", "startDate", "endDate"]
```

**Validation:** Spec 로드 완료

---

#### Step 2: Forward Check (Spec -> Code)

**Description:** 명세에 정의된 모든 항목이 코드에 구현되었는지 확인

**Sub-steps:**
1. 각 endpoint에 대해:
   - Controller에서 해당 mapping 검색
   - Method signature 일치 확인
2. 각 business logic에 대해:
   - Service 클래스 존재 확인
   - Method 존재 및 로직 확인
3. 각 data access에 대해:
   - Mapper interface 확인
   - MyBatis XML 쿼리 확인

**Forward Check Output:**
```yaml
forward_check:
  total_items: 10
  matched: 9
  missing: 1
  coverage: 90%

  missing_in_code:
    - spec_item: "POST /api/pa/pa01001/delete"
      expected_in: "PA01001Controller"
      status: "NOT_FOUND"
      severity: "major"
```

**Validation:** Forward coverage >= 90%

---

#### Step 3: Backward Check (Code -> Spec)

**Description:** 코드에 구현된 모든 기능이 명세에 정의되었는지 확인

**Sub-steps:**
1. Controller의 모든 endpoint 추출
2. Service의 모든 public method 추출
3. Mapper의 모든 method 추출
4. 각 항목이 Spec에 있는지 확인

**Backward Check Output:**
```yaml
backward_check:
  total_items: 11
  matched: 10
  extra: 1
  coverage: 91%

  missing_in_spec:
    - code_item: "POST /api/pa/pa01001/export"
      found_in: "PA01001Controller"
      status: "NOT_IN_SPEC"
      severity: "minor"  # 추가 기능은 minor
```

**Validation:** Backward coverage >= 85%

---

#### Step 4: Dimension Scoring

**Description:** 각 검증 차원별 점수 계산

**Sub-steps:**
1. Endpoint Match 점수 계산
2. Business Logic 점수 계산
3. Data Access 점수 계산
4. Integration 점수 계산

**Scoring Formula:**
```python
endpoint_score = matched_endpoints / total_endpoints * 100
business_score = (full_impl * 1.0 + partial * 0.5) / total * 100
data_access_score = matched_queries / total_queries * 100
integration_score = matched_integrations / total_integrations * 100

final_score = (
    endpoint_score * 0.25 +
    business_score * 0.30 +
    data_access_score * 0.25 +
    integration_score * 0.20
)
```

**Validation:** Score 계산 완료

---

#### Step 5: Report Generation

**Description:** Feature별 검증 리포트 생성

**Sub-steps:**
1. 검증 결과 집계
2. 점수 산정
3. Gap 목록 생성
4. 리포트 파일 생성

**Validation:** 리포트 생성 완료

---

#### Step 8: Schema Validation

**Description:** 생성된 validation-summary.yaml이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | root | metadata, summary, by_dimension, by_domain, gate_evaluation 필수 키 존재 | ERROR | Yes |
| V002 | metadata.generated_by | 정확히 "s5-02-assurance-functional-validation" | ERROR | Yes |
| V003 | summary.result | enum: PASS, CONDITIONAL, FAIL | ERROR | Yes |
| V004 | discrepancies[].direction | enum: forward, backward | ERROR | Yes |
| V005 | discrepancies[].dimension | enum: endpoint, business_logic, data_access, integration | ERROR | Yes |
| V006 | gate_evaluation.gate_id | 정확히 "G5.2" | ERROR | Yes |
| V007 | by_dimension | endpoint_match, business_logic, data_access, integration 모두 존재 | ERROR | Yes |
| V008 | summary.pass_rate | 범위: 0-100 | ERROR | Yes |
| V009 | summary.overall_score | 범위: 0-100 | ERROR | Yes |
| V010 | pass_rate | 계산된 값과 일치 | WARNING | No |
| V011 | result | PASS 시 pass_rate >= 90% | ERROR | Yes |
| V012 | by_dimension | dimension weights 합계 == 1.0 | WARNING | No |

**Sub-steps:**
1. validation-summary.yaml 스키마 검증
2. Dimension 가중치 검증
3. Gate 결과 일관성 검증
4. 오류 발생 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재검증 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.5 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | Spec 로드 성공 | Forward Check | Skip (ERROR) |
| DP-2 | Forward >= 90% | Backward Check | Gap 기록 |
| DP-3 | final_score >= 85 | PASS | final_score >= 50 ? CONDITIONAL : FAIL |
| DP-4 | FAIL | Remediation 생성 | 완료 |

**Score Terminology:**
- `final_score`: Per-feature weighted score (used in DP-3)
- `average_score`: Aggregate score across all features (used in Gate G5.2)

---

### 3.6 Large File Handling

> **⚠️ Read Tool Limit**: Claude Code Read tool has 256KB file size limit. Large input files require chunked reading.

#### Input Files That May Be Large

| Input | Location | Potential Size | Chunking Strategy |
|-------|----------|----------------|-------------------|
| Feature Specs | `work/specs/stage2-outputs/phase4/` | >200KB aggregate | Directory-based |
| Structural Report | `work/specs/stage5-outputs/phase1/` | Usually small | Offset/limit if large |
| SQL Fidelity Report | `work/specs/stage5-outputs/phase2/` | May be large | Domain-based split |

#### Reading Strategy for Feature Specs

```yaml
feature_specs_reading:
  strategy: "domain_scoped_parallel"
  description: |
    각 검증 세션은 자신이 담당하는 도메인/Feature의 Spec만 읽음
    전체 Inventory를 메모리에 로드하지 않음

  process:
    step_1: "디렉토리 구조 확인"
    step_2:
      - check: "chunked 형태인지 확인 (e.g., feature-inventory/)"
      - if_chunked: "_manifest.yaml 기반 청크별 읽기"
      - if_single: "파일 크기 확인 후 처리"
    step_3: "Feature별 개별 spec 파일 읽기"

  per_session:
    1: "할당된 Feature 목록 수신"
    2: "Feature별 main.yaml 개별 읽기"
    3: "검증 후 결과 반환"
    note: "전체 Inventory 로드 대신 Feature별 개별 접근"
```

#### Chunked Input Handling

```yaml
chunked_input_handling:
  # Stage 2 output may be chunked (source-inventory/)
  workflow:
    1_detect_format:
      action: "Check if directory or single file"
      directory_check: "ls -d source-inventory/ 2>/dev/null"

    2_if_chunked:
      action: "Read manifest then process chunks"
      steps:
        - "Read _manifest.yaml"
        - "For each chunk in manifest.chunks"
        - "  Read chunk.file"
        - "  Process and accumulate"

    3_if_single_large:
      action: "Use offset/limit reading"
      chunk_lines: 1500
      pattern: |
        for offset in range(0, total_lines, 1500):
          Read(file, offset=offset, limit=1500)
          # Parse and accumulate
```

#### SQL Fidelity Report Handling

```yaml
sql_fidelity_report:
  # May be large for domains with many features (PA: 456, MM: 126)
  threshold_kb: 200

  output_strategy:
    when_small: "single sql-fidelity-report.yaml"
    when_large:
      directory: "sql-fidelity-report/"
      files:
        - "_manifest.yaml"  # index + summary
        - "domain-mm.yaml"  # MM domain results
        - "domain-pa.yaml"  # PA domain results
        - "domain-sc.yaml"  # SC domain results
        # ... other domains

  reading_for_aggregation:
    method: "manifest_based"
    process: |
      1. Read _manifest.yaml for summary
      2. Read individual domain files as needed
      3. Aggregate for final report
```

#### Parallel Session Memory Optimization

```yaml
parallel_session_optimization:
  max_sessions: 10
  per_session_strategy:
    - "Feature 단위 처리 (batch 50)"
    - "처리 완료된 Feature 데이터 즉시 해제"
    - "결과만 aggregation 파일에 기록"
    - "대형 도메인(PA, MM)은 추가 분할"

  domain_splitting:
    PA: "3 sessions (150 features each)"
    MM: "1 session"
    others: "shared sessions"
```

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage5-outputs/phase2/"

  per_feature:
    pattern: "{Priority}/{Domain}/{Feature_ID}/"
    files:
      - "functional-validation.yaml"

  summary:
    - "validation-summary.yaml"
```

### 4.2 Output Files Summary

```
work/specs/stage5-outputs/phase2/
├── validation-summary.yaml           # 전체 요약
├── P0/
│   └── CM/
│       └── FEAT-CM-001/
│           └── functional-validation.yaml
├── P1/
│   └── SM/
│       └── FEAT-SM-001/
│           └── functional-validation.yaml
└── P2/
    ├── PA/
    │   ├── FEAT-PA-001/
    │   │   └── functional-validation.yaml
    │   └── FEAT-PA-002/
    │       └── functional-validation.yaml
    └── MM/
        └── ...
```

### 4.3 Output Schema

```yaml
# functional-validation.yaml (per feature)
metadata:
  generated_by: "s5-02-assurance-functional-validation"
  generated_at: "${TIMESTAMP}"
  feature_id: "${FEATURE_ID}"
  domain: "${DOMAIN}"

spec_reference:
  path: "work/specs/stage2-outputs/phase4/P2/PA/FEAT-PA-001/main.yaml"
  version: "1.0.0"

forward_check:
  total_items: 12
  matched: 11
  missing: 1
  coverage: 91.7%
  details:
    endpoints:
      total: 4
      matched: 4
      missing: 0
    business_logic:
      total: 4
      matched: 3
      missing: 1
    data_access:
      total: 4
      matched: 4
      missing: 0

backward_check:
  total_items: 13
  matched: 12
  extra: 1
  coverage: 92.3%
  extra_in_code:
    - item: "exportToExcel method"
      type: "service_method"
      severity: "info"

dimension_scores:
  endpoint_match:
    score: 100
    weight: 0.25
    weighted: 25.0
  business_logic:
    score: 85
    weight: 0.30
    weighted: 25.5
  data_access:
    score: 100
    weight: 0.25
    weighted: 25.0
  integration:
    score: 80
    weight: 0.20
    weighted: 16.0

final_score: 91.5
result: "PASS"  # PASS (>=85) | CONDITIONAL (>=50) | FAIL (<50)

gaps:
  - id: "GAP-001"
    type: "missing_in_code"
    category: "business_logic"
    severity: "major"
    spec_item: "deleteRecord method in PA01001Service"
    expected: "public void deleteRecord(String id)"
    found: null
    recommendation: "Implement deleteRecord method"

remediation_required: false
```

### 4.4 Summary Output Schema

```yaml
# validation-summary.yaml
metadata:
  generated_by: "s5-02-assurance-functional-validation"
  generated_at: "${TIMESTAMP}"
  total_features: 700
  validated_features: 700

overall_summary:
  average_score: 88.5
  passed: 630
  conditional: 50
  failed: 20
  pass_rate: 90.0%

by_domain:
  PA:
    features: 200
    average_score: 89.2
    passed: 185
    conditional: 10
    failed: 5
  MM:
    features: 100
    average_score: 87.8
    passed: 88
    conditional: 8
    failed: 4
  # ...

by_dimension:
  endpoint_match:
    average: 95.2%
  business_logic:
    average: 85.3%
  data_access:
    average: 92.1%
  integration:
    average: 78.5%

critical_gaps:
  total: 25
  by_category:
    missing_endpoint: 5
    missing_business_logic: 15
    missing_data_access: 3
    missing_integration: 2

gate_result:
  passed: true  # average_score >= 85 AND pass_rate >= 90%
  criteria_met:
    - "average_score: 88.5 >= 85"
    - "pass_rate: 90.0% >= 90%"
    - "no_critical_failures: 0 features with score < 50"
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| average_score | metric | >= 85 | FAIL | Yes |
| no_critical_failures | metric | no feature with score < 50 | FAIL | Yes |
| pass_rate | metric | >= 90% | FAIL | Yes |
| all_features_validated | structural | 100% features processed | ERROR | Yes |

### 5.2 Gate Criteria

```yaml
gate_criteria:
  id: "G5.2"
  name: "Functional Validation Gate"
  threshold: 90

  metrics:
    - metric: "average_score"
      weight: 0.4
      target: ">= 85"
      source: "validation-summary.yaml"
      blocking: true

    - metric: "no_critical_failures"
      weight: 0.3
      target: "no feature with score < 50"
      blocking: true

    - metric: "pass_rate"
      weight: 0.3
      target: ">= 90%"
      blocking: true

  on_pass:
    auto_commit: true
    message: "feat(S5-P5.2): Functional validation passed - ${average_score}%"

  on_fail:
    action: "generate_remediation"
    output: "work/specs/stage5-outputs/phase2/remediation/"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Spec not found | FileNotFoundError | 경로 오류 | 경로 확인 | Yes |
| Code parsing error | SyntaxError | 잘못된 Java 문법 | S4 재생성 | No |
| Timeout | Task timeout | 대용량 Feature | 배치 크기 축소 | Yes |
| False negative | 정상인데 FAIL | 매칭 규칙 불충분 | 규칙 완화 | No |

### 6.2 Gap Classification

| Severity | Criteria | Action |
|----------|----------|--------|
| Critical | Score < 50 | 즉시 수정 필요 |
| Major | Missing core function | S4 재생성 |
| Minor | Extra in code | 문서화 |
| Info | Style difference | 무시 가능 |

### 6.3 Escalation

| Condition | Action | Notify |
|-----------|--------|--------|
| Failed features > 10% | 배치 중단 | Tech Lead |
| Score < 50 | 긴급 검토 | Developer + Tech Lead |
| Pattern failure | 템플릿 검토 | Architect |

---

## 7. Examples

### 7.1 Sample Feature Validation

**Input Spec (FEAT-PA-001):**
```yaml
feature:
  id: "FEAT-PA-001"
  screen: "PA01001"

api_endpoints:
  - path: "/api/pa/pa01001/list"
    method: "POST"
  - path: "/api/pa/pa01001/save"
    method: "POST"

business_logic:
  service: "PA01001Service"
  methods:
    - name: "getList"
    - name: "save"

data_access:
  mapper: "PA01001Mapper"
  operations:
    - name: "selectList"
    - name: "insert"
    - name: "update"
```

**Generated Code (PA01001Controller.java):**
```java
@RestController
@RequestMapping("/api/pa/pa01001")
public class PA01001Controller {

    @PostMapping("/list")
    public ApiResponse<List<PA01001Response>> getList(
            @RequestBody PA01001SearchRequest request) {
        return ApiResponse.success(pa01001Service.getList(request));
    }

    @PostMapping("/save")
    public ApiResponse<Void> save(
            @RequestBody List<PA01001SaveRequest> requests) {
        pa01001Service.save(requests);
        return ApiResponse.success();
    }
}
```

**Validation Result:**
```yaml
forward_check:
  endpoints: 2/2 matched
  business_logic: 2/2 matched
  data_access: 3/3 matched
  coverage: 100%

backward_check:
  coverage: 100%
  extra_in_code: 0

final_score: 100
result: "PASS"
```

### 7.2 Conditional Pass Example

```yaml
# Spec defines 5 methods, code has 4
forward_check:
  total: 5
  matched: 4
  missing: 1
  coverage: 80%

# Code has 1 extra method
backward_check:
  total: 5
  matched: 4
  extra: 1
  coverage: 80%

dimension_scores:
  endpoint_match: 100
  business_logic: 75  # 1 missing
  data_access: 100
  integration: 50     # partial

final_score: 82.5  # < 85
result: "CONDITIONAL"

remediation_required: true
remediation_deadline: "1 week"
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| 빈 Spec | No endpoints | Score = 0, FAIL |
| 추가 기능 | Extra methods | Backward check warning |
| SP 호출 | Stored procedure | data_access 별도 처리 |
| Cross-domain | 외부 서비스 호출 | Integration check |

---

## 8. Business Logic Verification Framework

### 8.1 Verification Levels

```yaml
verification_levels:
  level_1_existence:
    description: "메서드 존재 여부 확인"
    weight: 0.3
    checks:
      - "Method signature matches spec"
      - "Method is public"
      - "Return type matches spec"
      - "Parameter types match spec"

  level_2_structure:
    description: "메서드 구조 확인"
    weight: 0.3
    checks:
      - "Has expected dependencies (Mapper calls)"
      - "Has transaction annotation (for write operations)"
      - "Has validation logic (for input)"
      - "Has error handling"

  level_3_implementation:
    description: "구현 내용 확인"
    weight: 0.4
    checks:
      - "Core logic statements present"
      - "Data transformation logic"
      - "Business rules applied"
      - "Return value construction"
```

### 8.2 Verification Patterns by Operation Type

#### 8.2.1 Query Operation Pattern

```yaml
query_operation:
  name: "Query/Select Operation"
  spec_indicators:
    - "type: SELECT"
    - "operation: list|get|find|search"

  required_elements:
    - element: "mapper_call"
      pattern: "mapper\\.(select|find|get)\\w*\\("
      weight: 0.4

    - element: "parameter_pass"
      pattern: "mapper\\.\\w+\\(.*request.*\\)"
      weight: 0.2

    - element: "result_transform"
      pattern: "stream\\(\\)|map\\(|Response\\.from\\("
      weight: 0.3

    - element: "return_statement"
      pattern: "return\\s+(?!null)"
      weight: 0.1

  scoring:
    full_implementation: "all required elements present"
    partial_implementation: "mapper_call + return_statement"
    missing: "mapper_call not found"
```

#### 8.2.2 Save Operation Pattern

```yaml
save_operation:
  name: "Save/Update Operation"
  spec_indicators:
    - "type: INSERT|UPDATE|SAVE"

  required_elements:
    - element: "transaction_annotation"
      pattern: "@Transactional"
      location: "method or class level"
      weight: 0.2

    - element: "row_status_check"
      pattern: "getRowStatus\\(\\)|RowStatus\\.|switch.*RowStatus"
      weight: 0.2

    - element: "insert_call"
      pattern: "mapper\\.(insert|save)\\w*\\("
      weight: 0.2

    - element: "update_call"
      pattern: "mapper\\.update\\w*\\("
      weight: 0.2

    - element: "entity_conversion"
      pattern: "toEntity\\(\\)|Entity\\.from\\(|Entity\\.builder\\("
      weight: 0.2
```

#### 8.2.3 Delete Operation Pattern

```yaml
delete_operation:
  name: "Delete Operation"
  spec_indicators:
    - "type: DELETE"

  required_elements:
    - element: "transaction_annotation"
      pattern: "@Transactional"
      weight: 0.3

    - element: "delete_call"
      pattern: "mapper\\.delete\\w*\\("
      weight: 0.5

    - element: "id_extraction"
      pattern: "getId\\(\\)|request\\.get\\w*Id\\("
      weight: 0.2
```

### 8.3 Verification Algorithm

```yaml
verification_algorithm:
  steps:
    1_load_spec:
      action: "Load feature spec"
      extract: ["method_name", "input_type", "output_type", "operation_type"]

    2_locate_code:
      action: "Find corresponding code"
      search: "next-hallain/src/main/java/**/service/{Screen}Service.java"
      pattern: "public\\s+{output_type}\\s+{method_name}\\s*\\("

    3_extract_method:
      action: "Extract method body"
      include: ["annotations", "signature", "body_content", "line_numbers"]

    4_detect_operation_type:
      action: "Map spec type to verification pattern"
      mapping:
        - "SELECT|GET|LIST|FIND" -> "query_operation"
        - "INSERT|UPDATE|SAVE" -> "save_operation"
        - "DELETE|REMOVE" -> "delete_operation"
        - "COMPLEX|PROCESS" -> "complex_operation"

    5_verify_elements:
      action: "Check required elements"
      process: |
        for each required_element in pattern:
            match = regex_search(method_body, element.pattern)
            element.status = "FOUND" if match else "MISSING"
            element.score = element.weight if found else 0

    6_calculate_score:
      formula: |
        total_score = sum(element.score for element in results)
        max_score = sum(element.weight for element in pattern)
        percentage = (total_score / max_score) * 100

    7_determine_status:
      rules:
        - "score >= 90" -> "FULL_IMPLEMENTATION"
        - "score >= 60" -> "PARTIAL_IMPLEMENTATION"
        - "score >= 30" -> "MINIMAL_IMPLEMENTATION"
        - "score < 30" -> "MISSING"
```

### 8.4 Verification Report Schema

```yaml
# business-logic-verification.yaml
metadata:
  feature_id: "FEAT-PA-001"
  verified_at: "${TIMESTAMP}"

methods:
  - method_name: "getList"
    operation_type: "query_operation"
    verification_result:
      overall_score: 95
      status: "FULL_IMPLEMENTATION"
      elements:
        - name: "mapper_call"
          status: "FOUND"
          location: "PA01001Service.java:23"
          score: 0.4
        - name: "result_transform"
          status: "FOUND"
          location: "PA01001Service.java:25-27"
          score: 0.3

  - method_name: "save"
    operation_type: "save_operation"
    verification_result:
      overall_score: 75
      status: "PARTIAL_IMPLEMENTATION"
      gaps:
        - id: "GAP-BL-001"
          type: "missing_logic"
          description: "RowStatus 기반 분기 처리 누락"
          severity: "major"
          recommendation: "Add switch/case for RowStatus (I/U/D)"

summary:
  total_methods: 5
  full_implementation: 3
  partial_implementation: 2
  average_score: 88.5
```

### 8.5 Verification Tool Configuration

```yaml
verification_tool:
  source_paths:
    - "next-hallain/src/main/java/**/service/*.java"

  spec_paths:
    - "work/specs/stage2-outputs/phase4/**/*.yaml"

  output_path:
    - "work/specs/stage5-outputs/phase2/business-logic/"

  scoring:
    full_threshold: 90
    partial_threshold: 60
    minimal_threshold: 30

  custom_patterns:
    - name: "hallain_validation"
      pattern: "ValidationUtil\\.validate\\("
      category: "validation"
      weight: 0.1
```

---

## Version History

### v1.2.0 (2026-01-08)
- Step 8: Schema Validation 추가
- s5-02-functional-validation.schema.yaml 스키마 참조
- 12개 검증 규칙 적용 (V001-V012)

### v1.1.0 (2026-01-07)
- **Business Logic Verification Framework 추가** (Section 8)
  - 3-Level verification (Existence, Structure, Implementation)
  - Operation type patterns (Query, Save, Delete, Complex)
  - 7-Step verification algorithm
  - Scoring formula with weighted elements
  - Report schema with gap identification

### v1.0.0 (2026-01-07)
- Initial version
- Bidirectional validation (Forward + Backward)
- 4-dimension scoring (Endpoint, Business, Data, Integration)
- Feature-level parallel execution
- 85% pass threshold, 90% pass rate requirement
