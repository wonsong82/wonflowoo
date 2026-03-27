---
name: s4-05-generation-integration-build
description: Use when integrating all generated code into a buildable artifact, running final build verification after code and test generation, or executing Stage 4 gate validation before advancing to Stage 5 (project)
---

# Integration Build

> **Skill ID**: S4-05
> **Skill Type**: Integration (Sequential - Stage Gate)
> **Stage**: 4 - Generation
> **Phase**: 4.5 - Integration Build
> **Wait For**: Phase 4.3, Phase 4.4

## 1. Overview

### 1.1 Purpose

Phase 4.3과 4.4에서 생성된 **모든 코드와 테스트를 통합**하고 **빌드 가능한 아티팩트**를 생성합니다. Stage 4의 **최종 Gate**로서 Stage 5 진입 조건을 검증합니다.

**통합 대상:**
- 모든 도메인의 생성 코드
- 모든 생성된 테스트
- Configuration 파일

**검증 항목:**
- 전체 빌드 성공
- 테스트 Pass Rate >= 80%
- 코드 커버리지 >= 80%
- 컴파일 오류 0개

### 1.2 Scope

**In Scope:**
- 전체 Gradle 빌드 실행
- 테스트 실행 및 리포트 생성
- JaCoCo 커버리지 리포트
- Stage Gate 판정
- 빌드 아티팩트 생성

**Out of Scope:**
- 코드 생성 (→ S4-03)
- 테스트 생성 (→ S4-04)
- 품질 검증 (→ S5)
- 배포 (→ CI/CD)

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Wait for Completion** | 4.3, 4.4 완료 대기 | 전체 통합 필요 |
| **Full Build** | 전체 프로젝트 빌드 | 통합 검증 |
| **Quality Gate** | 엄격한 Gate 기준 | Stage 5 품질 보장 |
| **Fail Recovery** | 단계별 복구 전략 | 빌드 실패 대응 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S4-05는 통합 빌드를 수행하며, **Mapper XML 컴파일 및 SQL 구문 검증이 빌드 성공 조건**

### 1.5 Relationships

**Wait For:**
| Phase | Required Condition |
|-------|-------------------|
| Phase 4.3 | generation-progress.yaml: 100% completed |
| Phase 4.4 | test-progress.yaml: 100% completed |

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s4-03-generation-domain-batch` | 전체 코드 생성 완료 |
| `s4-04-generation-test-generation` | 전체 테스트 생성 완료 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s5-01-assurance-structural-check` | Stage 5 시작 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S4-03"
    skill_name: "s4-03-generation-domain-batch"
    status: "completed"
    gate_passed: "G4.3"
    artifacts:
      - "generation-progress.yaml"
      - "100% features generated"

  - skill_id: "S4-04"
    skill_name: "s4-04-generation-test-generation"
    status: "completed"
    gate_passed: "G4.4"
    artifacts:
      - "test-progress.yaml"
      - "All tests generated"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| project | directory | `next-hallain/` | Java/Gradle | Yes |
| generation_progress | file | `work/specs/stage4-outputs/phase3/generation-progress.yaml` | YAML | Yes |
| test_progress | file | `work/specs/stage4-outputs/phase4/test-progress.yaml` | YAML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Bash | - | Gradle 빌드 실행 |
| Read | - | Progress 파일 읽기 |
| Write | - | 리포트 생성 |

**Build Requirements:**
- Java 17
- Gradle 8.x
- 충분한 메모리 (대형 프로젝트)

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: sequential
  unit: project
  parallelization:
    enabled: false
  lifecycle:
    timeout_minutes: 240
    retry_on_failure: 3

task:
  naming_pattern: "BUILD-{WAVE}"
  granularity: project
```

### 3.2 Build Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Verify     │────▶│    Clean     │────▶│    Build     │────▶│    Test      │
│   Readiness  │     │    Project   │     │    Project   │     │    Execute   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
        │                                                              │
        │                                                              ▼
        │                                        ┌──────────────────────────────┐
        │                                        │        Generate Reports      │
        │                                        │  - Test Report               │
        │                                        │  - Coverage Report           │
        │                                        │  - Build Artifact            │
        │                                        └──────────────┬───────────────┘
        │                                                       │
        │                                                       ▼
        │                                        ┌──────────────────────────────┐
        │                                        │       Stage Gate Check       │
        │                                        │  - Build Success?            │
        │                                        │  - Test Pass >= 80%?         │
        │                                        │  - Coverage >= 80%?          │
        │                                        └──────────────┬───────────────┘
        │                                                       │
        │                    ┌────────────┬─────────────────────┤
        │                    │            │                     │
        │                    ▼            ▼                     ▼
        │              ┌─────────┐  ┌─────────┐           ┌─────────┐
        │              │  PASS   │  │ CONDIT. │           │  FAIL   │
        │              │         │  │  PASS   │           │         │
        │              └────┬────┘  └────┬────┘           └────┬────┘
        │                   │            │                     │
        │                   ▼            ▼                     ▼
        │              Advance to   Remediation           Escalation
        │              Stage 5      + Proceed             Strategy
        │                                                      │
        └──────────────────────────────────────────────────────┘
```

### 3.3 Process Steps

#### Step 1: Verify Readiness

**Description:** 4.3, 4.4 완료 상태 확인

**Sub-steps:**
1. generation-progress.yaml 로드
2. test-progress.yaml 로드
3. 100% 완료 확인
4. 실패 항목 확인

**Readiness Check:**
```yaml
readiness_check:
  generation_progress:
    file: "work/specs/stage4-outputs/phase3/generation-progress.yaml"
    required:
      completion_percentage: 100
      ready_for_integration: true

  test_progress:
    file: "work/specs/stage4-outputs/phase4/test-progress.yaml"
    required:
      tests_generated: "all"
      ready_for_integration: true
```

**Validation:** 모든 전제조건 충족

---

#### Step 2: Clean Build

**Description:** 이전 빌드 아티팩트 정리

**Sub-steps:**
1. `./gradlew clean` 실행
2. build/ 디렉토리 삭제 확인
3. 캐시 정리 (필요 시)

**Commands:**
```bash
cd backend
./gradlew clean --info
rm -rf build/
```

**Validation:** 클린 상태 확인

---

#### Step 3: Compile Project

**Description:** 전체 프로젝트 컴파일

**Sub-steps:**
1. `./gradlew compileJava` 실행
2. 컴파일 오류 수집
3. 오류 분석 및 수정 시도

**Commands:**
```bash
cd backend
./gradlew compileJava --info 2>&1 | tee compile.log
```

**On Compile Error:**
```yaml
compile_error_handling:
  actions:
    - name: "Parse and categorize errors"
      description: "컴파일 오류 파싱 및 분류"
      extract: ["file_path", "line_number", "error_type", "error_message"]

    - name: "Apply auto-fix rules"
      description: "Auto-Fix Rule Engine 적용"
      reference: "Section 3.6 - Auto-Fix Rule Engine"
      categories:
        - auto_fixable: "즉시 자동 수정"
        - conditional_fix: "조건부 자동 수정"
        - regeneration_required: "Spec 기반 재생성"
        - escalate: "사람 개입 필요"

    - name: "Retry compilation"
      max_attempts: 3
      per_attempt_timeout: 10m
```

**Validation:** 컴파일 성공 (0 errors)

---

#### Step 4: Run Tests

**Description:** 전체 테스트 실행

**Sub-steps:**
1. `./gradlew test` 실행
2. 테스트 결과 수집
3. Pass Rate 계산
4. 실패 테스트 분석

**Commands:**
```bash
cd backend
./gradlew test --info 2>&1 | tee test.log
```

**Test Result Analysis:**
```yaml
test_analysis:
  report_path: "build/reports/tests/test/index.html"
  metrics:
    - total_tests
    - passed_tests
    - failed_tests
    - skipped_tests
    - pass_rate

  on_failure:
    - "Collect failed test details"
    - "Categorize failure types"
    - "Attempt auto-fix if possible"
```

**Validation:** Pass Rate >= 80%

---

#### Step 5: Generate Coverage Report

**Description:** JaCoCo 코드 커버리지 리포트 생성

**Sub-steps:**
1. `./gradlew jacocoTestReport` 실행
2. 커버리지 결과 수집
3. 패키지별 커버리지 분석

**Commands:**
```bash
cd backend
./gradlew jacocoTestReport
```

**Coverage Report:**
```yaml
coverage_report:
  report_path: "build/reports/jacoco/test/html/index.html"
  xml_path: "build/reports/jacoco/test/jacocoTestReport.xml"
  metrics:
    - line_coverage
    - branch_coverage
    - instruction_coverage
  threshold: 80%
```

**Validation:** Line Coverage >= 80%

---

#### Step 6: Build Artifact

**Description:** 최종 빌드 아티팩트 생성

**Sub-steps:**
1. `./gradlew build` 실행
2. JAR 파일 생성 확인
3. 아티팩트 무결성 검증

**Commands:**
```bash
cd backend
./gradlew build -x test  # 테스트는 이미 실행됨
```

**Build Artifacts:**
```yaml
artifacts:
  jar:
    path: "build/libs/hallain-backend-1.0.0-SNAPSHOT.jar"
    required: true

  reports:
    - "build/reports/tests/test/"
    - "build/reports/jacoco/test/"
```

**Validation:** JAR 파일 생성 완료

---

#### Step 7: Stage Gate Decision

**Description:** Stage 4 Gate 통과/실패 판정

**Gate Criteria:**
```yaml
stage_gate_criteria:
  id: "G-S4"
  name: "Stage 4 Gate"

  checks:
    - name: "build_succeeds"
      rule: "./gradlew build succeeds without errors"
      blocking: true

    - name: "test_pass_rate"
      rule: "Test report shows >= 80% pass rate"
      threshold: 80
      blocking: true

    - name: "no_compile_errors"
      rule: "Zero compilation errors"
      blocking: true

    - name: "code_coverage"
      rule: "JaCoCo report shows >= 80% line coverage"
      threshold: 80
      blocking: true
```

**Decision Matrix:**
```yaml
decision_matrix:
  PASS:
    conditions:
      - build_succeeds: true
      - test_pass_rate: ">= 80%"
      - no_compile_errors: true
      - code_coverage: ">= 80%"
    actions:
      - auto_commit: true
      - message: "feat(S4-P4.5): Integration build successful"
      - tag: "wave-{N}-rc1"
      - advance_to: "Stage 5"

  CONDITIONAL_PASS:
    conditions:
      - build_succeeds: true
      - test_pass_rate: "70-79%"
      - no_compile_errors: true
      - code_coverage: "70-79%"
    actions:
      - remediation_plan: true
      - deadline: "1 week"
      - advance_to: "Stage 5 (with conditions)"

  FAIL:
    conditions:
      - build_succeeds: false
      - OR test_pass_rate: "< 70%"
      - OR compile_errors: "> 0"
      - OR code_coverage: "< 70%"
    actions:
      - escalation: true
      - notify: ["Tech Lead", "Architect"]
      - block_stage_5: true
```

**Validation:** Gate 판정 완료

---

### 3.4 Failure Recovery

**On Build Failure:**
```yaml
on_fail_escalation:
  - retry: 1
    action: "auto_fix_compilation_errors"
    description: "Auto-Fix Rule Engine 적용 (Section 3.6 참조)"
    steps:
      - "Parse compile errors → structured_error_list.yaml"
      - "Categorize by severity (auto_fixable → escalate)"
      - "Apply auto-fixable and conditional fixes"
      - "Recompile to verify"
    expected_fix_rate: "> 80%"

  - retry: 2
    action: "regenerate_failing_components"
    description: "Spec 기반 재생성"
    steps:
      - "Identify regeneration_required errors"
      - "Load Feature Specs for affected features"
      - "Regenerate affected layers (Entity → Controller)"
      - "Re-apply auto-fix for new code"
    triggers:
      - "Missing method errors"
      - "Interface mismatch"
      - "Mapper-XML sync issues"

  - retry: 3
    action: "escalate_to_human"
    description: "Tech Lead에게 에스컬레이션"
    conditions:
      - "Auto-fix success rate < 50%"
      - "Circular dependency detected"
      - "Architectural issues identified"
    deliverables:
      - "auto-fix-report.yaml"
      - "escalated_issues list"
      - "Recommended manual fixes"
```

**Retry Decision Matrix:**
```yaml
retry_decision:
  after_retry_1:
    if_compile_errors_reduced: "> 50%"
      action: "Continue to retry 2"
    else:
      action: "Skip to retry 3 (escalate)"

  after_retry_2:
    if_compile_success: true
      action: "Proceed to test execution"
    else:
      action: "Proceed to retry 3 (escalate)"

  after_retry_3:
    action: "Block build, notify Tech Lead"
    output: "Build failure report with escalated issues"
```

#### Step 8: Schema Validation

**Description:** 생성된 빌드 리포트 및 자동 수정 리포트가 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | integration-build-report.yaml root | metadata, build_status, compile_result, test_result, coverage_result, gate_decision 필수 키 존재 | ERROR | Yes |
| V002 | auto-fix-report.yaml root | metadata, summary, by_category 필수 키 존재 | ERROR | Yes |
| V003 | metadata.generated_by | 정확히 "s4-05-generation-integration-build" | ERROR | Yes |
| V004 | metadata.generated_by (autofix) | 정확히 "s4-05-auto-fix-engine" | ERROR | Yes |
| V005 | build_status | enum: SUCCESS, CONDITIONAL, FAIL | ERROR | Yes |
| V006 | gate_decision.result | enum: PASS, CONDITIONAL_PASS, FAIL | ERROR | Yes |
| V007 | test_result.pass_rate | 범위: 0-100 | ERROR | Yes |
| V008 | coverage_result.line_coverage | 범위: 0-100 | ERROR | Yes |
| V009 | test_result | passed + failed + skipped == total_tests | WARNING | No |
| V010 | pass_rate | 계산된 값과 일치 | WARNING | No |
| V011 | gate_decision | PASS 시 pass_rate >= 80% AND line_coverage >= 80% | ERROR | Yes |
| V012 | summary (autofix) | auto_fixed + regenerated + escalated <= total_errors | WARNING | No |

**Sub-steps:**
1. integration-build-report.yaml 스키마 검증
2. auto-fix-report.yaml 스키마 검증 (존재 시)
3. Gate 결과 일관성 검증
4. 오류 발생 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 빌드 재실행 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.5 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | 4.3/4.4 완료 | 빌드 시작 | 대기 |
| DP-2 | 컴파일 성공 | 테스트 실행 | 오류 수정 |
| DP-3 | 테스트 >= 80% | 커버리지 체크 | 실패 분석 |
| DP-4 | 커버리지 >= 80% | Gate PASS | 커버리지 개선 |
| DP-5 | Gate PASS | Stage 5 진입 | Escalation |

---

### 3.6 Auto-Fix Rule Engine

컴파일 및 테스트 오류에 대한 자동 수정 규칙을 정의합니다.

#### 3.6.1 Error Categories

```yaml
error_categories:
  auto_fixable:
    description: "AI가 자동으로 수정 가능"
    confidence_threshold: 0.9
    action: "Apply fix automatically"
    examples:
      - "Missing standard library import"
      - "Missing Lombok annotation"
      - "Simple type wrapper conversion"

  conditional_fix:
    description: "조건 충족 시 자동 수정"
    confidence_threshold: 0.7
    action: "Apply fix with validation"
    requires:
      - "Pattern matches known safe conversion"
      - "No breaking changes to API"
    examples:
      - "Nullable type handling"
      - "Collection type coercion"

  regeneration_required:
    description: "Spec 기반 재생성 필요"
    confidence_threshold: 0.5
    action: "Regenerate from Feature Spec"
    triggers:
      - "Method signature mismatch"
      - "Missing interface method"
      - "Mapper-XML sync issue"

  needs_analysis:
    description: "분석 후 판단 필요"
    confidence_threshold: 0.3
    action: "Analyze root cause"
    escalate_after: "2 failed attempts"

  escalate:
    description: "사람 개입 필요"
    confidence_threshold: 0.0
    action: "Escalate to Tech Lead"
    examples:
      - "Architectural issue"
      - "Spec ambiguity"
      - "Cross-domain dependency error"
```

#### 3.6.2 Import Error Rules (Auto-Fixable)

```yaml
import_error_rules:
  pattern: "cannot find symbol.*class (\\w+)"
  severity: "auto_fixable"

  resolution:
    strategy: "import_resolution"
    steps:
      1: "Extract missing class name from error message"
      2: "Search in known package mappings"
      3: "Add import statement at correct position"

  known_mappings:
    # Spring Framework
    spring:
      - class: "RestController"
        import: "org.springframework.web.bind.annotation.RestController"
      - class: "RequestMapping"
        import: "org.springframework.web.bind.annotation.RequestMapping"
      - class: "PostMapping"
        import: "org.springframework.web.bind.annotation.PostMapping"
      - class: "GetMapping"
        import: "org.springframework.web.bind.annotation.GetMapping"
      - class: "Service"
        import: "org.springframework.stereotype.Service"
      - class: "Repository"
        import: "org.springframework.stereotype.Repository"
      - class: "Component"
        import: "org.springframework.stereotype.Component"
      - class: "Transactional"
        import: "org.springframework.transaction.annotation.Transactional"
      - class: "Autowired"
        import: "org.springframework.beans.factory.annotation.Autowired"

    # Lombok
    lombok:
      - class: "RequiredArgsConstructor"
        import: "lombok.RequiredArgsConstructor"
      - class: "AllArgsConstructor"
        import: "lombok.AllArgsConstructor"
      - class: "NoArgsConstructor"
        import: "lombok.NoArgsConstructor"
      - class: "Getter"
        import: "lombok.Getter"
      - class: "Setter"
        import: "lombok.Setter"
      - class: "Builder"
        import: "lombok.Builder"
      - class: "Data"
        import: "lombok.Data"
      - class: "Slf4j"
        import: "lombok.extern.slf4j.Slf4j"

    # Jakarta Validation
    jakarta:
      - class: "Valid"
        import: "jakarta.validation.Valid"
      - class: "NotNull"
        import: "jakarta.validation.constraints.NotNull"
      - class: "NotBlank"
        import: "jakarta.validation.constraints.NotBlank"
      - class: "Size"
        import: "jakarta.validation.constraints.Size"

    # Project Internal
    project:
      - class: "ApiResponse"
        import: "com.hallain.common.response.ApiResponse"
      - class: "PageResponse"
        import: "com.hallain.common.response.PageResponse"
      - class: "BusinessException"
        import: "com.hallain.common.exception.BusinessException"
      - class: "ErrorCode"
        import: "com.hallain.common.exception.ErrorCode"
      - class: "BaseEntity"
        import: "com.hallain.common.entity.BaseEntity"
      - class: "RowStatus"
        import: "com.hallain.common.entity.RowStatus"

  fallback:
    action: "search_in_project"
    command: "grep -r 'class {CLASS_NAME}' next-hallain/src/"
    on_not_found: "escalate"
```

#### 3.6.3 Type Mismatch Rules (Conditional Fix)

```yaml
type_mismatch_rules:
  pattern: "incompatible types: (\\S+) cannot be converted to (\\S+)"
  severity: "conditional_fix"

  safe_conversions:
    # Primitive wrappers
    - from: "int"
      to: "Integer"
      fix: "Use Integer.valueOf()"
      safe: true
    - from: "Integer"
      to: "int"
      fix: "Add null check: value != null ? value : 0"
      safe: true
    - from: "long"
      to: "Long"
      fix: "Use Long.valueOf()"
      safe: true
    - from: "Long"
      to: "long"
      fix: "Add null check: value != null ? value : 0L"
      safe: true

    # String conversions
    - from: "Long"
      to: "String"
      fix: "Use String.valueOf()"
      safe: true
    - from: "Integer"
      to: "String"
      fix: "Use String.valueOf()"
      safe: true
    - from: "String"
      to: "Long"
      fix: "Use Long.parseLong() with try-catch"
      safe: false
      requires: "exception_handling"

    # Collection types
    - from: "List<T>"
      to: "Collection<T>"
      fix: "Safe - List extends Collection"
      safe: true
    - from: "ArrayList<T>"
      to: "List<T>"
      fix: "Safe - ArrayList implements List"
      safe: true

  unsafe_conversions:
    action: "escalate"
    reason: "Type mismatch may indicate spec error"
    examples:
      - "Entity to DTO without mapper"
      - "Incompatible generic types"
```

#### 3.6.4 Missing Method Rules (Regeneration Required)

```yaml
missing_method_rules:
  pattern: "cannot find symbol.*method (\\w+)\\("
  severity: "regeneration_required"

  resolution:
    strategy: "check_and_regenerate"
    steps:
      1: "Identify source class (Mapper/Service/Controller)"
      2: "Check Feature Spec for method definition"
      3: "Regenerate affected layer"

  layer_detection:
    - pattern: ".*Mapper\\."
      layer: "Repository"
      action: "Regenerate Mapper interface and XML"
    - pattern: ".*Service\\."
      layer: "Service"
      action: "Regenerate Service class"
    - pattern: ".*Controller\\."
      layer: "Controller"
      action: "Check Service interface, then regenerate"

  common_causes:
    - cause: "Mapper method missing"
      symptom: "Service calls undefined Mapper method"
      fix: "Regenerate Mapper from spec"
    - cause: "Service method signature mismatch"
      symptom: "Controller expects different signature"
      fix: "Regenerate Service layer"
    - cause: "Interface sync issue"
      symptom: "Implementation doesn't match interface"
      fix: "Regenerate from interface definition"
```

#### 3.6.5 MyBatis/XML Error Rules

```yaml
mybatis_error_rules:
  - pattern: "Invalid bound statement.*not found: (\\S+)\\.(\\w+)"
    severity: "regeneration_required"
    resolution:
      strategy: "mapper_xml_sync"
      steps:
        1: "Check Mapper XML exists at resources/mapper/{domain}/"
        2: "Verify namespace matches interface FQCN"
        3: "Verify method id matches interface method name"
        4: "Regenerate XML if mismatch"

  - pattern: "Could not find result map '(\\S+)'"
    severity: "auto_fixable"
    resolution:
      strategy: "result_map_fix"
      steps:
        1: "Check resultMap id in XML"
        2: "Generate resultMap from Entity class"
        3: "Map columns to entity fields (underscore to camelCase)"

  - pattern: "Parameter '(\\w+)' not found"
    severity: "auto_fixable"
    resolution:
      strategy: "parameter_binding_fix"
      steps:
        1: "Check @Param annotation in Mapper interface"
        2: "Add missing @Param annotation"
        3: "Verify parameter name matches XML reference"
```

#### 3.6.6 Annotation Error Rules

```yaml
annotation_error_rules:
  - pattern: "@(\\w+) is not applicable to"
    severity: "auto_fixable"
    resolution:
      strategy: "annotation_placement"
      rules:
        - annotation: "@Transactional"
          valid_targets: ["TYPE", "METHOD"]
          common_mistake: "Applied to field"
          fix: "Move to method or class level"

        - annotation: "@Valid"
          valid_targets: ["PARAMETER", "FIELD"]
          common_mistake: "Applied to method"
          fix: "Move to parameter"

        - annotation: "@RequestBody"
          valid_targets: ["PARAMETER"]
          common_mistake: "Applied to method"
          fix: "Move to parameter"

        - annotation: "@PathVariable"
          valid_targets: ["PARAMETER"]
          common_mistake: "Missing value attribute"
          fix: "Add value matching path variable name"
```

#### 3.6.7 Test Error Rules

```yaml
test_error_rules:
  - pattern: "NullPointerException.*Mock"
    severity: "auto_fixable"
    resolution:
      strategy: "mock_setup_fix"
      steps:
        1: "Identify unmocked dependency"
        2: "Add @Mock annotation"
        3: "Add when().thenReturn() stub"

  - pattern: "Wanted but not invoked"
    severity: "conditional_fix"
    resolution:
      strategy: "verify_fix"
      steps:
        1: "Check if method was actually called"
        2: "Verify argument matchers"
        3: "Update test expectation or fix code"

  - pattern: "No qualifying bean of type"
    severity: "auto_fixable"
    resolution:
      strategy: "test_config_fix"
      steps:
        1: "Add @MockBean for missing dependency"
        2: "Or add @Import for required configuration"
```

#### 3.6.8 Fix Execution Workflow

```yaml
fix_workflow:
  max_iterations: 3
  per_iteration:
    timeout_minutes: 10

  steps:
    1_parse_error:
      action: "Parse compiler/test error output"
      input: "compile.log or test.log"
      extract:
        - file_path
        - line_number
        - error_type
        - error_message
      output: "structured_error_list.yaml"

    2_categorize:
      action: "Match against auto_fix_rules"
      input: "structured_error_list.yaml"
      output: "categorized_errors.yaml"

    3_prioritize:
      action: "Sort by fix probability"
      order:
        1: "auto_fixable"
        2: "conditional_fix"
        3: "regeneration_required"
        4: "needs_analysis"
        5: "escalate"
      output: "prioritized_fix_queue.yaml"

    4_apply_fixes:
      action: "Apply fixes in priority order"
      per_fix:
        - "Read affected file"
        - "Apply transformation rule"
        - "Write updated file"
        - "Log change to fix_log.yaml"
      validation: "Syntax check after each fix"

    5_recompile:
      action: "Verify fixes"
      command: "./gradlew compileJava"
      on_success: "Proceed to next error category"
      on_failure:
        - "Rollback last fix"
        - "Try alternative fix or escalate"

    6_report:
      action: "Generate fix report"
      output: "auto-fix-report.yaml"
      include:
        - total_errors: "Number of errors detected"
        - auto_fixed: "Errors fixed automatically"
        - regenerated: "Components regenerated from spec"
        - escalated: "Errors requiring human intervention"
        - fix_success_rate: "Percentage of auto-fixed errors"
```

#### 3.6.9 Fix Report Schema

```yaml
# auto-fix-report.yaml
metadata:
  generated_by: "s4-05-auto-fix-engine"
  generated_at: "2026-01-07T20:00:00Z"
  build_attempt: 2

summary:
  total_errors: 45
  auto_fixed: 38
  regenerated: 5
  escalated: 2
  fix_success_rate: 95.6%

by_category:
  import_errors:
    count: 25
    fixed: 25
    method: "known_mappings"
  type_mismatches:
    count: 8
    fixed: 6
    skipped: 2
    reason: "unsafe_conversion"
  missing_methods:
    count: 5
    regenerated: 5
    affected_features: ["FEAT-PA-123", "FEAT-MM-045"]
  mybatis_errors:
    count: 5
    fixed: 4
    escalated: 1
  annotation_errors:
    count: 2
    fixed: 2

escalated_issues:
  - file: "PA01001Service.java"
    line: 45
    error: "Circular dependency detected"
    reason: "Architectural issue requires human decision"
  - file: "MM02003Mapper.xml"
    line: 120
    error: "Complex dynamic SQL not parseable"
    reason: "Manual SQL review required"

changes_applied:
  - file: "PA01001Controller.java"
    changes:
      - line: 3
        type: "add_import"
        content: "import org.springframework.web.bind.annotation.RestController;"
      - line: 5
        type: "add_import"
        content: "import lombok.RequiredArgsConstructor;"
  - file: "QM01001Service.java"
    changes:
      - line: 25
        type: "add_null_check"
        before: "return entity.getId();"
        after: "return entity != null ? entity.getId() : null;"

next_action:
  if_success: "Proceed to test execution"
  if_failure: "Review escalated issues with Tech Lead"
```

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    build: "next-hallain/build/"

  artifacts:
    - name: "libs/"
      description: "Built JAR files"
      path: "next-hallain/build/libs/"

    - name: "reports/tests/"
      description: "Test execution reports"
      path: "next-hallain/build/reports/tests/test/"

    - name: "reports/jacoco/"
      description: "Code coverage reports"
      path: "next-hallain/build/reports/jacoco/test/"
```

### 4.2 Output Files

| File | Type | Purpose | Required |
|------|------|---------|----------|
| hallain-backend-*.jar | JAR | 실행 가능 아티팩트 | Yes |
| index.html (test) | HTML | 테스트 결과 리포트 | Yes |
| index.html (jacoco) | HTML | 커버리지 리포트 | Yes |
| jacocoTestReport.xml | XML | CI/CD용 커버리지 데이터 | Yes |
| integration-build-report.yaml | YAML | 빌드 결과 요약 | Yes |

### 4.3 Build Report Schema

```yaml
# integration-build-report.yaml
metadata:
  generated_by: "s4-05-generation-integration-build"
  generated_at: "2026-01-07T20:00:00Z"
  wave: 1
  model: "claude-opus-4-5-20251101"

build_status: "SUCCESS"  # SUCCESS | CONDITIONAL | FAIL

build_details:
  gradle_version: "8.5"
  java_version: "17"
  spring_boot_version: "3.2.1"
  total_classes: 4200
  total_lines: 250000

compile_result:
  status: "SUCCESS"
  errors: 0
  warnings: 15

test_result:
  status: "SUCCESS"
  total_tests: 2100
  passed: 1890
  failed: 168
  skipped: 42
  pass_rate: 90.0

coverage_result:
  status: "SUCCESS"
  line_coverage: 82.5
  branch_coverage: 75.3
  instruction_coverage: 80.1

  by_package:
    "com.hallain.pa": 85.2
    "com.hallain.mm": 81.0
    "com.hallain.sc": 79.5
    # ...

artifacts:
  - path: "build/libs/hallain-backend-1.0.0-SNAPSHOT.jar"
    size: "45MB"
  - path: "build/reports/tests/test/index.html"
  - path: "build/reports/jacoco/test/html/index.html"

gate_decision:
  result: "PASS"
  criteria_met:
    - "build_succeeds: true"
    - "test_pass_rate: 90.0% (>= 80%)"
    - "code_coverage: 82.5% (>= 80%)"
    - "compile_errors: 0"

next_stage: "Stage 5 - Assurance"
commit_message: "feat(S4-P4.5): Integration build successful"
tag: "wave-1-rc1"
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| build_succeeds | structural | `./gradlew build` 성공 | ERROR | Yes |
| test_pass_rate | metric | >= 80% | ERROR | Yes |
| no_compile_errors | structural | 0 errors | ERROR | Yes |
| code_coverage | metric | >= 80% | WARNING | Conditional |

### 5.2 Gate Criteria

```yaml
gate_criteria:
  id: "G4.5"
  name: "Integration Build Gate"
  threshold: 70
  human_approval: false

  metrics:
    - metric: "build_succeeds"
      weight: 0.3
      target: "true"
      command: "cd backend && ./gradlew build"
      blocking: true

    - metric: "test_pass_rate"
      weight: 0.3
      target: ">= 80%"
      source: "build/reports/tests/test/"
      threshold: 80
      blocking: true

    - metric: "no_compile_errors"
      weight: 0.2
      target: "0"
      blocking: true

    - metric: "code_coverage"
      weight: 0.2
      target: ">= 80%"
      command: "cd backend && ./gradlew jacocoTestReport"
      threshold: 80
      blocking: true

  on_pass:
    auto_commit: true
    message: "feat(S4-P4.5): Integration build successful"
    tag: "wave-{N}-rc1"
    advance_to: "Stage 5"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Out of Memory | OOM error | 대형 프로젝트 | Heap 증가 | Yes |
| Compile error | javac 실패 | 코드 오류 | Auto-fix 시도 | Yes |
| Test timeout | 테스트 멈춤 | 느린 테스트 | Timeout 증가 | Yes |
| Coverage low | < 80% | 테스트 부족 | 테스트 추가 | Yes |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Build 실패 3회 | critical | 수동 분석 | Tech Lead |
| Coverage < 70% | critical | 테스트 보강 | Architect |
| 전체 Gate 실패 | blocker | Stage 4 재검토 | Project Manager |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 컴파일 오류 | 오류 수정 → 재빌드 | Build |
| 테스트 실패 | 실패 분석 → 수정 → 재실행 | Test |
| 커버리지 미달 | 테스트 추가 → 재실행 | Test |
| 전체 실패 | 4.3/4.4 재검토 | Phase |

---

## 7. Examples

### 7.1 Sample Build Execution

**Gradle Build Output:**
```bash
$ cd backend && ./gradlew build

> Task :compileJava
Note: Processing 4200 source files

> Task :processResources
> Task :classes
> Task :jar
> Task :bootJar

> Task :compileTestJava
Note: Processing 2100 test source files

> Task :processTestResources
> Task :testClasses

> Task :test
2100 tests completed, 168 failed, 42 skipped

> Task :jacocoTestReport
Generating JaCoCo report...
Line coverage: 82.5%
Branch coverage: 75.3%

BUILD SUCCESSFUL in 15m 32s
```

### 7.2 Sample Gate Decision

**Gate PASS Example:**
```yaml
gate_evaluation:
  timestamp: "2026-01-07T20:30:00Z"
  evaluator: "s4-05-generation-integration-build"

  criteria_results:
    - criteria: "build_succeeds"
      result: true
      status: "PASS"

    - criteria: "test_pass_rate"
      target: ">= 80%"
      actual: "90.0%"
      status: "PASS"

    - criteria: "no_compile_errors"
      target: "0"
      actual: "0"
      status: "PASS"

    - criteria: "code_coverage"
      target: ">= 80%"
      actual: "82.5%"
      status: "PASS"

  final_decision: "PASS"
  next_action: "Advance to Stage 5"
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| 첫 빌드 | Clean project | Full build cycle |
| 재빌드 | 일부 변경 | Incremental build |
| 테스트 실패 많음 | < 70% pass | FAIL + Escalation |
| OOM 발생 | Large heap usage | Heap 조정 후 재시도 |

---

## Version History

### v1.2.0 (2026-01-08)
- Step 8: Schema Validation 추가
- s4-05-integration-build.schema.yaml 스키마 참조
- 12개 검증 규칙 적용 (V001-V012)

### v1.1.0 (2026-01-07)
- **Auto-Fix Rule Engine 추가** (Section 3.6)
  - 5개 Error Category 정의 (auto_fixable → escalate)
  - Import Error Rules with known_mappings (Spring, Lombok, Jakarta, Project)
  - Type Mismatch Rules with safe/unsafe conversions
  - Missing Method Rules with layer detection
  - MyBatis/XML Error Rules
  - Annotation Error Rules
  - Test Error Rules
  - Fix Execution Workflow (6-step process)
  - Fix Report Schema (auto-fix-report.yaml)
- **Failure Recovery 개선** (Section 3.4)
  - 각 retry 단계별 상세 steps 정의
  - Retry Decision Matrix 추가
  - expected_fix_rate 메트릭 추가
- **Compile Error Handling 개선** (Step 3)
  - Error categorization 추가
  - Auto-Fix Rule Engine 참조 연결

### v1.0.0 (2026-01-07)
- Initial version
- Stage Gate 통합
- Auto-fix 메커니즘 (기본)
- 3단계 Escalation 전략
