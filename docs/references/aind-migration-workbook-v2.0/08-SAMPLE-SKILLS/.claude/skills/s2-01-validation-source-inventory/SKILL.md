---
name: s2-01-validation-source-inventory
description: Use when creating ground truth inventory from legacy source code, establishing independent validation baseline, or preparing for spec-to-source comparison (project)
---

# Source Inventory (Ground Truth)

> **Skill ID**: S2-01
> **Skill Type**: Validation (품질 검증 - Ground Truth 생성)
> **Stage**: 2 - Validation
> **Phase**: 2.1 - Source Inventory

## 1. Overview

### 1.1 Purpose

Legacy 소스코드에서 **Stage 1 산출물과 독립적으로** Ground Truth 목록을 생성합니다. 이 목록은 Stage 1에서 생성된 Specification의 완전성을 검증하기 위한 비교 기준으로 사용됩니다.

**핵심 원칙:**
- **독립성 (Independence)**: Stage 1 산출물을 참조하지 않고 소스코드에서 직접 추출
- **완전성 (Completeness)**: 모든 Controller, Service, DAO, SQL/SP, Entity 누락 없이 스캔
- **정확성 (Accuracy)**: 실제 소스코드 구조를 있는 그대로 반영

**추출 대상:**
| Layer | Scan Target | Pattern |
|-------|-------------|---------|
| Controller | `*Controller.java` | `@Controller`, `@RestController` |
| Service | `*Service.java`, `*ServiceImpl.java` | `@Service`, interface/impl 쌍 |
| DAO | `*Dao.java`, `*Mapper.java` | DAO/Mapper 클래스 |
| SQL/SP | `*.xml` (MyBatis) | `<select>`, `<insert>`, `<update>`, `<delete>` |
| Entity | `*VO.java`, `*DTO.java`, `*Entity.java` | 도메인 객체 |

### 1.2 Validation Scope

| Dimension | Weight | Match Criteria |
|-----------|--------|----------------|
| Controller | 0.25 | 클래스 존재 및 메서드 목록 |
| Service | 0.25 | 인터페이스/구현체 매핑 |
| DAO | 0.20 | DAO/Mapper 클래스 및 메서드 |
| SQL | 0.20 | MyBatis 매퍼 SQL 목록 |
| Entity | 0.10 | VO/DTO/Entity 클래스 목록 |

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **독립성** | Stage 1 산출물 절대 참조 금지 | Confirmation bias 방지 |
| **완전성** | 5개 Layer 모두 스캔 | 누락된 컴포넌트 탐지 목적 |
| **결정론** | 동일 입력 → 동일 출력 | 재현 가능한 검증 |
| **원시성** | 소스 있는 그대로 추출 | 해석/가공 없이 raw data |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S2-01은 Ground Truth를 독립적으로 생성하며, **SQL/Mapper 계층이 검증의 핵심 기준**으로 사용됨

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s1-04-discovery-spec-generation` | Stage 1 완료 후 Validation 시작 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s2-02-validation-structural-comparison` | Ground truth 기반 비교 수행 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "s1-04-discovery-spec-generation"
    relationship: "Stage 1 완료 후 실행"
    outputs_used: []  # 독립적 - Stage 1 출력 사용 금지
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| legacy_source | directory | `${LEGACY_CODEBASE}/src/main/java/` | Java | Yes |
| sql_mappings | directory | `${LEGACY_CODEBASE}/src/main/resources/**/*.xml` | XML | Yes |
| domain_priorities | file | `work/assessment/data/phase2/domain-priorities.yaml` | YAML | Yes |

**CRITICAL - 사용 금지 입력:**
| Name | Location | Reason |
|------|----------|--------|
| stage1_specs | `work/specs/stage1-outputs/` | 독립성 보장 - 참조 금지 |
| feature-inventory.yaml | Stage 1 Phase 1 | 독립성 보장 - 참조 금지 |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Glob | - | 파일 패턴 매칭 |
| Grep | - | 어노테이션/패턴 검색 |
| Read | - | 파일 내용 읽기 |

**Access:**
- Legacy 소스코드 읽기 권한

**Resources:**
- 메모리: 도메인당 최대 3,000개 파일 처리

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
    timeout_minutes: 60
    retry_on_failure: 3
```

### 3.2 Validation Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Source Scan  │────▶│ Layer Parse  │────▶│ Dependency   │────▶│ Inventory    │
│ (Raw Files)  │     │ (5 Layers)   │     │ Extract      │     │ Generation   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 3.3 Process Steps

#### Step 1: Controller Layer Scan

**Description:** Controller 클래스 스캔 및 메서드 추출

**Sub-steps:**
1. `*Controller.java` 파일 패턴 검색
2. `@Controller`, `@RestController` 어노테이션 확인
3. `@RequestMapping` 계열 메서드 추출
4. HTTP Method 및 URL 패턴 기록

**Validation:** 모든 Controller 클래스 발견

**Outputs:**
- Controller 목록 (클래스명, 메서드명, URL)

---

#### Step 2: Service Layer Scan

**Description:** Service 인터페이스 및 구현체 스캔

**Sub-steps:**
1. `*Service.java` 인터페이스 검색
2. `*ServiceImpl.java` 구현체 매칭
3. `@Service` 어노테이션 확인
4. 클래스 레벨 어노테이션 수집 (`@Transactional`, `@Service` 등)
5. public 메서드 목록 추출 (full signature 포함)
6. 메서드 레벨 어노테이션 수집 (`@Transactional` 등)

**메서드 시그니처 추출:**
- 반환 타입 (return_type)
- 파라미터 목록 (parameters: name, type)
- 전체 시그니처 문자열 (signature)

**Validation:** 모든 Service 클래스 발견

**Outputs:**
- Service 목록 (인터페이스, 구현체, 메서드 + 시그니처)

---

#### Step 3: DAO Layer Scan

**Description:** DAO/Mapper 클래스 스캔

**Sub-steps:**
1. `*Dao.java`, `*Mapper.java` 패턴 검색
2. MyBatis Mapper 인터페이스 식별
3. 메서드 시그니처 추출

**Validation:** 모든 DAO 클래스 발견

**Outputs:**
- DAO 목록 (클래스명, 메서드명)

---

#### Step 4: SQL/SP Layer Scan

**Description:** MyBatis XML 매퍼 스캔

**Sub-steps:**
1. `*.xml` 파일 검색 (mapper 경로)
2. `<mapper namespace="">` 파싱
3. `<select>`, `<insert>`, `<update>`, `<delete>` 태그 추출
4. SQL ID 및 parameterType/resultType 기록

**Validation:** 모든 SQL 매핑 발견

**Outputs:**
- SQL 목록 (namespace, id, type)

---

#### Step 5: Entity Layer Scan

**Description:** VO/DTO/Entity 클래스 스캔

**Sub-steps:**
1. `*VO.java`, `*DTO.java`, `*Entity.java` 패턴 검색
2. 필드 목록 추출
3. 타입 정보 기록 (필수)
4. Java FQN 타입 정보 기록 (java.lang.String 등)

**필드 타입 추출:**
- type: 간단 타입명 (String, Integer, etc.) - **필수**
- java_type: Fully Qualified Name (java.lang.String 등) - 선택

**Validation:** 모든 Entity 클래스 발견

**Outputs:**
- Entity 목록 (클래스명, 필드 목록 + 타입)

---

#### Step 6: External Dependencies Scan

**Description:** DB Link, Stored Procedure, 외부 API 호출 수집

**Sub-steps:**
1. SQL XML에서 DB Link 패턴 검색 (`@TO_`, `@DBLINK` 등)
2. Stored Procedure/Function 호출 식별 (`CALL`, `PKG.FN_*` 패턴)
3. Service에서 외부 API 호출 검색 (RestTemplate, WebClient 등)
4. 사용처 매핑 (어떤 SQL/Service에서 사용하는지)

**추출 대상:**
| Type | Pattern | Example |
|------|---------|---------|
| DB Link | `@{LINK_NAME}` | `@TO_EPPROD_EAM` |
| Stored Procedure | `{PKG}.{FN/SP}_*` | `ECM_FUNCTION_PKG.FN_MILOGINHISTORY_NEW` |
| External API | `RestTemplate`, `WebClient` | HTTP 호출 |

**Validation:** 모든 외부 연동 발견

**Outputs:**
- external_dependencies 섹션 (db_links, stored_procedures, external_apis)

---

#### Step 7: Inventory Generation

**Description:** source-inventory.yaml 생성

**Sub-steps:**
1. 5개 Layer 결과 통합
2. external_dependencies 섹션 추가
3. 표준 헤더 추가
4. Summary 섹션 생성
5. Layers 섹션 생성
6. YAML 문법 검증

**Validation:** YAML 파일 생성 완료

---

#### Step 8: Schema Validation

**Description:** 생성된 source-inventory.yaml이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | root | 필수 키 존재 (metadata, summary, layers) | ERROR | Yes |
| V002 | file | YAML 파싱 오류 없음 | ERROR | Yes |
| V003 | metadata.independence_verified | true 여야 함 | ERROR | Yes |
| V004 | file | Stage 1 경로 참조 없음 | ERROR | Yes |
| V005 | file | FEAT-* 패턴 사용 안 함 | ERROR | Yes |
| V006 | metadata.generated_by | 정확히 일치 | ERROR | Yes |
| V007 | layers.controllers[].methods[].http_method | enum 검증 | ERROR | Yes |
| V008 | layers.sql_statements[].statements[].type | enum 검증 | ERROR | Yes |
| V009 | layers.entities[].type | enum 검증 (VO/DTO/Entity) | ERROR | Yes |
| V010 | layers | 5개 Layer 배열 모두 존재 | ERROR | Yes |

**Sub-steps:**
1. source-inventory.yaml 파일 로드
2. 독립성 검증:
   - Stage 1 경로 참조 없음 확인
   - FEAT-* 패턴 사용 없음 확인
3. 스키마 파일 로드 및 검증 규칙 적용
4. 검증 실패 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재생성 필요 (특히 independence 위반)
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.4 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | 파일 인코딩 오류 | UTF-8 → EUC-KR fallback | 정상 처리 |
| DP-2 | Service 구현체 없음 | WARNING 로그, interface만 기록 | 정상 매핑 |
| DP-3 | 빈 도메인 | ERROR 반환 | 정상 진행 |
| DP-4 | 예상 출력 >= 200KB (v1.3.0) | Layer별 분할 저장 | 단일 파일 저장 |

---

### 3.5 Large File Handling (v1.3.0)

> **⚠️ Read Tool Limit**: Claude Code Read 도구는 256KB 제한이 있음. 대형 도메인(PA 등)은 2MB+ 출력 가능하므로 분할 저장 필수

#### 3.5.1 크기 판단 기준

| 조건 | 처리 방식 |
|------|----------|
| 예상 출력 < 200KB | 단일 `source-inventory.yaml` 생성 |
| 예상 출력 >= 200KB | Layer별 `source-inventory/` 디렉토리 분할 저장 |

**크기 추정 공식:**
```yaml
estimated_size_kb: |
  controllers * 0.5KB +
  services * 0.8KB +
  daos * 0.3KB +
  sql_statements * 0.4KB +
  entities * 0.6KB +
  external_dependencies * 0.2KB
```

**임계값 예시:**
- PA 도메인: 124 controllers + 98 services + 87 daos + 456 sql + 234 entities ≈ 500KB → **분할 필요**
- QM 도메인: 20 controllers + 15 services + 12 daos + 50 sql + 30 entities ≈ 60KB → **단일 파일**

#### 3.5.2 분할 저장 구조

```
{output_directory}/
├── source-inventory/           # 분할 저장 시 디렉토리
│   ├── _manifest.yaml          # 인덱스 + metadata + summary
│   ├── controllers.yaml        # layers.controllers
│   ├── services.yaml           # layers.services
│   ├── daos.yaml               # layers.daos
│   ├── sql_statements.yaml     # layers.sql_statements
│   ├── entities.yaml           # layers.entities
│   └── external_deps.yaml      # external_dependencies
│
└── source-inventory.yaml       # 단일 파일 (작은 도메인)
```

#### 3.5.3 Manifest 파일 스키마

```yaml
# source-inventory/_manifest.yaml
metadata:
  generated_by: "s2-01-validation-source-inventory"
  generated_at: "2026-01-07T10:00:00Z"
  domain: "PA"
  source_path: "hallain/src/main/java/com/hallain/pa/"
  independence_verified: true
  chunked: true  # 분할 저장 표시
  chunk_version: "1.0"

summary:
  total_controllers: 124
  total_services: 98
  total_daos: 87
  total_sql_statements: 456
  total_entities: 234
  by_layer:
    # ... 기존 by_layer 내용

chunks:
  - name: "controllers"
    file: "controllers.yaml"
    item_count: 124
    size_kb: 62
  - name: "services"
    file: "services.yaml"
    item_count: 98
    size_kb: 78
  - name: "daos"
    file: "daos.yaml"
    item_count: 87
    size_kb: 26
  - name: "sql_statements"
    file: "sql_statements.yaml"
    item_count: 456
    size_kb: 182
  - name: "entities"
    file: "entities.yaml"
    item_count: 234
    size_kb: 140
  - name: "external_dependencies"
    file: "external_deps.yaml"
    item_count: 15
    size_kb: 3
```

#### 3.5.4 Chunk 파일 스키마

각 청크 파일은 해당 Layer 데이터만 포함:

```yaml
# source-inventory/controllers.yaml
# Chunk: controllers
# Parent: source-inventory/_manifest.yaml
# Generated: 2026-01-07T10:00:00Z

controllers:
  - class: "PA01001Controller"
    file: "src/main/java/com/hallain/pa/controller/PA01001Controller.java"
    methods:
      - name: "getList"
        http_method: "POST"
        url: "/pa/PA01001/list"
  # ... 나머지 controllers
```

#### 3.5.5 분할 저장 Process

```yaml
chunked_output_process:
  step_1:
    name: "크기 추정"
    action: "Layer별 항목 수로 예상 크기 계산"

  step_2:
    name: "분할 결정"
    condition: "estimated_size >= 200KB"
    if_true: "분할 저장 모드"
    if_false: "단일 파일 저장"

  step_3:
    name: "디렉토리 생성"
    action: "source-inventory/ 디렉토리 생성"

  step_4:
    name: "Layer별 저장"
    action: |
      각 Layer를 개별 YAML 파일로 저장:
      - controllers.yaml
      - services.yaml
      - daos.yaml
      - sql_statements.yaml
      - entities.yaml
      - external_deps.yaml

  step_5:
    name: "Manifest 생성"
    action: "_manifest.yaml에 metadata, summary, chunks 목록 기록"

  step_6:
    name: "검증"
    action: "모든 파일이 200KB 미만인지 확인"
```

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage2-outputs/phase1/"
    pattern: "{Priority}/{Domain}/"

  example: "work/specs/stage2-outputs/phase1/P2-Core/PA/"
```

### 4.2 Output Files

| File | Type | Purpose | Required | Constraints |
|------|------|---------|----------|-------------|
| source-inventory.yaml | YAML | Ground truth 목록 | Yes | 5개 Layer 모두 포함 |

### 4.3 File Header

```yaml
# Generated by: s2-01-validation-source-inventory
# Stage: 2 - Validation
# Phase: 2.1 - Source Inventory
# Domain: ${DOMAIN}
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
# IMPORTANT: This is GROUND TRUTH - generated independently from Stage 1
```

### 4.4 Output Schema

```yaml
# source-inventory.yaml
metadata:
  generated_by: "s2-01-validation-source-inventory"
  generated_at: "2026-01-07T10:00:00Z"
  domain: "PA"
  source_path: "hallain/src/main/java/com/hallain/pa/"
  independence_verified: true  # Stage 1 미참조 확인

summary:
  total_controllers: 124
  total_services: 98
  total_daos: 87
  total_sql_statements: 456
  total_entities: 234
  by_layer:
    controller:
      classes: 124
      methods: 512
    service:
      interfaces: 98
      implementations: 98
      methods: 678
    dao:
      classes: 87
      methods: 345
    sql:
      select: 234
      insert: 89
      update: 98
      delete: 35
    entity:
      vo: 120
      dto: 89
      entity: 25

layers:
  controllers:
    - class: "PA01001Controller"
      file: "src/main/java/com/hallain/pa/controller/PA01001Controller.java"
      methods:
        - name: "getList"
          http_method: "POST"
          url: "/pa/PA01001/list"
        - name: "getDetail"
          http_method: "POST"
          url: "/pa/PA01001/detail"

  services:
    - interface: "PA01001Service"
      implementation: "PA01001ServiceImpl"
      file: "src/main/java/com/hallain/pa/service/impl/PA01001ServiceImpl.java"
      class_annotations:
        - "@Service"
        - "@Transactional(readOnly=true)"
      methods:
        - name: "getList"
          return_type: "List<PA01001VO>"
          parameters:
            - name: "searchVO"
              type: "PA01001SearchVO"
          signature: "List<PA01001VO> getList(PA01001SearchVO)"
          annotations: []
        - name: "getDetail"
          return_type: "PA01001VO"
          parameters:
            - name: "planId"
              type: "String"
          signature: "PA01001VO getDetail(String)"
          annotations: []

  daos:
    - class: "PA01001Dao"
      file: "src/main/java/com/hallain/pa/dao/PA01001Dao.java"
      mapper_xml: "src/main/resources/mapper/pa/PA01001Mapper.xml"
      methods:
        - name: "selectList"
        - name: "selectDetail"

  sql_statements:
    - namespace: "com.hallain.pa.dao.PA01001Dao"
      xml_file: "src/main/resources/mapper/pa/PA01001Mapper.xml"
      statements:
        - id: "selectList"
          type: "select"
          result_type: "PA01001VO"
        - id: "selectDetail"
          type: "select"
          result_type: "PA01001VO"

  entities:
    - class: "PA01001VO"
      type: "VO"
      file: "src/main/java/com/hallain/pa/vo/PA01001VO.java"
      fields:
        - name: "planId"
          type: "String"
          java_type: "java.lang.String"
        - name: "planName"
          type: "String"
          java_type: "java.lang.String"

external_dependencies:
  db_links:
    - name: "TO_EPPROD_EAM"
      used_in:
        - "SiteMapper.selectSite"
  stored_procedures:
    - package: "ECM_FUNCTION_PKG"
      function: "FN_MILOGINHISTORY_NEW"
      called_from:
        - "SiteMapper.callMIProc"
  external_apis: []
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| file_exists | structural | `source-inventory.yaml` 존재 | ERROR | Yes |
| yaml_syntax | structural | YAML 파싱 오류 없음 | ERROR | Yes |
| layer_coverage | completeness | 5개 Layer 모두 존재 | ERROR | Yes |
| independence | integrity | Stage 1 출력 참조 없음 | ERROR | Yes |
| non_empty | content | 각 Layer에 최소 1개 항목 | WARNING | No |

### 5.2 Independence Verification

| Check | Criteria | Blocking |
|-------|----------|----------|
| No S1 reference | Stage 1 경로 참조 없음 | Yes |
| Raw source only | 소스코드에서만 추출 | Yes |
| No feature-id | Feature ID 사용 안 함 | Yes |

### 5.3 Gate Criteria

```yaml
gate_criteria:
  id: "G2.1"
  name: "Source Inventory Gate"
  tier: "phase_gate"
  threshold: 70
  metrics:
    - metric: "file_exists"
      weight: 0.4
      target: "true"
      formula: "source-inventory.yaml exists"
    - metric: "independence"
      weight: 0.4
      target: "true"
      formula: "NOT derived from Stage 1"
    - metric: "layer_completeness"
      weight: 0.2
      target: "5"
      formula: "count of non-empty layers"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Empty domain | layers 모두 0 | 잘못된 도메인 경로 | 경로 확인 | Yes |
| Encoding error | 파일 읽기 실패 | EUC-KR/UTF-8 혼용 | UTF-8 → EUC-KR fallback | Auto |
| Large domain | timeout | PA 2,895 파일 | batch 분할 | Yes |
| Orphan impl | 인터페이스 없음 | 구현체만 존재 | WARNING 로그 | Auto |
| **Large output** (v1.3.0) | Read tool 256KB 초과 | 대형 도메인 출력 | Layer별 분할 저장 (Section 3.5) | Auto |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Independence 위반 | critical | 즉시 중단, 재실행 | Tech Lead |
| Layer 누락 | major | WARNING 로그, 원인 분석 | Orchestrator |
| 비정상 패턴 | minor | 로그 기록, 계속 진행 | - |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 부분 실패 | 해당 도메인만 재실행 | Domain |
| 전체 실패 | 소스 경로 확인 후 재실행 | Phase |
| Independence 위반 | 출력 삭제, 처음부터 재실행 | Phase |

---

## 7. Examples

### 7.1 Sample Input

**Source Structure:**
```
hallain/src/main/java/com/hallain/pa/
├── controller/
│   └── PA01001Controller.java
├── service/
│   ├── PA01001Service.java
│   └── impl/
│       └── PA01001ServiceImpl.java
├── dao/
│   └── PA01001Dao.java
└── vo/
    └── PA01001VO.java

hallain/src/main/resources/mapper/pa/
└── PA01001Mapper.xml
```

### 7.2 Sample Output

```yaml
# Generated by: s2-01-validation-source-inventory
# Stage: 2 - Validation
# Phase: 2.1 - Source Inventory
# Domain: PA
# Generated: 2026-01-07T10:30:00Z
# Model: claude-opus-4-5-20251101
# IMPORTANT: This is GROUND TRUTH - generated independently from Stage 1

metadata:
  generated_by: "s2-01-validation-source-inventory"
  generated_at: "2026-01-07T10:30:00Z"
  domain: "PA"
  source_path: "hallain/src/main/java/com/hallain/pa/"
  independence_verified: true

summary:
  total_controllers: 1
  total_services: 1
  total_daos: 1
  total_sql_statements: 2
  total_entities: 1
  by_layer:
    controller:
      classes: 1
      methods: 3
    service:
      interfaces: 1
      implementations: 1
      methods: 3
    dao:
      classes: 1
      methods: 2
    sql:
      select: 2
      insert: 0
      update: 0
      delete: 0
    entity:
      vo: 1
      dto: 0
      entity: 0

layers:
  controllers:
    - class: "PA01001Controller"
      file: "src/main/java/com/hallain/pa/controller/PA01001Controller.java"
      methods:
        - name: "getList"
          http_method: "POST"
          url: "/pa/PA01001/list"
        - name: "getDetail"
          http_method: "POST"
          url: "/pa/PA01001/detail"
        - name: "save"
          http_method: "POST"
          url: "/pa/PA01001/save"

  services:
    - interface: "PA01001Service"
      implementation: "PA01001ServiceImpl"
      file: "src/main/java/com/hallain/pa/service/impl/PA01001ServiceImpl.java"
      class_annotations:
        - "@Service"
        - "@Transactional(readOnly=true)"
      methods:
        - name: "getList"
          return_type: "List<PA01001VO>"
          parameters:
            - name: "searchVO"
              type: "PA01001SearchVO"
          signature: "List<PA01001VO> getList(PA01001SearchVO)"
          annotations: []
        - name: "getDetail"
          return_type: "PA01001VO"
          parameters:
            - name: "planId"
              type: "String"
          signature: "PA01001VO getDetail(String)"
          annotations: []
        - name: "save"
          return_type: "int"
          parameters:
            - name: "vo"
              type: "PA01001VO"
          signature: "int save(PA01001VO)"
          annotations:
            - "@Transactional"

  daos:
    - class: "PA01001Dao"
      file: "src/main/java/com/hallain/pa/dao/PA01001Dao.java"
      mapper_xml: "src/main/resources/mapper/pa/PA01001Mapper.xml"
      methods:
        - name: "selectList"
        - name: "selectDetail"

  sql_statements:
    - namespace: "com.hallain.pa.dao.PA01001Dao"
      xml_file: "src/main/resources/mapper/pa/PA01001Mapper.xml"
      statements:
        - id: "selectList"
          type: "select"
          result_type: "PA01001VO"
        - id: "selectDetail"
          type: "select"
          result_type: "PA01001VO"

  entities:
    - class: "PA01001VO"
      type: "VO"
      file: "src/main/java/com/hallain/pa/vo/PA01001VO.java"
      fields:
        - name: "planId"
          type: "String"
          java_type: "java.lang.String"
        - name: "planName"
          type: "String"
          java_type: "java.lang.String"

external_dependencies:
  db_links: []
  stored_procedures: []
  external_apis: []
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| 빈 도메인 | 소스 파일 0개 | ERROR: No source files found |
| Service 인터페이스만 | 구현체 없음 | WARNING + interface만 기록 |
| DAO 없는 Service | 직접 JDBC 사용 | DAO layer 비어있음 기록 |
| XML 없는 DAO | Annotation 기반 | SQL layer 비어있음 기록 |

---

## Version History

### v1.3.0 (2026-01-13)
- **Large File Handling 추가**
  - Section 3.5: 대용량 파일 분할 저장 전략 추가
  - 256KB Read Tool 제한 대응
  - Layer별 분할 저장 구조 정의 (source-inventory/ 디렉토리)
  - Manifest 파일 스키마 (_manifest.yaml)
  - DP-4: 크기 기반 분할 결정 Decision Point 추가
- **Known Issues 추가**: Large output 이슈 및 해결책

### v1.2.0 (2026-01-13)
- Step 2: Service Layer - 메서드 시그니처 전체 비교 (parameters, signature) 추가
- Step 2: Service Layer - 클래스/메서드 어노테이션 수집 (@Transactional 등) 추가
- Step 5: Entity Layer - 필드 타입 필수화, java_type (FQN) 추가
- Step 6: External Dependencies Scan 신규 추가 (DB Link, Stored Procedure, External API)
- Step 7, 8 번호 재정렬

### v1.1.0 (2026-01-08)
- Step 7: Schema Validation 추가
- s2-01-source-inventory.schema.yaml 스키마 참조
- 10개 검증 규칙 (V001-V010) 적용
- 독립성 검증 규칙 강화 (V003-V005)

### v1.0.0 (2026-01-07)
- Initial version
- 5-Layer 독립적 Ground Truth 생성
- Independence verification 포함
