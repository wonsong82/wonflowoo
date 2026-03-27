---
name: s1-02-discovery-miplatform-protocol
description: Use when analyzing MiPlatform RIA protocol patterns, extracting request/response schemas from MiHandler usage, or documenting Dataset structures for API translation (project)
---

# MiPlatform Protocol Analysis

> **Skill ID**: S1-02
> **Skill Type**: Analysis (MiPlatform 프로토콜에서 스키마 추출)
> **Stage**: 1 - Discovery
> **Phase**: 1.2 - MiPlatform Protocol Analysis

## 1. Overview

### 1.1 Purpose

MiPlatform RIA 프로토콜을 사용하는 컨트롤러를 분석하여 request/response 스키마를 추출하고 `miplatform-protocol.yaml`을 생성합니다. 이 분석은 Spring Boot 마이그레이션 시 API 변환 계층 설계의 기초가 됩니다.

**분석 대상:**
- `MiHandler`를 사용하는 컨트롤러 메서드
- `.mi` 확장자 RequestMapping 엔드포인트
- PlatformData의 Dataset/Variable 구조

**추출 정보:**
- Request Dataset 스키마 (이름, VO 클래스, 컬럼 구조)
- Request Variable 목록 (이름, 타입)
- Response Dataset 스키마
- Response Variable 목록 (ErrorCode, COMM_* 등 표준 변수 포함)

### 1.2 Scope

**In Scope:**
- MiHandler 인스턴스화 패턴 감지
- `getObject()`, `getObjectList()`, `getMiPlatformMap()` 호출 분석
- `setDataset()`, `add()`, `addStr()` 호출 분석
- VO 클래스 필드 → Dataset 컬럼 타입 매핑
- miplatform-protocol.yaml 생성

**Out of Scope:**
- 일반 Spring MVC 엔드포인트 분석 (→ `s1-01-discovery-feature-inventory`)
- Service/DAO 계층 비즈니스 로직 분석 (→ `s1-03-discovery-deep-analysis`)
- 실제 API 변환 구현 (→ Stage 4)

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Coverage** | 95% 이상 MiPlatform 엔드포인트 커버 | 누락된 프로토콜은 API 변환 실패 초래 |
| **Schema Accuracy** | Dataset 컬럼 타입 정확한 추출 | 타입 불일치는 런타임 오류 발생 |
| **Completeness** | Request + Response 쌍 완전 추출 | 편향된 분석은 변환 설계 오류 유발 |
| **VO Tracing** | VO 클래스까지 추적하여 스키마 도출 | 동적 Dataset도 정적 스키마로 문서화 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S1-02는 프로토콜 스키마를 분석하나, **후속 Phase(S1-03)에서 SQL-First 역추적**을 통해 모든 SQL이 분석됨
> - MiPlatform VO 타입 정보가 S1-03 SQL 분석 시 parameterClass/resultClass 매핑에 활용됨

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s1-01-discovery-feature-inventory` (S1-01) | Feature 목록과 엔드포인트 기반으로 MiPlatform 분석 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s1-03-discovery-deep-analysis` (S1-03) | 프로토콜 스키마를 5-Layer SQL-First 분석에 활용 |
| `s3-01-preparation-api-design` (S3-01) | Request/Response 스키마 기반 API 설계 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S1-01"
    skill_name: "s1-01-discovery-feature-inventory"
    dependency_type: "input"
    artifact: "feature-inventory.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| feature_inventory | file | `work/specs/stage1-outputs/phase1/{Priority}/{Domain}/feature-inventory.yaml` | YAML | Yes |
| legacy_controllers | directory | `hallain/src/main/java/**/controller/` | Java | Yes |
| miplatform_framework | directory | `hallain/src/main/java/benitware/framework/` | Java | Yes |
| vo_classes | directory | `hallain/src/main/java/**/vo/` | Java | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Grep | - | MiHandler 패턴 검색 |
| Read | - | Java 파일 분석 |
| Glob | - | VO 클래스 파일 탐색 |

**Access:**
- Legacy 소스코드 읽기 권한

**Knowledge:**
- MiHandler API 이해 필수
- PlatformData 구조 (VariableList + DatasetList)

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: parallel
  unit: adaptive  # domain 또는 sub-wave (크기에 따라)
  task_naming:
    pattern: "FEAT-{DOMAIN}-MIP"
    example: "FEAT-PA-MIP, FEAT-MM-MIP"
  parallelization:
    max_sessions: 10
    batch_unit: adaptive
    timeout_minutes: 120
    retry_on_failure: 3

  # v1.3.0: Adaptive Batching
  size_assessment:
    thresholds:
      small_domain:
        max_controllers: 100
        max_endpoints: 200
        strategy: single_pass
      large_domain:
        min_controllers: 100
        min_endpoints: 200
        strategy: sub_wave_division

    assessment_command: |
      controller_count=$(find hallain/src/main/java/com/halla/{domain}/ \
        -name "*Controller.java" 2>/dev/null | wc -l)
      if [ $controller_count -gt 100 ]; then
        echo "LARGE_DOMAIN: Sub-wave division required"
      else
        echo "SMALL_DOMAIN: Single pass OK"
      fi
```

### 3.2 Process Steps

#### Step 1: MiHandler Detection

**Description:** 도메인 컨트롤러에서 MiHandler를 사용하는 메서드 탐색

**Sub-steps:**
1. feature-inventory.yaml에서 도메인 엔드포인트 목록 로드
2. 컨트롤러 파일에서 `MiHandler` 임포트/사용 검색
3. `.mi` RequestMapping 패턴 필터링

**Detection Patterns:**
```java
// MiHandler 인스턴스화 패턴
new MiHandler(request)
new MiHandler(request, false)
new MiHandler(request, object, boolean)

// RequestMapping 패턴
@RequestMapping("*.mi")
@RequestMapping(value = ".../.mi")
```

**Validation:** MiHandler 사용 메서드 목록 생성

**Outputs:**
- MiPlatform 엔드포인트 목록 (path, controller, method)

---

#### Step 2: Input Schema Extraction

**Description:** Request에서 Dataset/Variable 스키마 추출

**Sub-steps:**
1. `getObject(dsName, Class)` 호출 분석
   - Dataset 이름 추출
   - VO 클래스 참조 추출
2. `getObjectList(dsName, Class)` 호출 분석
   - 리스트 Dataset 식별
3. `getMiPlatformMap()`, `getMiPlatformList()` 호출 분석
   - 동적 스키마 마킹
4. Variable 추출 메서드 분석
   - `getValueString(name)` → STRING 타입
   - `getValueInt(name)` → INT 타입
   - `getPageNo()`, `getMaxResult()` → 페이징 변수

**Extraction Patterns:**
```java
// Dataset 추출
UserVO vo = (UserVO) miHandler.getObject("ds_master", UserVO.class);
List<UserVO> list = (List<UserVO>) miHandler.getObjectList("ds_detail", UserVO.class);

// Variable 추출
String userId = miHandler.getValueString("USER_ID");
int pageNo = miHandler.getValueInt("COMM_PageNo");
```

**Validation:** 각 엔드포인트에 request 스키마 할당

**Outputs:**
- Request Dataset 목록 (name, vo_class)
- Request Variable 목록 (name, type)

---

#### Step 3: Output Schema Extraction

**Description:** Response에서 Dataset/Variable 스키마 추출

**Sub-steps:**
1. `setDataset(list, dsName, Class)` 호출 분석
   - Output Dataset 이름 추출
   - VO 클래스 참조 추출
2. `add(key, value)`, `addStr()` 호출 분석
   - Output Variable 추출
3. 표준 변수 자동 추가
   - ErrorCode, ErrorMsg (setSuccess/setMessage에서)
   - COMM_PageNo, COMM_TotalCount, COMM_TotalPage (setPageInfo에서)

**Extraction Patterns:**
```java
// Dataset 출력
miHandler.setDataset(result, "ds_Mst", UserVO.class);

// Variable 출력
miHandler.add("COMM_Flag", "Y");
miHandler.addStr("STATUS", "SUCCESS");
miHandler.setSuccess(true);  // ErrorCode="0", ErrorMsg 설정
miHandler.setPageInfo(pagingProperty);  // COMM_* 페이징 변수
```

**Validation:** 각 엔드포인트에 response 스키마 할당

**Outputs:**
- Response Dataset 목록 (name, vo_class)
- Response Variable 목록 (name, type)

---

#### Step 4: VO Class Analysis

**Description:** VO 클래스 필드에서 Dataset 컬럼 스키마 도출

> **권장**: `columns[]` 추출을 권장합니다. VO 클래스 참조만으로는 불충분할 수 있습니다.

**Sub-steps:**
1. VO 클래스 파일 위치 탐색
   - 경로 패턴: `hallain/src/main/java/**/domain/*.java`, `**/vo/*.java`
2. 클래스 필드 목록 추출
   - `private` 필드 추출 (getter/setter 기반)
   - 상속 클래스 필드 포함 (SsoVO 등)
3. 필드 타입 → Dataset 컬럼 타입 매핑:
   - `String` → STRING
   - `int`, `Integer` → INTEGER
   - `double`, `Double`, `BigDecimal` → DECIMAL
   - `long`, `Long` → LONG
   - `Date`, `LocalDate` → DATE
4. 컬럼 크기 추정 (어노테이션 또는 기본값)
5. **`columns[]` 배열 생성** (권장)

**Type Mapping:**
| Java Type | Dataset Type | Default Size |
|-----------|--------------|--------------|
| String | STRING | 256 |
| int, Integer | INTEGER | - |
| long, Long | LONG | - |
| double, Double | DOUBLE | - |
| BigDecimal | DECIMAL | 18,6 |
| Date, LocalDate | DATE | - |
| byte[] | BLOB | - |

**Schema Status 결정:**
| 조건 | schema 값 |
|------|-----------|
| VO 클래스 존재, 필드 추출 성공 | `"COMPLETE"` |
| VO 클래스 없음 또는 추출 실패 | `"INCOMPLETE"` |
| getMiPlatformMap() 사용 | `"DYNAMIC"` |

**Validation:**
- 각 Dataset에 `columns[]` 배열 권장 (optional)
- VO 클래스가 없으면 `schema: "INCOMPLETE"`, `columns: []`

**Outputs:**
- VO-to-Schema 매핑 테이블
- Dataset별 `columns[]` 배열

---

#### Step 5: Protocol YAML Generation

**Description:** miplatform-protocol.yaml 파일 생성

> **⚠️ 스키마 준수 필수**: `output.schema.yaml` 정의를 정확히 따라야 합니다.

**Sub-steps:**
1. 표준 헤더 추가 (File Header 형식)
2. `metadata` 섹션 생성
   - `generated_by`: 반드시 `"s1-02-discovery-miplatform-protocol"` (정확히 일치)
   - `generated_at`: ISO8601 형식 (예: `"2026-01-07T10:00:00Z"`)
3. `summary` 섹션 생성
   - `coverage`: 반드시 `"N.N%"` 형식 (예: `"95.3%"`)
4. `protocols` 섹션 생성 (엔드포인트별 스키마)
   - ❌ `endpoints` 사용 금지 → ✅ `protocols` 사용
   - ❌ `method` 사용 금지 → ✅ `http_method` 사용
   - `datasets[].schema`: `"COMPLETE"` | `"INCOMPLETE"` | `"DYNAMIC"` (권장)
   - `datasets[].columns[]`: VO 필드에서 추출한 컬럼 목록 (권장)
5. YAML 문법 검증

**필드명 매핑 (금지 → 필수):**
| 금지 (❌) | 필수 (✅) |
|----------|----------|
| `endpoints` | `protocols` |
| `method` | `http_method` |
| `path` | `endpoint_path` |
| `type: STATIC` | `schema: COMPLETE` |
| `type: DYNAMIC` | `schema: DYNAMIC` |
| `schema_type` | `schema` |

**Validation:** YAML 파일 생성 및 문법 검증 통과

**Outputs:**
- `miplatform-protocol.yaml`

---

#### Step 6: Schema Validation

**Description:** 생성된 miplatform-protocol.yaml이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | root | 필수 키 존재 (metadata, summary, protocols) | ERROR | Yes |
| V002 | file | YAML 파싱 오류 없음 | ERROR | Yes |
| V003 | metadata.generated_by | 정확히 일치 | ERROR | Yes |
| V004 | protocols[].http_method | enum 검증 | ERROR | Yes |
| V005 | summary.coverage | 패턴 검증 (N.N%) | ERROR | Yes |
| V006 | protocols[].request.datasets[].schema | enum 검증 | WARNING | No |
| V007 | protocols[].request.datasets[].columns[].type | enum 검증 | ERROR | Yes |
| V008 | protocols[].request.variables[].type | enum 검증 | ERROR | Yes |
| V009 | summary | 커버리지 95% 이상 | WARNING | No |
| V010 | protocols | 최소 1개 이상 항목 | ERROR | Yes |

**Sub-steps:**
1. miplatform-protocol.yaml 파일 로드
2. 스키마 파일 로드 (s1-02-miplatform-protocol.schema.yaml)
3. 검증 규칙 적용:
   - 필수 키 존재 확인
   - 패턴 규칙 검증
   - enum 값 검증
   - 수치 일관성 검증
4. 검증 실패 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재생성 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.3 Sub-Wave Division Guidelines (v1.3.0)

> **⚠️ Output Token Limit 방지**: 대형 도메인(100+ controllers)은 sub-wave로 분할하여 truncation 방지

```yaml
sub_wave_division:
  trigger_conditions:
    - controller_count > 100
    - endpoint_estimate > 200
    - previous_truncation_detected: true

  division_strategy:
    method: prefix_grouping
    target_size: 30-50 controllers per wave

    # 실제 검증된 예시 (PA 도메인)
    example_pa_domain:
      - wave_1: PA01, PA02  # 26 controllers
      - wave_2: PA03        # 55 controllers
      - wave_3: PA04        # 118 controllers (large, but acceptable)
      - wave_4: PA05        # 80 controllers
      - wave_5: PA06        # 139 controllers (large, but acceptable)
      - wave_6: PA07, PA08+ # 44 controllers

    # 실제 검증된 예시 (EB 도메인)
    example_eb_domain:
      - wave_1: EB01, EB02, EB03  # 47 controllers
      - wave_2: EB04, EB05, EB06  # 33 controllers
      - wave_3: EB07-EB12+        # 36 controllers

  output_per_wave:
    file_pattern: "{domain_lower}{wave_id}-protocols.yaml"
    example: "pa01-02-protocols.yaml, eb07-12-protocols.yaml"
    location: "work/specs/"  # 임시 위치

  merge_strategy:
    tool: python_yaml_parser
    handle_format_variations: true  # 다양한 YAML 형식 지원
    deduplication: by_endpoint_path
    final_output: "miplatform-protocol.yaml"

  lean_output_format:
    description: "Sub-wave 출력 시 compact format 사용 (60-70% 크기 감소)"
    omit:
      - "datasets[].columns[]"  # S1-03에서 상세 추출
    preserve:
      - "endpoint_path, http_method, controller, method_name"
      - "standard_variables (ErrorCode, ErrorMsg)"
```

### 3.4 Large File Handling (v1.4.0)

> **⚠️ Read Tool Limit**: Claude Code Read 도구는 256KB 제한. Input/Output 모두 이 제한 고려 필요

```yaml
large_file_handling:
  input_reading:
    target: "feature-inventory.yaml (from s1-01)"
    strategy:
      step_1:
        name: "파일 크기 확인"
        action: "Bash: wc -c < feature-inventory.yaml"

      step_2:
        name: "크기 기반 로딩"
        if_small: "전체 Read (< 200KB)"
        if_large:
          name: "offset/limit 청크 읽기"
          chunk_lines: 1500
          process: |
            total_lines=$(wc -l < feature-inventory.yaml)
            for offset in 0 1500 3000 ...; do
              Read(feature-inventory.yaml, offset=offset, limit=1500)
              # YAML 파싱 및 endpoints[] 누적
            done
          note: "YAML 구조상 endpoint 항목 경계에서 분할 주의"

  output_writing:
    target: "miplatform-protocol.yaml"
    strategy:
      threshold_kb: 200
      if_large: |
        Sub-wave division이 이미 적용되어 있으므로,
        각 sub-wave 출력 파일이 200KB 미만이 되도록 wave 크기 조정:
        - 기본: 30-50 controllers per wave
        - 200KB 초과 시: wave 크기를 20-30으로 축소
      final_merge: |
        병합된 최종 파일이 256KB 초과 시:
        - 분할 저장: miplatform-protocol/ 디렉토리 구조 사용
        - _manifest.yaml + prefix별 분할 파일

    chunked_output_structure:
      description: "최종 병합 파일이 256KB 초과 시 분할 저장"
      structure: |
        miplatform-protocol/
        ├── _manifest.yaml       # metadata + summary + chunk 목록
        ├── pa01-protocols.yaml  # PA01* endpoints
        ├── pa02-protocols.yaml  # PA02* endpoints
        └── ...
```

### 3.5 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | VO 클래스 파일 없음 | schema: INCOMPLETE 마킹, 경고 로그 | 정상 스키마 추출 |
| DP-2 | 동적 Dataset (getMiPlatformMap) | schema: DYNAMIC 마킹 | 정상 스키마 추출 |
| DP-3 | MiHandler 미사용 엔드포인트 | Skip (non-MiPlatform) | 분석 진행 |
| DP-4 | 중첩 VO 참조 | 1단계만 추출, WARNING 로그 | 정상 진행 |
| DP-5 | controller_count > 100 (v1.3.0) | Sub-wave 분할 실행 | Single pass 진행 |
| DP-6 | Truncation 감지 (v1.3.0) | 자동 sub-wave 재실행 | 정상 완료 처리 |
| DP-7 | 출력 파일 > 200KB (v1.4.0) | 분할 저장 (miplatform-protocol/) | 단일 파일 저장 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage1-outputs/phase2/"
    pattern: "{Priority}/{Domain}/"

  example: "work/specs/stage1-outputs/phase2/P2/PA/"
```

### 4.2 Output Files

| File | Type | Purpose | Required | Constraints |
|------|------|---------|----------|-------------|
| miplatform-protocol.yaml | YAML | 프로토콜 스키마 정의 | Yes | Max 500 lines per file |
| dataset-schemas/ | Directory | VO별 상세 스키마 (대규모 도메인) | No | Optional |

### 4.3 File Header

```yaml
# Generated by: s1-02-discovery-miplatform-protocol
# Stage: 1 - Discovery
# Phase: 1.2 - MiPlatform Protocol Analysis
# Domain: ${DOMAIN}
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
```

### 4.4 Output Schema

> **⚠️ MANDATORY**: 출력 파일은 반드시 아래 스키마를 정확히 준수해야 합니다.
> - `output.schema.yaml` 참조
> - 필드명 변경 금지 (예: `endpoints` ❌ → `protocols` ✅)
> - 필수 필드 누락 시 Gate 실패

**스키마 준수 체크리스트:**
| 필드 | 필수 | 형식 | 주의사항 |
|------|------|------|----------|
| `metadata.generated_by` | ✅ | string | 정확히 `"s1-02-discovery-miplatform-protocol"` |
| `metadata.generated_at` | ✅ | ISO8601 | `"2026-01-07T10:00:00Z"` |
| `summary.coverage` | ✅ | string | 반드시 `"N.N%"` 형식 (예: `"95.3%"`) |
| `protocols[]` | ✅ | array | `endpoints[]` 사용 금지 |
| `protocols[].http_method` | ✅ | enum | `"GET"`, `"POST"`, `"PUT"`, `"DELETE"`, `"PATCH"` |
| `protocols[].request.datasets[].schema` | ⭕ | enum | `"COMPLETE"`, `"INCOMPLETE"`, `"DYNAMIC"` (권장) |
| `protocols[].request.datasets[].columns[]` | ⭕ | array | VO 필드 추출 권장 |
| `columns[].type` | ✅ | enum | `"STRING"`, `"INTEGER"`, `"LONG"`, `"DOUBLE"`, `"DECIMAL"`, `"DATE"`, `"BLOB"` |
| `variables[].type` | ✅ | enum | `"STRING"`, `"INTEGER"`, `"LONG"`, `"DOUBLE"`, `"BOOLEAN"` |

```yaml
# miplatform-protocol.yaml
metadata:
  generated_by: "s1-02-discovery-miplatform-protocol"  # EXACT MATCH 필수
  generated_at: "2026-01-07T10:00:00Z"                 # ISO8601 형식
  domain: "PA"
  source_path: "hallain/src/main/java/**/pa/"

summary:
  total_endpoints: 150
  miplatform_endpoints: 143
  coverage: "95.3%"           # 반드시 "N.N%" 형식
  by_pattern:
    with_dataset: 120
    variables_only: 23
    dynamic_schema: 7

protocols:                    # ❌ endpoints 사용 금지, ✅ protocols 사용
  - endpoint_path: "/pa/PA01001/list.mi"
    http_method: "POST"       # ❌ method 사용 금지, ✅ http_method 사용
    controller: "PA01001Controller"
    method_name: "getList"
    request:
      datasets:
        - name: "ds_master"
          vo_class: "PA01001MVO"
          schema: "COMPLETE"  # 권장: COMPLETE | INCOMPLETE | DYNAMIC
          columns:            # 권장: VO 필드에서 추출
            - name: "site_cd"
              type: "STRING"
              size: 256
            - name: "yyyymm"
              type: "STRING"
              size: 6
            - name: "odr_no"
              type: "STRING"
              size: 50
      variables:
        - name: "COMM_PageNo"
          type: "INTEGER"
        - name: "COMM_BlockSet"
          type: "INTEGER"
    response:
      datasets:
        - name: "ds_Mst"
          vo_class: "PA01001MVO"
          schema: "COMPLETE"  # 권장
          columns:            # 권장: VO 필드에서 추출
            - name: "site_cd"
              type: "STRING"
            - name: "site_nm"
              type: "STRING"
            - name: "total_qty"
              type: "DECIMAL"
      variables:
        - name: "ErrorCode"
          type: "STRING"
          standard: true
        - name: "ErrorMsg"
          type: "STRING"
          standard: true
        - name: "COMM_TotalCount"
          type: "INTEGER"
          standard: true
        - name: "COMM_TotalPage"
          type: "INTEGER"
          standard: true
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| file_exists | structural | `miplatform-protocol.yaml` 존재 | ERROR | Yes |
| yaml_syntax | structural | YAML 파싱 오류 없음 | ERROR | Yes |
| endpoint_coverage | metric | mi_endpoints >= 95% of total | ERROR | Yes |
| schema_complete | content | request AND response 정의됨 | ERROR | Yes |
| vo_resolved | metric | INCOMPLETE < 10% | WARNING | No |

### 5.2 Manual Reviews

| Review | Reviewer | Criteria | Required |
|--------|----------|----------|----------|
| Schema sampling | Tech Lead | 랜덤 5개 엔드포인트 스키마 검증 | No |

### 5.3 Gate Criteria

```yaml
gate_criteria:
  id: "G1.2"
  name: "Protocol Gate"
  threshold: 70
  metrics:
    - metric: "file_exists"
      weight: 0.2
      target: "true"
      formula: "miplatform-protocol.yaml exists"
    - metric: "endpoint_coverage"
      weight: 0.5
      target: ">= 95%"
      formula: "miplatform_endpoints / total_endpoints * 100"
    - metric: "schema_complete"
      weight: 0.3
      target: "100%"
      formula: "endpoints_with_both_schemas / miplatform_endpoints * 100"
```

### 5.4 Truncation Detection (v1.3.0)

> **⚠️ CRITICAL**: 출력 truncation은 95%+ 데이터 손실을 유발. 반드시 감지 및 복구 필요

```yaml
truncation_detection:
  checks:
    - id: TC-001
      name: "Summary-Protocol Consistency"
      description: "summary.total_endpoints와 protocols[] 배열 길이 일치 확인"
      rule: "summary.total_endpoints == len(protocols)"
      severity: critical
      action_on_fail: "MANDATORY sub-wave re-execution"

    - id: TC-002
      name: "Coverage Threshold"
      description: "커버리지 95% 미만 시 경고"
      rule: "coverage >= 95%"
      severity: warning
      action_on_fail: "Investigate missing endpoints"

    - id: TC-003
      name: "Protocol Completeness"
      description: "모든 protocol에 필수 필드 존재 확인"
      rule: "all protocols have: endpoint_path, http_method, controller, method_name"
      severity: error
      action_on_fail: "Incomplete protocol detected"

  detection_command: |
    # Summary count vs actual protocols count
    summary_count=$(grep "total_endpoints:" output.yaml | awk '{print $2}')
    protocol_count=$(grep -c "endpoint_path:" output.yaml)

    if [ "$summary_count" != "$protocol_count" ]; then
      echo "TRUNCATION DETECTED: $protocol_count / $summary_count protocols"
      exit 1
    fi

  auto_recovery:
    enabled: true
    strategy: |
      1. Detect truncation point in output
      2. Calculate required sub-wave count (target: 30-50 controllers/wave)
      3. Re-execute with sub-wave division
      4. Merge sub-wave results using Python parser
      5. Validate merged output
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| VO class not found | columns: [] | VO 파일 경로 불일치 | INCOMPLETE 마킹, 수동 보완 | No |
| Dynamic Dataset | schema: DYNAMIC | getMiPlatformMap() 사용 | DYNAMIC 마킹, 런타임 분석 필요 표시 | No |
| Nested VO | 필드 누락 | 복합 객체 참조 | 1단계만 추출, WARNING | No |
| Encoding error | 파일 읽기 실패 | EUC-KR/UTF-8 혼용 | UTF-8 먼저, 실패 시 EUC-KR | Auto |
| Large domain timeout | 120분 초과 | 대규모 도메인 | 서브도메인 분할 | Yes |
| **Output Truncation** (v1.3.0) | summary.total != len(protocols) | Output token limit (~25-30K) | Sub-wave 분할 재실행 | **Yes** |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Coverage < 90% | critical | Phase 중단, 원인 분석 | Tech Lead |
| Coverage 90-95% | major | WARNING 로그, 계속 진행 | Orchestrator |
| INCOMPLETE > 20% | major | VO 경로 재설정 필요 | Tech Lead |
| DYNAMIC > 30% | minor | 로그 기록, 계속 진행 | - |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 부분 실패 | 해당 도메인만 재실행 | Phase |
| 전체 실패 | 입력 데이터 확인 후 재실행 | Phase |
| 잘못된 출력 | 출력 파일 삭제 후 재실행 | Phase |

---

## 7. Examples

### 7.1 Sample Input

**Source Controller (MiHandler 사용):**
```java
package com.hallain.pa.controller;

import benitware.framework.foundation.channel.miplatform.MiHandler;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.ui.ModelMap;

@Controller
@RequestMapping("/pa/PA01001")
public class PA01001Controller {

    @RequestMapping("/list.mi")
    public String getList(HttpServletRequest request, ModelMap model) throws Exception {
        MiHandler miHandler = new MiHandler(request);

        // Request: Dataset에서 검색 조건 추출
        PA01001MVO vo = (PA01001MVO) miHandler.getObject("ds_master", PA01001MVO.class);
        int pageNo = miHandler.getValueInt("COMM_PageNo");
        int pageSize = miHandler.getValueInt("COMM_BlockSet");

        // Business Logic
        List<PA01001MVO> result = service.selectList(vo, pageNo, pageSize);
        int totalCount = service.selectCount(vo);

        // Response: Dataset 설정
        miHandler.clear();
        miHandler.setDataset(result, "ds_Mst", PA01001MVO.class);
        miHandler.add("COMM_TotalCount", totalCount);
        miHandler.add("COMM_TotalPage", (totalCount / pageSize) + 1);
        miHandler.setSuccess(true);

        model.put("MI_DATA", miHandler.getMiPlatformData());
        return "common/MiPlatform";
    }

    @RequestMapping("/save.mi")
    public String save(HttpServletRequest request, ModelMap model) throws Exception {
        MiHandler miHandler = new MiHandler(request);

        // Request: 다중 레코드 처리
        List<PA01001MVO> saveList = (List<PA01001MVO>)
            miHandler.getObjectList("ds_detail", PA01001MVO.class);

        for(PA01001MVO item : saveList) {
            service.save(item);  // rowStatus로 INSERT/UPDATE/DELETE 구분
        }

        miHandler.clear();
        miHandler.setSuccess("save.success", false);

        model.put("MI_DATA", miHandler.getMiPlatformData());
        return "common/MiPlatform";
    }
}
```

**Source VO Class:**
```java
package com.hallain.pa.vo;

public class PA01001MVO {
    private String siteCd;      // 사이트 코드
    private String siteNm;      // 사이트명
    private String yyyymm;      // 년월
    private String odrNo;       // 주문번호
    private BigDecimal totalQty; // 총수량
    private String rowStatus;   // INSERT/UPDATE/DELETE

    // getters and setters
}
```

### 7.2 Sample Output

```yaml
# Generated by: s1-02-discovery-miplatform-protocol
# Stage: 1 - Discovery
# Phase: 1.2 - MiPlatform Protocol Analysis
# Domain: PA
# Generated: 2026-01-07T10:30:00Z
# Model: claude-opus-4-5-20251101

metadata:
  generated_by: "s1-02-discovery-miplatform-protocol"
  generated_at: "2026-01-07T10:30:00Z"
  domain: "PA"
  source_path: "hallain/src/main/java/com/hallain/pa/"

summary:
  total_endpoints: 5
  miplatform_endpoints: 5
  coverage: "100%"
  by_pattern:
    with_dataset: 5
    variables_only: 0
    dynamic_schema: 0

protocols:
  - endpoint_path: "/pa/PA01001/list.mi"
    http_method: "POST"
    controller: "PA01001Controller"
    method_name: "getList"
    request:
      datasets:
        - name: "ds_master"
          vo_class: "PA01001MVO"
          schema: "COMPLETE"
          columns:
            - name: "siteCd"
              type: "STRING"
              size: 256
            - name: "yyyymm"
              type: "STRING"
              size: 6
            - name: "odrNo"
              type: "STRING"
              size: 50
      variables:
        - name: "COMM_PageNo"
          type: "INTEGER"
        - name: "COMM_BlockSet"
          type: "INTEGER"
    response:
      datasets:
        - name: "ds_Mst"
          vo_class: "PA01001MVO"
          schema: "COMPLETE"
          columns:
            - name: "siteCd"
              type: "STRING"
            - name: "siteNm"
              type: "STRING"
            - name: "yyyymm"
              type: "STRING"
            - name: "odrNo"
              type: "STRING"
            - name: "totalQty"
              type: "DECIMAL"
      variables:
        - name: "ErrorCode"
          type: "STRING"
          standard: true
        - name: "ErrorMsg"
          type: "STRING"
          standard: true
        - name: "COMM_TotalCount"
          type: "INTEGER"
        - name: "COMM_TotalPage"
          type: "INTEGER"

  - endpoint_path: "/pa/PA01001/save.mi"
    http_method: "POST"
    controller: "PA01001Controller"
    method_name: "save"
    request:
      datasets:
        - name: "ds_detail"
          vo_class: "PA01001MVO"
          schema: "COMPLETE"
          is_list: true
          columns:
            - name: "siteCd"
              type: "STRING"
            - name: "siteNm"
              type: "STRING"
            - name: "yyyymm"
              type: "STRING"
            - name: "odrNo"
              type: "STRING"
            - name: "totalQty"
              type: "DECIMAL"
            - name: "rowStatus"
              type: "STRING"
              note: "INSERT|UPDATE|DELETE"
      variables: []
    response:
      datasets: []
      variables:
        - name: "ErrorCode"
          type: "STRING"
          standard: true
        - name: "ErrorMsg"
          type: "STRING"
          standard: true
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| VO 클래스 없음 | 참조 VO 파일 누락 | `schema: INCOMPLETE`, 컬럼 빈 배열 |
| 동적 Dataset | `getMiPlatformMap()` 사용 | `schema: DYNAMIC`, 런타임 분석 필요 표시 |
| MiHandler 미사용 | 일반 ResponseEntity 반환 | Skip (non-MiPlatform), 통계에서 제외 |
| 중첩 VO | `OrderVO.items: List<ItemVO>` | 1단계만 추출, WARNING 로그 |
| 빈 응답 | `miHandler.setSuccess()` 만 호출 | datasets: [], variables에 표준 변수만 |

---

## Version History

### v1.4.0 (2026-01-13)
- **Read Tool 256KB Limit 대응**
  - Section 3.4: Large File Handling 신규 추가
  - Input reading: feature-inventory.yaml 대용량 파일 offset/limit 읽기 지원
  - Output writing: 최종 파일 256KB 초과 시 분할 저장 (miplatform-protocol/ 디렉토리)
  - DP-7: 출력 파일 크기 기반 분할 저장 결정

### v1.3.0 (2026-01-12)
- **Output Truncation 방지 및 복구**
  - Section 3.1: Adaptive Batching 도입 (domain → adaptive)
  - Section 3.3: Sub-Wave Division Guidelines 신규 추가
  - Section 5.4: Truncation Detection 신규 추가 (TC-001~003)
  - Section 6.1: Output Truncation 이슈 추가
- **검증된 개선 효과**
  - PA 도메인: 34 → 1,225 endpoints (36x 개선)
  - EB 도메인: 13 → 402 endpoints (31x 개선)
- **Decision Points 추가**
  - DP-5: controller_count > 100 시 Sub-wave 분할
  - DP-6: Truncation 감지 시 자동 재실행

### v1.2.0 (2026-01-12)
- **스키마 준수 강화**
  - Section 4.4: 스키마 준수 체크리스트 추가
  - Step 4: `columns[]` 추출 필수화 명시
  - Step 5: 필드명 매핑 테이블 추가 (금지 → 필수)
- **명확한 필드명 규칙**
  - `endpoints` → `protocols` 변경 필수
  - `method` → `http_method` 변경 필수
  - `type: STATIC/DYNAMIC` → `schema: COMPLETE/INCOMPLETE/DYNAMIC` 변경 필수
- **Schema Status 결정 로직 명시**

### v1.1.0 (2026-01-08)
- Step 6: Schema Validation 추가
- s1-02-miplatform-protocol.schema.yaml 스키마 참조
- 10개 검증 규칙 (V001-V010) 적용

### v1.0.0 (2026-01-07)
- Initial version
- MiHandler 패턴 분석 지원
- Dataset/Variable 스키마 추출
- VO 클래스 기반 컬럼 타입 매핑
