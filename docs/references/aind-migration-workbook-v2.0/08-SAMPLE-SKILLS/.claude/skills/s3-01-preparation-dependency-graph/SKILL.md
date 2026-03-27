---
name: s3-01-preparation-dependency-graph
description: Use when analyzing inter-domain dependencies for migration, identifying circular dependency chains, or designing dependency resolution strategies before code generation (project)
---

# Dependency Graph Analysis

> **Skill ID**: S3-01
> **Skill Type**: Analysis (도메인 간 의존성 분석)
> **Stage**: 3 - Preparation
> **Phase**: 3.1 - Dependency Graph Analysis

## 1. Overview

### 1.1 Purpose

Stage 2에서 완료된 모든 도메인의 Specification을 분석하여 **도메인 간 의존성 그래프**를 생성하고, **순환 의존성(Circular Dependency)**을 식별하여 해결 전략을 수립합니다.

**분석 대상:**
- 도메인 간 Service 호출 의존성
- 도메인 간 Entity/VO 참조 관계
- SQL 테이블 간 FK 관계 (간접 의존성)
- Common/Shared 모듈 의존성

**추출 정보:**
- 12개 도메인의 완전한 의존성 그래프
- 순환 의존성 체인 목록
- 각 체인별 해결 전략 (Interface Extraction, Event, Merge)

### 1.2 Analysis Scope

| Aspect | In Scope | Out of Scope |
|--------|----------|--------------|
| Dependencies | 도메인 간 (inter-domain) | 도메인 내 (intra-domain) |
| Depth | Service, Entity, SQL 레벨 | 메서드 파라미터 레벨 |
| Domains | 12개 전체 도메인 | 외부 시스템 |

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Completeness** | 12개 도메인 전체 분석 | 누락된 도메인은 순환 의존성 미탐지 |
| **Directionality** | A→B 방향성 명확화 | 해결 전략 결정에 필수 |
| **Severity** | 순환 체인별 심각도 분류 | 해결 우선순위 결정 |
| **Resolution Focus** | 각 체인에 해결 전략 제안 | S3-02 Interface Extraction 입력 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S3-01은 도메인 간 의존성을 분석하며, **SQL/Mapper 의존성이 실제 데이터 흐름을 결정**

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s2-04-validation-spec-completion` | 검증 완료된 Spec 제공 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s3-02-preparation-interface-extraction` | 순환 의존성 해소 인터페이스 설계 |
| `s3-04-preparation-architecture-design` | 아키텍처 설계 시 의존성 반영 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S2-04"
    skill_name: "s2-04-validation-spec-completion"
    dependency_type: "input"
    artifact: "completed main.yaml per domain"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| completed_specs | directory | `work/specs/stage2-outputs/phase4/` | YAML | Yes |
| domain_list | reference | Assessment data (12 domains) | - | Yes |

### 2.3 Domain List

```yaml
domains:
  - id: "PA"
    name: "Production"
    priority: "P2"
    files: 2895
  - id: "SC"
    name: "Supply Chain"
    priority: "P2"
    files: 824
  - id: "MM"
    name: "Materials"
    priority: "P2"
    files: 878
  - id: "SM"
    name: "System Management"
    priority: "P1"
    files: 645
  - id: "PE"
    name: "Personnel"
    priority: "P2"
    files: 582
  - id: "EA"
    name: "Enterprise Application"
    priority: "P2"
    files: 592
  - id: "SA"
    name: "Sales"
    priority: "P2"
    files: 595
  - id: "EB"
    name: "E-Board"
    priority: "P1"
    files: 753
  - id: "QM"
    name: "Quality Management"
    priority: "P3"
    files: 61
  - id: "BS"
    name: "Business Support"
    priority: "P3"
    files: 186
  - id: "CM"
    name: "Common"
    priority: "P0"
    files: 249
  - id: "benitware"
    name: "Framework"
    priority: "P0"
    files: 92
```

### 2.4 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Read | - | YAML Spec 파일 읽기 |
| Glob | - | 도메인별 Spec 파일 탐색 |

**Access:**
- Stage 2 완료된 Spec 디렉토리

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: sequential
  unit: none  # 전체 그래프 분석
  parallelization:
    enabled: false
    reason: "Complete graph required for cycle detection"
  lifecycle:
    timeout_minutes: 120
    retry_on_failure: 2
```

### 3.2 Analysis Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Load All    │────▶│ Build Dep    │────▶│ Detect       │────▶│ Resolution   │
│  Domain Specs│     │ Graph        │     │ Cycles       │     │ Strategy     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 3.3 Process Steps

#### Step 1: Load Domain Specifications

**Description:** 12개 도메인의 완료된 Spec 로드

**Sub-steps:**
1. `work/specs/stage2-outputs/phase4/` 하위 모든 도메인 디렉토리 탐색
2. 각 도메인의 main.yaml 로드
3. dependencies.external 섹션 추출
4. Cross-domain 참조 목록 구성

**Validation:** 12개 도메인 모두 로드 완료

**Outputs:**
- 도메인별 외부 의존성 목록

---

#### Step 2: Build Dependency Graph

**Description:** 방향성 그래프 구성

**Sub-steps:**
1. 노드 생성: 각 도메인 = 1 노드
2. 엣지 생성: 의존성 방향 (A → B = A가 B를 참조)
3. 엣지 속성 부여:
   - dependency_type: service | entity | sql
   - call_count: 참조 횟수
   - critical: 핵심 기능 여부

**Graph Representation:**
```yaml
graph:
  nodes:
    - id: "PA"
      type: "domain"
    - id: "MM"
      type: "domain"

  edges:
    - from: "PA"
      to: "MM"
      type: "service"
      weight: 15
      calls:
        - "MMService.getMaterialList"
        - "MMService.getStockInfo"
```

**Validation:** 모든 외부 의존성이 엣지로 표현됨

**Outputs:**
- `dependency-graph.yaml`

---

#### Step 3: Detect Circular Dependencies

**Description:** 순환 의존성 체인 탐지

**Sub-steps:**
1. DFS (Depth-First Search) 기반 사이클 탐지
2. 모든 순환 체인 수집
3. 체인별 참여 도메인 목록 생성
4. 체인별 심각도 평가:
   - **Critical**: PA-MM (34.6% + 10.5% = 45.1%)
   - **Major**: Core 도메인 포함 (SM, PE, EA)
   - **Minor**: Utility 도메인만

**Cycle Detection Algorithm:**
```
for each domain D in graph:
    visited = {D}
    dfs(D, visited, path=[D])

def dfs(current, visited, path):
    for neighbor in graph[current].dependencies:
        if neighbor in path:
            # Cycle found: path[path.index(neighbor):] + [neighbor]
            record_cycle(path[path.index(neighbor):] + [neighbor])
        elif neighbor not in visited:
            visited.add(neighbor)
            dfs(neighbor, visited, path + [neighbor])
```

**Validation:** 모든 사이클 식별 완료

**Outputs:**
- `circular-dependencies.yaml`

---

#### Step 4: Resolution Strategy

**Description:** 순환 의존성 해결 전략 수립

**Sub-steps:**
1. 각 순환 체인 분석
2. 해결 전략 선택:
   - **Interface Extraction**: 가장 약한 링크에 인터페이스 삽입
   - **Event-Based**: 비동기 이벤트로 분리
   - **Module Merge**: 강결합 도메인 통합 검토
3. 우선순위 결정 (Critical → Major → Minor)

**Resolution Strategy Matrix:**
| Chain Pattern | Recommended Strategy | Rationale |
|---------------|----------------------|-----------|
| PA → MM → PA | Interface Extraction | 두 핵심 도메인, 명확한 경계 필요 |
| SM → PE → SM | Interface Extraction | Admin 도메인, 권한 관리 인터페이스 |
| A → B (weak coupling) | Event-Based | 비동기 처리 가능 |
| A ↔ B (tight coupling) | Module Merge | 분리 비용 > 통합 비용 |

**Validation:** 모든 순환 체인에 전략 할당

**Outputs:**
- `resolution-plan.yaml`

---

#### Step 5: Schema Validation

**Description:** 생성된 모든 출력 파일이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | dependency-graph.yaml root | metadata, summary, nodes, edges 필수 키 존재 | ERROR | Yes |
| V002 | circular-dependencies.yaml root | metadata, summary, cycles 필수 키 존재 | ERROR | Yes |
| V003 | resolution-plan.yaml root | metadata, summary, resolutions 필수 키 존재 | ERROR | Yes |
| V004 | metadata.generated_by | 정확히 "s3-01-preparation-dependency-graph" | ERROR | Yes |
| V005 | edges[].dependency_type | enum: service, entity, sql, utility | ERROR | Yes |
| V006 | cycles[].severity | enum: critical, major, minor | ERROR | Yes |
| V007 | resolutions[].strategy | enum: interface_extraction, event_based, module_merge | ERROR | Yes |
| V008 | edges[].id | 패턴: ^E-\d{3}$ | ERROR | Yes |
| V009 | cycles[].id | 패턴: ^CYC-\d{3}$ | ERROR | Yes |
| V010 | nodes | 12개 도메인 모두 로드 | ERROR | Yes |
| V011 | summary | severity별 합계 == total_cycles | WARNING | No |
| V012 | resolutions | 모든 cycle에 resolution 할당 | WARNING | No |

**Sub-steps:**
1. dependency-graph.yaml 스키마 검증
2. circular-dependencies.yaml 스키마 검증
3. resolution-plan.yaml 스키마 검증
4. 오류 발생 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재분석 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.4 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | 순환 의존성 없음 | PASS (resolution 불필요) | 해결 전략 수립 |
| DP-2 | Critical 체인 존재 | Human Review 권장 | 자동 진행 |
| DP-3 | PA-MM 순환 존재 | Interface Extraction 우선 | 일반 전략 적용 |
| DP-4 | 3개 이상 도메인 체인 | 복잡도 WARNING | 2-노드 체인 처리 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage3-outputs/phase1/"

  example: "work/specs/stage3-outputs/phase1/"
```

### 4.2 Output Files

| File | Type | Purpose | Required |
|------|------|---------|----------|
| dependency-graph.yaml | YAML | 전체 의존성 그래프 | Yes |
| circular-dependencies.yaml | YAML | 순환 의존성 목록 | Yes |
| resolution-plan.yaml | YAML | 해결 전략 계획 | Yes |

### 4.3 File Header

```yaml
# Generated by: s3-01-preparation-dependency-graph
# Stage: 3 - Preparation
# Phase: 3.1 - Dependency Graph Analysis
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
```

### 4.4 Output Schemas

#### dependency-graph.yaml

```yaml
# dependency-graph.yaml
metadata:
  generated_by: "s3-01-preparation-dependency-graph"
  generated_at: "2026-01-07T12:00:00Z"
  total_domains: 12
  total_edges: 45

summary:
  nodes: 12
  edges: 45
  average_dependencies: 3.75
  max_outgoing: { domain: "PA", count: 8 }
  max_incoming: { domain: "CM", count: 11 }

nodes:
  - id: "PA"
    name: "Production"
    priority: "P2"
    outgoing_count: 8
    incoming_count: 3

  - id: "CM"
    name: "Common"
    priority: "P0"
    outgoing_count: 0
    incoming_count: 11

edges:
  - id: "E-001"
    from: "PA"
    to: "MM"
    direction: "PA → MM"
    dependency_type: "service"
    weight: 15
    critical: true
    calls:
      - service: "MMService"
        method: "getMaterialList"
        call_count: 8
      - service: "MMService"
        method: "getStockInfo"
        call_count: 7

  - id: "E-002"
    from: "MM"
    to: "PA"
    direction: "MM → PA"
    dependency_type: "service"
    weight: 5
    critical: true
    calls:
      - service: "PAService"
        method: "getProductionPlan"
        call_count: 5

  - id: "E-003"
    from: "PA"
    to: "CM"
    direction: "PA → CM"
    dependency_type: "utility"
    weight: 25
    critical: false
    calls:
      - service: "CommonService"
        method: "getCodeList"
        call_count: 25

adjacency_matrix:
  # PA MM SC SM PE EA SA EB QM BS CM BW
  PA: [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1]
  MM: [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1]
  SC: [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
  SM: [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1]
  PE: [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1]
  EA: [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1]
  SA: [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1]
  EB: [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1]
  QM: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
  BS: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
  CM: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
  BW: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

#### circular-dependencies.yaml

```yaml
# circular-dependencies.yaml
metadata:
  generated_by: "s3-01-preparation-dependency-graph"
  generated_at: "2026-01-07T12:00:00Z"

summary:
  total_cycles: 3
  critical_cycles: 1
  major_cycles: 1
  minor_cycles: 1

cycles:
  - id: "CYC-001"
    severity: "critical"
    domains: ["PA", "MM"]
    chain: "PA → MM → PA"
    length: 2
    total_calls: 20
    edges:
      - { from: "PA", to: "MM", weight: 15 }
      - { from: "MM", to: "PA", weight: 5 }
    impact:
      combined_file_percentage: 45.1
      blocking_wave: "Wave 6 (SC, MM)"
    notes: "핵심 순환 의존성 - 최우선 해결 필요"

  - id: "CYC-002"
    severity: "major"
    domains: ["SM", "PE"]
    chain: "SM → PE → SM"
    length: 2
    total_calls: 8
    edges:
      - { from: "SM", to: "PE", weight: 5 }
      - { from: "PE", to: "SM", weight: 3 }
    impact:
      combined_file_percentage: 14.7
      blocking_wave: "Wave 3 (SM, PE)"
    notes: "Admin 도메인 권한 관리 순환"

  - id: "CYC-003"
    severity: "minor"
    domains: ["EA", "SA"]
    chain: "EA → SA → EA"
    length: 2
    total_calls: 4
    edges:
      - { from: "EA", to: "SA", weight: 2 }
      - { from: "SA", to: "EA", weight: 2 }
    impact:
      combined_file_percentage: 14.2
      blocking_wave: "Wave 4 (EA, SA)"
    notes: "Business 도메인 통합 가능성 검토"
```

#### resolution-plan.yaml

```yaml
# resolution-plan.yaml
metadata:
  generated_by: "s3-01-preparation-dependency-graph"
  generated_at: "2026-01-07T12:00:00Z"

summary:
  total_resolutions: 3
  interface_extraction: 2
  event_based: 1
  module_merge: 0

resolutions:
  - cycle_id: "CYC-001"
    severity: "critical"
    chain: "PA → MM → PA"
    strategy: "interface_extraction"
    priority: 1

    analysis:
      weak_link: "MM → PA"
      reason: "MM의 PA 호출이 적고 (5회), 주로 생산계획 조회 목적"

    solution:
      action: "Extract ProductionPlanProvider interface"
      interface_name: "ProductionPlanProvider"
      package: "com.hallain.common.provider"
      methods:
        - signature: "getProductionPlan(String siteCd, String yyyymm)"
          return_type: "List<ProductionPlanDTO>"
        - signature: "getPlanStatus(String planId)"
          return_type: "PlanStatusDTO"

      implementation:
        provider_in: "PA domain (implements interface)"
        consumer_in: "MM domain (uses interface)"
        injection: "Spring @Autowired"

      migration_order:
        1: "Create interface in common module"
        2: "Implement in PA domain"
        3: "Update MM domain to use interface"
        4: "Remove direct PA dependency from MM"

    estimated_effort: "4-8 hours"
    wave_impact: "Wave 6 전 완료 필요"

  - cycle_id: "CYC-002"
    severity: "major"
    chain: "SM → PE → SM"
    strategy: "interface_extraction"
    priority: 2

    analysis:
      weak_link: "PE → SM"
      reason: "PE의 SM 호출은 주로 권한 검증 목적"

    solution:
      action: "Extract AuthorizationProvider interface"
      interface_name: "AuthorizationProvider"
      package: "com.hallain.common.provider"
      methods:
        - signature: "checkPermission(String userId, String menuId)"
          return_type: "boolean"
        - signature: "getUserRoles(String userId)"
          return_type: "List<RoleDTO>"

    estimated_effort: "2-4 hours"
    wave_impact: "Wave 3 전 완료 필요"

  - cycle_id: "CYC-003"
    severity: "minor"
    chain: "EA → SA → EA"
    strategy: "event_based"
    priority: 3

    analysis:
      pattern: "비동기 처리 가능한 호출 패턴"
      reason: "EA→SA: 주문 알림, SA→EA: 견적 등록 - 실시간 필요 없음"

    solution:
      action: "Introduce domain events"
      events:
        - name: "OrderCreatedEvent"
          publisher: "EA"
          subscriber: "SA"
        - name: "QuotationRegisteredEvent"
          publisher: "SA"
          subscriber: "EA"

    estimated_effort: "4-6 hours"
    wave_impact: "Wave 4에서 적용 가능"

execution_order:
  1: { resolution_id: "CYC-001", reason: "Critical - PA/MM Wave 선행" }
  2: { resolution_id: "CYC-002", reason: "Major - Wave 3 선행" }
  3: { resolution_id: "CYC-003", reason: "Minor - Wave 4 적용" }
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| all_domains_loaded | structural | 12개 도메인 로드 | ERROR | Yes |
| graph_complete | structural | dependency-graph.yaml 생성 | ERROR | Yes |
| cycles_identified | content | circular-dependencies.yaml 생성 | ERROR | Yes |
| resolution_assigned | content | 모든 cycle에 strategy 할당 | WARNING | No |

### 5.2 Manual Reviews

| Review | Reviewer | Criteria | Required |
|--------|----------|----------|----------|
| Critical cycle review | Architect | PA-MM 해결 전략 적절성 | Yes |
| Interface design | Tech Lead | 인터페이스 명세 검토 | No |

### 5.3 Gate Criteria

```yaml
gate_criteria:
  id: "G3.1"
  name: "Dependency Analysis Gate"
  threshold: 70
  metrics:
    - metric: "all_domains_analyzed"
      weight: 0.4
      target: "12"
      formula: "count of analyzed domains"
    - metric: "circular_identified"
      weight: 0.3
      target: "true"
      formula: "circular-dependencies.yaml generated"
    - metric: "resolution_defined"
      weight: 0.3
      target: "100%"
      formula: "cycles with strategy / total cycles"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Domain missing | 11개 이하 로드 | Spec 미완료 | S2-04 확인 | Yes |
| Complex cycle | 3+ 도메인 체인 | 다중 순환 | 분할 분석 | No |
| No dependencies | 그래프 엣지 0 | external 섹션 누락 | Spec 검증 | Yes |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Domain < 12 | critical | Phase 중단 | Tech Lead |
| Critical cycle > 3 | major | Architecture review | Architect |
| No resolution | minor | Manual strategy 필요 | Tech Lead |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 부분 도메인 누락 | 누락 도메인 Spec 완료 후 재실행 | Phase |
| 복잡 순환 | 수동 분석 후 resolution 추가 | Task |

---

## 7. Examples

### 7.1 Sample Input

**domain/PA/main.yaml (dependencies 섹션):**
```yaml
dependencies:
  internal:
    - from: "PA01001Controller"
      to: "PA01001Service"
  external:
    - domain: "MM"
      class: "MMService"
      methods: ["getMaterialList", "getStockInfo"]
      reason: "자재 정보 조회"
    - domain: "CM"
      class: "CommonService"
      methods: ["getCodeList"]
      reason: "공통코드 조회"
```

### 7.2 Sample Output

위의 4.4 Output Schema 섹션 참조

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| 순환 없음 | 단방향 의존성만 | cycles: [], resolution 불필요 |
| Self-loop | PA → PA | cycles: [PA-PA], WARNING |
| 3-way cycle | PA → MM → SC → PA | 3-node cycle 기록, 분할 권장 |
| CM 의존성만 | 모두 CM만 참조 | cycles: [], CM은 leaf node |

---

## Version History

### v1.1.0 (2026-01-08)
- Step 5: Schema Validation 추가
- s3-01-dependency-graph.schema.yaml 스키마 참조
- 12개 검증 규칙 적용 (V001-V012)

### v1.0.0 (2026-01-07)
- Initial version
- 12 도메인 의존성 그래프 분석
- 순환 의존성 탐지 알고리즘
- 해결 전략 (Interface, Event, Merge) 제안
