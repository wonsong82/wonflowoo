---
name: s1-01-discovery-feature-inventory
description: Use when starting legacy code migration, need to catalog API endpoints, or building feature list from Spring MVC controllers (project)
---

# Feature Inventory

> **Skill ID**: S1-01
> **Skill Type**: Analysis (소스코드에서 정보 추출)
> **Stage**: 1 - Discovery
> **Phase**: 1.1 - Feature Inventory

## 1. Overview

### 1.1 Purpose

Legacy Spring MVC 소스코드에서 Controller 클래스를 스캔하여 API 엔드포인트를 추출하고, 화면 ID(Screen ID) 기준으로 Feature 단위로 그룹핑하여 `feature-inventory.yaml`을 생성합니다.

**분석 대상:**
- `@Controller` 또는 `@RestController` 어노테이션이 있는 클래스
- `@RequestMapping`, `@GetMapping`, `@PostMapping` 등의 URL 매핑
- MiPlatform RIA 프레임워크의 요청 처리 패턴

**추출 정보:**
- Endpoint URL 및 HTTP Method
- Controller 클래스명 및 메서드명
- 화면 ID (Screen ID) - Feature 그룹핑 기준
- Request/Response 타입 정보

### 1.2 Scope

**In Scope:**
- Domain별 Controller 클래스 스캔
- `@RequestMapping` 계열 어노테이션 추출
- Screen ID 기반 Feature 그룹핑
- feature-inventory.yaml 생성

**Out of Scope:**
- Service/DAO 계층 분석 (→ `s1-03-discovery-deep-analysis`)
- MiPlatform 프로토콜 상세 분석 (→ `s1-02-discovery-miplatform-protocol`)
- SQL/MyBatis 매핑 분석 (→ `s1-03-discovery-deep-analysis`)

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Completeness** | 모든 Controller 클래스 100% 스캔 | 누락된 엔드포인트는 마이그레이션에서 제외됨 |
| **Accuracy** | URL 패턴 및 HTTP Method 정확한 추출 | 잘못된 매핑은 API 불일치 초래 |
| **Grouping** | Screen ID 기반 Feature 단위화 | 마이그레이션 단위 결정의 기초 |
| **Determinism** | 동일 입력 → 동일 출력 보장 | 재실행 시 일관된 결과 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S1-01은 Controller 계층만 분석하나, **후속 Phase(S1-03)에서 SQL-First 역추적**을 통해 모든 SQL이 분석됨
> - 본 Phase에서 식별된 Feature가 S1-03의 SQL 분석 범위를 결정

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| (없음 - Stage 1 첫 Phase) | 이 스킬이 Discovery의 시작점 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s1-02-discovery-miplatform-protocol` | Feature 목록 기반으로 MiPlatform 프로토콜 분석 |
| `s1-03-discovery-deep-analysis` | Feature별 5-Layer SQL-First 역추적 분석 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies: []
# 첫 번째 Phase이므로 선행 Skill 없음
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| legacy_source | directory | `${LEGACY_CODEBASE}/src/main/java/` | Java | Yes |
| domain_priorities | file | `work/assessment/data/phase2/domain-priorities.yaml` | YAML | Yes |
| controller_analysis | file | `work/assessment/data/phase3/controller-analysis.yaml` | YAML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Glob | - | Java 파일 패턴 매칭 |
| Grep | - | 어노테이션 패턴 검색 |
| Read | - | Java 파일 내용 읽기 |

**Access:**
- Legacy 소스코드 읽기 권한

**Resources:**
- 메모리: 대규모 도메인(PA)의 경우 많은 파일 처리 필요

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

### 3.2 Process Steps

#### Step 1: Controller Discovery

**Description:** 도메인 디렉토리에서 모든 Controller 클래스 파일 탐색

**Sub-steps:**
1. 도메인 경로 확인: `${LEGACY_CODEBASE}/src/main/java/**/{domain}/**/controller/`
2. `*Controller.java` 패턴 파일 목록 수집
3. `@Controller` 또는 `@RestController` 어노테이션 확인

**Validation:** Controller 클래스 파일 목록 생성 완료

**Outputs:**
- Controller 파일 경로 목록

**Rollback:** N/A (읽기 전용 작업)

---

#### Step 2: Endpoint Extraction

**Description:** 각 Controller에서 RequestMapping 정보 추출

**Sub-steps:**
1. 클래스 레벨 `@RequestMapping` 추출 (base path)
2. 메서드 레벨 매핑 어노테이션 추출:
   - `@RequestMapping`
   - `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`, `@PatchMapping`
3. URL 패턴 조합 (class base path + method path)
4. HTTP Method 식별

**Extraction Patterns:**
```java
// Class level
@RequestMapping("/api/pa")
@Controller
public class SampleController { ... }

// Method level
@RequestMapping(value = "/list", method = RequestMethod.POST)
@PostMapping("/list")
public ResponseEntity<?> getList(@RequestBody RequestDto dto) { ... }
```

**Validation:** 각 Controller의 모든 public 메서드 스캔 완료

**Outputs:**
- Endpoint 목록 (URL, Method, Controller, Method Name)

---

#### Step 3: Screen ID Extraction

**Description:** MiPlatform 패턴에서 Screen ID 추출

**Sub-steps:**
1. Controller 클래스명에서 Screen ID 패턴 추출
   - 예: `PA01001Controller` → Screen ID: `PA01001`
2. URL 패턴에서 Screen ID 추출
   - 예: `/pa/PA01001/list` → Screen ID: `PA01001`
3. 메서드 주석/JavaDoc에서 화면 참조 추출

**Screen ID Pattern:**
```regex
# Controller 클래스명 패턴
([A-Z]{2}\d{5})Controller

# URL 패턴
/[a-z]+/([A-Z]{2}\d{5})/
```

**Validation:** 90% 이상의 엔드포인트에 Screen ID 할당

**Outputs:**
- Screen ID 매핑 정보

---

#### Step 4: Feature Grouping

**Description:** Screen ID 기반으로 엔드포인트를 Feature 단위로 그룹핑

**Sub-steps:**
1. 동일 Screen ID의 엔드포인트 그룹핑
2. Feature ID 생성: `FEAT-{DOMAIN}-{NNN}`
   - 예: `FEAT-PA-001`, `FEAT-PA-002`
3. Feature별 메타데이터 집계:
   - 엔드포인트 수
   - Controller 클래스 수
   - 예상 복잡도 (엔드포인트 수 기반)

**Grouping Rules:**
```yaml
feature_grouping:
  primary_key: screen_id
  fallback_key: controller_class  # Screen ID 없는 경우
  feature_id_pattern: "FEAT-{DOMAIN}-{NNN:03d}"
```

**CRITICAL - Feature Integrity Rules:**

| Rule | Description | On Violation |
|------|-------------|--------------|
| **FR-1: Single Screen ID** | 하나의 Feature에는 반드시 단일 screen_id만 포함 | Feature 분리 필수 |
| **FR-2: No Cross-Screen Mixing** | 서로 다른 screen_id의 endpoint를 하나의 Feature에 혼합 금지 | ERROR - 재그룹핑 |
| **FR-3: Controller Affinity** | 동일 screen_id를 처리하는 Controller들만 같은 Feature에 포함 | WARNING |
| **FR-4: URL Prefix Consistency** | Feature 내 endpoint path는 일관된 prefix 유지 권장 | INFO |

**그룹핑 판단 기준:**
```
1. screen_id 추출 시도 (Controller 클래스명, URL 패턴)
2. screen_id 동일 → 같은 Feature
3. screen_id 다름 → 별도 Feature 생성
4. screen_id 추출 실패 → Controller 클래스 단위로 fallback
```

**잘못된 그룹핑 예시 (금지):**
```yaml
# ❌ WRONG - 서로 다른 screen_id 혼합
- feature_id: "FEAT-QM-008"
  screen_id: "QM04010"
  endpoints:
    - path: "/qm/qm_04/selectqm0401011m.mi"  # QM04010
    - path: "/qm/qm_03/selectqm0301018m.mi"  # QM03018 ← 다른 screen_id!
```

**올바른 그룹핑 예시:**
```yaml
# ✅ CORRECT - screen_id별 분리
- feature_id: "FEAT-QM-008"
  screen_id: "QM04010"
  endpoints:
    - path: "/qm/qm_04/selectqm0401011m.mi"
    - path: "/qm/qm_04/saveqm0401011m.mi"

- feature_id: "FEAT-QM-009"  # 별도 Feature
  screen_id: "QM03018"
  endpoints:
    - path: "/qm/qm_03/selectqm0301018m.mi"
    - path: "/qm/qm_03/saveqm0301018m.mi"
```

**Validation:** 모든 엔드포인트가 Feature에 할당됨, Feature별 단일 screen_id 준수

**Outputs:**
- Feature 목록 및 소속 엔드포인트

---

#### Step 5: Inventory Generation

**Description:** feature-inventory.yaml 파일 생성

**Sub-steps:**
1. 표준 헤더 추가
2. Summary 섹션 생성 (통계)
3. Features 섹션 생성 (상세 목록)
4. YAML 문법 검증

**Validation:** YAML 파일 생성 및 문법 검증 통과

**Outputs:**
- `feature-inventory.yaml`

---

#### Step 6: Schema Validation

**Description:** 생성된 feature-inventory.yaml이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Sub-steps:**
1. 생성된 `feature-inventory.yaml` 로드
2. 스키마 파일 로드
3. 구조 검증 (Structural Validation):
   - 필수 키 존재 확인: `metadata`, `summary`, `features`
   - YAML 문법 오류 없음
4. 내용 검증 (Content Validation):
   - `metadata.generated_by` = "s1-01-discovery-feature-inventory" (정확히 일치)
   - `metadata.generated_at` = ISO8601 형식 (YYYY-MM-DDTHH:MM:SSZ)
   - `metadata.domain` = 유효한 도메인 코드 (PA, CM, SM 등)
   - `features[].feature_id` = `FEAT-{DOMAIN}-{NNN}` 패턴
   - `features[].screen_id` = `{DOMAIN}{5자리}` 패턴
   - `features[].complexity` = `low`, `medium`, `high` 중 하나
   - `features[].endpoints[].method` = `GET`, `POST`, `PUT`, `DELETE`, `PATCH` 중 하나
   - `features[].endpoints[].path` = 소문자, `/`로 시작
5. 수치 검증 (Metric Validation):
   - `summary.total_features` = `features` 배열 길이와 일치
   - `summary.total_endpoints` = 모든 `features[].endpoints` 합계와 일치
   - `summary.by_complexity` 합계 = `summary.total_features`
6. 검증 실패 시 `validation-errors.yaml` 생성

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | root | 필수 키 존재 (metadata, summary, features) | ERROR | Yes |
| V002 | file | YAML 파싱 오류 없음 | ERROR | Yes |
| V003 | metadata.generated_by | 정확히 "s1-01-discovery-feature-inventory" | ERROR | Yes |
| V004 | features[].feature_id | `^FEAT-[A-Z]{2,3}-\d{3}$` 패턴 | ERROR | Yes |
| V005 | features[].screen_id | `^[A-Z]{2}\d{5}$` 패턴 | ERROR | Yes |
| V006 | features[].complexity | enum [low, medium, high] | ERROR | Yes |
| V007 | features[].endpoints[].method | enum [GET, POST, PUT, DELETE, PATCH] | ERROR | Yes |
| V008 | features[].endpoints[].path | `^/[a-z0-9/_-]+$` 패턴 (소문자) | WARNING | No |
| V009 | summary.total_features | features 배열 길이와 일치 | WARNING | No |
| V010 | summary.total_endpoints | endpoints 합계와 일치 | WARNING | No |

**On Validation Success:**
- Gate 통과 처리
- 다음 Phase 진행 가능

**On Validation Failure:**
- `validation-errors.yaml` 생성:
```yaml
# validation-errors.yaml
metadata:
  source_file: "feature-inventory.yaml"
  schema_file: "s1-01-feature-inventory.schema.yaml"
  validated_at: "2026-01-08T10:30:00Z"

result: "FAIL"
blocking_errors: 2
warnings: 1

errors:
  - rule_id: "V004"
    path: "features[0].feature_id"
    expected: "FEAT-{DOMAIN}-{NNN}"
    actual: "FEAT-PA-1"
    message: "feature_id 형식 오류: 3자리 숫자 필요"
    blocking: true

warnings:
  - rule_id: "V008"
    path: "features[0].endpoints[0].path"
    expected: "소문자 경로"
    actual: "/PA/PA01001/List"
    message: "endpoint path에 대문자 포함"
    blocking: false
```
- Gate 실패 처리 (blocking error 존재 시)
- Step 5 재실행 필요

**Outputs:**
- 검증 성공: 없음 (Gate 통과)
- 검증 실패: `validation-errors.yaml`

---

### 3.3 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | Screen ID 추출 실패 | Controller 클래스명으로 fallback 그룹핑 | 정상 그룹핑 진행 |
| DP-2 | 동일 URL 중복 발견 | WARNING 로그 후 첫 번째 유지 | 정상 진행 |
| DP-3 | 엔드포인트 0개 | ERROR 반환 (빈 도메인) | 정상 진행 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage1-outputs/phase1/"
    pattern: "{Priority}/{Domain}/"

  example: "work/specs/stage1-outputs/phase1/P2/PA/"
```

### 4.2 Output Files

| File | Type | Purpose | Required | Constraints |
|------|------|---------|----------|-------------|
| feature-inventory.yaml | YAML | Feature 목록 및 엔드포인트 매핑 | Yes | Max 300 lines per file |

### 4.3 File Header

```yaml
# Generated by: s1-01-discovery-feature-inventory
# Stage: 1 - Discovery
# Phase: 1.1 - Feature Inventory
# Domain: ${DOMAIN}
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
```

### 4.4 Output Schema

```yaml
# feature-inventory.yaml
metadata:
  generated_by: "s1-01-discovery-feature-inventory"
  generated_at: "2026-01-07T10:00:00Z"
  domain: "PA"
  source_path: "hallain/src/main/java/**/pa/"

summary:
  total_features: 443
  total_endpoints: 2043
  total_controllers: 124
  by_complexity:
    low: 200      # endpoints <= 3
    medium: 180   # endpoints 4-10
    high: 63      # endpoints > 10

features:
  - feature_id: "FEAT-PA-001"
    screen_id: "PA01001"
    name: "생산계획 조회"
    complexity: "medium"
    endpoints:
      - path: "/pa/PA01001/list"
        method: "POST"
        controller: "PA01001Controller"
        method_name: "getList"
        description: "생산계획 목록 조회"
      - path: "/pa/PA01001/detail"
        method: "POST"
        controller: "PA01001Controller"
        method_name: "getDetail"
        description: "생산계획 상세 조회"
    controllers:
      - class: "PA01001Controller"
        file: "src/main/java/com/hallain/pa/controller/PA01001Controller.java"
        methods_count: 5
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| file_exists | structural | `feature-inventory.yaml` 존재 | ERROR | Yes |
| yaml_syntax | structural | YAML 파싱 오류 없음 | ERROR | Yes |
| coverage | metric | endpoints >= 90% of expected | WARNING | Yes |
| no_orphan | content | 모든 endpoint가 feature에 할당 | ERROR | Yes |
| no_duplicate | content | 중복 endpoint URL 없음 | WARNING | No |

### 5.2 Manual Reviews

| Review | Reviewer | Criteria | Required |
|--------|----------|----------|----------|
| Sampling check | Tech Lead | 랜덤 10개 Feature의 정확성 확인 | No |

### 5.3 Gate Criteria

```yaml
gate_criteria:
  id: "G1.1"
  name: "Inventory Gate"
  threshold: 70
  metrics:
    - metric: "file_exists"
      weight: 0.3
      target: "true"
      formula: "feature-inventory.yaml exists"
    - metric: "endpoint_coverage"
      weight: 0.4
      target: ">= 90%"
      formula: "discovered_endpoints / expected_endpoints * 100"
    - metric: "feature_assignment"
      weight: 0.3
      target: "100%"
      formula: "assigned_endpoints / total_endpoints * 100"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| No controllers found | endpoints = 0 | 잘못된 도메인 경로 | 경로 확인 후 재실행 | Yes |
| Screen ID parse fail | screen_id = null | 비표준 네이밍 | Controller 클래스명으로 fallback | Auto |
| Encoding error | 파일 읽기 실패 | EUC-KR/UTF-8 혼용 | UTF-8 먼저, 실패 시 EUC-KR | Auto |
| Large file timeout | 60분 초과 | PA 도메인 2,895 파일 | batch 분할 처리 | Yes |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Coverage < 70% | critical | Phase 중단, 원인 분석 | Tech Lead |
| Coverage 70-90% | major | WARNING 로그, 계속 진행 | Orchestrator |
| Duplicate URLs > 10 | minor | 로그 기록, 계속 진행 | - |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 부분 실패 | 해당 도메인만 재실행 | Phase |
| 전체 실패 | 입력 데이터 확인 후 재실행 | Phase |
| 잘못된 출력 | 출력 파일 삭제 후 재실행 | Phase |

---

## 7. Examples

### 7.1 Sample Input

**Source Controller:**
```java
package com.hallain.pa.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/pa/PA01001")
public class PA01001Controller {

    @PostMapping("/list")
    public ResponseEntity<?> getList(@RequestBody PA01001ListReq request) {
        // 생산계획 목록 조회
        return ResponseEntity.ok(service.getList(request));
    }

    @PostMapping("/detail")
    public ResponseEntity<?> getDetail(@RequestBody PA01001DetailReq request) {
        // 생산계획 상세 조회
        return ResponseEntity.ok(service.getDetail(request));
    }

    @PostMapping("/save")
    public ResponseEntity<?> save(@RequestBody PA01001SaveReq request) {
        // 생산계획 저장
        return ResponseEntity.ok(service.save(request));
    }
}
```

### 7.2 Sample Output

```yaml
# Generated by: s1-01-discovery-feature-inventory
# Stage: 1 - Discovery
# Phase: 1.1 - Feature Inventory
# Domain: PA
# Generated: 2026-01-07T10:30:00Z
# Model: claude-opus-4-5-20251101

metadata:
  generated_by: "s1-01-discovery-feature-inventory"
  generated_at: "2026-01-07T10:30:00Z"
  domain: "PA"
  source_path: "hallain/src/main/java/com/hallain/pa/"

summary:
  total_features: 3
  total_endpoints: 9
  total_controllers: 3
  by_complexity:
    low: 1
    medium: 2
    high: 0

features:
  - feature_id: "FEAT-PA-001"
    screen_id: "PA01001"
    name: "PA01001"
    complexity: "medium"
    endpoints:
      - path: "/pa/PA01001/list"
        method: "POST"
        controller: "PA01001Controller"
        method_name: "getList"
      - path: "/pa/PA01001/detail"
        method: "POST"
        controller: "PA01001Controller"
        method_name: "getDetail"
      - path: "/pa/PA01001/save"
        method: "POST"
        controller: "PA01001Controller"
        method_name: "save"
    controllers:
      - class: "PA01001Controller"
        file: "src/main/java/com/hallain/pa/controller/PA01001Controller.java"
        methods_count: 3
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| 빈 도메인 | Controller 0개 | ERROR: No controllers found |
| Screen ID 없음 | 비표준 Controller명 | Fallback: Controller 클래스명으로 그룹핑 |
| 중복 URL | 동일 path 2개 | WARNING + 첫 번째만 유지 |
| 대규모 도메인 | PA (2,895 files) | 정상 처리 (timeout 연장 가능) |

---

## Version History

### v1.1.0 (2026-01-08)
- **Step 6: Schema Validation 추가**
- 스키마 기반 출력 검증 (s1-01-feature-inventory.schema.yaml 참조)
- 10개 검증 규칙 정의 (V001~V010)
- validation-errors.yaml 출력 명세 추가

### v1.0.0 (2026-01-07)
- Initial version
- Spring MVC Controller 스캔 지원
- Screen ID 기반 Feature 그룹핑
- MiPlatform 패턴 인식
