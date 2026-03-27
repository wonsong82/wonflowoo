---
name: s1-04-discovery-spec-generation
description: Use when generating migration specifications from deep analysis results, consolidating 5-layer traces into implementable YAML specs, or preparing code generation inputs (project)
---

# Spec Generation

> **Skill ID**: S1-04
> **Skill Type**: Generation (분석 결과를 Generation-ready Spec으로 변환)
> **Stage**: 1 - Discovery
> **Phase**: 1.4 - Spec Generation

## 1. Overview

### 1.1 Purpose

S1-03 Deep Analysis 결과를 Stage 4 Generation에서 사용할 수 있는 표준화된 YAML Specification으로 변환합니다. 이 Phase는 Discovery Stage의 마지막 단계로, 분석된 정보를 코드 생성에 적합한 형식으로 정규화합니다.

**변환 흐름:**
```
S1-03 (분석 결과) → S1-04 (정규화/명세화) → S4-03 (코드 생성)
     raw data          standardized spec       executable code
```

**생성 산출물:**
- `main.yaml` - Feature 통합 Specification (모든 Layer 요약)
- `api-specs/` - OpenAPI 형식 API 정의
- `business-logic/` - Service 구현 명세
- `data-model/` - Entity/Mapper 정의

**핵심 가치:**
- 분석 결과의 정규화 및 표준화
- 코드 생성을 위한 실행 가능한 명세 제공
- Layer 간 일관성 보장

### 1.2 Scope

**In Scope:**
- S1-03 분석 결과 통합 및 정규화
- OpenAPI 3.0 형식 API Spec 생성
- Service/Validation Spec 생성
- Entity/Mapper Spec 생성
- main.yaml 통합 명세 생성

**Out of Scope:**
- 소스 코드 직접 분석 (→ `s1-03-discovery-deep-analysis`)
- MiPlatform 프로토콜 분석 (→ `s1-02-discovery-miplatform-protocol`)
- 실제 코드 생성 (→ `s4-03-generation-domain-batch`)
- Spec 검증 (→ `s2-02-validation-structural-comparison`)

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Standardization** | 모든 출력을 표준 스키마로 정규화 | 일관된 코드 생성 품질 보장 |
| **Completeness** | main.yaml에 모든 Layer 정보 포함 | 단일 파일로 전체 Feature 이해 가능 |
| **Generation-Ready** | 코드 생성에 즉시 사용 가능한 형식 | Stage 4에서 추가 변환 불필요 |
| **Traceability** | 원본 분석 파일 참조 유지 | 문제 발생 시 추적 가능 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S1-04는 S1-03의 **SQL-First 분석 결과를 Spec으로 정규화**
> - SQL/MyBatis Layer(L4) 정보가 main.yaml의 핵심 섹션으로 포함됨
> - 생성된 Spec은 Stage 4의 **2-Phase 워크플로우(Query 이관 → Java 생성)**의 입력으로 사용

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s1-01-discovery-feature-inventory` (S1-01) | Feature ID, Screen ID 정보 제공 |
| `s1-02-discovery-miplatform-protocol` (S1-02) | Request/Response 스키마 제공 |
| `s1-03-discovery-deep-analysis` (S1-03) | 5-Layer SQL-First 분석 결과 제공 (주 입력) |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s2-02-validation-structural-comparison` (S2-02) | Spec vs Ground truth 비교 검증 |
| `s4-03-generation-domain-batch` (S4-03) | Spec 기반 2-Phase 코드 생성 (Query → Java) |
| `s5-02-assurance-functional-validation` (S5-02) | Spec-to-code 정합성 및 SQL Fidelity 검증 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S1-03"
    skill_name: "s1-03-discovery-deep-analysis"
    dependency_type: "input"
    artifacts:
      - "summary.yaml"
      - "api-endpoints/*.yaml"
      - "business-logic/*.yaml"
      - "data-access/*.yaml"
      - "data-model/*.yaml"

  - skill_id: "S1-02"
    skill_name: "s1-02-discovery-miplatform-protocol"
    dependency_type: "input"
    artifact: "miplatform-protocol.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| deep_analysis | directory | `work/specs/stage1-outputs/phase3/{Priority}/{Domain}/FEAT-{DOMAIN}-{NNN}/` | YAML | Yes |
| miplatform_protocol | file | `work/specs/stage1-outputs/phase2/{Priority}/{Domain}/miplatform-protocol.yaml` | YAML | Yes |
| feature_inventory | file | `work/specs/stage1-outputs/phase1/{Priority}/{Domain}/feature-inventory.yaml` | YAML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Read | - | YAML 파일 읽기 |
| Write | - | Spec 파일 생성 |

**Access:**
- Stage 1 Phase 1-3 출력 디렉토리 읽기 권한
- Stage 1 Phase 4 출력 디렉토리 쓰기 권한

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
    timeout_minutes: 60
    retry_on_failure: 3
  task_naming:
    pattern: "FEAT-{DOMAIN}-{NNN}-SPEC"
```

### 3.2 Process Steps

#### Step 1: Analysis Outputs Loading

**Description:** S1-03 분석 결과 및 관련 입력 파일 로드

**Sub-steps:**
1. `summary.yaml` 로드 및 파싱
2. Layer별 상세 파일 로드:
   - `api-endpoints/{feature_id}.yaml`
   - `business-logic/{feature_id}.yaml`
   - `data-access/{feature_id}.yaml`
   - `data-model/{feature_id}.yaml`
3. `miplatform-protocol.yaml`에서 해당 Feature 프로토콜 추출
4. `feature-inventory.yaml`에서 Feature 메타데이터 추출

**Validation:** 필수 입력 파일 존재 확인

**Outputs:**
- 통합된 분석 데이터 구조

---

#### Step 2: Layer Normalization

**Description:** 분석 결과를 표준 스키마로 정규화

**Sub-steps:**
1. 필드명 표준화 (camelCase → snake_case for YAML)
2. 타입 정규화:
   - Java 타입 → 표준 타입 (String → STRING, int → INTEGER)
   - Nullable 정보 추출
3. 참조 관계 정규화:
   - 클래스 참조 → 패키지 포함 FQCN
   - 메서드 참조 → 시그니처 포함
4. 중복 제거 및 병합

**Normalization Rules:**
```yaml
type_mapping:
  java_to_spec:
    String: STRING
    int: INTEGER
    Integer: INTEGER
    long: LONG
    Long: LONG
    double: DOUBLE
    Double: DOUBLE
    BigDecimal: DECIMAL
    Date: DATE
    LocalDate: DATE
    LocalDateTime: DATETIME
    boolean: BOOLEAN
    Boolean: BOOLEAN
    List: ARRAY
    Map: OBJECT
```

**Validation:** 모든 필드에 표준 타입 할당

**Outputs:**
- 정규화된 Layer 데이터

---

#### Step 3: API Spec Generation

**Description:** OpenAPI 형식 API Specification 생성

**Sub-steps:**
1. `openapi-spec.yaml` 생성:
   - OpenAPI 3.0 형식 endpoint 정의
   - Path, Method, Summary, Description
   - Request Body 스키마 참조
   - Response 스키마 참조
   - MiPlatform 확장 속성 (x-miplatform)

2. `dto-definitions.yaml` 생성:
   - Request DTO 정의
   - Response DTO 정의
   - 공통 DTO (Paging, Error 등)

3. `error-responses.yaml` 생성:
   - 표준 에러 코드 정의
   - MiPlatform ErrorCode/ErrorMsg 매핑

**API Spec Schema:**
```yaml
# openapi-spec.yaml
openapi: "3.0.3"
info:
  title: "${FEATURE_ID} API"
  version: "1.0.0"
  description: "${FEATURE_NAME}"
  x-miplatform:
    enabled: true
    screen_id: "${SCREEN_ID}"

paths:
  /path/to/endpoint:
    post:
      operationId: "operationName"
      summary: "Operation summary"
      x-miplatform:
        dataset_request: "ds_master"
        dataset_response: "ds_Mst"
      requestBody:
        $ref: "#/components/requestBodies/OperationRequest"
      responses:
        "200":
          $ref: "#/components/responses/OperationResponse"
```

**Validation:** 모든 endpoint에 request/response 스키마 정의

**Outputs:**
- `api-specs/openapi-spec.yaml`
- `api-specs/dto-definitions.yaml`
- `api-specs/error-responses.yaml`

---

#### Step 4: Business Logic Spec Generation

**Description:** Service 계층 구현 명세 생성

**Sub-steps:**
1. `service-spec.yaml` 생성:
   - Service 클래스 정의
   - 메서드 시그니처
   - 주입 의존성 (DAO, 다른 Service)
   - 트랜잭션 설정

2. `validation-spec.yaml` 생성:
   - 필드별 검증 규칙
   - 에러 메시지 정의
   - 검증 순서

3. `business-rules.yaml` 생성:
   - 비즈니스 조건 로직
   - 계산 규칙
   - 상태 전이 규칙

**Service Spec Schema:**
```yaml
# service-spec.yaml
services:
  - class_name: "${DOMAIN}${FEATURE_ID}Service"
    package: "com.hallain.${domain}.service"
    interface: "${DOMAIN}${FEATURE_ID}Service"

    dependencies:
      - type: "repository"
        name: "${DOMAIN}${FEATURE_ID}Repository"
        injection: "constructor"

    methods:
      - name: "selectList"
        signature: "List<${DTO}> selectList(${SearchDTO} searchDto)"
        transaction:
          enabled: false
          read_only: true
        implementation:
          type: "simple_delegation"
          delegate_to: "repository.selectList"

      - name: "save"
        signature: "void save(List<${DTO}> dtoList)"
        transaction:
          enabled: true
          isolation: "DEFAULT"
          propagation: "REQUIRED"
        implementation:
          type: "batch_processing"
          logic:
            - "Iterate dtoList"
            - "Check rowStatus (INSERT/UPDATE/DELETE)"
            - "Delegate to repository method"
```

**Validation:** 모든 Service 메서드에 구현 명세 정의

**Outputs:**
- `business-logic/service-spec.yaml`
- `business-logic/validation-spec.yaml`
- `business-logic/business-rules.yaml`

---

#### Step 5: Data Model Spec Generation

**Description:** Entity 및 MyBatis Mapper 명세 생성

**Sub-steps:**
1. `entity-spec.yaml` 생성:
   - Entity/DTO 클래스 정의
   - 필드 목록 및 타입
   - DB 컬럼 매핑
   - Lombok 어노테이션 설정

2. `mybatis-mapper-spec.yaml` 생성:
   - Mapper Interface 정의
   - XML Mapper 파일 명세
   - SQL 쿼리 템플릿
   - Dynamic SQL 조건

**Entity Spec Schema:**
```yaml
# entity-spec.yaml
entities:
  - class_name: "${DOMAIN}${FEATURE_ID}DTO"
    package: "com.hallain.${domain}.dto"
    table: "TB_${TABLE_NAME}"

    annotations:
      - "@Data"
      - "@Builder"
      - "@NoArgsConstructor"
      - "@AllArgsConstructor"

    fields:
      - name: "siteCd"
        type: "String"
        column: "SITE_CD"
        db_type: "VARCHAR(10)"
        nullable: false
        description: "사이트 코드"

      - name: "totalQty"
        type: "BigDecimal"
        column: "TOTAL_QTY"
        db_type: "NUMBER(18,6)"
        nullable: true
        description: "총수량"
```

**MyBatis Mapper Spec Schema:**
```yaml
# mybatis-mapper-spec.yaml
mapper:
  namespace: "com.hallain.${domain}.repository.${DOMAIN}${FEATURE_ID}Mapper"
  interface: "${DOMAIN}${FEATURE_ID}Repository"
  xml_file: "mapper/${domain}/${DOMAIN}${FEATURE_ID}Mapper.xml"

  statements:
    - id: "selectList"
      type: "select"
      result_type: "${DTO}"
      parameter_type: "${SearchDTO}"
      sql_template: |
        SELECT ${COLUMNS}
        FROM ${TABLE}
        WHERE 1=1
        <if test="siteCd != null">
          AND SITE_CD = #{siteCd}
        </if>
      dynamic_conditions:
        - field: "siteCd"
          operator: "equals"
          condition_type: "if_not_null"
```

**Validation:** 모든 VO 클래스에 Entity/Mapper 정의

**Outputs:**
- `data-model/entity-spec.yaml`
- `data-model/mybatis-mapper-spec.yaml`

---

#### Step 6: Main.yaml Integration

**Description:** 통합 Specification 파일 생성

**Sub-steps:**
1. 메타데이터 섹션 생성
2. Overview 섹션 생성 (Feature 요약)
3. Feature Classification 결정
4. Layers 섹션 생성 (파일 참조 + 요약)
5. Dependencies 섹션 생성
6. Technical Notes 섹션 생성
7. YAML 문법 검증 및 저장

**main.yaml Schema:**
```yaml
# main.yaml
metadata:
  generated_by: "s1-04-discovery-spec-generation"
  generated_at: "2026-01-07T10:00:00Z"
  domain: "${DOMAIN}"
  feature_id: "FEAT-${DOMAIN}-${NNN}"
  screen_id: "${SCREEN_ID}"
  priority: "${PRIORITY}"
  source_phase: "S1-P1.3"

overview:
  name: "${FEATURE_NAME}"
  description: "${FEATURE_DESCRIPTION}"
  complexity: "low|medium|high"
  migration_effort: "1-3|4-7|8+"  # Story points estimate

feature_classification:
  category: "CRUD|Search|Process|Report|Integration"
  patterns:
    - "Master-Detail"
    - "List-Search"
    - "Batch-Processing"
  mi_enabled: true
  requires_transaction: true
  requires_pagination: true

layers:
  l1_api_endpoints:
    directory: "api-specs/"
    files:
      - "openapi-spec.yaml"
      - "dto-definitions.yaml"
      - "error-responses.yaml"
    summary:
      total_endpoints: 3
      by_method:
        POST: 3
      mi_coverage: "100%"

  l2_business_logic:
    directory: "business-logic/"
    files:
      - "service-spec.yaml"
      - "validation-spec.yaml"
      - "business-rules.yaml"
    summary:
      services: 1
      methods: 5
      transactional_methods: 2
      validation_rules: 8

  l3_data_access:
    embedded: true  # main.yaml에 포함
    summary:
      repositories: 1
      mapper_statements: 5

  l4_data_model:
    directory: "data-model/"
    files:
      - "entity-spec.yaml"
      - "mybatis-mapper-spec.yaml"
    summary:
      entities: 2
      total_fields: 15

  l5_database:
    embedded: true
    summary:
      tables: ["TB_PROD_PLAN", "TB_PROD_PLAN_DTL"]
      stored_procedures: []

dependencies:
  internal:
    - from: "${FeatureController}"
      to: "${FeatureService}"
      type: "injection"
    - from: "${FeatureService}"
      to: "${FeatureRepository}"
      type: "injection"
  external:
    - domain: "CM"
      service: "CommonCodeService"
      methods: ["getCodeList", "getCodeName"]
      reason: "공통코드 조회"

technical_notes:
  migration_warnings:
    - type: "WARNING"
      layer: "L5"
      code: "ORACLE_SPECIFIC"
      description: "CONNECT BY 사용 - CTE 변환 필요"
    - type: "INFO"
      layer: "L2"
      description: "트랜잭션 경계 명확 - @Transactional 적용 가능"

  special_handling:
    - type: "MiPlatform"
      description: "MiHandler 패턴 → REST API 변환 필요"
    - type: "Pagination"
      description: "ROWNUM 기반 페이징 → PageHelper 적용"

generation_hints:
  controller:
    base_class: "BaseController"
    annotations: ["@RestController", "@RequestMapping"]
  service:
    base_class: null
    annotations: ["@Service", "@RequiredArgsConstructor"]
  repository:
    base_class: null
    annotations: ["@Repository", "@Mapper"]
```

**Validation:** main.yaml >= 500 bytes

**Outputs:**
- `main.yaml`

---

#### Step 7: Schema Validation

**Description:** 생성된 main.yaml 및 하위 파일들이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | root | 필수 키 존재 (metadata, overview, layers, generation_hints) | ERROR | Yes |
| V002 | file | YAML 파싱 오류 없음 | ERROR | Yes |
| V003 | metadata.generated_by | 정확히 일치 | ERROR | Yes |
| V004 | metadata.feature_id | FEAT-{DOMAIN}-{NNN} 패턴 | ERROR | Yes |
| V005 | main.yaml | 파일 크기 >= 500 bytes | ERROR | Yes |
| V006 | layers | 5개 Layer 요약 모두 존재 | ERROR | Yes |
| V007 | feature_classification.category | enum 검증 | ERROR | Yes |
| V008 | directories | api-specs/, business-logic/, data-model/ 존재 | ERROR | Yes |
| V009 | overview.complexity | enum 검증 (low/medium/high) | ERROR | Yes |
| V010 | generation_hints | controller/service/repository 정의 | WARNING | No |

**Sub-steps:**
1. main.yaml 파일 로드
2. 하위 디렉토리 존재 확인:
   - api-specs/
   - business-logic/
   - data-model/
3. 스키마 파일 로드 및 검증 규칙 적용
4. 검증 실패 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재생성 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.3 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | MiPlatform 사용 | x-miplatform 확장 속성 추가 | 표준 REST API 형식 |
| DP-2 | Pagination 필요 | PageHelper/Pageable 스펙 추가 | 단순 List 반환 |
| DP-3 | Transaction 필요 | @Transactional 스펙 추가 | read-only 설정 |
| DP-4 | Cross-domain 의존성 | dependencies.external에 기록 | internal만 기록 |
| DP-5 | Dynamic SQL 사용 | mybatis-mapper-spec에 조건 추가 | 정적 SQL만 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage1-outputs/phase4/"
    pattern: "{Priority}/{Domain}/FEAT-{DOMAIN}-{NNN}/"

  example: "work/specs/stage1-outputs/phase4/P2-Core/PA/FEAT-PA-001/"
```

### 4.2 Output Files

| File | Type | Purpose | Required | Constraints |
|------|------|---------|----------|-------------|
| main.yaml | YAML | Feature 통합 Specification | Yes | Min 500 bytes, Max 1000 lines |
| api-specs/openapi-spec.yaml | YAML | OpenAPI 3.0 API 정의 | Yes | Max 300 lines |
| api-specs/dto-definitions.yaml | YAML | Request/Response DTO | Yes | Max 200 lines |
| api-specs/error-responses.yaml | YAML | 에러 응답 정의 | Yes | Max 100 lines |
| business-logic/service-spec.yaml | YAML | Service 구현 명세 | Yes | Max 300 lines |
| business-logic/validation-spec.yaml | YAML | 검증 규칙 명세 | Yes | Max 150 lines |
| business-logic/business-rules.yaml | YAML | 비즈니스 규칙 | Yes | Max 100 lines |
| data-model/entity-spec.yaml | YAML | Entity/DTO 정의 | Yes | Max 200 lines |
| data-model/mybatis-mapper-spec.yaml | YAML | MyBatis Mapper 명세 | Yes | Max 300 lines |

### 4.3 File Header

```yaml
# Generated by: s1-04-discovery-spec-generation
# Stage: 1 - Discovery
# Phase: 1.4 - Spec Generation
# Domain: ${DOMAIN}
# Feature: ${FEATURE_ID}
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
# Source: work/specs/stage1-outputs/phase3/...
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| main_exists | structural | `main.yaml` 존재 | ERROR | Yes |
| main_size | structural | `main.yaml` >= 500 bytes | ERROR | Yes |
| yaml_syntax | structural | YAML 파싱 오류 없음 | ERROR | Yes |
| directories_exist | structural | api-specs/, business-logic/, data-model/ 존재 | ERROR | Yes |
| layer_complete | content | 5개 Layer 요약 포함 | ERROR | Yes |
| endpoint_spec | content | 모든 endpoint에 request/response 정의 | WARNING | No |
| service_spec | content | 모든 service method에 구현 명세 | WARNING | No |

### 5.2 Manual Reviews

| Review | Reviewer | Criteria | Required |
|--------|----------|----------|----------|
| Spec sampling | Tech Lead | 랜덤 3개 Feature Spec 검토 | No |

### 5.3 Gate Criteria

```yaml
gate_criteria:
  id: "G1.4"
  name: "Spec Generation Gate"
  tier: "discovery_quality_gate"  # 상향 조정: Discovery 품질이 전체 파이프라인에 영향
  threshold: 85  # 70→85 상향 (QUERY-FIRST 전략에 따른 SQL 분석 품질 보장)
  metrics:
    - metric: "main_exists"
      weight: 0.3
      target: "true"
      formula: "main.yaml exists"
    - metric: "main_size"
      weight: 0.3
      target: ">= 500 bytes"
      formula: "file_size(main.yaml) >= 500"
    - metric: "directories"
      weight: 0.4
      target: "3"
      formula: "count of required directories"
  auto_commit:
    enabled: true
    message: "feat(S1-P1.4): Spec generation {feature_id}"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| S1-03 output missing | 입력 파일 없음 | Deep Analysis 미완료 | S1-03 재실행 후 진행 | No |
| Schema normalization fail | 타입 매핑 실패 | 비표준 Java 타입 | UNKNOWN 타입 마킹, 수동 검토 | No |
| main.yaml < 500 bytes | Gate 실패 | 불충분한 분석 데이터 | S1-03 재실행 또는 수동 보완 | Yes |
| Cross-domain reference | 외부 의존성 | 타 도메인 Service 참조 | dependencies.external에 기록 | No |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| main.yaml < 300 bytes | critical | Phase 중단, S1-03 재검토 | Tech Lead |
| Required dir missing | major | ERROR 로그, 계속 진행 불가 | Orchestrator |
| Normalization fail > 10% | minor | WARNING 로그, 계속 진행 | - |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 부분 실패 | 해당 Feature만 재실행 | Feature |
| 입력 누락 | S1-03 재실행 후 진행 | Phase (S1-P1.3) |
| 전체 실패 | 출력 디렉토리 삭제 후 재실행 | Phase |

---

## 7. Examples

### 7.1 Sample Input

**S1-03 summary.yaml:**
```yaml
metadata:
  feature_id: "FEAT-PA-001"
  screen_id: "PA01001"
  domain: "PA"

overview:
  name: "생산계획 조회"
  complexity: "medium"
  endpoints_count: 3
  services_count: 1

layers:
  l1_api_endpoints:
    file: "api-endpoints/FEAT-PA-001.yaml"
  l2_business_logic:
    file: "business-logic/FEAT-PA-001.yaml"
  # ...
```

### 7.2 Sample Output

**main.yaml:**
```yaml
# Generated by: s1-04-discovery-spec-generation
# Stage: 1 - Discovery
# Phase: 1.4 - Spec Generation
# Domain: PA
# Feature: FEAT-PA-001
# Generated: 2026-01-07T10:30:00Z
# Model: claude-opus-4-5-20251101

metadata:
  generated_by: "s1-04-discovery-spec-generation"
  generated_at: "2026-01-07T10:30:00Z"
  domain: "PA"
  feature_id: "FEAT-PA-001"
  screen_id: "PA01001"
  priority: "P2-Core"

overview:
  name: "생산계획 조회"
  description: "생산계획 목록/상세 조회 및 저장 기능"
  complexity: "medium"
  migration_effort: "4-7"

feature_classification:
  category: "CRUD"
  patterns:
    - "Master-Detail"
    - "List-Search"
  mi_enabled: true
  requires_transaction: true
  requires_pagination: true

layers:
  l1_api_endpoints:
    directory: "api-specs/"
    files:
      - "openapi-spec.yaml"
      - "dto-definitions.yaml"
      - "error-responses.yaml"
    summary:
      total_endpoints: 3
      by_method:
        POST: 3

  l2_business_logic:
    directory: "business-logic/"
    files:
      - "service-spec.yaml"
      - "validation-spec.yaml"
      - "business-rules.yaml"
    summary:
      services: 1
      methods: 5
      transactional_methods: 2

  l3_data_access:
    embedded: true
    summary:
      repositories: 1
      mapper_statements: 5

  l4_data_model:
    directory: "data-model/"
    files:
      - "entity-spec.yaml"
      - "mybatis-mapper-spec.yaml"
    summary:
      entities: 2
      total_fields: 15

  l5_database:
    embedded: true
    summary:
      tables: ["TB_PROD_PLAN", "TB_PROD_PLAN_DTL"]

dependencies:
  internal:
    - from: "PA01001Controller"
      to: "PA01001Service"
      type: "injection"
    - from: "PA01001Service"
      to: "PA01001Repository"
      type: "injection"
  external:
    - domain: "CM"
      service: "CommonCodeService"
      methods: ["getCodeList"]

technical_notes:
  migration_warnings:
    - type: "INFO"
      layer: "L2"
      description: "트랜잭션 경계 명확"
  special_handling:
    - type: "MiPlatform"
      description: "MiHandler → REST API 변환"
    - type: "Pagination"
      description: "ROWNUM → PageHelper"

generation_hints:
  controller:
    base_class: "BaseController"
    annotations: ["@RestController", "@RequestMapping(\"/api/pa/pa01001\")"]
  service:
    annotations: ["@Service", "@RequiredArgsConstructor", "@Transactional"]
  repository:
    annotations: ["@Repository", "@Mapper"]
```

**api-specs/openapi-spec.yaml:**
```yaml
# Generated by: s1-04-discovery-spec-generation
openapi: "3.0.3"
info:
  title: "FEAT-PA-001 API"
  version: "1.0.0"
  description: "생산계획 조회"
  x-miplatform:
    enabled: true
    screen_id: "PA01001"

paths:
  /api/pa/pa01001/list:
    post:
      operationId: "getList"
      summary: "생산계획 목록 조회"
      tags: ["PA01001"]
      x-miplatform:
        original_path: "/pa/PA01001/list.mi"
        dataset_request: "ds_master"
        dataset_response: "ds_Mst"
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
                $ref: "#/components/schemas/PA01001ListResponse"

components:
  schemas:
    PA01001SearchRequest:
      type: object
      properties:
        siteCd:
          type: string
          description: "사이트 코드"
        yyyymm:
          type: string
          description: "년월"
        pageNo:
          type: integer
          description: "페이지 번호"
        pageSize:
          type: integer
          description: "페이지 크기"

    PA01001ListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: "#/components/schemas/PA01001DTO"
        totalCount:
          type: integer
        pageNo:
          type: integer
        pageSize:
          type: integer

    PA01001DTO:
      type: object
      properties:
        siteCd:
          type: string
        siteNm:
          type: string
        yyyymm:
          type: string
        odrNo:
          type: string
        totalQty:
          type: number
          format: decimal
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| MiPlatform 미사용 | 일반 REST Controller | x-miplatform 속성 생략 |
| Transaction 없음 | read-only 조회만 | transactional: false |
| 외부 의존성 없음 | 단일 도메인 기능 | dependencies.external: [] |
| Dynamic SQL 없음 | 정적 쿼리만 | dynamic_conditions: [] |
| SP 호출 | Stored Procedure 사용 | stored_procedures 섹션에 기록 |

---

## Version History

### v1.1.0 (2026-01-08)
- Step 7: Schema Validation 추가
- s1-04-main-spec.schema.yaml 스키마 참조
- 10개 검증 규칙 (V001-V010) 적용
- 하위 디렉토리 존재 검증

### v1.0.0 (2026-01-07)
- Initial version
- OpenAPI 3.0 형식 API Spec 생성
- Service/Validation/Business Rules Spec 생성
- Entity/MyBatis Mapper Spec 생성
- main.yaml 통합 명세 생성
