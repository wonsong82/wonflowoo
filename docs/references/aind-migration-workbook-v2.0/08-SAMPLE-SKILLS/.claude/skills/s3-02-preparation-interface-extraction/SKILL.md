---
name: s3-02-preparation-interface-extraction
description: Use when designing interfaces to break circular dependencies between domains, defining cross-domain API contracts, or preparing interface specifications for dependency resolution (project)
---

# Interface Extraction

> **Skill ID**: S3-02
> **Skill Type**: Generation (순환 의존성 해소 인터페이스 설계)
> **Stage**: 3 - Preparation
> **Phase**: 3.2 - Interface Extraction

## 1. Overview

### 1.1 Purpose

S3-01에서 식별된 **순환 의존성 체인**을 해소하기 위한 **인터페이스를 설계**하고, 도메인 간 **API 계약(Contract)**을 정의합니다. 이 인터페이스는 Spring Boot 마이그레이션 시 의존성 역전(DI)을 통해 순환 참조를 끊는 핵심 역할을 합니다.

**생성 대상:**
- Provider Interface 명세
- DTO (Data Transfer Object) 정의
- Cross-domain Contract 문서

**사용 용도:**
- S4-01 Project Scaffold에서 공통 모듈 생성
- S4-03 Domain Batch에서 Interface 구현
- 의존성 역전 패턴 적용

### 1.2 Generation Scope

| Aspect | Included | Excluded |
|--------|----------|----------|
| Interfaces | Provider interfaces (순환 해소용) | Internal service interfaces |
| DTOs | Cross-domain transfer objects | Domain-internal VOs |
| Contracts | API contracts (method signatures) | Implementation details |

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Minimal Interface** | 필요한 메서드만 정의 | 과도한 인터페이스는 결합도 증가 |
| **Domain Agnostic DTO** | 도메인 중립적 DTO 설계 | 양방향 의존성 방지 |
| **Contract First** | 명세 선 정의, 구현 후 | 명확한 계약 보장 |
| **Spring Compatible** | Spring DI 패턴 호환 | 구현 용이성 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S3-02는 순환 의존성 해소를 위한 인터페이스를 설계하며, **SQL 트랜잭션 경계가 인터페이스 설계에 영향**

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s3-01-preparation-dependency-graph` | 순환 의존성 체인 및 해결 계획 제공 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s3-04-preparation-architecture-design` | 공통 모듈 패키지 구조에 인터페이스 반영 |
| `s4-01-generation-project-scaffold` | Interface 파일 생성 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S3-01"
    skill_name: "s3-01-preparation-dependency-graph"
    dependency_type: "input"
    artifacts:
      - "circular-dependencies.yaml"
      - "resolution-plan.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| circular_dependencies | file | `work/specs/stage3-outputs/phase1/circular-dependencies.yaml` | YAML | Yes |
| resolution_plan | file | `work/specs/stage3-outputs/phase1/resolution-plan.yaml` | YAML | Yes |
| domain_specs | directory | `work/specs/stage2-outputs/phase4/` | YAML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Read | - | Resolution plan 읽기 |
| Write | - | Interface 명세 생성 |

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: parallel
  unit: circular_chain
  parallelization:
    max_parallel: 5
    batch_size: 5
    timeout_minutes: 60
    retry_on_failure: 2
```

### 3.2 Generation Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Load        │────▶│ Analyze      │────▶│ Design       │────▶│ Generate     │
│  Resolution  │     │ Weak Link    │     │ Interface    │     │ Contracts    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 3.3 Process Steps

#### Step 1: Load Resolution Plan

**Description:** 순환 의존성 해결 계획 로드

**Sub-steps:**
1. resolution-plan.yaml 로드
2. strategy가 "interface_extraction"인 항목 필터링
3. 우선순위별 정렬

**Validation:** interface_extraction 대상 존재

**Outputs:**
- Interface 추출 대상 목록

---

#### Step 2: Analyze Weak Link

**Description:** 약한 링크 상세 분석

**Sub-steps:**
1. 해당 도메인 Spec에서 외부 호출 상세 추출
2. 호출되는 메서드 시그니처 분석
3. 파라미터/리턴 타입 추출
4. 호출 빈도 및 중요도 평가

**Analysis Example:**
```yaml
# MM → PA 약한 링크 분석
weak_link:
  from: "MM"
  to: "PA"
  calls:
    - class: "PAService"
      method: "getProductionPlan"
      parameters:
        - name: "siteCd"
          type: "String"
        - name: "yyyymm"
          type: "String"
      return_type: "List<PAProductionPlanVO>"
      call_count: 5
```

**Validation:** 모든 메서드 시그니처 추출 완료

**Outputs:**
- 메서드 시그니처 목록

---

#### Step 3: Design Interface

**Description:** Provider Interface 설계

**Sub-steps:**
1. Interface 네이밍: `{Domain}Provider` 또는 `{Function}Provider`
2. 메서드 시그니처 설계 (도메인 중립적)
3. DTO 설계 (양쪽 도메인에서 사용 가능)
4. Package 결정: `com.hallain.common.provider`

**Design Patterns:**
```java
// Provider Interface 패턴
public interface ProductionPlanProvider {
    List<ProductionPlanDTO> getProductionPlan(String siteCd, String yyyymm);
    PlanStatusDTO getPlanStatus(String planId);
}

// DTO 패턴 (도메인 중립적)
public class ProductionPlanDTO {
    private String planId;
    private String siteCd;
    private String yyyymm;
    private BigDecimal totalQty;
    // getters, setters
}
```

**Naming Conventions:**
| Element | Pattern | Example |
|---------|---------|---------|
| Interface | `{Function}Provider` | `ProductionPlanProvider` |
| DTO | `{Entity}DTO` | `ProductionPlanDTO` |
| Package | `com.hallain.common.provider` | - |

**Validation:** 인터페이스 및 DTO 설계 완료

**Outputs:**
- Interface 명세
- DTO 명세

---

#### Step 4: Generate Contracts

**Description:** Cross-domain Contract 문서 생성

**Sub-steps:**
1. Interface 명세 YAML 생성
2. DTO 명세 YAML 생성
3. 구현 가이드 포함
4. cross-domain-contracts.yaml 통합

**Validation:** YAML 문법 검증

**Outputs:**
- `interfaces/{interface-name}.yaml`
- `cross-domain-contracts.yaml`

---

#### Step 5: Schema Validation

**Description:** 생성된 Interface 명세 및 Contract 파일이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | interfaces/*.yaml root | metadata, interface, dtos 필수 키 존재 | ERROR | Yes |
| V002 | cross-domain-contracts.yaml root | metadata, summary, interfaces, dtos 필수 키 존재 | ERROR | Yes |
| V003 | metadata.generated_by | 정확히 "s3-02-preparation-interface-extraction" | ERROR | Yes |
| V004 | interface.name | 패턴: ^[A-Z][a-zA-Z]+Provider$ | ERROR | Yes |
| V005 | dtos[].name | 패턴: ^[A-Z][a-zA-Z]+DTO$ | ERROR | Yes |
| V006 | interface.package | 패턴: ^com\.hallain\. | ERROR | Yes |
| V007 | metadata.cycle_id | 패턴: ^CYC-\d{3}$ | ERROR | Yes |
| V008 | interface.methods[].return_type | 존재 및 비어있지 않음 | ERROR | Yes |
| V009 | interfaces | 모든 interface_extraction 체인 처리 | ERROR | Yes |
| V010 | dtos[].fields | 모든 DTO 필드 정의 | WARNING | No |

**Sub-steps:**
1. 개별 interface 파일 스키마 검증
2. cross-domain-contracts.yaml 스키마 검증
3. Interface/DTO 네이밍 컨벤션 검증
4. 오류 발생 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, Interface 재설계 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.4 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | 메서드 5개 이상 | Interface 분할 검토 | 단일 Interface |
| DP-2 | 복잡한 VO 리턴 | DTO 변환 필요 | 기본 타입 사용 |
| DP-3 | 양방향 호출 | 2개 Interface 생성 | 단방향 Interface |
| DP-4 | CM 도메인 대상 | common에 직접 추가 | provider 패키지 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage3-outputs/phase2/"

  structure:
    - "interfaces/"
    - "cross-domain-contracts.yaml"
```

### 4.2 Output Files

| File | Type | Purpose | Required |
|------|------|---------|----------|
| interfaces/{name}.yaml | YAML | 개별 Interface 명세 | Yes |
| cross-domain-contracts.yaml | YAML | 전체 Contract 통합 | Yes |

### 4.3 File Header

```yaml
# Generated by: s3-02-preparation-interface-extraction
# Stage: 3 - Preparation
# Phase: 3.2 - Interface Extraction
# Cycle: ${CYCLE_ID}
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
```

### 4.4 Output Schemas

#### interfaces/{interface-name}.yaml

```yaml
# interfaces/production-plan-provider.yaml
metadata:
  generated_by: "s3-02-preparation-interface-extraction"
  generated_at: "2026-01-07T13:00:00Z"
  cycle_id: "CYC-001"
  chain: "PA → MM → PA"

interface:
  name: "ProductionPlanProvider"
  package: "com.hallain.common.provider"
  purpose: "PA 도메인의 생산계획 정보를 MM 도메인에 제공"

  breaks_dependency:
    from: "MM"
    to: "PA"
    original_calls:
      - "PAService.getProductionPlan"
      - "PAService.getPlanStatus"

  methods:
    - name: "getProductionPlan"
      description: "사이트/년월별 생산계획 조회"
      parameters:
        - name: "siteCd"
          type: "String"
          description: "사이트 코드"
        - name: "yyyymm"
          type: "String"
          description: "년월 (YYYYMM)"
      return_type: "List<ProductionPlanDTO>"
      throws: []

    - name: "getPlanStatus"
      description: "생산계획 상태 조회"
      parameters:
        - name: "planId"
          type: "String"
          description: "계획 ID"
      return_type: "PlanStatusDTO"
      throws:
        - "PlanNotFoundException"

  implementation:
    provider_domain: "PA"
    provider_class: "PAProductionPlanProviderImpl"
    consumer_domain: "MM"
    injection_type: "constructor"

dtos:
  - name: "ProductionPlanDTO"
    package: "com.hallain.common.dto"
    description: "생산계획 정보 전송 객체"
    fields:
      - name: "planId"
        type: "String"
        description: "계획 ID"
      - name: "siteCd"
        type: "String"
        description: "사이트 코드"
      - name: "yyyymm"
        type: "String"
        description: "년월"
      - name: "totalQty"
        type: "BigDecimal"
        description: "총수량"
      - name: "status"
        type: "String"
        description: "상태 (DRAFT, CONFIRMED, CLOSED)"

  - name: "PlanStatusDTO"
    package: "com.hallain.common.dto"
    description: "계획 상태 정보"
    fields:
      - name: "planId"
        type: "String"
      - name: "status"
        type: "String"
      - name: "lastModified"
        type: "LocalDateTime"
      - name: "modifiedBy"
        type: "String"

exceptions:
  - name: "PlanNotFoundException"
    package: "com.hallain.common.exception"
    extends: "RuntimeException"
    message_pattern: "Plan not found: {planId}"

migration_guide:
  step_1:
    action: "Create interface and DTOs in common module"
    files:
      - "common/src/main/java/com/hallain/common/provider/ProductionPlanProvider.java"
      - "common/src/main/java/com/hallain/common/dto/ProductionPlanDTO.java"
      - "common/src/main/java/com/hallain/common/dto/PlanStatusDTO.java"

  step_2:
    action: "Implement interface in PA domain"
    files:
      - "pa/src/main/java/com/hallain/pa/provider/PAProductionPlanProviderImpl.java"
    notes: "기존 PAService 로직 재사용"

  step_3:
    action: "Update MM domain to use interface"
    changes:
      - file: "mm/src/main/java/com/hallain/mm/service/MMService.java"
        before: "@Autowired private PAService paService;"
        after: "@Autowired private ProductionPlanProvider productionPlanProvider;"

  step_4:
    action: "Remove direct PA dependency from MM pom.xml"
    changes:
      - file: "mm/pom.xml"
        action: "Remove <dependency>pa</dependency>"
```

#### cross-domain-contracts.yaml

```yaml
# cross-domain-contracts.yaml
metadata:
  generated_by: "s3-02-preparation-interface-extraction"
  generated_at: "2026-01-07T13:00:00Z"
  total_interfaces: 2
  total_dtos: 4

summary:
  cycles_resolved: 2
  interfaces_created: 2
  dtos_created: 4
  common_package: "com.hallain.common"

interfaces:
  - name: "ProductionPlanProvider"
    file: "interfaces/production-plan-provider.yaml"
    cycle_id: "CYC-001"
    breaks: "MM → PA"
    methods_count: 2
    dtos_count: 2

  - name: "AuthorizationProvider"
    file: "interfaces/authorization-provider.yaml"
    cycle_id: "CYC-002"
    breaks: "PE → SM"
    methods_count: 2
    dtos_count: 2

dtos:
  - name: "ProductionPlanDTO"
    used_by: ["ProductionPlanProvider"]
    fields_count: 5

  - name: "PlanStatusDTO"
    used_by: ["ProductionPlanProvider"]
    fields_count: 4

  - name: "PermissionDTO"
    used_by: ["AuthorizationProvider"]
    fields_count: 3

  - name: "RoleDTO"
    used_by: ["AuthorizationProvider"]
    fields_count: 4

dependency_inversion_map:
  - consumer: "MM"
    provider: "PA"
    interface: "ProductionPlanProvider"
    injection_point: "MMService constructor"

  - consumer: "PE"
    provider: "SM"
    interface: "AuthorizationProvider"
    injection_point: "PEService constructor"

package_structure:
  common:
    provider:
      - "ProductionPlanProvider.java"
      - "AuthorizationProvider.java"
    dto:
      - "ProductionPlanDTO.java"
      - "PlanStatusDTO.java"
      - "PermissionDTO.java"
      - "RoleDTO.java"
    exception:
      - "PlanNotFoundException.java"
      - "UnauthorizedException.java"

generation_ready:
  interfaces: true
  dtos: true
  ready_for_s4: true
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| all_chains_addressed | structural | 모든 interface_extraction 체인 처리 | ERROR | Yes |
| interface_spec_valid | content | 메서드 시그니처 완전 | ERROR | Yes |
| dto_fields_complete | content | 모든 DTO 필드 정의 | WARNING | No |
| yaml_syntax | structural | YAML 파싱 오류 없음 | ERROR | Yes |

### 5.2 Manual Reviews

| Review | Reviewer | Criteria | Required |
|--------|----------|----------|----------|
| Interface design | Architect | SOLID 원칙 준수 | Yes |
| DTO field mapping | Tech Lead | Legacy VO 매핑 정확성 | No |

### 5.3 Gate Criteria

```yaml
gate_criteria:
  id: "G3.2"
  name: "Interface Extraction Gate"
  threshold: 70
  metrics:
    - metric: "all_circular_addressed"
      weight: 0.5
      target: "100%"
      formula: "interfaces_created / cycles_with_interface_strategy"
    - metric: "interface_specs_valid"
      weight: 0.3
      target: "true"
      formula: "all interfaces have method signatures and DTOs"
    - metric: "contracts_documented"
      weight: 0.2
      target: "true"
      formula: "cross-domain-contracts.yaml generated"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Resolution plan missing | 입력 없음 | S3-01 미완료 | S3-01 완료 후 재실행 | Yes |
| Complex VO structure | DTO 설계 실패 | 중첩 객체 | 플랫 DTO + 별도 조회 | No |
| Circular DTO | DTO 간 참조 순환 | 설계 오류 | DTO 분리 | Yes |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Interface 설계 실패 | critical | 수동 설계 필요 | Architect |
| DTO 복잡도 높음 | major | 단순화 검토 | Tech Lead |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 특정 체인 실패 | 해당 체인만 재설계 | Chain |
| 전체 실패 | Resolution plan 검토 | Phase |

---

## 7. Examples

### 7.1 Sample Input

**resolution-plan.yaml (일부):**
```yaml
resolutions:
  - cycle_id: "CYC-001"
    chain: "PA → MM → PA"
    strategy: "interface_extraction"
    analysis:
      weak_link: "MM → PA"
    solution:
      interface_name: "ProductionPlanProvider"
```

**PA domain spec (dependencies.external):**
```yaml
# MM 도메인이 PA를 호출하는 부분
external_callers:
  - domain: "MM"
    calls:
      - class: "PAService"
        method: "getProductionPlan"
        signature: "List<PAProductionPlanVO> getProductionPlan(String siteCd, String yyyymm)"
```

### 7.2 Sample Output

위의 4.4 Output Schema 섹션 참조

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| 메서드 없음 | 호출 없는 의존성 | 빈 Interface (WARNING) |
| 10+ 메서드 | 많은 호출 | Interface 분할 권장 |
| 기본 타입만 | String, int 리턴 | DTO 없이 Interface만 |
| void 리턴 | 상태 변경 메서드 | void 메서드 포함 |

---

## Version History

### v1.1.0 (2026-01-08)
- Step 5: Schema Validation 추가
- s3-02-interface-extraction.schema.yaml 스키마 참조
- 10개 검증 규칙 적용 (V001-V010)

### v1.0.0 (2026-01-07)
- Initial version
- Provider Interface 설계 패턴
- Cross-domain DTO 정의
- Migration guide 포함
