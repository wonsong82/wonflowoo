---
name: s3-04-preparation-architecture-design
description: Use when designing target Spring Boot architecture, defining package structures, establishing layer standards, or requiring human approval for architectural decisions before code generation (project)
---

# Architecture Design

> **Skill ID**: S3-04
> **Skill Type**: Generation (Target 아키텍처 설계)
> **Stage**: 3 - Preparation
> **Phase**: 3.4 - Architecture Design
> **HUMAN APPROVAL REQUIRED**: Yes

## 1. Overview

### 1.1 Purpose

마이그레이션 대상 시스템의 **Spring Boot 3.2 아키텍처**를 설계합니다. 패키지 구조, 레이어 표준, 컴포넌트 구성을 정의하여 Stage 4 코드 생성의 기준을 수립합니다.

**⚠️ CRITICAL: 이 Phase는 Human Approval 필수입니다.**

**생성 대상:**
- Package 구조 명세
- Layer 표준 문서
- Component 다이어그램
- 코딩 컨벤션

**사용 용도:**
- S4-01 Project Scaffold 기준
- S4-03 Domain Batch 코드 생성 가이드
- 개발팀 아키텍처 참조 문서

### 1.2 Design Scope

| Aspect | Included | Excluded |
|--------|----------|----------|
| Structure | Package layout, module structure | Business logic |
| Layers | Controller, Service, Repository | Domain algorithms |
| Patterns | DI, AOP, Transaction | UI patterns (API only) |
| Standards | Naming, annotations, exceptions | External system integration details |

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Spring Boot Standard** | Spring Boot 3.2 권장 패턴 준수 | 생태계 호환성, 유지보수성 |
| **Domain-Driven Package** | 도메인별 모듈 구조 | 명확한 경계, 병렬 개발 |
| **Layered Architecture** | Controller → Service → Repository | 관심사 분리, 테스트 용이 |
| **Reference Alignment** | next-hallain-sample 패턴 참조 | 일관성, 검증된 패턴 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S3-04는 Spring Boot 아키텍처를 설계하며, **MyBatis Mapper 구조가 Repository 계층 설계의 기초**

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s2-04-validation-spec-completion` | 완료된 Feature Spec |
| `s3-01-preparation-dependency-graph` | 도메인 의존성 그래프 |
| `s3-02-preparation-interface-extraction` | Cross-domain 인터페이스 |
| `s3-03-preparation-technical-debt` | 기술 부채 분석 (선택) |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s3-05-preparation-generation-spec` | 아키텍처 기반 코드 생성 템플릿 |
| `s4-01-generation-project-scaffold` | 프로젝트 구조 생성 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S2-04"
    skill_name: "s2-04-validation-spec-completion"
    dependency_type: "input"
    artifact: "completed specs"

  - skill_id: "S3-01"
    skill_name: "s3-01-preparation-dependency-graph"
    dependency_type: "input"
    artifact: "dependency-graph.yaml"

  - skill_id: "S3-02"
    skill_name: "s3-02-preparation-interface-extraction"
    dependency_type: "input"
    artifact: "cross-domain-contracts.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| validated_specs | directory | `work/specs/stage2-outputs/` | YAML | Yes |
| interface_specs | directory | `work/specs/stage3-outputs/phase2/` | YAML | Yes |
| reference_architecture | directory | `next-hallain-sample/` | Java/Gradle | Yes |
| dependency_graph | file | `work/specs/stage3-outputs/phase1/dependency-graph.yaml` | YAML | Yes |

### 2.3 Reference Architecture

**next-hallain-sample 구조:**
```
next-hallain-sample/
├── build.gradle.kts
├── settings.gradle.kts
├── src/
│   └── main/
│       ├── java/
│       │   └── com/hallain/
│       │       ├── HallainApplication.java
│       │       ├── common/
│       │       ├── config/
│       │       └── {domain}/
│       └── resources/
│           ├── application.yml
│           └── mapper/
└── src/test/
```

### 2.4 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Read | - | Reference 분석 |
| Write | - | 설계 문서 생성 |

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: sequential
  unit: project  # 단일 아키텍처 설계
  parallelization:
    enabled: false
  lifecycle:
    timeout_minutes: 240
    retry_on_failure: 2
  human_approval:
    required: true
    approvers: ["tech_lead", "architect"]
```

### 3.2 Design Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Analyze     │────▶│ Design       │────▶│ Document     │────▶│ Human        │
│  Reference   │     │ Structure    │     │ Standards    │     │ Approval     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 3.3 Process Steps

#### Step 1: Analyze Reference Architecture

**Description:** next-hallain-sample 구조 분석

**Sub-steps:**
1. Reference 프로젝트 구조 분석
2. 사용된 패턴/어노테이션 식별
3. 설정 파일 구조 분석
4. 테스트 구조 분석

**Analysis Points:**
```yaml
reference_analysis:
  build_tool: "Gradle Kotlin DSL"
  spring_version: "3.2.x"
  java_version: "17"
  layers:
    - controller: "@RestController, @RequestMapping"
    - service: "@Service, @Transactional"
    - repository: "@Repository, @Mapper"
    - dto: "record 또는 class"
  configurations:
    - "application.yml multi-profile"
    - "MyBatis configuration"
    - "Swagger/OpenAPI"
```

**Validation:** Reference 분석 완료

**Outputs:**
- Reference 분석 결과

---

#### Step 2: Design Package Structure

**Description:** 패키지 및 모듈 구조 설계

**Sub-steps:**
1. 루트 패키지 결정: `com.hallain`
2. 모듈 구조 결정: Monolith vs Multi-module
3. 도메인별 패키지 구조 정의
4. 공통 모듈 구조 정의

**Package Structure Decision:**
```yaml
structure_decision:
  approach: "monolithic"  # Strategy에서 결정됨
  rationale:
    - "기존 모놀리식 구조 유지"
    - "도메인 간 강결합 (12개 도메인)"
    - "점진적 분리 가능한 구조"

  package_layout:
    root: "com.hallain"
    domains:
      pattern: "com.hallain.{domain}"
      structure:
        - controller
        - service
        - repository
        - dto
        - entity
    common:
      pattern: "com.hallain.common"
      structure:
        - config
        - exception
        - provider
        - dto
        - util
```

**Validation:** 패키지 구조 설계 완료

---

#### Step 3: Define Layer Standards

**Description:** 각 레이어별 표준 정의

**Sub-steps:**
1. Controller 레이어 표준
2. Service 레이어 표준
3. Repository 레이어 표준
4. DTO/Entity 표준
5. Exception 표준

**Layer Standards:**
```yaml
layer_standards:
  controller:
    annotations:
      class: ["@RestController", "@RequestMapping", "@Tag"]
      method: ["@Operation", "@PostMapping/@GetMapping"]
    naming: "{Domain}{Screen}Controller"
    responsibilities:
      - "HTTP 요청/응답 처리"
      - "Request validation (@Valid)"
      - "Response 변환"
    prohibited:
      - "비즈니스 로직"
      - "직접 Repository 호출"

  service:
    annotations:
      class: ["@Service", "@Transactional"]
      method: ["@Transactional(readOnly=true) for read"]
    naming: "{Domain}{Function}Service"
    responsibilities:
      - "비즈니스 로직"
      - "트랜잭션 관리"
      - "도메인 간 조율"
    prohibited:
      - "HTTP 관련 로직"
      - "직접 SQL 실행"

  repository:
    annotations:
      class: ["@Repository", "@Mapper"]
    naming: "{Domain}{Entity}Mapper"
    responsibilities:
      - "데이터 접근"
      - "MyBatis SQL 매핑"
    prohibited:
      - "비즈니스 로직"
      - "트랜잭션 관리"
```

**Validation:** 모든 레이어 표준 정의 완료

---

#### Step 4: Document Standards

**Description:** 아키텍처 문서 생성

**Sub-steps:**
1. architecture-design.yaml 생성
2. layer-standards.md 생성
3. 컴포넌트 다이어그램 (선택)
4. Human Approval 체크리스트 포함

**Validation:** 문서 생성 완료

---

#### Step 5: Human Approval

**Description:** 아키텍처 승인 프로세스

**Approval Checklist:**
- [ ] Package structure follows company standards
- [ ] Layer separation is clean
- [ ] Cross-cutting concerns addressed
- [ ] Security integration points verified
- [ ] Performance considerations documented
- [ ] Reference architecture alignment confirmed

**Approvers:**
- Tech Lead (필수)
- Architect (필수)

**Approval Record:**
```yaml
approval_record:
  status: "PENDING|APPROVED|REJECTED"
  tech_lead:
    name: ""
    date: ""
    comments: ""
  architect:
    name: ""
    date: ""
    comments: ""
  conditions: []
```

---

### 3.4 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | Multi-module 필요 | 모듈 분리 설계 | Monolith 유지 |
| DP-2 | PA 도메인 크기 | Sub-package 분리 | 단일 패키지 |
| DP-3 | Interface 존재 | common.provider 포함 | 생략 |
| DP-4 | Approval 거부 | 수정 후 재제출 | 다음 Phase 진행 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage3-outputs/phase4/"

  structure:
    - "architecture-design.yaml"
    - "layer-standards.md"
    - "component-diagram.md"  # Optional
    - "approval-record.yaml"
```

### 4.2 Output Files

| File | Type | Purpose | Required |
|------|------|---------|----------|
| architecture-design.yaml | YAML | 아키텍처 설계 명세 | Yes |
| layer-standards.md | MD | 레이어별 표준 문서 | Yes |
| component-diagram.md | MD | 컴포넌트 다이어그램 | No |
| approval-record.yaml | YAML | Human Approval 기록 | Yes |

### 4.3 File Header

```yaml
# Generated by: s3-04-preparation-architecture-design
# Stage: 3 - Preparation
# Phase: 3.4 - Architecture Design
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
# HUMAN APPROVAL REQUIRED
```

### 4.4 Output Schemas

#### architecture-design.yaml

```yaml
# architecture-design.yaml
metadata:
  generated_by: "s3-04-preparation-architecture-design"
  generated_at: "2026-01-07T15:00:00Z"
  version: "1.0.0"
  status: "PENDING_APPROVAL"  # PENDING_APPROVAL, APPROVED, REJECTED

project:
  name: "hallain-tft"
  group_id: "com.hallain"
  artifact_id: "hallain-tft"
  version: "1.0.0-SNAPSHOT"
  java_version: "17"
  spring_boot_version: "3.2.x"

architecture:
  style: "Monolithic Layered Architecture"
  rationale:
    - "기존 모놀리식 구조 유지 (Strategy 결정)"
    - "12개 도메인 간 강결합 존재"
    - "점진적 분리 가능한 내부 구조"

package_structure:
  root: "com.hallain"

  application:
    package: "com.hallain"
    main_class: "HallainApplication"

  common:
    package: "com.hallain.common"
    sub_packages:
      - name: "config"
        purpose: "Spring configuration classes"
        examples: ["WebConfig", "MyBatisConfig", "SwaggerConfig"]
      - name: "exception"
        purpose: "Custom exceptions and handlers"
        examples: ["BusinessException", "GlobalExceptionHandler"]
      - name: "provider"
        purpose: "Cross-domain interfaces"
        examples: ["ProductionPlanProvider", "AuthorizationProvider"]
      - name: "dto"
        purpose: "Cross-domain DTOs"
        examples: ["ProductionPlanDTO", "RoleDTO"]
      - name: "util"
        purpose: "Utility classes"
        examples: ["DateUtils", "StringUtils"]
      - name: "annotation"
        purpose: "Custom annotations"
        examples: ["@CurrentUser", "@Auditable"]

  domains:
    pattern: "com.hallain.{domain}"
    domains:
      - id: "pa"
        full_name: "Production"
        sub_packages: ["controller", "service", "repository", "dto", "entity"]
        notes: "가장 큰 도메인, sub-package 고려"
      - id: "mm"
        full_name: "Materials"
        sub_packages: ["controller", "service", "repository", "dto", "entity"]
      - id: "sc"
        full_name: "Supply Chain"
        sub_packages: ["controller", "service", "repository", "dto", "entity"]
      - id: "sm"
        full_name: "System Management"
        sub_packages: ["controller", "service", "repository", "dto", "entity"]
      - id: "pe"
        full_name: "Personnel"
        sub_packages: ["controller", "service", "repository", "dto", "entity"]
      - id: "ea"
        full_name: "Enterprise Application"
        sub_packages: ["controller", "service", "repository", "dto", "entity"]
      - id: "sa"
        full_name: "Sales"
        sub_packages: ["controller", "service", "repository", "dto", "entity"]
      - id: "eb"
        full_name: "E-Board"
        sub_packages: ["controller", "service", "repository", "dto", "entity"]
      - id: "qm"
        full_name: "Quality Management"
        sub_packages: ["controller", "service", "repository", "dto", "entity"]
      - id: "bs"
        full_name: "Business Support"
        sub_packages: ["controller", "service", "repository", "dto", "entity"]
      - id: "cm"
        full_name: "Common Business"
        sub_packages: ["controller", "service", "repository", "dto", "entity"]

    domain_package_structure:
      controller:
        naming: "{Domain}{Screen}Controller"
        annotations: ["@RestController", "@RequestMapping", "@Tag"]
      service:
        naming: "{Domain}{Function}Service"
        annotations: ["@Service", "@Transactional"]
      repository:
        naming: "{Domain}{Entity}Mapper"
        annotations: ["@Repository", "@Mapper"]
      dto:
        naming: "{Entity}Request, {Entity}Response, {Entity}DTO"
        style: "Java Record (preferred) or Class"
      entity:
        naming: "{Entity}Entity"
        notes: "MyBatis용 VO (JPA Entity 아님)"

resource_structure:
  base: "src/main/resources"
  structure:
    - path: "application.yml"
      purpose: "Main configuration"
    - path: "application-{profile}.yml"
      purpose: "Profile-specific configs (local, dev, prod)"
    - path: "mapper/{domain}/*.xml"
      purpose: "MyBatis mapper XMLs per domain"
    - path: "messages/"
      purpose: "i18n message bundles"

configurations:
  spring_boot:
    - name: "WebMvcConfiguration"
      purpose: "Web MVC settings"
    - name: "MyBatisConfiguration"
      purpose: "MyBatis settings"
    - name: "SwaggerConfiguration"
      purpose: "OpenAPI documentation"
    - name: "SecurityConfiguration"
      purpose: "Security settings (SSO integration)"

  datasource:
    type: "HikariCP"
    database: "Oracle 11g XE"

  mybatis:
    config:
      map_underscore_to_camel_case: true
      default_statement_timeout: 30
    mapper_locations: "classpath:mapper/**/*.xml"

cross_cutting_concerns:
  exception_handling:
    strategy: "@ControllerAdvice + @ExceptionHandler"
    base_exception: "BusinessException"
    response_format:
      success: { code: 0, message: "Success", data: {} }
      error: { code: -1, message: "Error message", data: null }

  logging:
    framework: "SLF4J + Logback"
    pattern: "[%d{yyyy-MM-dd HH:mm:ss}] [%thread] %-5level %logger{36} - %msg%n"
    levels:
      root: "INFO"
      com.hallain: "DEBUG"

  validation:
    framework: "Jakarta Validation (@Valid)"
    custom_validators: "common.validation package"

  security:
    framework: "Spring Security"
    authentication: "SSO Integration (SAML)"
    authorization: "Method-level @PreAuthorize"

  transaction:
    manager: "DataSourceTransactionManager"
    default_behavior: "@Transactional on Service layer"
    read_only: "@Transactional(readOnly=true) for queries"

interface_integration:
  provider_interfaces:
    - interface: "ProductionPlanProvider"
      package: "com.hallain.common.provider"
      implemented_by: "com.hallain.pa.provider.PAProductionPlanProviderImpl"
      consumed_by: "com.hallain.mm.service.MMService"
    - interface: "AuthorizationProvider"
      package: "com.hallain.common.provider"
      implemented_by: "com.hallain.sm.provider.SMAuthorizationProviderImpl"
      consumed_by: "com.hallain.pe.service.PEService"

directory_structure:
  example: |
    hallain-tft/
    ├── build.gradle.kts
    ├── settings.gradle.kts
    ├── src/
    │   ├── main/
    │   │   ├── java/
    │   │   │   └── com/hallain/
    │   │   │       ├── HallainApplication.java
    │   │   │       ├── common/
    │   │   │       │   ├── config/
    │   │   │       │   ├── exception/
    │   │   │       │   ├── provider/
    │   │   │       │   ├── dto/
    │   │   │       │   └── util/
    │   │   │       ├── pa/
    │   │   │       │   ├── controller/
    │   │   │       │   ├── service/
    │   │   │       │   ├── repository/
    │   │   │       │   ├── dto/
    │   │   │       │   └── entity/
    │   │   │       ├── mm/
    │   │   │       │   └── ... (same structure)
    │   │   │       └── ... (other domains)
    │   │   └── resources/
    │   │       ├── application.yml
    │   │       ├── application-local.yml
    │   │       ├── application-dev.yml
    │   │       ├── application-prod.yml
    │   │       └── mapper/
    │   │           ├── pa/
    │   │           ├── mm/
    │   │           └── ...
    │   └── test/
    │       └── java/
    │           └── com/hallain/
    │               ├── common/
    │               └── {domain}/
    └── docker/
        └── docker-compose.yml

human_approval:
  required: true
  # S3-04 승인 시 S3-01, S3-02 산출물도 함께 검토
  approval_scope:
    - "S3-04: architecture-design.yaml, layer-standards.md"
    - "S3-01: dependency-graph.yaml, circular-dependencies.yaml"
    - "S3-02: interfaces/*.yaml, cross-domain-contracts.yaml"
  checklist:
    # S3-04 Architecture Design 검토
    - item: "Package structure follows company standards"
      status: "PENDING"
      scope: "S3-04"
    - item: "Layer separation is clean"
      status: "PENDING"
      scope: "S3-04"
    - item: "Cross-cutting concerns addressed"
      status: "PENDING"
      scope: "S3-04"
    - item: "Security integration points verified"
      status: "PENDING"
      scope: "S3-04"
    - item: "Performance considerations documented"
      status: "PENDING"
      scope: "S3-04"
    - item: "Reference architecture alignment confirmed"
      status: "PENDING"
      scope: "S3-04"
    # S3-01 Dependency Graph 검토 (함께 승인)
    - item: "All domain dependencies accurately mapped"
      status: "PENDING"
      scope: "S3-01"
    - item: "Circular dependency chains identified and resolution planned"
      status: "PENDING"
      scope: "S3-01"
    # S3-02 Interface Extraction 검토 (함께 승인)
    - item: "Interface contracts properly defined for circular dependency resolution"
      status: "PENDING"
      scope: "S3-02"
    - item: "Cross-domain DTOs designed without domain-specific dependencies"
      status: "PENDING"
      scope: "S3-02"
  approvers:
    tech_lead:
      required: true
      status: "PENDING"
    architect:
      required: true
      status: "PENDING"
```

#### layer-standards.md

```markdown
# Layer Standards

## 1. Controller Layer

### Annotations
- `@RestController` - REST API 컨트롤러
- `@RequestMapping("/api/{domain}/{screen}")` - 기본 경로
- `@Tag(name = "Screen Name")` - Swagger 문서화

### Naming Convention
- `{Domain}{Screen}Controller` (예: PA01001Controller)

### Responsibilities
- HTTP 요청/응답 처리
- Request validation (@Valid)
- Response 변환

### Example
```java
@RestController
@RequestMapping("/api/pa/pa01001")
@Tag(name = "PA01001 - 생산계획 관리")
@RequiredArgsConstructor
public class PA01001Controller {

    private final PA01001Service pa01001Service;

    @PostMapping("/list")
    @Operation(summary = "생산계획 목록 조회")
    public ApiResponse<List<PA01001Response>> getList(
            @Valid @RequestBody PA01001SearchRequest request) {
        return ApiResponse.success(pa01001Service.getList(request));
    }
}
```

### Prohibited
- 비즈니스 로직 직접 구현
- Repository 직접 호출
- 트랜잭션 관리

---

## 2. Service Layer

### Annotations
- `@Service` - 서비스 빈 등록
- `@Transactional` - 트랜잭션 관리
- `@Transactional(readOnly = true)` - 조회 전용

### Naming Convention
- `{Domain}{Function}Service` (예: PA01001Service)

### Responsibilities
- 비즈니스 로직 구현
- 트랜잭션 경계 관리
- 도메인 간 조율

### Example
```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PA01001Service {

    private final PA01001Mapper pa01001Mapper;

    public List<PA01001Response> getList(PA01001SearchRequest request) {
        return pa01001Mapper.selectList(request)
            .stream()
            .map(PA01001Response::from)
            .toList();
    }

    @Transactional
    public void save(List<PA01001SaveRequest> requests) {
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

---

## 3. Repository Layer

### Annotations
- `@Mapper` - MyBatis 매퍼
- `@Repository` - 필요시 추가

### Naming Convention
- `{Domain}{Entity}Mapper` (예: PA01001Mapper)

### Responsibilities
- 데이터 접근
- MyBatis SQL 매핑

### Example
```java
@Mapper
public interface PA01001Mapper {

    List<PA01001Entity> selectList(PA01001SearchRequest request);

    int selectCount(PA01001SearchRequest request);

    int insert(PA01001Entity entity);

    int update(PA01001Entity entity);

    int delete(String id);
}
```

---

## 4. DTO Standards

### Request DTO
```java
public record PA01001SearchRequest(
    @NotBlank String siteCd,
    String yyyymm,
    @Min(1) int pageNo,
    @Min(1) @Max(100) int pageSize
) {}
```

### Response DTO
```java
public record PA01001Response(
    String planId,
    String siteCd,
    String yyyymm,
    BigDecimal totalQty,
    LocalDateTime createdAt
) {
    public static PA01001Response from(PA01001Entity entity) {
        return new PA01001Response(
            entity.getPlanId(),
            entity.getSiteCd(),
            entity.getYyyymm(),
            entity.getTotalQty(),
            entity.getCreatedAt()
        );
    }
}
```

---

## 5. Exception Standards

### Base Exception
```java
public class BusinessException extends RuntimeException {
    private final ErrorCode errorCode;

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }
}
```

### Global Handler
```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ApiResponse<Void> handleBusiness(BusinessException e) {
        return ApiResponse.error(e.getErrorCode());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ApiResponse<Void> handleValidation(MethodArgumentNotValidException e) {
        return ApiResponse.error(ErrorCode.INVALID_INPUT);
    }
}
```
```

#### approval-record.yaml

```yaml
# approval-record.yaml
metadata:
  generated_by: "s3-04-preparation-architecture-design"
  generated_at: "2026-01-07T15:00:00Z"
  architecture_version: "1.0.0"

approval:
  status: "PENDING"  # PENDING, APPROVED, REJECTED, APPROVED_WITH_CONDITIONS

  checklist:
    - item: "Package structure follows company standards"
      status: "PENDING"
      reviewer_notes: ""

    - item: "Layer separation is clean"
      status: "PENDING"
      reviewer_notes: ""

    - item: "Cross-cutting concerns addressed"
      status: "PENDING"
      reviewer_notes: ""

    - item: "Security integration points verified"
      status: "PENDING"
      reviewer_notes: ""

    - item: "Performance considerations documented"
      status: "PENDING"
      reviewer_notes: ""

    - item: "Reference architecture alignment confirmed"
      status: "PENDING"
      reviewer_notes: ""

  approvers:
    tech_lead:
      required: true
      status: "PENDING"
      name: ""
      approved_at: ""
      comments: ""

    architect:
      required: true
      status: "PENDING"
      name: ""
      approved_at: ""
      comments: ""

  conditions: []

  history:
    - timestamp: "2026-01-07T15:00:00Z"
      action: "SUBMITTED"
      by: "AI"
      notes: "Initial architecture design submitted for review"
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| package_structure_defined | structural | architecture-design.yaml 생성 | ERROR | Yes |
| all_layers_specified | content | 5개 레이어 모두 정의 | ERROR | Yes |
| common_components_designed | content | config, exception, provider 포함 | ERROR | Yes |
| approval_record_created | structural | approval-record.yaml 생성 | ERROR | Yes |

### 5.2 Manual Reviews (REQUIRED)

| Review | Reviewer | Criteria | Required |
|--------|----------|----------|----------|
| Package structure | Architect | 회사 표준 준수 | **Yes** |
| Layer separation | Tech Lead | 관심사 분리 명확 | **Yes** |
| Security points | Architect | 보안 통합 지점 확인 | **Yes** |

### 5.3 Gate Criteria

```yaml
gate_criteria:
  id: "G3.4"
  name: "Architecture Design Gate"
  threshold: 70
  human_approval_required: true
  metrics:
    - metric: "package_structure_defined"
      weight: 0.2
      target: "true"
    - metric: "all_layers_specified"
      weight: 0.2
      target: "5 layers"
    - metric: "common_components_designed"
      weight: 0.2
      target: "true"
    - metric: "human_approval"
      weight: 0.4
      target: "APPROVED"
      type: "human_approval"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Reference missing | 분석 불가 | next-hallain-sample 부재 | Sample 프로젝트 생성 | No |
| Interface missing | provider 누락 | S3-02 미완료 | S3-02 완료 확인 | Yes |
| Approval rejected | 진행 불가 | 설계 문제 | 피드백 반영 수정 | Yes |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Design rejected | critical | 피드백 기반 재설계 | Tech Lead |
| Conflict with reference | major | 조율 미팅 | Architect |

### 6.3 Approval Process

```yaml
approval_process:
  submission:
    - Generate architecture-design.yaml
    - Generate layer-standards.md
    - Create approval-record.yaml with PENDING status

  review:
    - Tech Lead reviews package structure
    - Architect reviews overall design
    - Each reviewer updates checklist status

  decision:
    all_approved:
      - Update status to APPROVED
      - Record approval timestamps
      - Proceed to S3-05
    rejected:
      - Update status to REJECTED
      - Record rejection reasons
      - Return to Step 2 (Design)
    approved_with_conditions:
      - Update status to APPROVED_WITH_CONDITIONS
      - Record conditions
      - Apply conditions in S3-05
```

---

## 7. Examples

### 7.1 Sample Reference Analysis

**next-hallain-sample 분석 결과:**
```yaml
reference_analysis:
  patterns_identified:
    - pattern: "Controller layer uses @RestController"
    - pattern: "Service layer uses @Service + @Transactional"
    - pattern: "Repository uses @Mapper (MyBatis)"
    - pattern: "DTO uses Java Record"
    - pattern: "Response wrapper: ApiResponse<T>"
    - pattern: "Exception handling: @ControllerAdvice"
```

### 7.2 Sample Approval Flow

```yaml
approval_flow_example:
  step_1:
    action: "AI generates architecture design"
    output: "architecture-design.yaml, approval-record.yaml"

  step_2:
    action: "Tech Lead reviews"
    result: "APPROVED with comment: 'Add caching consideration'"

  step_3:
    action: "Architect reviews"
    result: "APPROVED"

  final:
    status: "APPROVED_WITH_CONDITIONS"
    conditions: ["Add Redis caching strategy in S3-05"]
```

---

## Version History

### v1.0.0 (2026-01-07)
- Initial version
- Spring Boot 3.2 아키텍처 설계
- Monolithic layered architecture
- Human approval workflow
