---
name: s5-03-assurance-api-contract-test
description: Use when validating REST APIs against OpenAPI specifications, verifying MiPlatform protocol compatibility, or generating API documentation for migration validation (project)
---

# API Contract Test

> **Skill ID**: S5-03
> **Skill Type**: Validation (Limited Parallel)
> **Stage**: 5 - Assurance
> **Phase**: 5.3 - API Contract Test
> **Parallelization**: Limited (max 5 sessions, batch 2 domains)
> **Risk Context**: R-002 (MiPlatform Dependency Mitigation)

## 1. Overview

### 1.1 Purpose

생성된 REST API가 **OpenAPI 명세와 일치**하는지, 그리고 **MiPlatform 프로토콜과 호환**되는지 검증합니다. Legacy MiPlatform 클라이언트가 신규 API를 호출할 수 있도록 하위 호환성을 보장합니다.

**검증 대상:**
- OpenAPI Specification 생성 및 일치성
- MiPlatform Dataset Request/Response 호환성
- Content-Type 및 Encoding 검증
- Error Response 형식 일치

**Risk Mitigation:**
- R-002: MiPlatform Dependency (95.3% endpoint)
- Legacy 클라이언트 호환성 필수

### 1.2 Scope

**In Scope:**
- OpenAPI 3.0 명세 생성
- Controller -> OpenAPI 일치 검증
- MiPlatform Dataset 구조 호환성
- Request/Response 스키마 검증
- Error Response 표준화

**Out of Scope:**
- 실제 MiPlatform 클라이언트 테스트 (-> E2E)
- 기능 검증 (-> S5-02)
- 성능 테스트 (-> S5-04)

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Contract-First** | API 계약 기준 검증 | 클라이언트 호환성 |
| **MiPlatform Compatible** | Dataset 구조 유지 | Legacy 호환 |
| **Standard Compliant** | OpenAPI 3.0 준수 | 문서화 표준 |
| **Version Aware** | API 버전 관리 | 하위 호환성 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S5-03은 API 계약을 검증하며, **MiPlatform 호환성은 SQL 결과를 Dataset으로 변환하는 과정 포함**

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s5-02-assurance-functional-validation` | 기능 검증 완료 필요 |
| `s1-02-discovery-miplatform-protocol` | MiPlatform 프로토콜 참조 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s5-04-assurance-performance-baseline` | 계약 검증 후 성능 분석 |
| `s5-05-assurance-quality-gate` | 최종 품질 판정 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S5-02"
    skill_name: "s5-02-assurance-functional-validation"
    status: "completed"
    artifacts:
      - "validation-summary.yaml"
      - "pass_rate >= 90%"

  - skill_id: "S1-02"
    skill_name: "s1-02-discovery-miplatform-protocol"
    status: "completed"
    artifacts:
      - "miplatform-protocol.yaml"
      - "dataset schemas"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| generated_controllers | directory | `next-hallain/src/main/java/` | Java | Yes |
| miplatform_specs | directory | `work/specs/stage1-outputs/phase2/` | YAML | Yes |
| api_specs | directory | `work/specs/stage2-outputs/phase4/` | YAML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| SpringDoc | 2.x | OpenAPI 생성 |
| swagger-parser | 2.x | OpenAPI 검증 |
| Read | - | 코드/스펙 읽기 |
| Grep | - | 패턴 검색 |

**Dependencies:**
```kotlin
implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.3.0")
```

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: parallel
  unit: domain
  parallelization:
    enabled: true
    max_sessions: 5
    batch_size: 2
    session_timeout_minutes: 120
    retry_on_failure: 2

task:
  naming_pattern: "API-{DOMAIN}"
  granularity: domain
```

### 3.2 Contract Validation Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    API CONTRACT VALIDATION PIPELINE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────────┐     ┌──────────────────┐                        │
│   │  OpenAPI         │     │  MiPlatform      │                        │
│   │  Generation      │     │  Compatibility   │                        │
│   └────────┬─────────┘     └────────┬─────────┘                        │
│            │                         │                                  │
│            ▼                         ▼                                  │
│   ┌──────────────────┐     ┌──────────────────┐                        │
│   │  Schema          │     │  Dataset         │                        │
│   │  Validation      │     │  Structure       │                        │
│   └────────┬─────────┘     └────────┬─────────┘                        │
│            │                         │                                  │
│            └────────────┬────────────┘                                  │
│                         ▼                                               │
│            ┌──────────────────────┐                                    │
│            │  Contract Report     │                                    │
│            │  Generation          │                                    │
│            └──────────────────────┘                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 OpenAPI Validation Details

#### 3.3.1 OpenAPI Generation

```yaml
openapi_generation:
  source: "Controller classes with @RestController"
  output: "openapi/{domain}.yaml"

  extraction_rules:
    path: "@RequestMapping + @PostMapping/@GetMapping"
    method: "HTTP method annotation"
    request_body: "@RequestBody parameter"
    response: "Return type"
    description: "@Operation annotation (if present)"

  generation_approach:
    - "Scan @RestController classes"
    - "Extract @RequestMapping base path"
    - "Extract method-level mappings"
    - "Infer schema from DTO classes"
    - "Generate OpenAPI 3.0 YAML"
```

#### 3.3.2 OpenAPI Schema Structure

```yaml
# openapi/pa.yaml (generated)
openapi: "3.0.3"
info:
  title: "PA Domain API"
  version: "1.0.0"
  description: "Production Administration APIs"

servers:
  - url: "/api"

paths:
  /pa/pa01001/list:
    post:
      operationId: "getPA01001List"
      summary: "PA01001 목록 조회"
      tags:
        - "PA01001"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/PA01001SearchRequest"
      responses:
        "200":
          description: "Success"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ApiResponse_List_PA01001Response"
        "400":
          description: "Bad Request"
        "500":
          description: "Internal Server Error"

components:
  schemas:
    PA01001SearchRequest:
      type: object
      properties:
        siteCd:
          type: string
        startDate:
          type: string
          format: date
```

### 3.4 MiPlatform Compatibility Details

#### 3.4.1 MiPlatform Protocol Requirements

```yaml
miplatform_requirements:
  request_format:
    content_type: "application/json"  # or legacy XML
    structure:
      - "Dataset wrapper"
      - "Row-based data"
      - "Column definitions"

  response_format:
    content_type: "application/json"
    structure:
      - "Dataset structure"
      - "Column metadata"
      - "Row data array"

  compatibility_checks:
    - "Column name mapping"
    - "Data type mapping"
    - "Null handling"
    - "Date format"
```

#### 3.4.2 Dataset Structure Mapping

```yaml
dataset_mapping:
  legacy_miplatform:
    request:
      structure: |
        <Dataset id="ds_input">
          <ColumnInfo>
            <Column id="SITE_CD" type="STRING" size="10"/>
            <Column id="START_DATE" type="DATE"/>
          </ColumnInfo>
          <Rows>
            <Row>
              <Col id="SITE_CD">S01</Col>
              <Col id="START_DATE">20260101</Col>
            </Row>
          </Rows>
        </Dataset>

    response:
      structure: |
        <Dataset id="ds_output">
          <ColumnInfo>...</ColumnInfo>
          <Rows>...</Rows>
        </Dataset>

  new_api:
    request:
      structure: |
        {
          "siteCd": "S01",
          "startDate": "2026-01-01"
        }

    response:
      structure: |
        {
          "success": true,
          "data": [
            { "siteCd": "S01", "..." }
          ]
        }

  mapping_rules:
    - legacy: "SITE_CD"
      new: "siteCd"
      transform: "SNAKE_TO_CAMEL"

    - legacy: "DATE (YYYYMMDD)"
      new: "date (YYYY-MM-DD)"
      transform: "DATE_FORMAT"
```

### 3.5 Process Steps

#### Step 1: Generate OpenAPI Specs

**Description:** Controller에서 OpenAPI 명세 생성

**Sub-steps:**
1. 도메인별 Controller 스캔
2. Endpoint 정보 추출
3. DTO 스키마 추출
4. OpenAPI YAML 생성

**OpenAPI Generation:**
```bash
# SpringDoc을 통한 자동 생성 또는 수동 추출
# /v3/api-docs endpoint 호출 또는 코드 분석
```

**Validation:** OpenAPI 파일 생성 완료

---

#### Step 2: Validate OpenAPI Schema

**Description:** 생성된 OpenAPI가 표준을 준수하는지 검증

**Sub-steps:**
1. OpenAPI 3.0 스키마 검증
2. 필수 필드 확인
3. 참조 무결성 확인
4. 타입 일관성 확인

**Schema Validation Rules:**
```yaml
schema_validation:
  required_fields:
    - "openapi"
    - "info.title"
    - "info.version"
    - "paths"

  path_requirements:
    - "At least one operation per path"
    - "Valid HTTP method"
    - "Response defined for 200/4xx/5xx"

  schema_requirements:
    - "All $ref targets exist"
    - "Property types are valid"
    - "Required fields are defined"
```

**Validation:** 스키마 오류 0개

---

#### Step 3: Compare with Stage 1 Specs

**Description:** 생성된 OpenAPI와 Stage 1 MiPlatform 명세 비교

**Sub-steps:**
1. MiPlatform 프로토콜 로드
2. Endpoint 매핑 비교
3. Request/Response 필드 비교
4. 누락/추가 항목 식별

**Comparison Output:**
```yaml
miplatform_comparison:
  total_endpoints: 50
  matched: 48
  modified: 2
  compatibility_rate: 96%

  modifications:
    - endpoint: "/api/pa/pa01001/list"
      change: "field_renamed"
      legacy: "SITE_CD"
      new: "siteCd"
      compatible: true  # 변환 가능

    - endpoint: "/api/pa/pa01002/save"
      change: "type_changed"
      legacy: "STRING"
      new: "INTEGER"
      compatible: false  # 수동 검토 필요
```

**Validation:** Compatibility >= 95%

---

#### Step 4: Validate MiPlatform Compatibility

**Description:** Legacy MiPlatform 클라이언트 호환성 검증

**Sub-steps:**
1. Dataset 구조 매핑 확인
2. 필드명 변환 규칙 확인
3. 데이터 타입 호환성 확인
4. 날짜/숫자 포맷 확인

**Compatibility Checks:**
```yaml
compatibility_checks:
  field_mapping:
    rule: "All legacy fields have corresponding new fields"
    status: "PASS"

  type_compatibility:
    rule: "Data types are compatible or convertible"
    warnings:
      - "DATE format change: YYYYMMDD -> YYYY-MM-DD"

  null_handling:
    rule: "Null handling consistent"
    status: "PASS"

  encoding:
    rule: "UTF-8 encoding"
    status: "PASS"
```

**Validation:** 호환성 이슈 < 5 (Critical 0)

---

#### Step 5: Generate Contract Report

**Description:** API 계약 검증 리포트 생성

**Sub-steps:**
1. OpenAPI 검증 결과 집계
2. MiPlatform 호환성 결과 집계
3. 이슈 목록 생성
4. 리포트 파일 생성

**Validation:** 리포트 생성 완료

---

#### Step 7: Schema Validation

**Description:** 생성된 contract-report.yaml이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | root | metadata, summary, openapi_validation, miplatform_compatibility, gate_evaluation 필수 키 존재 | ERROR | Yes |
| V002 | metadata.generated_by | 정확히 "s5-03-assurance-api-contract-test" | ERROR | Yes |
| V003 | summary.result | enum: PASS, CONDITIONAL, FAIL | ERROR | Yes |
| V004 | violations[].type | enum: openapi_violation, miplatform_incompatibility, schema_error | ERROR | Yes |
| V005 | gate_evaluation.gate_id | 정확히 "G5.3" | ERROR | Yes |
| V006 | summary.compliance_rate | 범위: 0-100 | ERROR | Yes |
| V007 | miplatform_compatibility.compatibility_rate | 범위: 0-100 | ERROR | Yes |
| V008 | result | PASS 시 compliance_rate >= 95% | ERROR | Yes |
| V009 | result | PASS 시 compatibility_rate >= 95% | ERROR | Yes |
| V010 | openapi_validation | spec_generated == total_controllers | WARNING | No |

**Sub-steps:**
1. contract-report.yaml 스키마 검증
2. OpenAPI/MiPlatform 호환성 검증
3. Gate 결과 일관성 검증
4. 오류 발생 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재검증 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.6 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | OpenAPI 생성 성공 | Schema 검증 | ERROR |
| DP-2 | Schema 유효 | 호환성 검증 | 수정 필요 |
| DP-3 | Match >= 95% | PASS | Gap 분석 |
| DP-4 | Critical 이슈 | FAIL | WARNING |

### 3.7 Large File Handling

> **⚠️ Read Tool Limit**: Claude Code Read tool has 256KB file size limit.

#### Input Files That May Be Large

| Input | Source Skill | Location | Potential Size | Chunking Type |
|-------|--------------|----------|----------------|---------------|
| MiPlatform Protocol | s1-02 | `work/specs/stage1-outputs/phase2/` | >200KB | Layer-based |
| API Specs | s2-04 | `work/specs/stage2-outputs/phase4/` | >200KB | Domain-based directory |

#### MiPlatform Protocol Reading Strategy

```yaml
miplatform_protocol_reading:
  step_1: "파일/디렉토리 존재 확인"
  step_2:
    - check: "miplatform-protocol/ 디렉토리 존재?"
    - if_yes: "manifest 기반 청크 읽기"
    - if_no: "단일 파일 처리로 진행"

  chunked_directory_structure:
    directory: "miplatform-protocol/"
    files:
      - "_manifest.yaml"          # metadata + chunk 목록
      - "dataset_schemas.yaml"    # Dataset 스키마 정의
      - "request_patterns.yaml"   # Request 패턴
      - "response_patterns.yaml"  # Response 패턴
      - "field_mappings.yaml"     # 필드 매핑 규칙

  reading_order:
    1: "manifest 읽기 → 청크 목록 확인"
    2: "필요한 청크만 선택적 읽기"
    3: "field_mappings.yaml 우선 (호환성 검증 핵심)"
```

#### API Specs Reading Strategy

```yaml
api_specs_reading:
  strategy: "domain_scoped"
  base_path: "work/specs/stage2-outputs/phase4/{domain}/"

  per_domain_process:
    1: "해당 도메인 디렉토리만 접근"
    2: "필요한 Feature Spec만 읽기"
    3: "메모리 내 누적 없이 즉시 검증"

  large_spec_handling:
    check: "wc -c < spec_file.yaml"
    if_large:
      - "offset/limit으로 섹션별 읽기"
      - "endpoints 섹션 우선 처리"
```

#### Parallel Session Input Strategy

```yaml
parallel_session_input:
  max_sessions: 5
  batch_size: 2  # domains per session

  per_session:
    1: "할당된 도메인 목록 수신"
    2: "MiPlatform protocol 공통 데이터 1회 읽기"
    3: "도메인별 API spec 순차 읽기"
    4: "Controller 파일 읽기 (개별 파일은 소형)"

  memory_optimization:
    - "도메인별 검증 완료 후 메모리 해제"
    - "검증 결과만 누적"
    - "전체 데이터 메모리 적재 금지"
```

#### Legacy Single File Compatibility

```yaml
legacy_file_handling:
  check: "miplatform-protocol.yaml 단일 파일 존재?"
  if_exists:
    size_check: "wc -c < miplatform-protocol.yaml"
    if_small: "전체 Read"
    if_large:
      strategy: "offset/limit"
      chunk_lines: 1500
      process: |
        1. Read(file, offset=0, limit=1500)
        2. Parse header + dataset_schemas
        3. Read(file, offset=1500, limit=1500)
        4. ... 파일 끝까지 반복
```

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage5-outputs/phase3/"

  artifacts:
    - name: "openapi/"
      description: "Generated OpenAPI specifications"
      required: true
    - name: "contract-validation.yaml"
      required: true
    - name: "miplatform-compatibility.yaml"
      required: true
```

### 4.2 Output Files Summary

```
work/specs/stage5-outputs/phase3/
├── openapi/
│   ├── pa.yaml           # PA domain OpenAPI
│   ├── mm.yaml           # MM domain OpenAPI
│   ├── sm.yaml           # SM domain OpenAPI
│   └── ...
├── contract-validation.yaml    # 전체 계약 검증 결과
└── miplatform-compatibility.yaml  # MiPlatform 호환성 결과
```

### 4.3 Contract Validation Output Schema

```yaml
# contract-validation.yaml
metadata:
  generated_by: "s5-03-assurance-api-contract-test"
  generated_at: "${TIMESTAMP}"

summary:
  domains_validated: 12
  total_endpoints: 700
  openapi_generated: 700
  schema_valid: 695
  contract_match_rate: 95.3%

by_domain:
  PA:
    endpoints: 200
    openapi_generated: true
    schema_valid: true
    endpoints_matched: 195
    match_rate: 97.5%
  MM:
    endpoints: 100
    openapi_generated: true
    schema_valid: true
    endpoints_matched: 94
    match_rate: 94.0%
  # ...

openapi_validation:
  total_files: 12
  valid: 12
  invalid: 0
  warnings:
    - file: "pa.yaml"
      warning: "Missing description for 3 endpoints"
      severity: "info"

schema_issues:
  - domain: "PA"
    endpoint: "/api/pa/pa01001/list"
    issue: "Missing response schema for 400"
    severity: "minor"

result: "PASS"
gate_score: 95.3
```

### 4.4 MiPlatform Compatibility Output Schema

```yaml
# miplatform-compatibility.yaml
metadata:
  generated_by: "s5-03-assurance-api-contract-test"
  generated_at: "${TIMESTAMP}"
  legacy_spec_ref: "work/specs/stage1-outputs/phase2/"

summary:
  total_endpoints: 700
  fully_compatible: 665
  compatible_with_transform: 30
  incompatible: 5
  compatibility_rate: 99.3%

field_mapping:
  total_fields: 5000
  direct_mapping: 4800
  transform_required: 195
  unmapped: 5

  transform_rules_applied:
    - rule: "SNAKE_TO_CAMEL"
      count: 4800
    - rule: "DATE_FORMAT"
      count: 150
    - rule: "NUMBER_FORMAT"
      count: 45

compatibility_issues:
  - endpoint: "/api/pa/pa02003/export"
    issue: "New endpoint not in legacy"
    severity: "info"
    action: "Document as new feature"

  - endpoint: "/api/mm/mm01001/list"
    field: "QTY"
    issue: "Type changed from STRING to INTEGER"
    legacy_type: "STRING"
    new_type: "INTEGER"
    severity: "warning"
    action: "Verify client handling"

  - endpoint: "/api/sc/sc01005/save"
    issue: "Removed deprecated field"
    field: "OLD_FLAG"
    severity: "critical"
    action: "Add backwards compatibility"

critical_issues: 1
warnings: 4
info: 10

result: "CONDITIONAL"  # critical > 0
gate_passed: false
remediation_required: true
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| openapi_generated | structural | All domains have OpenAPI | FAIL | Yes |
| schema_valid | structural | No schema validation errors | FAIL | Yes |
| contract_match | metric | >= 95% | FAIL | Yes |
| miplatform_compatible | metric | No critical incompatibilities | FAIL | Yes |

### 5.2 Gate Criteria

```yaml
gate_criteria:
  id: "G5.3"
  name: "API Contract Gate"
  threshold: 70

  metrics:
    - metric: "openapi_generated"
      weight: 0.25
      target: "All domains"
      blocking: true

    - metric: "schema_valid"
      weight: 0.25
      target: "No validation errors"
      blocking: true

    - metric: "contract_match_rate"
      weight: 0.25
      target: ">= 95%"
      blocking: true

    - metric: "miplatform_compatible"
      weight: 0.25
      target: "No critical issues"
      blocking: true

  on_pass:
    auto_commit: true
    message: "feat(S5-P5.3): API contract test passed"

  on_fail:
    action: "document_gaps"
    escalate: "api_team"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| OpenAPI generation fail | File not created | Annotation 누락 | Annotation 추가 | Yes |
| Schema validation error | Invalid $ref | DTO 누락 | DTO 확인 | Yes |
| Encoding mismatch | 깨진 문자 | Charset 불일치 | UTF-8 강제 | Yes |
| Complex type mapping | 타입 불일치 | Generic 처리 | 수동 매핑 | No |

### 6.2 Compatibility Issue Handling

| Severity | Criteria | Action |
|----------|----------|--------|
| Critical | Breaking change | 즉시 수정 필요 |
| Warning | Convertible change | 변환 로직 추가 |
| Info | New feature | 문서화 |

### 6.3 Escalation

| Condition | Action | Notify |
|-----------|--------|--------|
| Critical issue | Gate 실패 | API Team + Tech Lead |
| Warning > 10 | 리뷰 요청 | Developer |
| Schema invalid | S4 재검토 | Developer |

---

## 7. Examples

### 7.1 Sample OpenAPI Generation

**Controller Input:**
```java
@RestController
@RequestMapping("/api/pa/pa01001")
public class PA01001Controller {

    @Operation(summary = "목록 조회")
    @PostMapping("/list")
    public ApiResponse<List<PA01001Response>> getList(
            @RequestBody PA01001SearchRequest request) {
        return ApiResponse.success(service.getList(request));
    }
}
```

**Generated OpenAPI:**
```yaml
paths:
  /pa/pa01001/list:
    post:
      summary: "목록 조회"
      operationId: "getList"
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/PA01001SearchRequest"
      responses:
        "200":
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/PA01001Response"
```

### 7.2 MiPlatform Compatibility Example

**Legacy Request (XML):**
```xml
<Dataset id="ds_input">
  <ColumnInfo>
    <Column id="SITE_CD" type="STRING"/>
  </ColumnInfo>
  <Rows>
    <Row><Col id="SITE_CD">S01</Col></Row>
  </Rows>
</Dataset>
```

**New API Request (JSON):**
```json
{
  "siteCd": "S01"
}
```

**Mapping Rule:**
```yaml
field_mapping:
  - legacy_name: "SITE_CD"
    new_name: "siteCd"
    transform: "SNAKE_TO_CAMEL"
    compatible: true
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| Generic Response | `ApiResponse<T>` | Unwrap generic |
| Nested DTO | Complex object | Flatten schema |
| File upload | MultipartFile | Binary schema |
| Pagination | Page object | Standard pagination |

---

## 8. MiPlatform Transformation Layer

### 8.1 Architecture

```yaml
transformation_layer:
  components:
    - name: "MiPlatformRequestConverter"
      type: "Filter/Interceptor"
      responsibility: "Incoming Dataset XML → JSON DTO"
      location: "com.hallain.common.miplatform"

    - name: "MiPlatformResponseConverter"
      type: "ResponseBodyAdvice"
      responsibility: "JSON Response → Dataset XML"
      location: "com.hallain.common.miplatform"

    - name: "FieldMappingRegistry"
      type: "Singleton"
      responsibility: "필드명 매핑 규칙 저장소"

    - name: "TypeConverter"
      type: "Utility"
      responsibility: "데이터 타입 변환"

  flow:
    request: |
      MiPlatform Client
          ↓ (Dataset XML or JSON with legacy names)
      MiPlatformRequestFilter
          ↓ (Detect content type)
      DatasetParser or JsonFieldMapper
          ↓ (Apply mapping: SITE_CD → siteCd)
      Controller (@RequestBody DTO)

    response: |
      Controller (return DTO)
          ↓
      MiPlatformResponseAdvice
          ↓ (Check client type)
      JsonFieldMapper or DatasetBuilder
          ↓
      MiPlatform Client
```

### 8.2 Field Mapping Configuration

```yaml
field_mapping:
  global_rules:
    naming_transform:
      legacy_to_new: "SNAKE_CASE → camelCase"
      new_to_legacy: "camelCase → SNAKE_CASE"
      examples:
        - legacy: "SITE_CD" → new: "siteCd"
        - legacy: "START_DATE" → new: "startDate"

    type_transform:
      date:
        legacy_format: "YYYYMMDD"
        new_format: "YYYY-MM-DD"
      datetime:
        legacy_format: "YYYYMMDDHHmmss"
        new_format: "YYYY-MM-DDTHH:mm:ss"
      boolean:
        legacy_values: ["Y", "N", "1", "0"]
        new_values: [true, false]
        mapping: { "Y": true, "N": false }
      number:
        legacy_type: "STRING"
        new_type: "NUMBER"
        null_handling: "empty string → null"

  domain_specific:
    PA:
      /api/pa/pa01001/list:
        request:
          - { legacy: SITE_CD, new: siteCd, type: string }
          - { legacy: START_DT, new: startDate, type: date }
        response:
          - { legacy: PA_NO, new: paNo, type: string }
          - { legacy: REG_DT, new: regDate, type: datetime }
```

### 8.3 Implementation Components

#### 8.3.1 Request Filter

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class MiPlatformRequestFilter extends OncePerRequestFilter {

    private final FieldMappingRegistry mappingRegistry;
    private final DatasetParser datasetParser;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain chain) {

        String clientType = request.getHeader("X-Client-Type");

        if (isMiPlatformClient(clientType)) {
            MiPlatformRequestWrapper wrappedRequest =
                new MiPlatformRequestWrapper(request, mappingRegistry);
            chain.doFilter(wrappedRequest, response);
        } else {
            chain.doFilter(request, response);
        }
    }

    private boolean isMiPlatformClient(String clientType) {
        return "MiPlatform".equals(clientType) || "XPLATFORM".equals(clientType);
    }
}
```

#### 8.3.2 Field Mapping Registry

```java
@Component
public class FieldMappingRegistry {

    private final Map<String, EndpointMapping> endpointMappings;

    public String toLegacyFieldName(String endpoint, String newFieldName) {
        EndpointMapping mapping = endpointMappings.get(endpoint);
        if (mapping != null) {
            return mapping.getNewToLegacy().getOrDefault(newFieldName,
                CaseUtils.toSnakeCase(newFieldName).toUpperCase());
        }
        return CaseUtils.toSnakeCase(newFieldName).toUpperCase();
    }

    public String toNewFieldName(String endpoint, String legacyFieldName) {
        EndpointMapping mapping = endpointMappings.get(endpoint);
        if (mapping != null) {
            return mapping.getLegacyToNew().getOrDefault(legacyFieldName,
                CaseUtils.toCamelCase(legacyFieldName.toLowerCase()));
        }
        return CaseUtils.toCamelCase(legacyFieldName.toLowerCase());
    }

    public Object transformValue(String fieldType, Object value, Direction direction) {
        if (value == null) return null;

        return switch (fieldType) {
            case "date" -> transformDate(value, direction);
            case "datetime" -> transformDateTime(value, direction);
            case "boolean" -> transformBoolean(value, direction);
            default -> value;
        };
    }

    private Object transformDate(Object value, Direction direction) {
        String str = value.toString();
        if (direction == Direction.LEGACY_TO_NEW && str.length() == 8) {
            // YYYYMMDD → YYYY-MM-DD
            return str.substring(0, 4) + "-" + str.substring(4, 6) + "-" + str.substring(6, 8);
        } else if (direction == Direction.NEW_TO_LEGACY) {
            // YYYY-MM-DD → YYYYMMDD
            return str.replace("-", "");
        }
        return value;
    }
}
```

#### 8.3.3 Response Advice

```java
@ControllerAdvice
public class MiPlatformResponseAdvice implements ResponseBodyAdvice<Object> {

    private final FieldMappingRegistry mappingRegistry;

    @Override
    public Object beforeBodyWrite(Object body, MethodParameter returnType,
                                   MediaType contentType, Class converterType,
                                   ServerHttpRequest request,
                                   ServerHttpResponse response) {

        String clientType = request.getHeaders().getFirst("X-Client-Type");

        if (isMiPlatformClient(clientType)) {
            String endpoint = request.getURI().getPath();
            return transformToLegacyFormat(body, endpoint);
        }
        return body;
    }

    private Object transformToLegacyFormat(Object body, String endpoint) {
        if (body instanceof ApiResponse<?> apiResponse) {
            Object data = apiResponse.getData();
            Object transformed = transformObject(data, endpoint, Direction.NEW_TO_LEGACY);
            return ApiResponse.success(transformed);
        }
        return body;
    }
}
```

### 8.4 Dataset XML Parser

```java
@Component
public class DatasetParser {

    public <T> T parseDataset(String xml, Class<T> targetType, String endpoint,
                               FieldMappingRegistry registry) {
        // Parse XML
        Document doc = parseXml(xml);

        // Extract columns and rows
        Map<String, ColumnInfo> columns = parseColumnInfo(doc);
        List<Map<String, Object>> rows = parseRows(doc, columns);

        // Transform field names
        List<Map<String, Object>> transformed = rows.stream()
            .map(row -> transformRow(row, endpoint, registry, Direction.LEGACY_TO_NEW))
            .collect(Collectors.toList());

        return convertToType(transformed, targetType);
    }

    public String buildDataset(Object data, String datasetId, String endpoint,
                                FieldMappingRegistry registry) {
        StringBuilder xml = new StringBuilder();
        xml.append("<Dataset id=\"").append(datasetId).append("\">\n");

        List<?> rows = data instanceof List ? (List<?>) data : List.of(data);

        if (!rows.isEmpty()) {
            // Build ColumnInfo and Rows
            buildColumnInfo(xml, rows.get(0), endpoint, registry);
            buildRows(xml, rows, endpoint, registry);
        }

        xml.append("</Dataset>");
        return xml.toString();
    }
}
```

### 8.5 Configuration File

```yaml
# resources/miplatform/field-mappings.yaml
version: "1.0.0"

global:
  naming:
    legacy_pattern: "UPPER_SNAKE_CASE"
    new_pattern: "camelCase"

  type_mappings:
    date:
      legacy: "YYYYMMDD"
      new: "yyyy-MM-dd"
    datetime:
      legacy: "YYYYMMDDHHmmss"
      new: "yyyy-MM-dd'T'HH:mm:ss"
    boolean:
      legacy_true: ["Y", "1"]
      legacy_false: ["N", "0"]

domains:
  PA:
    endpoints:
      /api/pa/pa01001/list:
        request:
          - { legacy: SITE_CD, new: siteCd, type: string }
          - { legacy: START_DT, new: startDate, type: date }
          - { legacy: USE_YN, new: useYn, type: boolean }
        response:
          - { legacy: PA_NO, new: paNo, type: string }
          - { legacy: QTY, new: quantity, type: number }

special_mappings:
  - legacy: "SEQ_NO"
    new: "sequenceNumber"
  - legacy: "CRT_DT"
    new: "createdAt"
```

### 8.6 Compatibility Test Cases

```yaml
compatibility_tests:
  - name: "Legacy XML Request"
    input:
      content_type: "application/xml"
      body: |
        <Dataset id="ds_input">
          <ColumnInfo>
            <Column id="SITE_CD" type="STRING"/>
          </ColumnInfo>
          <Rows>
            <Row><Col id="SITE_CD">S01</Col></Row>
          </Rows>
        </Dataset>
    expected:
      controller_receives:
        siteCd: "S01"

  - name: "Legacy JSON Field Names"
    input:
      content_type: "application/json"
      headers:
        X-Client-Type: "MiPlatform"
      body: '{"SITE_CD": "S01", "START_DT": "20260101"}'
    expected:
      controller_receives:
        siteCd: "S01"
        startDate: "2026-01-01"

  - name: "Response Transformation"
    setup:
      endpoint: "/api/pa/pa01001/list"
      client_type: "MiPlatform"
    controller_returns:
      - paNo: "PA001"
        regDate: "2026-01-01T10:00:00"
    expected:
      - PA_NO: "PA001"
        REG_DT: "20260101100000"
```

---

## Version History

### v1.2.0 (2026-01-08)
- Step 7: Schema Validation 추가
- s5-03-api-contract.schema.yaml 스키마 참조
- 10개 검증 규칙 적용 (V001-V010)

### v1.1.0 (2026-01-07)
- **MiPlatform Transformation Layer 추가** (Section 8)
  - Architecture design (Filter, Advice, Registry)
  - Field mapping configuration (global + domain-specific)
  - Implementation components (Java code)
  - Dataset XML parser
  - Configuration YAML format
  - Compatibility test cases

### v1.0.0 (2026-01-07)
- Initial version
- OpenAPI 3.0 generation and validation
- MiPlatform compatibility checking
- Field mapping transformation rules
- 95% contract match requirement
