---
name: s4-04-generation-test-generation
description: Use when generating unit and integration tests for generated code, running parallel test generation with code generation, or achieving test coverage targets for migration validation (project)
---

# Test Generation

> **Skill ID**: S4-04
> **Skill Type**: Generation (Parallel Batch)
> **Stage**: 4 - Generation
> **Phase**: 4.4 - Test Generation
> **Parallel With**: Phase 4.3 (Domain Batch Generation)
> **Risk Context**: R-005 (Zero Test Coverage Mitigation)

## 1. Overview

### 1.1 Purpose

생성된 코드에 대한 **Unit 테스트와 Integration 테스트를 자동 생성**합니다. Phase 4.3과 **병렬로 실행**되며, 각 Feature 코드 생성 완료 시 테스트 생성이 트리거됩니다.

**Risk Mitigation:**
- R-005: Zero test coverage in legacy code
- Legacy 시스템의 테스트 부재를 신규 시스템에서 해소

**생성 대상:**
- Service Layer Unit Tests
- Controller Layer Tests (MockMvc)
- Repository/Mapper Tests (MyBatis Test)

**Coverage Targets:**
- Service: 80%
- Controller: 70%
- Repository: 60%
- **Overall: 80%**

### 1.2 Scope

**In Scope:**
- Unit Test 생성 (Service, Controller)
- Repository Test 생성 (MyBatis)
- Test 컴파일 검증
- Test 실행 및 Pass Rate 확인

**Out of Scope:**
- E2E 테스트 (→ 별도 Phase)
- Performance 테스트 (→ S5-04)
- Business logic 코드 생성 (→ S4-03)

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Pipeline Coordination** | S4-03 완료 시 즉시 트리거 | 병렬 효율성 |
| **Coverage Focused** | 80% 커버리지 목표 | 품질 보증 |
| **Spec-Based** | Feature Spec 기반 테스트 케이스 | 정확한 검증 |
| **Fail-Fast** | 테스트 실패 즉시 피드백 | 빠른 수정 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S4-04는 테스트를 생성하며, **Repository 테스트에서 SQL 결과 검증이 필수**

### 1.5 Relationships

**Parallel:**
| Skill | Coordination |
|-------|--------------|
| `s4-03-generation-domain-batch` | GEN-{FEAT_ID} 완료 시 TEST-{FEAT_ID} 트리거 |

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s4-01-generation-project-scaffold` | 테스트 인프라 필요 |
| `s3-05-preparation-generation-spec` | 테스트 템플릿 필요 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s4-05-generation-integration-build` | 테스트 포함 빌드 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S4-01"
    skill_name: "s4-01-generation-project-scaffold"
    status: "completed"
    artifacts:
      - "Test dependencies in build.gradle.kts"
      - "src/test/java/ directory"

  - skill_id: "S3-05"
    skill_name: "s3-05-preparation-generation-spec"
    status: "completed"
    artifacts:
      - "test-template.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| generated_code | directory | `next-hallain/src/main/java/` | Java | Yes |
| feature_specs | directory | `work/specs/stage2-outputs/phase4/` | YAML | Yes |
| test_template | file | `work/specs/stage3-outputs/phase5/test-template.yaml` | YAML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Task | - | 병렬 세션 디스패치 |
| Write | - | 테스트 파일 생성 |
| Bash | - | 테스트 실행 |

**Test Dependencies:**
```kotlin
testImplementation("org.springframework.boot:spring-boot-starter-test")
testImplementation("org.mybatis.spring.boot:mybatis-spring-boot-starter-test:3.0.3")
testImplementation("com.h2database:h2")  // In-memory DB for tests
```

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
    retry_on_failure: 3

task:
  naming_pattern: "TEST-{FEAT_ID}"
  granularity: feature

parallel_coordination:
  with_phase: "4.3"
  coordination_type: "feature_pipeline"
  trigger: "GEN-{FEAT_ID} completion"
  action: "Queue TEST-{FEAT_ID}"
```

### 3.2 Feature Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FEATURE PIPELINE (S4-03 ↔ S4-04)                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Phase 4.3: Code Generation          Phase 4.4: Test Generation        │
│                                                                         │
│   ┌──────────────────────┐           ┌──────────────────────┐          │
│   │  GEN-FEAT-PA-001     │──trigger─▶│  TEST-FEAT-PA-001    │          │
│   │  (Code Generation)   │           │  (Test Generation)   │          │
│   └──────────────────────┘           └──────────────────────┘          │
│                                                                         │
│   ┌──────────────────────┐           ┌──────────────────────┐          │
│   │  GEN-FEAT-PA-002     │──trigger─▶│  TEST-FEAT-PA-002    │          │
│   │  (Code Generation)   │           │  (Test Generation)   │          │
│   └──────────────────────┘           └──────────────────────┘          │
│                                                                         │
│   ┌──────────────────────┐           ┌──────────────────────┐          │
│   │  GEN-FEAT-MM-001     │──trigger─▶│  TEST-FEAT-MM-001    │          │
│   │  (Code Generation)   │           │  (Test Generation)   │          │
│   └──────────────────────┘           └──────────────────────┘          │
│                                                                         │
│         ▼                                     ▼                         │
│   ┌──────────────────────┐           ┌──────────────────────┐          │
│   │ generation-progress  │           │   test-progress      │          │
│   │      .yaml           │           │      .yaml           │          │
│   └──────────────────────┘           └──────────────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Test Coverage Strategy

```yaml
test_coverage_targets:
  service_layer:
    target: 80
    test_types:
      - "Unit tests with mocked dependencies"
      - "Business logic validation"
      - "Exception handling tests"

  controller_layer:
    target: 70
    test_types:
      - "MockMvc integration tests"
      - "Request validation tests"
      - "Response structure tests"

  repository_layer:
    target: 60
    test_types:
      - "MyBatis mapper tests"
      - "SQL execution tests"
      - "Parameter binding tests"

  overall: 80
```

### 3.4 Process Steps

#### Step 1: Queue Management

**Description:** S4-03에서 트리거된 테스트 작업 큐 관리

**Sub-steps:**
1. GEN-{FEAT_ID} 완료 메시지 수신
2. TEST-{FEAT_ID} 작업 큐에 추가
3. 우선순위 기반 정렬
4. 세션 할당

**Queue Structure:**
```yaml
test_queue:
  pending:
    - { task_id: "TEST-FEAT-PA-001", triggered_by: "GEN-FEAT-PA-001" }
    - { task_id: "TEST-FEAT-PA-002", triggered_by: "GEN-FEAT-PA-002" }
  in_progress:
    - { task_id: "TEST-FEAT-MM-001", session: "S3" }
  completed:
    - { task_id: "TEST-FEAT-CM-001", result: "PASS" }
```

**Validation:** 큐 관리 정상 동작

---

#### Step 2: Generate Service Tests

**Description:** Service Layer Unit Test 생성

**Sub-steps:**
1. Service 클래스 분석
2. 메서드별 테스트 케이스 생성
3. Mock 객체 설정
4. Assert 문 작성

**Service Test Template:**
```java
@ExtendWith(MockitoExtension.class)
class {Screen}ServiceTest {

    @Mock
    private {Screen}Mapper {screen}Mapper;

    @InjectMocks
    private {Screen}Service {screen}Service;

    @Test
    @DisplayName("{methodName} - 정상 케이스")
    void {methodName}_success() {
        // given
        {InputType} request = create{InputType}();
        {OutputType} expected = create{OutputType}();
        when({screen}Mapper.{mapperMethod}(any())).thenReturn(expected);

        // when
        var result = {screen}Service.{methodName}(request);

        // then
        assertThat(result).isNotNull();
        assertThat(result.{field}()).isEqualTo(expected.{field}());
        verify({screen}Mapper).{mapperMethod}(any());
    }

    @Test
    @DisplayName("{methodName} - 데이터 없음")
    void {methodName}_notFound() {
        // given
        when({screen}Mapper.{mapperMethod}(any())).thenReturn(null);

        // when & then
        assertThatThrownBy(() -> {screen}Service.{methodName}(create{InputType}()))
            .isInstanceOf(BusinessException.class);
    }
}
```

**Validation:** Service 테스트 생성 완료

---

#### Step 3: Generate Controller Tests

**Description:** Controller Layer MockMvc Test 생성

**Sub-steps:**
1. Controller 클래스 분석
2. 엔드포인트별 테스트 케이스 생성
3. MockMvc 설정
4. Request/Response 검증

**Controller Test Template:**
```java
@WebMvcTest({Screen}Controller.class)
@Import(TestSecurityConfig.class)
class {Screen}ControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private {Screen}Service {screen}Service;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("GET /api/{domain}/{screen}/list - 목록 조회 성공")
    void getList_success() throws Exception {
        // given
        var response = List.of(create{Screen}Response());
        when({screen}Service.get{Entity}List(any())).thenReturn(response);

        // when & then
        mockMvc.perform(post("/api/{domain}/{screen}/list")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(create{Screen}SearchRequest())))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data").isArray())
            .andExpect(jsonPath("$.data[0].{field}").exists());
    }

    @Test
    @DisplayName("POST /api/{domain}/{screen}/save - 저장 성공")
    void save_success() throws Exception {
        // given
        doNothing().when({screen}Service).save{Entity}(any());

        // when & then
        mockMvc.perform(post("/api/{domain}/{screen}/save")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(List.of(create{Screen}SaveRequest()))))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true));
    }

    @Test
    @DisplayName("Validation 오류 - 필수값 누락")
    void validation_error() throws Exception {
        // given
        var invalidRequest = new {Screen}SearchRequest(null, null);

        // when & then
        mockMvc.perform(post("/api/{domain}/{screen}/list")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(invalidRequest)))
            .andExpect(status().isBadRequest());
    }
}
```

**Validation:** Controller 테스트 생성 완료

---

#### Step 4: Generate Repository Tests

**Description:** MyBatis Mapper Test 생성

**Sub-steps:**
1. Mapper Interface 분석
2. SQL 실행 테스트 생성
3. H2 인메모리 DB 설정
4. 테스트 데이터 준비

**Repository Test Template:**
```java
@MybatisTest
@AutoConfigureTestDatabase(replace = Replace.NONE)
@Import(MyBatisTestConfig.class)
class {Screen}MapperTest {

    @Autowired
    private {Screen}Mapper {screen}Mapper;

    @Test
    @DisplayName("selectList - 목록 조회")
    void selectList_success() {
        // given
        var request = {Screen}SearchRequest.builder()
            .siteCd("S01")
            .build();

        // when
        var result = {screen}Mapper.selectList(request);

        // then
        assertThat(result).isNotNull();
    }

    @Test
    @DisplayName("insert - 데이터 삽입")
    void insert_success() {
        // given
        var entity = create{Screen}Entity();

        // when
        int result = {screen}Mapper.insert(entity);

        // then
        assertThat(result).isEqualTo(1);
    }

    @Test
    @DisplayName("update - 데이터 수정")
    void update_success() {
        // given
        var entity = create{Screen}Entity();
        {screen}Mapper.insert(entity);

        entity.updateField("newValue");

        // when
        int result = {screen}Mapper.update(entity);

        // then
        assertThat(result).isEqualTo(1);
    }
}
```

**Validation:** Repository 테스트 생성 완료

---

#### Step 5: Test Compilation

**Description:** 생성된 테스트 코드 컴파일 검증

**Sub-steps:**
1. `./gradlew compileTestJava` 실행
2. 컴파일 오류 확인
3. 오류 수정

**Validation:** 테스트 컴파일 성공

---

#### Step 6: Test Execution

**Description:** 테스트 실행 및 Pass Rate 확인

**Sub-steps:**
1. `./gradlew test` 실행
2. 테스트 결과 수집
3. Pass Rate 계산
4. 실패 테스트 분석

**Execution Commands:**
```bash
cd backend
./gradlew test --info
./gradlew jacocoTestReport
```

**Validation:** Pass Rate >= 80%

---

### 3.5 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | GEN 완료 | TEST 큐에 추가 | 대기 |
| DP-2 | 컴파일 성공 | 테스트 실행 | 수정 후 재시도 |
| DP-3 | Pass Rate >= 80% | Gate 통과 | 실패 분석 |
| DP-4 | 개별 테스트 실패 | 수정 시도 | 스킵 후 계속 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "next-hallain/src/test/java/com/hallain/"

  per_feature:
    - "{domain}/service/{Screen}ServiceTest.java"
    - "{domain}/controller/{Screen}ControllerTest.java"
    - "{domain}/repository/{Screen}MapperTest.java"

  tracking:
    - name: "test-progress.yaml"
      path: "work/specs/stage4-outputs/phase4/"
```

### 4.2 Output Files Summary

**Per Feature:**
```
next-hallain/src/test/java/com/hallain/{domain}/
├── service/
│   └── {Screen}ServiceTest.java
├── controller/
│   └── {Screen}ControllerTest.java
└── repository/
    └── {Screen}MapperTest.java
```

### 4.3 Progress Output Schema

```yaml
# test-progress.yaml
metadata:
  generated_by: "s4-04-generation-test-generation"
  started_at: "2026-01-07T10:00:00Z"
  last_updated: "2026-01-07T18:00:00Z"

summary:
  total_features: 700
  tests_generated: 700
  tests_passed: 560
  tests_failed: 140
  pass_rate: 80.0

by_layer:
  service:
    total: 700
    passed: 600
    coverage: 85.7%
  controller:
    total: 700
    passed: 520
    coverage: 74.3%
  repository:
    total: 700
    passed: 450
    coverage: 64.3%

failed_tests:
  - test: "{Screen}ServiceTest.testMethod"
    reason: "NullPointerException"
    feature: "FEAT-PA-123"
  # ...

coverage_report:
  overall: 81.2%
  by_package:
    "com.hallain.pa": 82.5%
    "com.hallain.mm": 80.1%
    # ...

ready_for_integration: true
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| all_tests_generated | metric | progress 100% | ERROR | Yes |
| test_compilation_succeeds | structural | `./gradlew compileTestJava` | ERROR | Yes |
| test_execution_passes | metric | pass rate >= 80% | ERROR | Yes |
| coverage_threshold | metric | JaCoCo >= 80% | WARNING | No |

### 5.2 Gate Criteria

```yaml
gate_criteria:
  id: "G4.4"
  name: "Test Generation Gate"
  threshold: 70
  metrics:
    - metric: "all_tests_generated"
      weight: 0.3
      target: "100%"
      source: "test-progress.yaml"
      blocking: true
    - metric: "test_compilation_succeeds"
      weight: 0.3
      target: "true"
      command: "cd backend && ./gradlew compileTestJava"
      blocking: true
    - metric: "test_execution_passes"
      weight: 0.4
      target: ">= 80%"
      command: "cd backend && ./gradlew test"
      threshold: 80
      blocking: true
  on_pass:
    auto_commit: true
    message: "feat(S4-P4.4): Test generation complete"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Test compile error | 컴파일 실패 | Import 누락 | Import 추가 | Yes |
| Mock setup error | NullPointer | Mock 미설정 | Mock 추가 | Yes |
| DB connection error | Connection refused | H2 미설정 | Config 확인 | Yes |
| Timeout | 테스트 타임아웃 | 느린 쿼리 | Timeout 증가 | Yes |

### 6.2 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 개별 테스트 실패 | 테스트 수정 후 재실행 | Test |
| 배치 실패 | 체크포인트에서 재시작 | Batch |
| 전체 실패 | Pass Rate 미달 분석 | Phase |

---

## 7. Examples

### 7.1 Sample Service Test

**Generated Test for QM01001Service:**
```java
package com.hallain.qm.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class QM01001ServiceTest {

    @Mock
    private QM01001Mapper qm01001Mapper;

    @InjectMocks
    private QM01001Service qm01001Service;

    @Test
    @DisplayName("getInspectionList - 정상 조회")
    void getInspectionList_success() {
        // given
        var request = QM01001SearchRequest.builder()
            .siteCd("S01")
            .build();
        var entities = List.of(
            QM01001Entity.builder().inspectionId("INS001").build()
        );
        when(qm01001Mapper.selectList(any())).thenReturn(entities);

        // when
        var result = qm01001Service.getInspectionList(request);

        // then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).inspectionId()).isEqualTo("INS001");
        verify(qm01001Mapper).selectList(any());
    }

    @Test
    @DisplayName("saveInspection - INSERT 케이스")
    void saveInspection_insert() {
        // given
        var request = QM01001SaveRequest.builder()
            .rowStatus(RowStatus.INSERT)
            .build();
        when(qm01001Mapper.insert(any())).thenReturn(1);

        // when
        qm01001Service.saveInspection(List.of(request));

        // then
        verify(qm01001Mapper).insert(any());
    }
}
```

### 7.2 Sample Controller Test

**Generated Test for QM01001Controller:**
```java
package com.hallain.qm.controller;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(QM01001Controller.class)
class QM01001ControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private QM01001Service qm01001Service;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("POST /api/qm/qm01001/list - 목록 조회")
    void getList_success() throws Exception {
        // given
        var response = List.of(new QM01001Response("INS001", "S01"));
        when(qm01001Service.getInspectionList(any())).thenReturn(response);

        var request = new QM01001SearchRequest("S01", null);

        // when & then
        mockMvc.perform(post("/api/qm/qm01001/list")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data[0].inspectionId").value("INS001"));
    }
}
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| 빈 결과 | Empty list | 빈 배열 반환 테스트 |
| 예외 케이스 | Invalid input | Exception 테스트 |
| 대량 데이터 | 1000 rows | Pagination 테스트 |
| 트랜잭션 | Save with error | Rollback 테스트 |

---

## Version History

### v1.0.0 (2026-01-07)
- Initial version
- Service/Controller/Repository 테스트 지원
- Phase 4.3과 병렬 조율
- 80% 커버리지 목표
