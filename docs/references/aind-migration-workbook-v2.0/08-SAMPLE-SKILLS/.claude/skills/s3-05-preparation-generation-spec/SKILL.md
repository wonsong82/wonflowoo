---
name: s3-05-preparation-generation-spec
description: Use when creating code generation templates, defining transformation rules for iBatis to MyBatis, or preparing generation specifications for Stage 4 code generation (project)
---

# Generation Spec

> **Skill ID**: S3-05
> **Skill Type**: Generation (코드 생성 템플릿 및 규칙 정의)
> **Stage**: 3 - Preparation
> **Phase**: 3.5 - Generation Spec

## 1. Overview

### 1.1 Purpose

승인된 아키텍처를 기반으로 **코드 생성 템플릿**과 **변환 규칙**을 정의합니다. Stage 4에서 일관된 코드 생성을 위한 명세를 제공합니다.

**생성 대상:**
- Layer별 코드 템플릿 (Controller, Service, Repository, DTO, Entity, Mapper XML)
- iBatis → MyBatis 변환 규칙
- 네이밍 컨벤션 규칙
- Annotation 적용 규칙

**사용 용도:**
- S4-02 Mini-Pilot 코드 생성 기준
- S4-03 Domain Batch 대량 생성 가이드
- 코드 품질 일관성 보장

### 1.2 Generation Scope

| Aspect | Included | Excluded |
|--------|----------|----------|
| Templates | Controller, Service, Repository, DTO, Entity, Mapper XML | Test templates (S4-04) |
| Rules | iBatis→MyBatis, naming, annotations | Business logic transformation |
| Layers | All 6 layers | Configuration files |

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Template-Driven** | 템플릿 기반 생성 | 일관성 보장, 품질 관리 |
| **Reference Aligned** | next-hallain-sample 패턴 준수 | 검증된 코드 패턴 |
| **Transformation Rules** | 명시적 변환 규칙 | iBatis→MyBatis 정확한 변환 |
| **Extensible** | 도메인 특성 반영 가능 | 유연한 적용 |

### 1.4 SQL 보존 필수 규칙 (QUERY-FIRST 원칙 - 전체 선행 이관)

> **CRITICAL**: Query 이관이 어떤 Task보다 우선한다. Legacy SQL은 100% 보존되어야 한다.

```yaml
# ┌─────────────────────────────────────────────────────────────────────────┐
# │                    QUERY-FIRST 전략 (전체 선행 이관)                      │
# │                                                                         │
# │  "Feature별 작업이 아닌, Query 전체를 먼저 이관한 후 Java 코드 생성"       │
# └─────────────────────────────────────────────────────────────────────────┘
#
#  STAGE A: Query 전체 이관 (1,318개 Mapper XML)
#           │
#           ▼
#  STAGE B: Query Fidelity 검증 (100% PASS 필수)
#           │
#           ▼
#  STAGE C: Java 코드 생성 (Query 검증 PASS 후에만)

generation_strategy:
  name: "Query 전체 선행 이관"
  principle: "Query 전체를 먼저 이관 → 검증 → Java 생성"

  stage_a_query_migration:
    scope: "전체 sqlmap 파일 (1,318개)"
    output: "next-hallain/src/main/resources/mapper/{domain}/"
    priority: "어떤 Task보다 우선"

  stage_b_query_verification:
    gate: "Query Fidelity Gate"
    threshold: "100%"  # 99% 불가
    human_review: "REQUIRED"

  stage_c_java_generation:
    precondition: "STAGE B Gate PASS"
    scope: "Query 검증 완료된 Feature만"

mandatory_rules:
  RULE_SQL_DIRECT_COPY:
    priority: P0  # 최우선
    description: "Legacy sqlmap SQL 직접 복사 후 문법만 변환"
    rationale: "MM0101051M 케이스에서 SQL 재생성으로 인한 로직 변조 발생"
    steps:
      1. Legacy sqlmap XML 파일 열기 (hallain/src/main/resources/com/halla/{domain}/sqlmap/)
      2. SQL 전체 복사 (주석, 공백, 포맷 포함)
      3. iBatis → MyBatis 문법만 변환:
         - "#var#" → "#{var}"
         - "$var$" → "${var}"
         - "<isNotEmpty>" → "<if test>"
         - "parameterClass" → "parameterType"
         - "resultClass" → "resultType"
      4. 로직/조건/조인/값 수정 절대 금지
    on_violation: "BLOCK - 생성 중단, Human Review 필수"

  RULE_NO_SQL_INTERPRETATION:
    priority: P0
    description: "SQL 해석/재생성 금지"
    rationale: "Stage 1 스펙 기반 SQL 재작성으로 비즈니스 로직 변조 발생"
    prohibited:
      - Stage 1 스펙 기반 SQL 재작성
      - 컬럼명/테이블명 추측
      - 비즈니스 로직 재해석
      - 조건값 변경 (예: 'INPRCH' → '1', ORD_PRG_STAT_CD IN 값 변경)
      - JOIN 조건 수정
      - GROUP BY/ORDER BY 구조 변경
      - DECODE/CASE 로직 간소화
    on_violation: "BLOCK - Legacy SQL로 덮어쓰기"

  RULE_PHASE_SEPARATION:
    priority: P0
    description: "2-Phase 분리 준수"
    rationale: "Query 이관과 Java 생성을 분리하여 SQL 보존 보장"
    phases:
      phase_1: "Query 전체 이관 (Mapper XML)"
      gate: "Query Fidelity Gate (100% PASS)"
      phase_2: "Java 코드 생성 (Query 검증 후에만)"
    on_violation: "Java 생성 불가"

  verification_checklist:
    description: "Mapper XML 생성 후 필수 검증"
    items:
      - "[ ] 테이블명 100% 일치"
      - "[ ] 컬럼명 100% 일치"
      - "[ ] JOIN 조건 100% 일치 (EE.MAT_ORD_NO = FF.MAT_ORD_NO 등)"
      - "[ ] WHERE 절 조건값 100% 일치 (IN, =, LIKE 등)"
      - "[ ] GROUP BY/ORDER BY 100% 일치"
      - "[ ] 서브쿼리 구조 100% 일치"
      - "[ ] DECODE/CASE 로직 100% 일치"
```

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s3-04-preparation-architecture-design` | 승인된 아키텍처 설계 |
| `s2-04-validation-spec-completion` | 완료된 Feature Spec |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s4-01-generation-project-scaffold` | 프로젝트 초기 구조 생성 |
| `s4-02-generation-mini-pilot` | 파일럿 코드 생성 |
| `s4-03-generation-domain-batch` | 대량 코드 생성 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S3-04"
    skill_name: "s3-04-preparation-architecture-design"
    dependency_type: "input"
    artifacts:
      - "architecture-design.yaml"
      - "layer-standards.md"
    status: "APPROVED required"

  - skill_id: "S2-04"
    skill_name: "s2-04-validation-spec-completion"
    dependency_type: "input"
    artifact: "completed specs"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| architecture_design | file | `work/specs/stage3-outputs/phase4/architecture-design.yaml` | YAML | Yes |
| completed_specs | directory | `work/specs/stage2-outputs/phase4/` | YAML | Yes |
| reference_implementation | directory | `next-hallain-sample/` | Java | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Read | - | Reference 코드 분석 |
| Write | - | 템플릿 파일 생성 |

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: parallel
  unit: layer
  parallelization:
    max_parallel: 3
    batch_size: 3  # 6 templates / 2 batches
    timeout_minutes: 120
    retry_on_failure: 2
```

### 3.2 Generation Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Analyze     │────▶│ Create       │────▶│ Define       │────▶│ Validate     │
│  Reference   │     │ Templates    │     │ Rules        │     │ Completeness │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 3.3 Process Steps

#### Step 1: Analyze Reference Implementation

**Description:** next-hallain-sample 코드 패턴 상세 분석

**Sub-steps:**
1. 각 Layer 파일 구조 분석
2. 사용된 어노테이션 목록화
3. Import 패턴 파악
4. 코드 스타일 (formatting, naming) 추출

**Analysis Output:**
```yaml
reference_patterns:
  controller:
    imports:
      - "lombok.RequiredArgsConstructor"
      - "org.springframework.web.bind.annotation.*"
      - "io.swagger.v3.oas.annotations.*"
    annotations:
      class: ["@RestController", "@RequestMapping", "@Tag", "@RequiredArgsConstructor"]
      method: ["@PostMapping", "@GetMapping", "@Operation"]
    injection: "Constructor injection via @RequiredArgsConstructor"

  service:
    imports:
      - "lombok.RequiredArgsConstructor"
      - "org.springframework.stereotype.Service"
      - "org.springframework.transaction.annotation.Transactional"
    annotations:
      class: ["@Service", "@RequiredArgsConstructor", "@Transactional(readOnly=true)"]
      method: ["@Transactional"]
    transaction: "Class-level readOnly, method-level write"

  mapper:
    imports:
      - "org.apache.ibatis.annotations.Mapper"
    annotations:
      class: ["@Mapper"]
    style: "Interface-based MyBatis mapper"
```

**Validation:** 6개 레이어 패턴 분석 완료

---

#### Step 2: Create Layer Templates

**Description:** 각 레이어별 코드 템플릿 생성

**Sub-steps:**
1. Controller 템플릿 생성
2. Service 템플릿 생성
3. Repository (Mapper) 템플릿 생성
4. DTO 템플릿 생성
5. Entity 템플릿 생성
6. Mapper XML 템플릿 생성

**Template Variables:**
```yaml
template_variables:
  domain:
    - ${DOMAIN} # pa, mm, sc...
    - ${DOMAIN_UPPER} # PA, MM, SC...
    - ${DOMAIN_PASCAL} # Pa, Mm, Sc...
  screen:
    - ${SCREEN_ID} # PA01001
    - ${SCREEN_NAME} # 생산계획 관리
  entity:
    - ${ENTITY_NAME} # ProductionPlan
    - ${ENTITY_NAME_LOWER} # productionPlan
    - ${TABLE_NAME} # TB_PROD_PLAN
  method:
    - ${METHOD_NAME} # selectList
    - ${HTTP_METHOD} # POST
    - ${URL_PATH} # /list
  fields:
    - ${FIELD_NAME} # siteCd
    - ${FIELD_TYPE} # String
    - ${DB_COLUMN} # SITE_CD
```

**Validation:** 6개 템플릿 생성 완료

---

#### Step 3: Define Transformation Rules

**Description:** iBatis → MyBatis 변환 규칙 정의

**Sub-steps:**
1. 태그 변환 규칙
2. 파라미터 바인딩 변환
3. 동적 SQL 변환
4. 결과 매핑 변환

**Transformation Rules:**
```yaml
ibatis_to_mybatis:
  tags:
    # Root tag
    - from: "<sqlMap namespace=\"{ns}\">"
      to: "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE mapper PUBLIC \"-//mybatis.org//DTD Mapper 3.0//EN\" \"http://mybatis.org/dtd/mybatis-3-mapper.dtd\">\n<mapper namespace=\"com.hallain.{domain}.repository.{Entity}Mapper\">"

    # Type attributes
    - from: "parameterClass=\"{type}\""
      to: "parameterType=\"{type}\""
    - from: "resultClass=\"{type}\""
      to: "resultType=\"{type}\""
    - from: "resultMap=\"{map}\""
      to: "resultMap=\"{map}\""

  parameter_binding:
    # Variable binding
    - from: "#variable#"
      to: "#{variable}"
    - from: "$variable$"
      to: "${variable}"

  dynamic_sql:
    # isNotNull → if
    - from: "<isNotNull property=\"{prop}\">"
      to: "<if test=\"{prop} != null\">"
    - from: "</isNotNull>"
      to: "</if>"

    # isNotEmpty → if
    - from: "<isNotEmpty property=\"{prop}\">"
      to: "<if test=\"{prop} != null and {prop} != ''\">"
    - from: "</isNotEmpty>"
      to: "</if>"

    # isEqual → if
    - from: "<isEqual property=\"{prop}\" compareValue=\"{val}\">"
      to: "<if test=\"{prop} == '{val}'\">"
    - from: "</isEqual>"
      to: "</if>"

    # iterate → foreach
    - from: "<iterate property=\"{prop}\" open=\"(\" close=\")\" conjunction=\",\">"
      to: "<foreach item=\"item\" collection=\"{prop}\" open=\"(\" separator=\",\" close=\")\">"
    - from: "</iterate>"
      to: "</foreach>"
    - from: "#list[]#"
      to: "#{item}"

  stored_procedures:
    # Procedure call
    - from: "<procedure id=\"{id}\">{call {proc}(?, ?, ?)}</procedure>"
      to: "<select id=\"{id}\" statementType=\"CALLABLE\">{call {proc}(#{param1, mode=IN}, #{param2, mode=IN}, #{param3, mode=OUT, jdbcType=CURSOR, resultMap=resultMap})}</select>"
```

**Validation:** 변환 규칙 완전성 검증

---

#### Step 4: Define Naming Conventions

**Description:** 네이밍 컨벤션 규칙 정의

**Sub-steps:**
1. 클래스명 규칙
2. 메서드명 규칙
3. 패키지명 규칙
4. 파일명 규칙

**Naming Conventions:**
```yaml
naming_conventions:
  classes:
    controller: "{Screen}Controller"  # PA01001Controller
    service: "{Screen}Service"  # PA01001Service
    mapper: "{Screen}Mapper"  # PA01001Mapper
    request_dto: "{Screen}{Action}Request"  # PA01001SearchRequest
    response_dto: "{Screen}Response"  # PA01001Response
    entity: "{Screen}Entity"  # PA01001Entity

  methods:
    select_list: "get{Entity}List"
    select_one: "get{Entity}"
    select_count: "get{Entity}Count"
    insert: "create{Entity}"
    update: "update{Entity}"
    delete: "delete{Entity}"
    save: "save{Entity}"  # Insert/Update/Delete 통합

  packages:
    controller: "com.hallain.{domain}.controller"
    service: "com.hallain.{domain}.service"
    repository: "com.hallain.{domain}.repository"
    dto: "com.hallain.{domain}.dto"
    entity: "com.hallain.{domain}.entity"

  files:
    java: "{ClassName}.java"
    mapper_xml: "{Screen}Mapper.xml"  # PA01001Mapper.xml
    mapper_xml_path: "resources/mapper/{domain}/"
```

**Validation:** 네이밍 규칙 완전성 검증

---

#### Step 5: Validate Completeness

**Description:** 생성 스펙 완전성 검증

**Sub-steps:**
1. 6개 템플릿 존재 확인
2. 변환 규칙 커버리지 확인
3. 네이밍 규칙 완전성 확인
4. generation-rules.yaml 통합 생성

**Validation:** Phase Gate 기준 충족 확인

---

#### Step 6: Schema Validation

**Description:** 생성된 템플릿 및 규칙 파일이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | generation-templates/*.yaml root | metadata, template 필수 키 존재 | ERROR | Yes |
| V002 | generation-rules.yaml root | metadata, summary, templates, ibatis_to_mybatis, naming_conventions 필수 키 존재 | ERROR | Yes |
| V003 | metadata.generated_by | 정확히 "s3-05-preparation-generation-spec" | ERROR | Yes |
| V004 | metadata.layer | enum: controller, service, repository, dto, entity, mapper_xml | ERROR | Yes |
| V005 | templates[].status | enum: ready, draft, pending | ERROR | Yes |
| V006 | template.file_name | 템플릿 변수 (${SCREEN_ID} 등) 포함 | WARNING | No |
| V007 | template.package | 도메인 변수 (${DOMAIN}) 포함 | WARNING | No |
| V008 | summary.templates_created | >= 6 (6개 레이어 템플릿) | ERROR | Yes |
| V009 | naming_conventions | classes, methods, packages 모두 정의 | ERROR | Yes |
| V010 | ibatis_to_mybatis | root_element, attributes, parameter_binding, dynamic_sql 모두 정의 | ERROR | Yes |
| V011 | templates[].status | 모든 템플릿 status가 ready | WARNING | No |

**Sub-steps:**
1. 각 레이어 템플릿 파일 스키마 검증
2. generation-rules.yaml 스키마 검증
3. iBatis→MyBatis 변환 규칙 완전성 검증
4. 오류 발생 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 템플릿 재생성 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.4 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | Java Record 지원 | DTO에 record 사용 | class 사용 |
| DP-2 | SP 호출 존재 | CALLABLE 매핑 포함 | 일반 쿼리만 |
| DP-3 | 대형 도메인 (PA) | Sub-package 템플릿 | 단일 패키지 |
| DP-4 | Lombok 사용 | @RequiredArgsConstructor | 생성자 직접 작성 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage3-outputs/phase5/"

  structure:
    - "generation-templates/"
    - "generation-rules.yaml"
```

### 4.2 Output Files

| File | Type | Purpose | Required |
|------|------|---------|----------|
| generation-templates/controller-template.yaml | YAML | Controller 생성 템플릿 | Yes |
| generation-templates/service-template.yaml | YAML | Service 생성 템플릿 | Yes |
| generation-templates/repository-template.yaml | YAML | Mapper Interface 템플릿 | Yes |
| generation-templates/dto-template.yaml | YAML | Request/Response DTO 템플릿 | Yes |
| generation-templates/entity-template.yaml | YAML | Entity 템플릿 | Yes |
| generation-templates/mapper-xml-template.yaml | YAML | MyBatis XML 템플릿 | Yes |
| generation-rules.yaml | YAML | 변환 규칙 통합 | Yes |

### 4.3 File Header

```yaml
# Generated by: s3-05-preparation-generation-spec
# Stage: 3 - Preparation
# Phase: 3.5 - Generation Spec
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
```

### 4.4 Output Schemas

#### generation-templates/controller-template.yaml

```yaml
# controller-template.yaml
metadata:
  generated_by: "s3-05-preparation-generation-spec"
  layer: "controller"
  version: "1.0.0"

template:
  file_name: "${SCREEN_ID}Controller.java"
  package: "com.hallain.${DOMAIN}.controller"

  imports:
    - "lombok.RequiredArgsConstructor"
    - "org.springframework.web.bind.annotation.*"
    - "io.swagger.v3.oas.annotations.Operation"
    - "io.swagger.v3.oas.annotations.tags.Tag"
    - "jakarta.validation.Valid"
    - "com.hallain.common.response.ApiResponse"
    - "com.hallain.${DOMAIN}.service.${SCREEN_ID}Service"
    - "com.hallain.${DOMAIN}.dto.*"

  class_annotations:
    - "@RestController"
    - "@RequestMapping(\"/api/${DOMAIN}/${SCREEN_ID_LOWER}\")"
    - "@Tag(name = \"${SCREEN_ID} - ${SCREEN_NAME}\")"
    - "@RequiredArgsConstructor"

  class_body: |
    private final ${SCREEN_ID}Service ${SCREEN_ID_LOWER}Service;

    ${METHODS}

  method_templates:
    get_list:
      annotations:
        - "@PostMapping(\"/list\")"
        - "@Operation(summary = \"${SCREEN_NAME} 목록 조회\")"
      signature: "public ApiResponse<List<${SCREEN_ID}Response>> get${ENTITY_NAME}List(@Valid @RequestBody ${SCREEN_ID}SearchRequest request)"
      body: |
        return ApiResponse.success(${SCREEN_ID_LOWER}Service.get${ENTITY_NAME}List(request));

    get_one:
      annotations:
        - "@PostMapping(\"/detail\")"
        - "@Operation(summary = \"${SCREEN_NAME} 상세 조회\")"
      signature: "public ApiResponse<${SCREEN_ID}Response> get${ENTITY_NAME}(@Valid @RequestBody ${SCREEN_ID}DetailRequest request)"
      body: |
        return ApiResponse.success(${SCREEN_ID_LOWER}Service.get${ENTITY_NAME}(request));

    save:
      annotations:
        - "@PostMapping(\"/save\")"
        - "@Operation(summary = \"${SCREEN_NAME} 저장\")"
      signature: "public ApiResponse<Void> save${ENTITY_NAME}(@Valid @RequestBody List<${SCREEN_ID}SaveRequest> requests)"
      body: |
        ${SCREEN_ID_LOWER}Service.save${ENTITY_NAME}(requests);
        return ApiResponse.success();

example_output: |
  package com.hallain.pa.controller;

  import lombok.RequiredArgsConstructor;
  import org.springframework.web.bind.annotation.*;
  import io.swagger.v3.oas.annotations.Operation;
  import io.swagger.v3.oas.annotations.tags.Tag;
  import jakarta.validation.Valid;
  import com.hallain.common.response.ApiResponse;
  import com.hallain.pa.service.PA01001Service;
  import com.hallain.pa.dto.*;

  @RestController
  @RequestMapping("/api/pa/pa01001")
  @Tag(name = "PA01001 - 생산계획 관리")
  @RequiredArgsConstructor
  public class PA01001Controller {

      private final PA01001Service pa01001Service;

      @PostMapping("/list")
      @Operation(summary = "생산계획 목록 조회")
      public ApiResponse<List<PA01001Response>> getProductionPlanList(
              @Valid @RequestBody PA01001SearchRequest request) {
          return ApiResponse.success(pa01001Service.getProductionPlanList(request));
      }

      @PostMapping("/detail")
      @Operation(summary = "생산계획 상세 조회")
      public ApiResponse<PA01001Response> getProductionPlan(
              @Valid @RequestBody PA01001DetailRequest request) {
          return ApiResponse.success(pa01001Service.getProductionPlan(request));
      }

      @PostMapping("/save")
      @Operation(summary = "생산계획 저장")
      public ApiResponse<Void> saveProductionPlan(
              @Valid @RequestBody List<PA01001SaveRequest> requests) {
          pa01001Service.saveProductionPlan(requests);
          return ApiResponse.success();
      }
  }
```

#### generation-templates/service-template.yaml

```yaml
# service-template.yaml
metadata:
  generated_by: "s3-05-preparation-generation-spec"
  layer: "service"
  version: "1.0.0"

template:
  file_name: "${SCREEN_ID}Service.java"
  package: "com.hallain.${DOMAIN}.service"

  imports:
    - "lombok.RequiredArgsConstructor"
    - "org.springframework.stereotype.Service"
    - "org.springframework.transaction.annotation.Transactional"
    - "com.hallain.${DOMAIN}.repository.${SCREEN_ID}Mapper"
    - "com.hallain.${DOMAIN}.dto.*"
    - "com.hallain.${DOMAIN}.entity.${SCREEN_ID}Entity"
    - "java.util.List"

  class_annotations:
    - "@Service"
    - "@RequiredArgsConstructor"
    - "@Transactional(readOnly = true)"

  class_body: |
    private final ${SCREEN_ID}Mapper ${SCREEN_ID_LOWER}Mapper;

    ${METHODS}

  method_templates:
    get_list:
      annotations: []
      signature: "public List<${SCREEN_ID}Response> get${ENTITY_NAME}List(${SCREEN_ID}SearchRequest request)"
      body: |
        return ${SCREEN_ID_LOWER}Mapper.selectList(request)
            .stream()
            .map(${SCREEN_ID}Response::from)
            .toList();

    get_count:
      annotations: []
      signature: "public int get${ENTITY_NAME}Count(${SCREEN_ID}SearchRequest request)"
      body: |
        return ${SCREEN_ID_LOWER}Mapper.selectCount(request);

    get_one:
      annotations: []
      signature: "public ${SCREEN_ID}Response get${ENTITY_NAME}(${SCREEN_ID}DetailRequest request)"
      body: |
        return ${SCREEN_ID}Response.from(${SCREEN_ID_LOWER}Mapper.selectOne(request));

    save:
      annotations:
        - "@Transactional"
      signature: "public void save${ENTITY_NAME}(List<${SCREEN_ID}SaveRequest> requests)"
      body: |
        for (${SCREEN_ID}SaveRequest request : requests) {
            switch (request.rowStatus()) {
                case INSERT -> ${SCREEN_ID_LOWER}Mapper.insert(request.toEntity());
                case UPDATE -> ${SCREEN_ID_LOWER}Mapper.update(request.toEntity());
                case DELETE -> ${SCREEN_ID_LOWER}Mapper.delete(request.id());
            }
        }

example_output: |
  package com.hallain.pa.service;

  import lombok.RequiredArgsConstructor;
  import org.springframework.stereotype.Service;
  import org.springframework.transaction.annotation.Transactional;
  import com.hallain.pa.repository.PA01001Mapper;
  import com.hallain.pa.dto.*;
  import com.hallain.pa.entity.PA01001Entity;
  import java.util.List;

  @Service
  @RequiredArgsConstructor
  @Transactional(readOnly = true)
  public class PA01001Service {

      private final PA01001Mapper pa01001Mapper;

      public List<PA01001Response> getProductionPlanList(PA01001SearchRequest request) {
          return pa01001Mapper.selectList(request)
              .stream()
              .map(PA01001Response::from)
              .toList();
      }

      public int getProductionPlanCount(PA01001SearchRequest request) {
          return pa01001Mapper.selectCount(request);
      }

      @Transactional
      public void saveProductionPlan(List<PA01001SaveRequest> requests) {
          for (PA01001SaveRequest request : requests) {
              switch (request.rowStatus()) {
                  case INSERT -> pa01001Mapper.insert(request.toEntity());
                  case UPDATE -> pa01001Mapper.update(request.toEntity());
                  case DELETE -> pa01001Mapper.delete(request.id());
              }
          }
      }
  }
```

#### generation-templates/mapper-xml-template.yaml

```yaml
# mapper-xml-template.yaml
metadata:
  generated_by: "s3-05-preparation-generation-spec"
  layer: "mapper_xml"
  version: "1.0.0"

template:
  file_name: "${SCREEN_ID}Mapper.xml"
  path: "src/main/resources/mapper/${DOMAIN}/"

  structure: |
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
    <mapper namespace="com.hallain.${DOMAIN}.repository.${SCREEN_ID}Mapper">

        ${SQL_STATEMENTS}

    </mapper>

  sql_templates:
    select_list: |
      <select id="selectList" parameterType="${SCREEN_ID}SearchRequest" resultType="${SCREEN_ID}Entity">
          SELECT ${SELECT_COLUMNS}
          FROM ${TABLE_NAME}
          WHERE 1=1
          ${WHERE_CONDITIONS}
          ${ORDER_BY}
          ${PAGINATION}
      </select>

    select_count: |
      <select id="selectCount" parameterType="${SCREEN_ID}SearchRequest" resultType="int">
          SELECT COUNT(*)
          FROM ${TABLE_NAME}
          WHERE 1=1
          ${WHERE_CONDITIONS}
      </select>

    select_one: |
      <select id="selectOne" parameterType="${SCREEN_ID}DetailRequest" resultType="${SCREEN_ID}Entity">
          SELECT ${SELECT_COLUMNS}
          FROM ${TABLE_NAME}
          WHERE ${PRIMARY_KEY_CONDITION}
      </select>

    insert: |
      <insert id="insert" parameterType="${SCREEN_ID}Entity">
          INSERT INTO ${TABLE_NAME} (
              ${INSERT_COLUMNS}
          ) VALUES (
              ${INSERT_VALUES}
          )
      </insert>

    update: |
      <update id="update" parameterType="${SCREEN_ID}Entity">
          UPDATE ${TABLE_NAME}
          SET ${UPDATE_SET}
          WHERE ${PRIMARY_KEY_CONDITION}
      </update>

    delete: |
      <delete id="delete" parameterType="String">
          DELETE FROM ${TABLE_NAME}
          WHERE ${PRIMARY_KEY_CONDITION}
      </delete>

  dynamic_sql_patterns:
    if_not_null: |
      <if test="${FIELD} != null">
          AND ${DB_COLUMN} = #{${FIELD}}
      </if>

    if_not_empty: |
      <if test="${FIELD} != null and ${FIELD} != ''">
          AND ${DB_COLUMN} = #{${FIELD}}
      </if>

    foreach: |
      <foreach item="item" collection="${LIST_FIELD}" open="(" separator="," close=")">
          #{item}
      </foreach>

    pagination_oracle: |
      <if test="pageNo != null and pageSize != null">
          OFFSET #{offset} ROWS FETCH NEXT #{pageSize} ROWS ONLY
      </if>

example_output: |
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
      "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
  <mapper namespace="com.hallain.pa.repository.PA01001Mapper">

      <select id="selectList" parameterType="PA01001SearchRequest" resultType="PA01001Entity">
          SELECT PLAN_ID, SITE_CD, YYYYMM, ODR_NO, TOTAL_QTY, CREATED_AT
          FROM TB_PROD_PLAN
          WHERE 1=1
          <if test="siteCd != null and siteCd != ''">
              AND SITE_CD = #{siteCd}
          </if>
          <if test="yyyymm != null and yyyymm != ''">
              AND YYYYMM = #{yyyymm}
          </if>
          ORDER BY CREATED_AT DESC
          OFFSET #{offset} ROWS FETCH NEXT #{pageSize} ROWS ONLY
      </select>

      <select id="selectCount" parameterType="PA01001SearchRequest" resultType="int">
          SELECT COUNT(*)
          FROM TB_PROD_PLAN
          WHERE 1=1
          <if test="siteCd != null and siteCd != ''">
              AND SITE_CD = #{siteCd}
          </if>
      </select>

      <insert id="insert" parameterType="PA01001Entity">
          INSERT INTO TB_PROD_PLAN (
              PLAN_ID, SITE_CD, YYYYMM, ODR_NO, TOTAL_QTY, CREATED_AT
          ) VALUES (
              #{planId}, #{siteCd}, #{yyyymm}, #{odrNo}, #{totalQty}, SYSDATE
          )
      </insert>

      <update id="update" parameterType="PA01001Entity">
          UPDATE TB_PROD_PLAN
          SET SITE_CD = #{siteCd},
              YYYYMM = #{yyyymm},
              ODR_NO = #{odrNo},
              TOTAL_QTY = #{totalQty}
          WHERE PLAN_ID = #{planId}
      </update>

      <delete id="delete" parameterType="String">
          DELETE FROM TB_PROD_PLAN
          WHERE PLAN_ID = #{planId}
      </delete>

  </mapper>
```

#### generation-rules.yaml

```yaml
# generation-rules.yaml
metadata:
  generated_by: "s3-05-preparation-generation-spec"
  generated_at: "2026-01-07T16:00:00Z"
  version: "1.0.0"

summary:
  templates_created: 6
  transformation_rules: 25
  naming_rules: 18

templates:
  - name: "controller-template.yaml"
    layer: "controller"
    status: "ready"
  - name: "service-template.yaml"
    layer: "service"
    status: "ready"
  - name: "repository-template.yaml"
    layer: "repository"
    status: "ready"
  - name: "dto-template.yaml"
    layer: "dto"
    status: "ready"
  - name: "entity-template.yaml"
    layer: "entity"
    status: "ready"
  - name: "mapper-xml-template.yaml"
    layer: "mapper_xml"
    status: "ready"

ibatis_to_mybatis:
  # Root element transformation
  root_element:
    from: "<sqlMap namespace=\"{ns}\">"
    to: "<mapper namespace=\"com.hallain.{domain}.repository.{Entity}Mapper\">"

  # Attribute transformations
  attributes:
    - { from: "parameterClass", to: "parameterType" }
    - { from: "resultClass", to: "resultType" }

  # Parameter binding
  parameter_binding:
    - { from: "#var#", to: "#{var}" }
    - { from: "$var$", to: "${var}" }

  # Dynamic SQL
  dynamic_sql:
    isNotNull:
      from: "<isNotNull property=\"{p}\">"
      to: "<if test=\"{p} != null\">"
    isNotEmpty:
      from: "<isNotEmpty property=\"{p}\">"
      to: "<if test=\"{p} != null and {p} != ''\">"
    isEqual:
      from: "<isEqual property=\"{p}\" compareValue=\"{v}\">"
      to: "<if test=\"{p} == '{v}'\">"
    iterate:
      from: "<iterate property=\"{p}\" open=\"(\" close=\")\" conjunction=\",\">"
      to: "<foreach item=\"item\" collection=\"{p}\" open=\"(\" separator=\",\" close=\")\">"

  # Stored procedure
  stored_procedure:
    pattern: "CALLABLE statement type"
    example: |
      # iBatis
      <procedure id="callProc">{call PKG.PROC(?, ?)}</procedure>

      # MyBatis
      <select id="callProc" statementType="CALLABLE">
          {call PKG.PROC(#{param1, mode=IN}, #{result, mode=OUT, jdbcType=CURSOR})}
      </select>

naming_conventions:
  classes:
    controller: "{Screen}Controller"
    service: "{Screen}Service"
    mapper: "{Screen}Mapper"
    request: "{Screen}{Action}Request"
    response: "{Screen}Response"
    entity: "{Screen}Entity"

  methods:
    list: "get{Entity}List"
    one: "get{Entity}"
    count: "get{Entity}Count"
    create: "create{Entity}"
    update: "update{Entity}"
    delete: "delete{Entity}"
    save: "save{Entity}"

  packages:
    base: "com.hallain"
    domain_pattern: "com.hallain.{domain}.{layer}"

  files:
    java: "{ClassName}.java"
    xml: "{Screen}Mapper.xml"
    xml_path: "resources/mapper/{domain}/"

annotation_rules:
  controller:
    class: ["@RestController", "@RequestMapping", "@Tag", "@RequiredArgsConstructor"]
    list_method: ["@PostMapping(\"/list\")", "@Operation"]
    detail_method: ["@PostMapping(\"/detail\")", "@Operation"]
    save_method: ["@PostMapping(\"/save\")", "@Operation"]

  service:
    class: ["@Service", "@RequiredArgsConstructor", "@Transactional(readOnly=true)"]
    write_method: ["@Transactional"]

  repository:
    class: ["@Mapper"]

  dto:
    class: []  # Java Record 사용 시 불필요
    validation: ["@NotNull", "@NotBlank", "@Size", "@Min", "@Max"]

generation_order:
  # 2-Phase 분리: Query 전체 선행 이관
  phase_1_query_migration:
    description: "Query 전체 이관 (Mapper XML)"
    order:
      1: "Mapper XML (iBatis → MyBatis 변환)"
    gate: "Query Fidelity Gate (100% PASS 필수)"

  phase_2_java_generation:
    description: "Java 코드 생성 (Query 검증 후)"
    precondition: "Phase 1 Gate PASS"
    order:
      1: "Entity"
      2: "DTO (Request, Response)"
      3: "Mapper Interface"
      4: "Service"
      5: "Controller"

  # Legacy 참조용 (단일 Feature 작업 시 - 권장하지 않음)
  legacy_per_feature:
    deprecated: true
    note: "Feature별 작업 대신 Query 전체 선행 이관 전략 사용"
    order:
      1: "Entity"
      2: "DTO (Request, Response)"
      3: "Mapper Interface"
      4: "Mapper XML"
      5: "Service"
      6: "Controller"

ready_for_stage4: true
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| all_templates_created | structural | 6개 템플릿 모두 존재 | ERROR | Yes |
| naming_conventions_defined | content | 네이밍 규칙 완전 | ERROR | Yes |
| ibatis_mybatis_mapping | content | 변환 규칙 완전 | ERROR | Yes |
| yaml_syntax | structural | YAML 파싱 오류 없음 | ERROR | Yes |

### 5.2 Gate Criteria

```yaml
gate_criteria:
  id: "G3.5"
  name: "Generation Spec Gate"
  threshold: 70
  metrics:
    - metric: "all_templates_created"
      weight: 0.4
      target: "6"
      formula: "count of templates"
    - metric: "naming_conventions_defined"
      weight: 0.3
      target: "true"
    - metric: "ibatis_mybatis_mapping"
      weight: 0.3
      target: "complete"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Architecture not approved | 입력 없음 | S3-04 미승인 | Approval 대기 | Yes |
| Reference missing | 패턴 분석 실패 | Sample 프로젝트 부재 | Sample 생성 | No |
| Complex iBatis pattern | 변환 불가 | 비표준 구문 | 수동 규칙 추가 | Yes |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Template 생성 실패 | critical | 수동 템플릿 작성 | Tech Lead |
| 변환 규칙 누락 | major | 규칙 추가 | Developer |

---

## 7. Examples

### 7.1 Sample iBatis to MyBatis Conversion

**Input (iBatis):**
```xml
<sqlMap namespace="pa01001">
    <select id="selectList" parameterClass="PA01001MVO" resultClass="PA01001MVO">
        SELECT SITE_CD, YYYYMM, TOTAL_QTY
        FROM TB_PROD_PLAN
        WHERE 1=1
        <isNotNull property="siteCd">
            AND SITE_CD = #siteCd#
        </isNotNull>
        <isNotEmpty property="yyyymm">
            AND YYYYMM = #yyyymm#
        </isNotEmpty>
    </select>
</sqlMap>
```

**Output (MyBatis):**
```xml
<mapper namespace="com.hallain.pa.repository.PA01001Mapper">
    <select id="selectList" parameterType="PA01001SearchRequest" resultType="PA01001Entity">
        SELECT SITE_CD, YYYYMM, TOTAL_QTY
        FROM TB_PROD_PLAN
        WHERE 1=1
        <if test="siteCd != null">
            AND SITE_CD = #{siteCd}
        </if>
        <if test="yyyymm != null and yyyymm != ''">
            AND YYYYMM = #{yyyymm}
        </if>
    </select>
</mapper>
```

### 7.2 Sample Template Application

**Input (Feature Spec):**
```yaml
feature:
  screen_id: "PA01001"
  domain: "pa"
  table: "TB_PROD_PLAN"
  endpoints:
    - { path: "/list", method: "POST" }
    - { path: "/save", method: "POST" }
```

**Output (Generated Controller):**
- PA01001Controller.java (see example_output in template)

---

## Version History

### v1.2.0 (2026-01-09)
- **QUERY-FIRST 전략 (전체 선행 이관)** 반영
- Section 1.4: 2-Phase 분리 전략 추가 (STAGE A → B → C)
- RULE_PHASE_SEPARATION 추가 (Query 이관 → Gate → Java 생성)
- generation_order: 2-Phase 구조로 재구성
- MM0101051M 케이스 스터디 기반 재발 방지 전략

### v1.1.0 (2026-01-08)
- Step 6: Schema Validation 추가
- s3-05-generation-spec.schema.yaml 스키마 참조
- 11개 검증 규칙 적용 (V001-V011)

### v1.0.0 (2026-01-07)
- Initial version
- 6개 레이어 템플릿
- iBatis → MyBatis 변환 규칙
- 네이밍 컨벤션
