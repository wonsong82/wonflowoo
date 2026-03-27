---
name: s5-01-assurance-structural-check
description: Use when validating generated code against architecture standards, checking coding conventions from Stage 3 design, or identifying structural violations after code generation (project)
---

# Structural Check

> **Skill ID**: S5-01
> **Skill Type**: Validation (Limited Parallel)
> **Stage**: 5 - Assurance
> **Phase**: 5.1 - Structural Check
> **Parallelization**: Limited (max 5 sessions, batch 3 domains)
> **Architecture Reference**: Stage 3 Phase 4 Output

## 1. Overview

### 1.1 Purpose

생성된 코드가 **Stage 3에서 정의된 아키텍처 표준**을 준수하는지 검증합니다. 코딩 컨벤션, 패키지 구조, 어노테이션 사용 등 구조적 측면의 품질을 확인합니다.

**검증 대상:**
- Package Structure (layer-standards.md 기준)
- Naming Conventions (클래스명, 메서드명, 필드명)
- Annotation Usage (@RestController, @Service, @Mapper 등)
- Import Organization
- Code Style (Checkstyle 기반)

**검증 기준:**
- Stage 3-04: architecture-design.yaml
- Stage 3-05: generation-rules.yaml

### 1.2 Scope

**In Scope:**
- 패키지 구조 검증 (Controller, Service, Repository 분리)
- 클래스 명명 규칙 검증 ({Screen}Controller, {Screen}Service 등)
- 어노테이션 패턴 검증
- Import 문 정리 확인
- Checkstyle 규칙 적용

**Out of Scope:**
- 비즈니스 로직 검증 (-> S5-02)
- API 계약 검증 (-> S5-03)
- 성능 분석 (-> S5-04)

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Standard Compliance** | S3 아키텍처 설계 준수 | 일관성 보장 |
| **Automated Detection** | 정적 분석 도구 활용 | 객관적 검증 |
| **Auto-Remediation** | 간단한 위반은 자동 수정 | 효율성 |
| **Early Detection** | Assurance 첫 단계 | 조기 수정 가능 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S5-01은 구조 검증을 수행하며, **Mapper XML 구조 및 namespace 규칙 준수 검증**

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s4-05-generation-integration-build` | 생성 완료된 코드 필요 |
| `s3-04-preparation-architecture-design` | 아키텍처 기준 필요 |
| `s3-05-preparation-generation-spec` | 생성 규칙 필요 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s5-02-assurance-functional-validation` | 구조 검증 후 기능 검증 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S4-05"
    skill_name: "s4-05-generation-integration-build"
    status: "completed"
    artifacts:
      - "next-hallain/src/main/java/"
      - "Build success confirmed"

  - skill_id: "S3-04"
    skill_name: "s3-04-preparation-architecture-design"
    status: "completed"
    artifacts:
      - "architecture-design.yaml"
      - "layer-standards.md"

  - skill_id: "S3-05"
    skill_name: "s3-05-preparation-generation-spec"
    status: "completed"
    artifacts:
      - "generation-rules.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| generated_code | directory | `next-hallain/src/main/java/` | Java | Yes |
| architecture_design | file | `work/specs/stage3-outputs/phase4/architecture-design.yaml` | YAML | Yes |
| generation_rules | file | `work/specs/stage3-outputs/phase5/generation-rules.yaml` | YAML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Checkstyle | 10.x | 코드 스타일 검사 |
| SpotBugs | 4.x | 정적 분석 (선택) |
| Glob | - | 파일 패턴 검색 |
| Grep | - | 코드 검색 |

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
    batch_size: 3
    session_timeout_minutes: 120
    retry_on_failure: 2

task:
  naming_pattern: "STRUCT-{DOMAIN}"
  granularity: domain
```

### 3.2 Validation Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    STRUCTURAL CHECK PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐      │
│   │  Load    │────▶│ Package  │────▶│ Naming   │────▶│ Annot.   │      │
│   │ Standards│     │ Structure│     │ Rules    │     │ Usage    │      │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘      │
│                                                                         │
│                         │                │                │             │
│                         ▼                ▼                ▼             │
│                    ┌─────────────────────────────────────────┐          │
│                    │        Checkstyle Analysis              │          │
│                    └─────────────────────────────────────────┘          │
│                                         │                               │
│                                         ▼                               │
│                    ┌─────────────────────────────────────────┐          │
│                    │         Report Generation               │          │
│                    └─────────────────────────────────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Process Steps

#### Step 1: Load Architecture Standards

**Description:** Stage 3 아키텍처 표준 로드

**Sub-steps:**
1. `architecture-design.yaml` 로드
2. `generation-rules.yaml` 로드
3. `layer-standards.md` 파싱
4. 검증 규칙 추출

**Standards to Extract:**
```yaml
architecture_standards:
  package_structure:
    base: "com.hallain.{domain}"
    layers:
      - controller: "{base}/controller"
      - service: "{base}/service"
      - repository: "{base}/repository"
      - dto: "{base}/dto"
      - entity: "{base}/entity"
      - mapper: "{base}/mapper"

  naming_conventions:
    controller: "{Screen}Controller"
    service: "{Screen}Service"
    mapper: "{Screen}Mapper"
    dto_request: "{Screen}{Action}Request"
    dto_response: "{Screen}{Action}Response"
    entity: "{Screen}Entity"

  annotation_patterns:
    controller:
      class: ["@RestController", "@RequestMapping"]
      method: ["@PostMapping", "@GetMapping"]
    service:
      class: ["@Service", "@Transactional"]
    mapper:
      class: ["@Mapper"]
```

**Validation:** 표준 로드 완료

---

#### Step 2: Package Structure Check

**Description:** 패키지 구조가 아키텍처 표준을 준수하는지 검증

**Sub-steps:**
1. 도메인별 패키지 존재 확인
2. Layer 분리 확인 (controller/service/repository)
3. 계층 간 의존성 방향 확인
4. 불필요한 패키지 탐지

**Package Structure Rules:**
```yaml
structure_rules:
  - rule: "controller_separate"
    description: "Controller는 service만 의존"
    pattern: "controller/*.java"
    allowed_imports:
      - "service.*"
      - "dto.*"
    forbidden_imports:
      - "repository.*"
      - "entity.*"
      - "mapper.*"

  - rule: "service_separate"
    description: "Service는 repository만 의존"
    pattern: "service/*.java"
    allowed_imports:
      - "repository.*"
      - "mapper.*"
      - "dto.*"
      - "entity.*"
    forbidden_imports:
      - "controller.*"

  - rule: "no_circular"
    description: "순환 의존성 금지"
    check: "domain_to_domain_dependency"
```

**Validation:** 구조 위반 0개

---

#### Step 3: Naming Convention Check

**Description:** 클래스, 메서드, 필드 명명 규칙 검증

**Sub-steps:**
1. 클래스명 패턴 검증
2. 메서드명 패턴 검증
3. 필드명 패턴 검증
4. 상수명 패턴 검증

**Naming Patterns:**
```yaml
naming_rules:
  class_names:
    - pattern: ".*Controller$"
      location: "controller/"
      valid: true
    - pattern: ".*Service$"
      location: "service/"
      valid: true
    - pattern: ".*Mapper$"
      location: "mapper/"
      valid: true
    - pattern: ".*Request$|.*Response$"
      location: "dto/"
      valid: true

  method_names:
    - pattern: "^get[A-Z].*"
      type: "query"
    - pattern: "^save[A-Z].*"
      type: "mutation"
    - pattern: "^select[A-Z].*|^insert|^update|^delete"
      type: "mapper"

  field_names:
    - pattern: "^[a-z][a-zA-Z0-9]*$"
      type: "instance"
    - pattern: "^[A-Z][A-Z_0-9]*$"
      type: "constant"
```

**Validation:** 명명 위반 < 10

---

#### Step 4: Annotation Usage Check

**Description:** Spring/MyBatis 어노테이션 사용 패턴 검증

**Sub-steps:**
1. Controller 어노테이션 확인
2. Service 어노테이션 확인
3. Mapper 어노테이션 확인
4. 누락된 어노테이션 탐지

**Annotation Rules:**
```yaml
annotation_rules:
  controller:
    required_class:
      - "@RestController"
      - "@RequestMapping"
    required_method:
      - "@PostMapping|@GetMapping|@PutMapping|@DeleteMapping"

  service:
    required_class:
      - "@Service"
    optional_class:
      - "@Transactional"
    required_method: []

  mapper:
    required_class:
      - "@Mapper"
```

**Validation:** 어노테이션 위반 0개

---

#### Step 5: Checkstyle Analysis

**Description:** Checkstyle 도구를 통한 코드 스타일 검사

**Sub-steps:**
1. Checkstyle 설정 로드
2. 도메인별 검사 실행
3. 위반 사항 수집
4. 심각도 분류

**Checkstyle Categories:**
```yaml
checkstyle_checks:
  critical:
    - "MissingJavadocMethod"  # Public API
    - "UnusedImports"
    - "IllegalImport"

  major:
    - "MagicNumber"
    - "ParameterNumber"
    - "LineLength"

  minor:
    - "Indentation"
    - "WhitespaceAround"
```

**Validation:** Critical 위반 0개

---

#### Step 6: Report Generation

**Description:** 구조 검증 리포트 생성

**Sub-steps:**
1. 위반 항목 집계
2. 심각도별 분류
3. 도메인별 요약
4. 자동 수정 가능 항목 식별

**Validation:** 리포트 생성 완료

---

#### Step 6: Schema Validation

**Description:** 생성된 structural-report.yaml이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | root | metadata, summary, by_domain, gate_evaluation 필수 키 존재 | ERROR | Yes |
| V002 | metadata.generated_by | 정확히 "s5-01-assurance-structural-check" | ERROR | Yes |
| V003 | summary.result | enum: PASS, CONDITIONAL, FAIL | ERROR | Yes |
| V004 | violations[].category | enum: package_structure, naming_convention, annotation_usage, import_organization, code_style | ERROR | Yes |
| V005 | violations[].severity | enum: error, warning, info | ERROR | Yes |
| V006 | gate_evaluation.gate_id | 정확히 "G5.1" | ERROR | Yes |
| V007 | summary.compliance_rate | 범위: 0-100 | ERROR | Yes |
| V008 | violations | violations.length == total_violations | WARNING | No |
| V009 | result | PASS 시 compliance_rate >= 95% | ERROR | Yes |
| V010 | by_domain | 도메인별 violations 합계 == total_violations | WARNING | No |

**Sub-steps:**
1. structural-report.yaml 스키마 검증
2. Gate 결과 일관성 검증
3. 오류 발생 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재검증 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.4 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | 표준 로드 성공 | Step 2 진행 | ERROR 종료 |
| DP-2 | 구조 위반 발견 | 위반 기록 | 통과 |
| DP-3 | 자동 수정 가능 | 자동 수정 실행 | 수동 수정 필요 기록 |
| DP-4 | Error = 0 | Gate 통과 | 수정 후 재검증 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage5-outputs/phase1/"
    pattern: "{Domain}/"  # Per workflow convention

  artifacts:
    root_level:
      - name: "structural-report.yaml"
        required: true
        description: "Aggregated summary across all domains"
    per_domain:
      pattern: "{Domain}/"
      files:
        - name: "structural-report.yaml"
          required: true
        - name: "checkstyle-report.xml"
          required: false
        - name: "spotbugs-report.xml"
          required: false
```

### 4.2 Output Files Summary

```
work/specs/stage5-outputs/phase1/
├── structural-report.yaml       # 전체 요약 (aggregated)
├── PA/
│   ├── structural-report.yaml   # PA 도메인 상세
│   ├── checkstyle-report.xml
│   └── spotbugs-report.xml
├── MM/
│   ├── structural-report.yaml   # MM 도메인 상세
│   ├── checkstyle-report.xml
│   └── spotbugs-report.xml
└── ...
```

### 4.3 Output Schema

```yaml
# structural-report.yaml
metadata:
  generated_by: "s5-01-assurance-structural-check"
  generated_at: "${TIMESTAMP}"
  architecture_ref: "work/specs/stage3-outputs/phase4/architecture-design.yaml"

summary:
  total_files_checked: 1500
  total_violations: 25
  by_severity:
    error: 0
    warning: 15
    info: 10
  by_category:
    package_structure: 3
    naming_convention: 8
    annotation_usage: 5
    code_style: 9

by_domain:
  PA:
    files_checked: 450
    violations: 8
    errors: 0
    warnings: 5
    infos: 3
  MM:
    files_checked: 200
    violations: 5
    errors: 0
    warnings: 3
    infos: 2
  # ...

violations:
  - id: "STRUCT-001"
    severity: "warning"
    category: "naming_convention"
    file: "next-hallain/src/main/java/com/hallain/pa/service/PA01001Svc.java"
    line: 1
    rule: "class_naming"
    message: "Service class should end with 'Service', not 'Svc'"
    auto_fix: true
    suggested_fix: "Rename to PA01001Service"

  - id: "STRUCT-002"
    severity: "warning"
    category: "package_structure"
    file: "next-hallain/src/main/java/com/hallain/mm/controller/MM01001Controller.java"
    line: 15
    rule: "layer_dependency"
    message: "Controller should not import entity directly"
    auto_fix: false
    suggested_fix: "Use DTO instead of Entity in controller"

auto_remediation:
  performed: true
  fixes_applied: 8
  fixes_skipped: 2
  reason_skipped:
    - "Requires manual review: structural change"

result: "PASS"  # PASS | CONDITIONAL | FAIL
gate_score: 85
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| no_structural_errors | metric | errors == 0 | FAIL | Yes |
| warnings_acceptable | metric | warnings < 10 per domain | WARNING | No |
| checkstyle_passes | structural | No Checkstyle errors | FAIL | Yes |
| naming_compliance | metric | compliance >= 95% | WARNING | No |

### 5.2 Gate Criteria

```yaml
gate_criteria:
  id: "G5.1"
  name: "Structural Check Gate"
  threshold: 70
  metrics:
    - metric: "no_structural_errors"
      weight: 0.5
      target: "errors == 0"
      blocking: true
    - metric: "warnings_acceptable"
      weight: 0.3
      target: "warnings < 10/domain"
      blocking: false
    - metric: "checkstyle_passes"
      weight: 0.2
      target: "No critical violations"
      blocking: true
  on_pass:
    auto_commit: true
    message: "feat(S5-P5.1): Structural check passed"
  on_fail:
    action: "auto_remediate"
    remediation_types:
      - "naming_fixes"
      - "annotation_additions"
      - "import_cleanup"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Checkstyle config missing | Config not found | 설정 파일 누락 | 기본 설정 사용 | Yes |
| Large codebase timeout | Timeout | 파일 수 과다 | 배치 크기 축소 | Yes |
| False positive | 정상 패턴 위반 보고 | 예외 케이스 | 화이트리스트 추가 | No |

### 6.2 Auto-Remediation

| Violation Type | Auto-Fix | Method |
|----------------|----------|--------|
| Import cleanup | Yes | Organize imports |
| Naming simple fix | Yes | Rename (no reference) |
| Missing annotation | Yes | Add annotation |
| Layer violation | No | Manual refactoring |
| Complex naming | No | Manual review |

### 6.3 Escalation

| Condition | Action | Notify |
|-----------|--------|--------|
| Error >= 1 | Gate 실패 | Tech Lead |
| Warning >= 20 | 리뷰 요청 | Developer |
| Auto-fix 실패 | 수동 수정 | Developer |

---

## 7. Examples

### 7.1 Sample Structural Report

```yaml
# PA/structural-report.yaml (per-domain report)
domain: "PA"
checked_at: "2026-01-07T14:30:00Z"

packages:
  controller:
    expected: "com.hallain.pa.controller"
    found: true
    files: 45
  service:
    expected: "com.hallain.pa.service"
    found: true
    files: 45
  mapper:
    expected: "com.hallain.pa.mapper"
    found: true
    files: 45

naming_compliance:
  controllers: 100%
  services: 98%  # 1 violation
  mappers: 100%
  dtos: 95%  # 2 violations

violations:
  - file: "PA02003Svc.java"
    rule: "service_naming"
    current: "PA02003Svc"
    expected: "PA02003Service"
    auto_fixed: true

layer_dependencies:
  valid: true
  checked_files: 135
  violations: 0

checkstyle:
  errors: 0
  warnings: 3
  details:
    - rule: "LineLength"
      count: 2
    - rule: "MagicNumber"
      count: 1
```

### 7.2 Checkstyle Configuration Example

```xml
<!-- checkstyle.xml -->
<?xml version="1.0"?>
<!DOCTYPE module PUBLIC "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN"
    "https://checkstyle.org/dtds/configuration_1_3.dtd">
<module name="Checker">
    <module name="TreeWalker">
        <!-- Naming -->
        <module name="TypeName">
            <property name="format" value="^[A-Z][a-zA-Z0-9]*$"/>
        </module>
        <module name="MethodName">
            <property name="format" value="^[a-z][a-zA-Z0-9]*$"/>
        </module>

        <!-- Imports -->
        <module name="UnusedImports"/>
        <module name="IllegalImport"/>

        <!-- Size -->
        <module name="LineLength">
            <property name="max" value="150"/>
        </module>
    </module>
</module>
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| Legacy 명명 | 기존 명명 패턴 | 예외 허용 목록 |
| Cross-domain util | 공용 유틸리티 | common 패키지 허용 |
| Generated code marker | AI 생성 주석 | 무시 |

---

## 8. Checkstyle Configuration Details

### 8.1 Configuration Structure

```yaml
checkstyle_configuration:
  version: "10.x"
  config_files:
    - name: "checkstyle-main.xml"
      description: "메인 소스 코드 검사"
      target: "src/main/java/**/*.java"

    - name: "checkstyle-test.xml"
      description: "테스트 코드 검사 (완화된 규칙)"
      target: "src/test/java/**/*.java"

    - name: "checkstyle-suppressions.xml"
      description: "예외 처리 목록"
      target: "All"
```

### 8.2 Layer-Specific Rules

```xml
<!-- checkstyle-main.xml -->
<?xml version="1.0"?>
<!DOCTYPE module PUBLIC "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN"
    "https://checkstyle.org/dtds/configuration_1_3.dtd">

<module name="Checker">
    <property name="charset" value="UTF-8"/>
    <property name="severity" value="warning"/>

    <module name="FileLength">
        <property name="max" value="500"/>
    </module>

    <module name="TreeWalker">
        <!-- CONTROLLER LAYER RULES -->
        <module name="TypeName">
            <property name="format" value="^[A-Z][a-zA-Z0-9]*Controller$"/>
            <property name="tokens" value="CLASS_DEF"/>
        </module>

        <!-- SERVICE LAYER RULES -->
        <module name="Regexp">
            <property name="format" value="public\s+\w+Entity\s+\w+\("/>
            <property name="illegalPattern" value="true"/>
            <property name="message" value="Service should return DTO, not Entity"/>
        </module>

        <!-- IMPORT ORGANIZATION -->
        <module name="ImportOrder">
            <property name="groups" value="java,javax,jakarta,org.springframework,com.hallain"/>
            <property name="ordered" value="true"/>
            <property name="separated" value="true"/>
        </module>

        <module name="UnusedImports"/>
        <module name="IllegalImport">
            <property name="illegalPkgs" value="sun, com.sun"/>
        </module>

        <!-- CODE COMPLEXITY -->
        <module name="MethodLength">
            <property name="max" value="50"/>
        </module>
        <module name="ParameterNumber">
            <property name="max" value="7"/>
        </module>
        <module name="CyclomaticComplexity">
            <property name="max" value="10"/>
        </module>

        <!-- SPRING-SPECIFIC -->
        <module name="Regexp">
            <property name="format" value="@Autowired\s+private"/>
            <property name="illegalPattern" value="true"/>
            <property name="message" value="Use constructor injection instead of field injection"/>
        </module>

        <!-- LINE LENGTH -->
        <module name="LineLength">
            <property name="max" value="150"/>
            <property name="ignorePattern" value="^package.*|^import.*"/>
        </module>
    </module>
</module>
```

### 8.3 Custom Checks

```yaml
custom_checks:
  layer_dependency:
    name: "LayerDependencyCheck"
    description: "계층 간 의존성 방향 검증"
    rules:
      - layer: "controller"
        can_import: ["service", "dto"]
        cannot_import: ["repository", "mapper", "entity"]
        violation_severity: "error"

      - layer: "service"
        can_import: ["repository", "mapper", "dto", "entity"]
        cannot_import: ["controller"]
        violation_severity: "error"

      - layer: "mapper"
        can_import: ["entity"]
        cannot_import: ["controller", "service", "dto"]
        violation_severity: "error"

  annotation_presence:
    name: "RequiredAnnotationCheck"
    rules:
      - class_pattern: ".*Controller$"
        required: ["@RestController", "@RequestMapping"]
      - class_pattern: ".*Service$"
        required: ["@Service"]
      - class_pattern: ".*Mapper$"
        required: ["@Mapper"]
```

### 8.4 Suppressions Configuration

```xml
<!-- checkstyle-suppressions.xml -->
<?xml version="1.0"?>
<!DOCTYPE suppressions PUBLIC
    "-//Checkstyle//DTD SuppressionFilter Configuration 1.2//EN"
    "https://checkstyle.org/dtds/suppressions_1_2.dtd">

<suppressions>
    <!-- Generated code -->
    <suppress files=".*Generated.*\.java" checks=".*"/>

    <!-- Entity/DTO can have many fields -->
    <suppress files=".*Entity\.java" checks="TooManyFields"/>
    <suppress files=".*(Request|Response)\.java" checks="TooManyFields"/>

    <!-- Test classes relaxed rules -->
    <suppress files=".*Test\.java" checks="MethodLength"/>
    <suppress files=".*Test\.java" checks="LineLength"/>

    <!-- Legacy migration (temporary) -->
    <suppress files=".*legacy.*" checks=".*"/>
</suppressions>
```

### 8.5 Auto-Fix Mapping

```yaml
auto_fix_mapping:
  fixable_rules:
    - rule: "UnusedImports"
      action: "Remove unused import statements"
      tool: "IDE or checkstyle-fix"

    - rule: "ImportOrder"
      action: "Reorder imports"
      tool: "google-java-format"

    - rule: "WhitespaceAround"
      action: "Fix whitespace"
      tool: "spotless"

    - rule: "MissingOverride"
      action: "Add @Override annotation"
      tool: "IDE quick-fix"

  manual_review_rules:
    - rule: "MethodLength"
      reason: "Method extraction requires logic understanding"
      review_by: "Developer"

    - rule: "CyclomaticComplexity"
      reason: "Logic simplification requires design decision"
      review_by: "Developer + Tech Lead"

    - rule: "LayerDependencyCheck"
      reason: "Architecture violation requires design review"
      review_by: "Architect"
```

### 8.6 Build Integration

```kotlin
// build.gradle.kts
plugins {
    id("checkstyle")
}

checkstyle {
    toolVersion = "10.12.5"
    configFile = file("config/checkstyle/checkstyle-main.xml")
    configProperties = mapOf(
        "suppressionFile" to file("config/checkstyle/checkstyle-suppressions.xml").absolutePath,
        "basePackage" to "com.hallain"
    )
    isIgnoreFailures = false
    maxWarnings = 50
    maxErrors = 0
}

tasks.withType<Checkstyle> {
    reports {
        xml.required.set(true)
        html.required.set(true)
    }
}

tasks.named<Checkstyle>("checkstyleTest") {
    configFile = file("config/checkstyle/checkstyle-test.xml")
    maxWarnings = 100
}
```

---

## Version History

### v1.2.0 (2026-01-08)
- Step 6: Schema Validation 추가
- s5-01-structural-check.schema.yaml 스키마 참조
- 10개 검증 규칙 적용 (V001-V010)

### v1.1.0 (2026-01-07)
- **Checkstyle Configuration Details 추가** (Section 8)
  - Layer-specific rules (Controller, Service, Mapper)
  - Custom checks (LayerDependencyCheck, AnnotationPresenceCheck)
  - Suppressions configuration
  - Auto-fix mapping (fixable vs manual review)
  - Build integration (Gradle)

### v1.0.0 (2026-01-07)
- Initial version
- Package structure validation
- Naming convention check
- Annotation usage validation
- Checkstyle integration
- Auto-remediation support
