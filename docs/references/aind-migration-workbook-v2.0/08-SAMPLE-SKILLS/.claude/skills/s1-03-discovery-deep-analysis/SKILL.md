---
name: s1-03-discovery-deep-analysis
description: Use when performing 5-layer trace analysis for legacy features using SQL-FIRST approach, tracing code flow from SQL/SP upward to DAO, Service, and Controller, or documenting complete feature dependencies (project)
---

# Deep Analysis (5-Layer Trace) - SQL-FIRST Approach

> **Skill ID**: S1-03
> **Skill Type**: Analysis (Feature 단위 5-Layer 추적 분석)
> **Stage**: 1 - Discovery
> **Phase**: 1.3 - Deep Analysis

## 1. Overview

### 1.1 Purpose

Feature 단위로 **SQL/SP → DAO → Service → Controller** 순서로 역추적하여 5-Layer 분석 결과를 생성합니다. 이 분석은 **QUERY-FIRST 원칙**에 따라 SQL을 시작점으로 하여 마이그레이션 대상 코드의 완전한 의존성 맵을 제공합니다.

**QUERY-FIRST 원칙:**
> SQL 보존 100% 필수 (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - SQL/SP를 시작점으로 역추적하여 모든 쿼리가 누락 없이 분석되도록 보장
> - Controller-First 접근법의 위험(DB 중심 피처 누락) 방지

**5-Layer 구조 (분석 순서):**
| 분석 순서 | Layer | 설명 | 분석 대상 |
|----------|-------|------|-----------|
| 1 | L4 - SQL/MyBatis | SQL 매핑 (시작점) | SQL 쿼리, Stored Procedure, iBatis XML |
| 2 | L3 - Data Access | 데이터 접근 | DAO/Mapper 클래스, 쿼리 메서드 |
| 3 | L2 - Business Logic | 비즈니스 규칙 | Service 클래스, 트랜잭션, 검증 로직 |
| 4 | L1 - API Endpoints | 외부 인터페이스 | Controller 메서드, URL 매핑, Request/Response |
| 5 | L5 - Data Model | 데이터 구조 | VO/DTO/Entity 클래스, 필드 매핑 |

**추적 정보:**
- SQL namespace → DAO class 매핑
- DAO → Service caller 역추적
- Service → Controller endpoint 역추적
- Layer 간 호출 관계 (Reverse Call Graph)
- 트랜잭션 경계
- SQL 쿼리 및 SP 매핑

### 1.2 Scope

**In Scope:**
- Feature별 Controller → Service → DAO 호출 추적
- iBatis XML 매퍼 파일 분석
- VO/DTO 클래스 의존성 추출
- SQL 쿼리 및 SP 호출 문서화
- Layer별 분석 결과 파일 생성

**Out of Scope:**
- Feature 목록 생성 (→ `s1-01-discovery-feature-inventory`)
- MiPlatform 프로토콜 분석 (→ `s1-02-discovery-miplatform-protocol`)
- YAML Specification 생성 (→ `s1-04-discovery-spec-generation`)

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **QUERY-FIRST** | SQL/SP를 시작점으로 역추적 | DB 중심 피처 누락 방지, SQL 100% 보존 보장 |
| **Completeness** | 5개 Layer 모두 문서화 | 누락된 Layer는 마이그레이션 품질 저하 |
| **Reverse Traceability** | SQL → DAO → Service → Controller 역추적 | 모든 쿼리가 분석에 포함됨을 보장 |
| **Dependency Clarity** | 클래스/메서드 간 의존성 명시 | 순환 의존성 및 결합도 파악 |
| **Determinism** | 동일 Feature → 동일 분석 결과 | 재실행 시 일관된 결과 보장 |

### 1.4 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s1-01-discovery-feature-inventory` (S1-01) | Feature 목록 및 Controller 정보 제공 |
| `s1-02-discovery-miplatform-protocol` (S1-02) | MiPlatform Request/Response 스키마 제공 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s1-04-discovery-spec-generation` (S1-04) | 분석 결과 기반 YAML Spec 생성 |
| `s2-02-validation-structural-comparison` (S2-02) | Ground Truth와 비교 검증 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S1-01"
    skill_name: "s1-01-discovery-feature-inventory"
    dependency_type: "input"
    artifact: "feature-inventory.yaml"
  - skill_id: "S1-02"
    skill_name: "s1-02-discovery-miplatform-protocol"
    dependency_type: "input"
    artifact: "miplatform-protocol.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| feature_inventory | file | `work/specs/stage1-outputs/phase1/{Priority}/{Domain}/feature-inventory.yaml` | YAML | Yes |
| miplatform_protocol | file | `work/specs/stage1-outputs/phase2/{Priority}/{Domain}/miplatform-protocol.yaml` | YAML | Yes |
| legacy_source | directory | `${LEGACY_CODEBASE}/src/main/java/` | Java | Yes |
| ibatis_mappers | directory | `${LEGACY_CODEBASE}/src/main/resources/com/halla/{domain}/sqlmap/` | XML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Grep | - | 클래스/메서드 참조 검색 |
| Read | - | Java/XML 파일 분석 |
| Glob | - | 파일 패턴 매칭 |
| LSP | - | 정의/참조 추적 (가능한 경우) |

**Access:**
- Legacy 소스코드 읽기 권한
- iBatis XML 매퍼 파일 접근

**Knowledge:**
- Spring MVC 아키텍처 패턴
- iBatis/MyBatis XML 매핑 구조
- Java 클래스 의존성 분석

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
```

### 3.2 Process Steps

#### Step 1: Feature Context Loading

**Description:** 분석 대상 Feature 정보 로드

**Sub-steps:**
1. feature-inventory.yaml에서 Feature 메타데이터 로드
2. miplatform-protocol.yaml에서 프로토콜 스키마 로드
3. Feature에 속한 Controller/Endpoint 목록 확인

**Validation:** Feature 정보 로드 완료

**Outputs:**
- Feature 컨텍스트 (endpoints, controllers, protocols)

---

#### Step 2: L4 - SQL/MyBatis Layer Analysis (시작점)

**Description:** SQL 쿼리 및 SP 분석 - **QUERY-FIRST의 시작점**

> **QUERY-FIRST**: 이 단계가 분석의 시작점입니다. SQL/SP를 먼저 분석하여 모든 쿼리가 누락 없이 포함되도록 합니다.

**Sub-steps:**
1. Feature에 해당하는 iBatis XML 매퍼 파일 식별 (namespace 기반)
2. 모든 SQL 쿼리 추출 및 분류 (SELECT, INSERT, UPDATE, DELETE)
3. Stored Procedure 호출 식별
4. 동적 SQL 패턴 분석 (isNotNull, iterate 등)
5. 테이블/컬럼 의존성 추출
6. **역추적 준비**: namespace.id → DAO 클래스 매핑 정보 수집

**Analysis Patterns:**
```xml
<sqlMap namespace="pa01001">
    <select id="selectList" parameterClass="PA01001MVO" resultClass="PA01001MVO">
        SELECT USER_ID, USER_NAME, DEPT_CD, CREATE_DT
        FROM TB_USER
        WHERE 1=1
        <isNotNull property="deptCd">
            AND DEPT_CD = #deptCd#
        </isNotNull>
    </select>

    <procedure id="callProcedure" parameterMap="procParams">
        {call PKG_USER.PROC_UPDATE(?, ?, ?)}
    </procedure>
</sqlMap>
```

**Extraction:**
- SQL namespace 및 ID
- SQL 유형 (SELECT/INSERT/UPDATE/DELETE/CALL)
- 테이블명 목록
- 컬럼 목록 (SELECT, WHERE, JOIN)
- 동적 SQL 조건
- SP 호출 정보
- parameterClass/resultClass (VO 타입 힌트)

**Validation:** Feature의 모든 SQL/SP가 문서화됨

**Outputs:**
- `sql-mybatis/{feature_id}.yaml`
- 역추적용 mapper_id 목록

---

#### Step 3: L3 - Data Access Analysis (역추적 1단계)

**Description:** DAO/Mapper 계층 분석 - SQL namespace.id를 호출하는 DAO 클래스 역추적

**Sub-steps:**
1. Step 2에서 추출한 mapper_id (namespace.id) 검색
2. DAO 클래스에서 해당 mapper_id를 호출하는 메서드 식별
3. DAO 메서드 시그니처 분석 (파라미터, 리턴 타입)
4. **역추적 준비**: DAO 클래스 → Service caller 매핑 정보 수집

**Reverse Trace Pattern:**
```java
// mapper_id "pa01001.selectList"를 호출하는 DAO 메서드 찾기
@Repository
public class PA01001DAO extends AbstractDAO {
    public List<PA01001MVO> selectList(PA01001MVO vo) {
        return selectList("pa01001.selectList", vo);  // ← mapper_id 역추적
    }
}
```

**Extraction:**
- DAO 클래스명 및 패키지
- 메서드명 및 시그니처
- Mapper ID 매핑
- SQL 쿼리 유형
- Input/Output 타입

**Validation:** 모든 mapper_id에 대응하는 DAO 메서드 식별

**Outputs:**
- `data-access/{feature_id}.yaml`
- 역추적용 DAO 클래스/메서드 목록

---

#### Step 4: L2 - Business Logic Analysis (역추적 2단계)

**Description:** Service 계층 분석 - DAO 클래스를 주입받아 호출하는 Service 역추적

**Sub-steps:**
1. Step 3에서 식별된 DAO 클래스를 @Autowired로 주입받는 Service 클래스 검색
2. DAO 메서드를 호출하는 Service 메서드 식별
3. 메서드 시그니처 및 @Transactional 분석
4. 비즈니스 로직 패턴 분석 (validation, calculation, transformation)
5. **역추적 준비**: Service 클래스 → Controller caller 매핑 정보 수집

**Reverse Trace Pattern:**
```java
// PA01001DAO를 주입받는 Service 찾기
@Service
public class PA01001Service {
    @Autowired
    private PA01001DAO pa01001DAO;  // ← DAO 역추적

    @Transactional
    public List<PA01001MVO> selectList(PA01001MVO vo) {
        return pa01001DAO.selectList(vo);  // ← DAO 메서드 호출 역추적
    }
}
```

**Extraction:**
- Service 클래스명 및 패키지
- DAO 의존성 (주입된 DAO 클래스)
- 트랜잭션 경계 (@Transactional)
- Validation 규칙
- Cross-Service 호출

**Validation:** 모든 DAO 메서드에 대응하는 Service 메서드 식별

**Outputs:**
- `business-logic/{feature_id}.yaml`
- 역추적용 Service 클래스/메서드 목록

---

#### Step 5: L1 - API Endpoint Analysis (역추적 3단계)

**Description:** Controller 계층 분석 - Service 클래스를 주입받아 호출하는 Controller 역추적

**Sub-steps:**
1. Step 4에서 식별된 Service 클래스를 @Autowired로 주입받는 Controller 클래스 검색
2. Service 메서드를 호출하는 Controller 메서드 식별
3. RequestMapping 어노테이션 상세 추출 (URL, HTTP Method)
4. Request/Response 타입 분석

**Reverse Trace Pattern:**
```java
// PA01001Service를 주입받는 Controller 찾기
@Controller
@RequestMapping("/pa/PA01001")
public class PA01001Controller {
    @Autowired
    private PA01001Service pa01001Service;  // ← Service 역추적

    @RequestMapping("/list.mi")
    public String getList(HttpServletRequest request, ModelMap model) {
        List<PA01001MVO> result = pa01001Service.selectList(vo);  // ← Service 메서드 호출 역추적
        return "common/MiPlatform";
    }
}
```

**Extraction:**
- Controller 클래스명 및 URL 패턴
- HTTP Method, URL Pattern
- Request Parameter/Body 타입
- Response 타입
- Service 의존성 (역방향 확인)

**Validation:** 모든 Service 메서드에 대응하는 Controller endpoint 식별 (orphan SQL 탐지)

**Outputs:**
- `api-endpoints/{feature_id}.yaml`

---

#### Step 6: L5 - Data Model Analysis

**Description:** VO/DTO 클래스 구조 분석

**Sub-steps:**
1. VO/DTO 클래스 파일 탐색
2. 필드 목록 및 타입 추출
3. 어노테이션 분석 (@Column, @Transient 등)
4. 상속 관계 추적 (extends BaseVO)

**Analysis Patterns:**
```java
public class UserVO extends BaseVO {
    private String userId;
    private String userName;
    private String deptCd;
    private Date createDt;
    private String rowStatus;  // MiPlatform 표준
}
```

**Extraction:**
- 클래스명 및 패키지
- 필드 목록 (이름, 타입, 어노테이션)
- 상속 구조
- MiPlatform 표준 필드 식별 (rowStatus 등)

**Validation:** Feature에서 사용하는 모든 VO 클래스 문서화

**Outputs:**
- `data-model/{feature_id}.yaml`

---

#### Step 7: Summary Generation

**Description:** Feature별 통합 분석 요약 생성

**Sub-steps:**
1. 5개 Layer 분석 결과 통합
2. 의존성 그래프 생성
3. 복잡도 메트릭 계산
4. 마이그레이션 주의사항 도출

**Outputs:**
- `summary.yaml`

---

#### Step 8: Schema Validation

**Description:** 생성된 summary.yaml 및 Layer 파일들이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | root | 필수 키 존재 (metadata, overview, layers) | ERROR | Yes |
| V002 | file | YAML 파싱 오류 없음 | ERROR | Yes |
| V003 | metadata.generated_by | 정확히 일치 | ERROR | Yes |
| V004 | metadata.feature_id | FEAT-{DOMAIN}-{NNN} 패턴 | ERROR | Yes |
| V005 | layers | 5개 Layer 파일 참조 존재 | ERROR | Yes |
| V006 | overview.complexity | enum 검증 (low/medium/high) | ERROR | Yes |
| V007 | dependencies.internal | 최소 1개 이상 | WARNING | No |
| V008 | Layer 파일 | 각 Layer 파일 존재 및 유효 | ERROR | Yes |

**Sub-steps:**
1. summary.yaml 파일 로드
2. 5개 Layer 파일 존재 확인:
   - api-endpoints/{feature_id}.yaml
   - business-logic/{feature_id}.yaml
   - data-access/{feature_id}.yaml
   - sql-mybatis/{feature_id}.yaml
   - data-model/{feature_id}.yaml
3. 스키마 파일 로드 및 검증 규칙 적용
4. 검증 실패 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재생성 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.3 Large File Handling (v2.1.0)

> **⚠️ Read Tool Limit**: Claude Code Read 도구는 256KB 제한. 대형 도메인의 입력 파일은 이 제한을 초과할 수 있음

```yaml
large_file_handling:
  input_files:
    feature_inventory:
      source: "s1-01 output"
      potential_size: "대형 도메인(PA, EB)에서 200KB+ 가능"
      strategy:
        step_1:
          name: "형식 감지"
          actions:
            - "feature-inventory/ 디렉토리 존재 확인"
            - "존재하면 → 분할 형식"
            - "없으면 → 단일 파일 형식"

        step_2_chunked:
          name: "분할 형식 로드"
          actions:
            - "feature-inventory/_manifest.yaml 읽기"
            - "필요한 feature만 해당 청크 파일에서 로드"

        step_2_single:
          name: "단일 파일 로드"
          check: "파일 크기 확인 (Bash: wc -c)"
          if_small: "전체 Read (< 200KB)"
          if_large:
            name: "offset/limit 청크 읽기"
            chunk_lines: 1500
            process: |
              total_lines=$(wc -l < feature-inventory.yaml)
              for offset in 0 1500 3000 ...; do
                Read(file, offset=offset, limit=1500)
                # YAML 파싱 및 features[] 누적
              done

    miplatform_protocol:
      source: "s1-02 output"
      potential_size: "대형 도메인에서 200KB+ 가능"
      strategy:
        step_1:
          name: "형식 감지"
          actions:
            - "miplatform-protocol/ 디렉토리 존재 확인"
            - "존재하면 → 분할 형식"
            - "없으면 → 단일 파일 형식"

        step_2_chunked:
          name: "분할 형식 로드"
          actions:
            - "miplatform-protocol/_manifest.yaml 읽기"
            - "필요한 protocol만 해당 청크 파일에서 로드"

        step_2_single:
          name: "단일 파일 로드"
          check: "파일 크기 확인"
          if_small: "전체 Read"
          if_large: "offset/limit 청크 읽기 (동일 전략)"

  output_files:
    note: "Feature 단위 출력이므로 일반적으로 256KB 미만"
    per_feature_limit: |
      각 파일별 제한:
      - summary.yaml: Max 200 lines
      - api-endpoints/*.yaml: Max 100 lines/endpoint
      - business-logic/*.yaml: Max 150 lines
      - data-access/*.yaml: Max 100 lines
      - sql-mybatis/*.yaml: Max 100 lines
      - data-model/*.yaml: Max 100 lines
```

### 3.4 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | SQL mapper_id에 대응하는 DAO 없음 | orphan_sql 마킹, WARNING 로그 (직접 호출 가능성) | 정상 역추적 |
| DP-2 | DAO에 대응하는 Service 없음 | Controller → DAO 직접 연결로 분석 | 정상 역추적 |
| DP-3 | Service에 대응하는 Controller 없음 | internal_service 마킹 (배치/스케줄러 가능성) | 정상 역추적 |
| DP-4 | SP 호출 감지 | SP 상세 분석 (파라미터, 결과) | 일반 SQL 분석 |
| DP-5 | Cross-domain 의존성 | WARNING + dependencies.external에 기록 | 정상 진행 |
| DP-6 | VO 클래스 없음 (parameterClass) | VO: INLINE 마킹 (Map 사용 추정) | 정상 VO 분석 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage1-outputs/phase3/"
    pattern: "{Priority}/{Domain}/FEAT-{DOMAIN}-{NNN}/"

  example: "work/specs/stage1-outputs/phase3/P2/PA/FEAT-PA-001/"
```

### 4.2 Output Files

| File | Type | Purpose | Required | Constraints |
|------|------|---------|----------|-------------|
| summary.yaml | YAML | Feature 분석 요약 | Yes | Max 200 lines |
| api-endpoints/{feature_id}.yaml | YAML | L1 Controller 분석 | Yes | Max 100 lines/endpoint |
| business-logic/{feature_id}.yaml | YAML | L2 Service 분석 | Yes | Max 150 lines |
| data-access/{feature_id}.yaml | YAML | L3 DAO 분석 | Yes | Max 100 lines |
| sql-mybatis/{feature_id}.yaml | YAML | L4 SQL/MyBatis 분석 | Yes | Max 100 lines |
| data-model/{feature_id}.yaml | YAML | L5 VO 분석 | Yes | Max 100 lines |

### 4.3 File Header

```yaml
# Generated by: s1-03-discovery-deep-analysis
# Stage: 1 - Discovery
# Phase: 1.3 - Deep Analysis
# Domain: ${DOMAIN}
# Feature: ${FEATURE_ID}
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
```

### 4.4 Output Schema

```yaml
# summary.yaml
metadata:
  generated_by: "s1-03-discovery-deep-analysis"
  generated_at: "2026-01-07T10:00:00Z"
  domain: "PA"
  feature_id: "FEAT-PA-001"
  screen_id: "PA01001"

overview:
  name: "생산계획 조회"
  description: "생산계획 목록/상세 조회 및 저장 기능"
  complexity: "medium"
  endpoints_count: 3
  services_count: 1
  daos_count: 1
  vos_count: 2
  sql_count: 5

layers:
  l1_api_endpoints:
    file: "api-endpoints/FEAT-PA-001.yaml"
    summary:
      total: 3
      by_method:
        POST: 3
  l2_business_logic:
    file: "business-logic/FEAT-PA-001.yaml"
    summary:
      services: 1
      transactional_methods: 1
      validations: 2
  l3_data_access:
    file: "data-access/FEAT-PA-001.yaml"
    summary:
      daos: 1
      mapper_ids: 5
  l4_sql_mybatis:
    file: "sql-mybatis/FEAT-PA-001.yaml"
    summary:
      tables: ["TB_PROD_PLAN", "TB_PROD_PLAN_DTL"]
      sql_types:
        SELECT: 2
        INSERT: 1
        UPDATE: 1
        DELETE: 1
      stored_procedures: []
  l5_data_model:
    file: "data-model/FEAT-PA-001.yaml"
    summary:
      vo_classes: 2
      total_fields: 15

dependencies:
  internal:
    - from: "PA01001Controller"
      to: "PA01001Service"
      type: "injection"
    - from: "PA01001Service"
      to: "PA01001DAO"
      type: "injection"
  external:
    - domain: "CM"
      class: "CommonService"
      methods: ["getCodeList"]
      reason: "공통코드 조회"

migration_notes:
  - type: "WARNING"
    layer: "L4"
    description: "Oracle CONNECT BY 사용 - 재귀 쿼리 변환 필요"
  - type: "INFO"
    layer: "L2"
    description: "트랜잭션 경계 명확 - @Transactional 적용 가능"

database:
  tables:
    - name: "TB_PROD_PLAN"
      operations: ["SELECT", "INSERT", "UPDATE", "DELETE"]
      columns_used: ["PLAN_ID", "SITE_CD", "YYYYMM", "ODR_NO", "TOTAL_QTY"]
    - name: "TB_PROD_PLAN_DTL"
      operations: ["SELECT", "INSERT"]
      columns_used: ["PLAN_ID", "SEQ", "ITEM_CD", "ITEM_QTY"]
  stored_procedures: []
  dynamic_sql_patterns:
    - type: "isNotNull"
      count: 3
    - type: "iterate"
      count: 1
```

```yaml
# api-endpoints/FEAT-PA-001.yaml
metadata:
  feature_id: "FEAT-PA-001"
  layer: "L1 - API Endpoints"

endpoints:
  - path: "/pa/PA01001/list.mi"
    method: "POST"
    controller:
      class: "PA01001Controller"
      method: "getList"
      file: "src/main/java/com/hallain/pa/controller/PA01001Controller.java"
      line: 45
    request:
      type: "MiPlatform"
      datasets: ["ds_master"]
      variables: ["COMM_PageNo", "COMM_BlockSet"]
    response:
      type: "MiPlatform"
      datasets: ["ds_Mst"]
      variables: ["ErrorCode", "ErrorMsg", "COMM_TotalCount"]
    service_calls:
      - class: "PA01001Service"
        method: "selectList"
        parameters: ["PA01001MVO", "int", "int"]
      - class: "PA01001Service"
        method: "selectCount"
        parameters: ["PA01001MVO"]

  - path: "/pa/PA01001/save.mi"
    method: "POST"
    controller:
      class: "PA01001Controller"
      method: "save"
      file: "src/main/java/com/hallain/pa/controller/PA01001Controller.java"
      line: 78
    request:
      type: "MiPlatform"
      datasets: ["ds_detail"]
      variables: []
    response:
      type: "MiPlatform"
      datasets: []
      variables: ["ErrorCode", "ErrorMsg"]
    service_calls:
      - class: "PA01001Service"
        method: "save"
        parameters: ["List<PA01001MVO>"]
```

```yaml
# business-logic/FEAT-PA-001.yaml
metadata:
  feature_id: "FEAT-PA-001"
  layer: "L2 - Business Logic"

services:
  - class: "PA01001Service"
    package: "com.hallain.pa.service"
    file: "src/main/java/com/hallain/pa/service/PA01001Service.java"
    injections:
      - type: "DAO"
        class: "PA01001DAO"
        field: "pa01001DAO"
    methods:
      - name: "selectList"
        signature: "List<PA01001MVO> selectList(PA01001MVO vo, int pageNo, int pageSize)"
        transactional: false
        line: 25
        logic:
          - type: "validation"
            description: "검색 조건 유효성 검사"
          - type: "dao_call"
            target: "pa01001DAO.selectList"
        dao_calls:
          - dao: "PA01001DAO"
            method: "selectList"
            mapper_id: "pa01001.selectList"

      - name: "selectCount"
        signature: "int selectCount(PA01001MVO vo)"
        transactional: false
        line: 42
        dao_calls:
          - dao: "PA01001DAO"
            method: "selectCount"
            mapper_id: "pa01001.selectCount"

      - name: "save"
        signature: "void save(List<PA01001MVO> list)"
        transactional: true
        line: 55
        logic:
          - type: "iteration"
            description: "rowStatus별 INSERT/UPDATE/DELETE 분기"
        dao_calls:
          - dao: "PA01001DAO"
            method: "insertPlan"
            mapper_id: "pa01001.insertPlan"
            condition: "rowStatus == 'INSERT'"
          - dao: "PA01001DAO"
            method: "updatePlan"
            mapper_id: "pa01001.updatePlan"
            condition: "rowStatus == 'UPDATE'"
          - dao: "PA01001DAO"
            method: "deletePlan"
            mapper_id: "pa01001.deletePlan"
            condition: "rowStatus == 'DELETE'"
```

```yaml
# data-access/FEAT-PA-001.yaml
metadata:
  feature_id: "FEAT-PA-001"
  layer: "L3 - Data Access"

daos:
  - class: "PA01001DAO"
    package: "com.hallain.pa.dao"
    file: "src/main/java/com/hallain/pa/dao/PA01001DAO.java"
    extends: "AbstractDAO"
    mapper_file: "com/halla/pa/sqlmap/sqlmap-PA01001.xml"
    methods:
      - name: "selectList"
        mapper_id: "pa01001.selectList"
        operation: "SELECT"
        input_type: "PA01001MVO"
        output_type: "List<PA01001MVO>"
        line: 15

      - name: "selectCount"
        mapper_id: "pa01001.selectCount"
        operation: "SELECT"
        input_type: "PA01001MVO"
        output_type: "int"
        line: 20

      - name: "insertPlan"
        mapper_id: "pa01001.insertPlan"
        operation: "INSERT"
        input_type: "PA01001MVO"
        output_type: "int"
        line: 25

      - name: "updatePlan"
        mapper_id: "pa01001.updatePlan"
        operation: "UPDATE"
        input_type: "PA01001MVO"
        output_type: "int"
        line: 30

      - name: "deletePlan"
        mapper_id: "pa01001.deletePlan"
        operation: "DELETE"
        input_type: "PA01001MVO"
        output_type: "int"
        line: 35
```

```yaml
# data-model/FEAT-PA-001.yaml
metadata:
  feature_id: "FEAT-PA-001"
  layer: "L5 - Data Model"

vo_classes:
  - class: "PA01001MVO"
    package: "com.hallain.pa.vo"
    file: "src/main/java/com/hallain/pa/vo/PA01001MVO.java"
    extends: "BaseVO"
    usage:
      - layer: "L1"
        purpose: "Request/Response Dataset"
      - layer: "L2"
        purpose: "Service 파라미터/리턴"
      - layer: "L3"
        purpose: "DAO 파라미터/리턴"
    fields:
      - name: "siteCd"
        type: "String"
        db_column: "SITE_CD"
        description: "사이트 코드"
      - name: "siteNm"
        type: "String"
        db_column: "SITE_NM"
        description: "사이트명"
      - name: "yyyymm"
        type: "String"
        db_column: "YYYYMM"
        description: "년월"
      - name: "odrNo"
        type: "String"
        db_column: "ODR_NO"
        description: "주문번호"
      - name: "totalQty"
        type: "BigDecimal"
        db_column: "TOTAL_QTY"
        description: "총수량"
      - name: "rowStatus"
        type: "String"
        db_column: null
        description: "MiPlatform 행상태 (INSERT/UPDATE/DELETE)"
        miplatform_standard: true
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| file_exists | structural | summary.yaml 존재 | ERROR | Yes |
| yaml_syntax | structural | YAML 파싱 오류 없음 | ERROR | Yes |
| layer_complete | content | 5개 Layer 모두 문서화 | ERROR | Yes |
| endpoint_traced | metric | 100% endpoint → service 추적 | ERROR | Yes |
| service_traced | metric | 100% service → dao 추적 | WARNING | No |
| sql_mapped | metric | 90% mapper_id → SQL 매핑 | WARNING | No |

### 5.2 Manual Reviews

| Review | Reviewer | Criteria | Required |
|--------|----------|----------|----------|
| Dependency accuracy | Tech Lead | 랜덤 3개 Feature 의존성 검증 | No |

### 5.3 Gate Criteria

```yaml
gate_criteria:
  id: "G1.3"
  name: "Deep Analysis Gate"
  threshold: 70
  metrics:
    - metric: "file_exists"
      weight: 0.2
      target: "true"
      formula: "summary.yaml exists"
    - metric: "layer_complete"
      weight: 0.4
      target: "5"
      formula: "count of documented layers"
    - metric: "endpoint_traced"
      weight: 0.3
      target: ">= 100%"
      formula: "traced_endpoints / total_endpoints * 100"
    - metric: "sql_mapped"
      weight: 0.1
      target: ">= 90%"
      formula: "mapped_sql / total_mapper_ids * 100"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Service not found | L2 empty | Controller → DAO 직접 호출 | L2 skip, direct mapping 기록 | No |
| iBatis XML missing | SQL empty | 매퍼 파일 경로 불일치 | MISSING 마킹, 수동 확인 필요 | No |
| VO class not found | L4 incomplete | 동적 Map 사용 | INLINE 마킹, 필드 추론 | No |
| Cross-domain call | 외부 의존성 | CM, SM 등 타 도메인 Service 호출 | dependencies.external에 기록 | No |
| Large feature | 30분 초과 | 100+ endpoints | Feature 분할 또는 timeout 연장 | Yes |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Layer count < 3 | critical | Phase 중단, 소스 구조 확인 | Tech Lead |
| Endpoint trace < 80% | major | WARNING 로그, 계속 진행 | Orchestrator |
| SQL mapping < 70% | major | iBatis 경로 재설정 필요 | Tech Lead |
| Cross-domain > 10 | minor | 로그 기록, 의존성 분석 필요 | - |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 부분 실패 | 해당 Feature만 재실행 | Feature |
| Layer 누락 | 해당 Layer만 재분석 | Feature |
| 전체 실패 | 입력 데이터 확인 후 재실행 | Phase |

---

## 7. Examples

### 7.1 Sample Input

**feature-inventory.yaml (일부):**
```yaml
features:
  - feature_id: "FEAT-PA-001"
    screen_id: "PA01001"
    name: "생산계획 조회"
    endpoints:
      - path: "/pa/PA01001/list.mi"
        method: "POST"
        controller: "PA01001Controller"
        method_name: "getList"
```

**Controller Source:**
```java
@Controller
@RequestMapping("/pa/PA01001")
public class PA01001Controller {

    @Autowired
    private PA01001Service pa01001Service;

    @RequestMapping("/list.mi")
    public String getList(HttpServletRequest request, ModelMap model) {
        MiHandler miHandler = new MiHandler(request);
        PA01001MVO vo = (PA01001MVO) miHandler.getObject("ds_master", PA01001MVO.class);
        int pageNo = miHandler.getValueInt("COMM_PageNo");

        List<PA01001MVO> result = pa01001Service.selectList(vo, pageNo, 20);
        int totalCount = pa01001Service.selectCount(vo);

        miHandler.clear();
        miHandler.setDataset(result, "ds_Mst", PA01001MVO.class);
        miHandler.add("COMM_TotalCount", totalCount);
        miHandler.setSuccess(true);

        model.put("MI_DATA", miHandler.getMiPlatformData());
        return "common/MiPlatform";
    }
}
```

**Service Source:**
```java
@Service
public class PA01001Service {

    @Autowired
    private PA01001DAO pa01001DAO;

    public List<PA01001MVO> selectList(PA01001MVO vo, int pageNo, int pageSize) {
        vo.setStartRow((pageNo - 1) * pageSize + 1);
        vo.setEndRow(pageNo * pageSize);
        return pa01001DAO.selectList(vo);
    }

    public int selectCount(PA01001MVO vo) {
        return pa01001DAO.selectCount(vo);
    }
}
```

**iBatis XML:**
```xml
<sqlMap namespace="pa01001">
    <select id="selectList" parameterClass="PA01001MVO" resultClass="PA01001MVO">
        SELECT * FROM (
            SELECT ROWNUM RN, A.* FROM (
                SELECT SITE_CD, SITE_NM, YYYYMM, ODR_NO, TOTAL_QTY
                FROM TB_PROD_PLAN
                WHERE 1=1
                <isNotNull property="siteCd">
                    AND SITE_CD = #siteCd#
                </isNotNull>
                ORDER BY YYYYMM DESC
            ) A
        ) WHERE RN BETWEEN #startRow# AND #endRow#
    </select>

    <select id="selectCount" parameterClass="PA01001MVO" resultClass="int">
        SELECT COUNT(*) FROM TB_PROD_PLAN
        WHERE 1=1
        <isNotNull property="siteCd">
            AND SITE_CD = #siteCd#
        </isNotNull>
    </select>
</sqlMap>
```

### 7.2 Sample Output

위의 4.4 Output Schema 섹션 참조

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| Service 없음 | Controller → DAO 직접 호출 | L2: services: [], direct_dao: true |
| iBatis XML 없음 | 매퍼 파일 누락 | SQL: MISSING, manual_review: true |
| 동적 VO | Map<String, Object> 사용 | VO: INLINE, fields: inferred |
| SP 호출 | {call PKG.PROC(?)} | stored_procedures 섹션에 기록 |
| Cross-domain | CommonService 호출 | dependencies.external에 기록 |

---

## Version History

### v2.1.0 (2026-01-13)
- **Read Tool 256KB Limit 대응**
  - Section 3.3: Large File Handling 신규 추가
  - Input reading: feature-inventory.yaml, miplatform-protocol.yaml 대용량 파일 처리 지원
  - 분할 형식(디렉토리) 및 단일 파일 형식 모두 지원
  - offset/limit 기반 청크 읽기 전략 추가

### v2.0.0 (2026-01-09)
- **QUERY-FIRST 전략 도입**: SQL-First 역추적 방식으로 전면 전환
- 분석 순서 변경: L4(SQL) → L3(DAO) → L2(Service) → L1(Controller) → L5(VO)
- 역추적 로직 추가 (SQL namespace → DAO class → Service caller → Controller endpoint)
- Decision Points 업데이트 (orphan_sql, internal_service 탐지 추가)
- Controller-First 접근법의 위험(DB 중심 피처 누락) 방지

### v1.1.0 (2026-01-08)
- Step 8: Schema Validation 추가
- s1-03-deep-analysis.schema.yaml 스키마 참조
- 8개 검증 규칙 (V001-V008) 적용
- 5-Layer 파일 존재 검증

### v1.0.0 (2026-01-07)
- Initial version
- 5-Layer trace 분석 지원
- Controller → Service → DAO → SQL 추적 (deprecated in v2.0.0)
- VO 클래스 필드 분석
- Cross-domain 의존성 탐지
