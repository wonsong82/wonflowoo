---
name: s4-03-generation-domain-batch
description: Use when generating code for all features in batch mode, executing parallel code generation across domains, or running large-scale feature code generation after mini-pilot validation (project)
---

# Domain Batch Generation

> **Skill ID**: S4-03
> **Skill Type**: Generation (Parallel Batch)
> **Stage**: 4 - Generation
> **Phase**: 4.3 - Domain Batch Generation
> **Parallel With**: Phase 4.4 (Test Generation)

## 1. Overview

### 1.1 Purpose

Mini-Pilot에서 검증된 템플릿과 패턴을 사용하여 **전체 Feature의 코드를 대량 배치 생성**합니다. Priority 순서에 따라 도메인별로 실행하며, 최대 10개 병렬 세션으로 효율적으로 처리합니다.

**생성 대상:**
- 전체 도메인의 모든 Feature
- 6-Layer 코드 (Controller, Service, Repository, DTO, Entity, Mapper XML)

**병렬 실행:**
- Phase 4.4 (Test Generation)와 **동시 실행**
- Feature 생성 완료 시 테스트 생성 큐에 등록

### 1.2 Scope

**In Scope:**
- 모든 도메인의 전체 Feature 생성
- Priority 기반 실행 순서
- 병렬 세션 관리 (max 10)
- 체크포인트 및 진행 추적

**Out of Scope:**
- 테스트 코드 생성 (→ S4-04, 병렬 실행)
- 빌드 및 통합 (→ S4-05)
- 템플릿 수정 (Mini-Pilot에서 완료)

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Priority Ordered** | P0 → P1 → P2 → P3 순서 | 비즈니스 중요도 반영 |
| **Parallel Execution** | 최대 10 세션 병렬 | 처리 속도 극대화 |
| **Checkpoint Based** | 배치별 체크포인트 | 장애 복구 용이 |
| **Progress Tracked** | 실시간 진행 추적 | 가시성 확보 |

### 1.4 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s4-02-generation-mini-pilot` | 검증된 템플릿 필요 |
| `s4-01-generation-project-scaffold` | 프로젝트 구조 필요 |

**Parallel:**
| Skill | Coordination |
|-------|--------------|
| `s4-04-generation-test-generation` | Feature 완료 시 테스트 큐에 등록 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s4-05-generation-integration-build` | 생성 완료 후 통합 빌드 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S4-02"
    skill_name: "s4-02-generation-mini-pilot"
    status: "completed"
    gate_passed: "G4.2"
    artifacts:
      - "validated templates"
      - "ready_for_batch: true"

  - skill_id: "S4-01"
    skill_name: "s4-01-generation-project-scaffold"
    status: "completed"
    artifacts:
      - "next-hallain/"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| project | directory | `next-hallain/` | Java/Gradle | Yes |
| all_specs | directory | `work/specs/stage2-outputs/phase4/` | YAML | Yes |
| refined_templates | directory | `work/specs/stage3-outputs/phase5/` | YAML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Task | - | 병렬 세션 디스패치 |
| Write | - | 코드 파일 생성 |
| Bash | - | 컴파일 검증 |

**Resources:**
- 최대 10개 병렬 세션
- 세션당 타임아웃 60분

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
    checkpoint_frequency: "per_batch"
    session_affinity: "domain"

task:
  naming_pattern: "GEN-{FEAT_ID}"
  granularity: feature
```

### 3.1.1 Execution Modes (v1.2.0)

스킬 실행 시 범위와 Phase 분리 방식을 선택할 수 있습니다.

```yaml
execution_modes:
  full_batch:
    description: "전체 Feature 대상 배치 생성"
    phase_separation: "strict"  # PHASE 1 전체 완료 후 PHASE 2
    scope: "all_features"
    use_case: "최종 프로덕션 마이그레이션"
    workflow:
      - "PHASE 1: 전체 Query 이관 (1,300+ files)"
      - "Query Fidelity Gate (100%)"
      - "PHASE 2: 전체 Java 생성"

  incremental_batch:
    description: "검증 완료 Feature만 대상"
    phase_separation: "domain"  # 도메인별 Query→Java 순차
    scope: "validated_features_only"
    prerequisite: "Stage 2 검증 완료 Feature 존재"
    use_case: "점진적 검증 및 파일럿 확장"
    workflow:
      - "검증 완료 Feature 식별"
      - "도메인별: Query 이관 → Java 생성"
      - "Compilation 검증"

  decision_point:
    trigger: "스킬 실행 시작"
    prompt: "배치 실행 모드를 선택하세요"
    options:
      - label: "incremental_batch (권장)"
        description: "검증 완료 Feature만 - 점진적 검증에 적합"
      - label: "full_batch"
        description: "전체 Feature - 최종 마이그레이션용"
```

**Decision Point 사용:**
- 스킬 시작 시 `AskUserQuestion`으로 모드 선택
- 기본값: `incremental_batch` (안전한 점진적 접근)
- 사용자가 명시적으로 "전체" 또는 "full" 요청 시: `full_batch`

### 3.2 Batching Strategy

```yaml
batching_strategy:
  type: "priority_ordered"
  order:
    - priority: "P0"
      domains: ["benitware", "CM", "schedule"]
      estimated_features: 50
    - priority: "P1"
      domains: ["SM", "EB"]
      estimated_features: 200
    - priority: "P2"
      domains: ["PA", "MM", "SC", "EA", "SA", "PE"]
      estimated_features: 400
    - priority: "P3"
      domains: ["QM", "BS"]
      estimated_features: 50

  batch_assignment:
    method: "round_robin"
    session_affinity: "domain"  # 동일 도메인은 같은 세션
```

### 3.3 Parallel Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BATCH DISPATCHER                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Feature Queue (Priority Ordered)                                      │
│   ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                     │
│   │P0-01│ │P0-02│ │P0-03│ │P1-01│ │P1-02│ │ ... │                     │
│   └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘                     │
│      │       │       │       │       │       │                          │
│      └───────┼───────┼───────┼───────┼───────┘                          │
│              │       │       │       │                                  │
│              ▼       ▼       ▼       ▼                                  │
│   ┌──────────────────────────────────────────┐                         │
│   │          Session Pool (max 10)           │                         │
│   │  ┌─────┐ ┌─────┐ ┌─────┐     ┌─────┐   │                         │
│   │  │ S1  │ │ S2  │ │ S3  │ ... │ S10 │   │                         │
│   │  │ PA  │ │ MM  │ │ SC  │     │ QM  │   │                         │
│   │  └──┬──┘ └──┬──┘ └──┬──┘     └──┬──┘   │                         │
│   └─────┼───────┼───────┼───────────┼───────┘                         │
│         │       │       │           │                                  │
│         ▼       ▼       ▼           ▼                                  │
│   ┌──────────────────────────────────────────┐                         │
│   │         Checkpoint Manager               │                         │
│   │  - Save state per batch                  │                         │
│   │  - Enable resume on failure              │                         │
│   │  - Track progress                        │                         │
│   └──────────────────────────────────────────┘                         │
│                       │                                                 │
│                       ▼                                                 │
│   ┌──────────────────────────────────────────┐                         │
│   │         Progress Tracker                 │                         │
│   │  generation-progress.yaml                │                         │
│   └──────────────────────────────────────────┘                         │
│                       │                                                 │
│                       ▼                                                 │
│   ┌──────────────────────────────────────────┐                         │
│   │    Test Generation Queue (S4-04)         │                         │
│   │    Triggered on GEN-{FEAT_ID} complete   │                         │
│   └──────────────────────────────────────────┘                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.4 Process Steps

#### Step 1: Initialize Batch Queue

**Description:** Priority 순서대로 Feature 큐 초기화

**Sub-steps:**
1. Feature Inventory에서 전체 Feature 목록 로드
2. Priority 순서로 정렬 (P0 → P3)
3. 도메인별 그룹화
4. 배치 분할 (50 features/batch)

**Queue Structure:**
```yaml
batch_queue:
  total_features: 700
  batches:
    - batch_id: "B001"
      priority: "P0"
      domain: "CM"
      features: ["FEAT-CM-001", "FEAT-CM-002", ...]
      count: 50
    - batch_id: "B002"
      priority: "P1"
      domain: "SM"
      features: [...]
```

**Validation:** 큐 초기화 완료

---

#### Step 2: Dispatch to Sessions

**Description:** 세션에 배치 할당 및 실행

**Sub-steps:**
1. 사용 가능한 세션 확인
2. Round-robin으로 배치 할당
3. 세션 시작 (Task tool 사용)
4. 세션 상태 모니터링

**Session Dispatch:**
```yaml
session_dispatch:
  method: "Task tool with subagent"
  prompt_template: |
    Generate code for batch {BATCH_ID}
    Domain: {DOMAIN}
    Features: {FEATURE_LIST}
    Use templates from: work/specs/stage3-outputs/phase5/
    Output to: next-hallain/src/main/java/com/hallain/{domain}/
```

**Validation:** 모든 배치 세션에 할당

---

#### Step 3: Query 전체 선행 이관 (2-Phase 분리)

**Description:** Feature별 작업이 아닌, Query 전체를 먼저 이관한 후 Java 코드 생성

> **CRITICAL - QUERY-FIRST 원칙 (전체 선행 이관)**
> - Query 이관이 어떤 Task보다 우선한다
> - 모든 Mapper XML(1,318개)을 먼저 일괄 변환
> - Query Fidelity 검증 100% PASS 후에만 Java 코드 생성

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      2-PHASE 분리 워크플로우                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PHASE 1: Query 전체 이관                                                │
│  ─────────────────────────                                              │
│  [Mapper XML 1] → [Mapper XML 2] → ... → [Mapper XML 1318]              │
│                              │                                          │
│                              ▼                                          │
│                    Query Fidelity Gate                                  │
│                    (100% PASS 필수)                                     │
│                              │                                          │
│                              ▼                                          │
│  PHASE 2: Java 코드 생성 (Query 검증 PASS 후에만)                        │
│  ─────────────────────────                                              │
│  Feature 1: [Controller] → [Service] → [DTO] → [Entity]                │
│  Feature 2: [Controller] → [Service] → [DTO] → [Entity]                │
│  ...                                                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### PHASE 1: Query 전체 이관 (Mapper XML 일괄 변환)

```yaml
phase_1_query_migration:
  name: "Query 전체 이관"
  scope: "전체 sqlmap 파일 (1,318개)"
  priority: P0  # 최우선

  execution_order:
    1: MM (126)   # 케이스 발생 도메인 - 최우선
    2: PA (456)   # 최대 도메인
    3: SC (131)   # 복잡 도메인
    4: "나머지 도메인"

  per_file_workflow:
    1_load_legacy:
      action: "Legacy sqlmap XML 파일 로드"
      path: "hallain/src/main/resources/com/halla/{domain}/sqlmap/sqlmap-{featureId}.xml"
      on_missing: "STOP - 파일 없으면 진행 불가"

    2_copy_sql:
      action: "SQL 원문 100% 복사"
      copy_as_is:
        - 테이블명
        - 컬럼명
        - JOIN 조건
        - WHERE 조건 (값 포함)
        - GROUP BY/ORDER BY
        - 서브쿼리 구조
        - DECODE/CASE 로직
        - 주석

    3_syntax_only:
      action: "iBatis → MyBatis 문법만 변환"
      allowed:
        - "#var# → #{var}"
        - "$var$ → ${var}"
        - "<isNotEmpty> → <if test>"
        - "parameterClass → parameterType"
        - "resultClass → resultType"
        - "namespace 변경"
      prohibited:
        - "SQL 로직 재해석/재생성"
        - "컬럼명/테이블명 추측"
        - "조건값 변경 (예: 'INPRCH' → '1')"
        - "JOIN 조건 수정"
        - "GROUP BY/ORDER BY 구조 변경"
        - "DECODE/CASE 간소화"

    4_write_mapper:
      action: "Generated Mapper XML 저장"
      output: "next-hallain/src/main/resources/mapper/{domain}/{Screen}Mapper.xml"

  output:
    directory: "next-hallain/src/main/resources/mapper/"
    total_files: 1318
    by_domain:
      mm/: "126 files"
      pa/: "456 files"
      sc/: "131 files"
      # ... 나머지 도메인

  checkpoint: "도메인 완료 시 저장"
  parallel: false  # 순차 처리로 추적성 확보

  completion_gate:
    name: "Query Migration Gate"
    criteria: "전체 1,318개 파일 변환 완료"
    next: "Query Fidelity Check"
```

---

### QUERY FIDELITY GATE (PHASE 1 → PHASE 2 전환 조건)

```yaml
query_fidelity_gate:
  name: "Query Fidelity Gate"
  type: "Blocking"
  position: "PHASE 1 완료 후, PHASE 2 시작 전"

  scope: "전체 Mapper XML (1,318개)"

  per_statement_checklist:
    - id: "TBL-001"
      check: "테이블명 100% 일치"
    - id: "COL-001"
      check: "컬럼명 100% 일치"
    - id: "JOIN-001"
      check: "JOIN 조건 100% 일치"
    - id: "WHERE-001"
      check: "WHERE 조건값 100% 일치"
    - id: "GRPORD-001"
      check: "GROUP BY/ORDER BY 100% 일치"
    - id: "LOGIC-001"
      check: "DECODE/CASE 로직 100% 일치"
    - id: "SUB-001"
      check: "서브쿼리 구조 100% 일치"

  pass_criteria:
    match_rate: 100%  # 99%도 불가
    human_review: "APPROVED"

  on_fail:
    action: "BLOCK - Java 코드 생성 불가"
    resolution:
      1. "미스매치 Mapper XML 식별"
      2. "Legacy sqlmap에서 해당 SQL 재복사"
      3. "문법만 변환"
      4. "Fidelity Check 재실행"
    escalation: "Human Review 필수"
```

---

### PHASE 2: Java 코드 생성 (Query 검증 PASS 후)

```yaml
phase_2_java_generation:
  name: "Java 코드 생성"

  preconditions:
    mandatory:
      - "PHASE 1: Query 이관 100% 완료"
      - "Query Fidelity Gate: PASS"
      - "Human Review: APPROVED"
    on_unmet:
      action: "Java 코드 생성 시작 불가"
      message: "Query 이관 및 검증이 완료되어야 합니다"

  per_feature_generation:
    note: "Mapper XML은 이미 PHASE 1에서 생성됨"
    files:
      - "{domain}/entity/{Screen}Entity.java"
      - "{domain}/dto/{Screen}SearchRequest.java"
      - "{domain}/dto/{Screen}DetailRequest.java"
      - "{domain}/dto/{Screen}SaveRequest.java"
      - "{domain}/dto/{Screen}Response.java"
      - "{domain}/repository/{Screen}Mapper.java"  # Interface only
      - "{domain}/service/{Screen}Service.java"
      - "{domain}/controller/{Screen}Controller.java"

    reference:
      mapper_xml: "next-hallain/src/main/resources/mapper/{domain}/{Screen}Mapper.xml"
      note: "Mapper XML은 이미 존재 (PHASE 1 산출물)"

  parallel:
    enabled: true
    max_sessions: 10
    batch_size: 50

  on_complete:
    - "Update generation-progress.yaml"
    - "Queue TEST-{FEAT_ID} to S4-04"
```

**Validation:** PHASE 1 완료 → Gate PASS → PHASE 2 실행

---

#### Step 4: Checkpoint Management

**Description:** 배치별 체크포인트 저장

**Sub-steps:**
1. 배치 완료 시 상태 저장
2. 실패 시 롤백 포인트 기록
3. 재시작 시 체크포인트부터 재개

**Checkpoint Structure:**
```yaml
checkpoint:
  file: "work/specs/stage4-outputs/phase3/checkpoint.yaml"
  content:
    last_completed_batch: "B015"
    failed_features: ["FEAT-PA-123", "FEAT-PA-456"]
    retry_queue: ["FEAT-PA-123"]
    resume_from: "B016"
```

**Validation:** 체크포인트 저장 완료

---

#### Step 5: Progress Tracking

**Description:** 실시간 진행 상황 추적

**Tracking Metrics:**
```yaml
progress_tracking:
  file: "work/specs/stage4-outputs/phase3/generation-progress.yaml"
  metrics:
    - total_features
    - completed_features
    - failed_features
    - in_progress
    - completion_percentage
    - estimated_remaining_time
  update_frequency: "per_feature"
```

**Validation:** 진행률 100%

---

#### Step 6: Parallel Coordination with S4-04

**Description:** 테스트 생성과의 병렬 조율

**Coordination Rules:**
```yaml
parallel_coordination:
  with_phase: "4.4"
  coordination_type: "feature_pipeline"
  trigger: "GEN-{FEAT_ID} completion"
  action: "Queue TEST-{FEAT_ID}"
  message_format:
    feature_id: "{FEAT_ID}"
    generated_files: [...]
    timestamp: "..."
```

**Validation:** 테스트 큐 등록 완료

---

#### Step 7: Schema Validation

**Description:** 생성된 진행 상황 및 체크포인트 파일이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | generation-progress.yaml root | metadata, summary, by_priority, by_domain 필수 키 존재 | ERROR | Yes |
| V002 | checkpoint.yaml root | metadata, status 필수 키 존재 | ERROR | Yes |
| V003 | metadata.generated_by | 정확히 "s4-03-generation-domain-batch" | ERROR | Yes |
| V004 | by_priority | P0, P1, P2, P3 모두 존재 | ERROR | Yes |
| V005 | summary.completion_percentage | 범위: 0-100 | ERROR | Yes |
| V006 | summary | completed <= total_features | ERROR | Yes |
| V007 | summary | completed + failed + in_progress == total_features | WARNING | No |
| V008 | by_priority | Priority별 합계 == summary.completed | WARNING | No |
| V009 | by_domain | 도메인별 합계 == summary.completed | WARNING | No |
| V010 | ready_for_integration | 100% 완료 시 true | ERROR | Yes |

**Sub-steps:**
1. generation-progress.yaml 스키마 검증
2. checkpoint.yaml 스키마 검증
3. 일관성 메트릭 검증
4. 오류 발생 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 진행 상황 재확인 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.5 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | 세션 timeout | 재시도 (max 3) | 계속 진행 |
| DP-2 | 생성 실패 | 실패 큐에 추가, 다음 진행 | 계속 진행 |
| DP-3 | 배치 완료 | 체크포인트 저장 | 계속 진행 |
| DP-4 | 전체 완료 | 컴파일 검증 | N/A |

---

### 3.6 Large File Handling

> **⚠️ Read Tool Limit**: Claude Code Read tool has 256KB file size limit. Large input files require chunked reading.

#### Input Files That May Be Large

| Input | Location | Potential Size | Chunking Type |
|-------|----------|----------------|---------------|
| Feature Inventory | `work/specs/stage2-outputs/phase4/` | >200KB with 700+ features | Directory-based chunks |
| Source Inventory | `source-inventory/` or `source-inventory.yaml` | 200KB~2.2MB | Layer-based chunks |
| Domain Specs | Per-domain main.yaml | Usually small | Offset/limit if large |

#### Reading Strategy

```yaml
large_file_reading:
  threshold_kb: 200

  process:
    step_1: "파일/디렉토리 존재 확인"
    step_2:
      - check: "디렉토리 형태인지 확인 (e.g., source-inventory/)"
      - if_directory: "_manifest.yaml 읽고 청크별 순차 처리"
      - if_single_file: "파일 크기 확인 후 처리"
    step_3:
      - check: "단일 파일 크기 확인 (wc -c)"
      - if_small: "전체 Read"
      - if_large: "offset/limit으로 청크 읽기"
```

#### Chunked Directory Reading

```yaml
chunked_directory_reading:
  # When input is a chunked directory (e.g., source-inventory/)
  workflow:
    1_read_manifest:
      action: "Read _manifest.yaml"
      content: "metadata + summary + chunks list"

    2_iterate_chunks:
      action: "Process each chunk file"
      pattern: |
        for chunk in manifest.chunks:
          Read(directory + "/" + chunk.file)
          # Process chunk data
          # Accumulate results

    3_aggregate:
      action: "Combine results from all chunks"
```

#### Offset/Limit Reading for Legacy Files

```yaml
offset_limit_reading:
  # When input is a large single file (legacy format)
  chunk_lines: 1500  # ~150KB per chunk

  workflow:
    1_get_total_lines:
      command: "wc -l < file.yaml"

    2_read_in_chunks:
      pattern: |
        total_lines = wc -l
        for offset in range(0, total_lines, 1500):
          Read(file, offset=offset, limit=1500)
          # Parse YAML fragment
          # Handle partial records at boundaries

    3_merge_results:
      action: "Combine parsed data"
```

#### Batch Session Input Strategy

```yaml
batch_session_input:
  # For each parallel session
  strategy: "domain_scoped"
  description: |
    각 세션은 자신이 담당하는 도메인의 Spec만 읽음
    전체 Inventory를 메모리에 로드하지 않음

  per_session:
    1: "할당된 도메인 목록 수신"
    2: "도메인별 Spec 파일만 읽기"
    3: "Feature별 순차 처리"

  memory_optimization:
    - "전체 Inventory 로드 대신 도메인별 분할 처리"
    - "처리 완료된 Feature 데이터는 즉시 해제"
    - "진행 상황만 추적 파일에 기록"
```

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "next-hallain/src/main/java/com/hallain/"
    resources: "next-hallain/src/main/resources/mapper/"

  tracking:
    - name: "generation-progress.yaml"
      path: "work/specs/stage4-outputs/phase3/"
    - name: "checkpoint.yaml"
      path: "work/specs/stage4-outputs/phase3/"
```

### 4.2 Output Files Summary

**Per Domain:**
```
next-hallain/src/main/java/com/hallain/{domain}/
├── controller/
│   ├── {Screen1}Controller.java
│   ├── {Screen2}Controller.java
│   └── ...
├── service/
│   ├── {Screen1}Service.java
│   └── ...
├── repository/
│   ├── {Screen1}Mapper.java
│   └── ...
├── dto/
│   ├── {Screen1}SearchRequest.java
│   ├── {Screen1}Response.java
│   └── ...
└── entity/
    ├── {Screen1}Entity.java
    └── ...

next-hallain/src/main/resources/mapper/{domain}/
├── {Screen1}Mapper.xml
├── {Screen2}Mapper.xml
└── ...
```

### 4.3 Progress Output Schema

```yaml
# generation-progress.yaml
metadata:
  generated_by: "s4-03-generation-domain-batch"
  started_at: "2026-01-07T10:00:00Z"
  last_updated: "2026-01-07T16:00:00Z"

summary:
  total_features: 700
  completed: 700
  failed: 0
  in_progress: 0
  completion_percentage: 100.0

by_priority:
  P0:
    total: 50
    completed: 50
    domains: ["benitware", "CM", "schedule"]
  P1:
    total: 200
    completed: 200
    domains: ["SM", "EB"]
  P2:
    total: 400
    completed: 400
    domains: ["PA", "MM", "SC", "EA", "SA", "PE"]
  P3:
    total: 50
    completed: 50
    domains: ["QM", "BS"]

by_domain:
  PA:
    total: 443
    completed: 443
    failed: 0
  MM:
    total: 120
    completed: 120
    failed: 0
  # ... other domains

failed_features: []

session_stats:
  total_sessions: 10
  avg_features_per_session: 70
  total_execution_time_minutes: 360

ready_for_integration: true
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| all_features_generated | metric | progress 100% | ERROR | Yes |
| compilation_succeeds | structural | `./gradlew compileJava` | ERROR | Yes |
| no_generation_failures | metric | failed = 0 | WARNING | No |
| files_per_feature | structural | 9 files each | WARNING | No |

### 5.2 Gate Criteria

```yaml
gate_criteria:
  id: "G4.3"
  name: "Domain Batch Gate"
  threshold: 70
  metrics:
    - metric: "all_features_generated"
      weight: 0.4
      target: "100%"
      source: "generation-progress.yaml"
      blocking: true
    - metric: "compilation_succeeds"
      weight: 0.4
      target: "true"
      command: "cd backend && ./gradlew compileJava"
      blocking: true
    - metric: "no_generation_failures"
      weight: 0.2
      target: "0"
      blocking: false
  on_pass:
    auto_commit: true
    message: "feat(S4-P4.3): Domain batch generation complete"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Session timeout | 60분 초과 | 대형 배치 | 배치 크기 감소 | Yes |
| Rate limit | API 오류 | 과다 요청 | Backoff 적용 | Yes |
| Compile error | 특정 Feature | 템플릿 이슈 | 개별 수정 | Yes |
| Memory issue | OOM | 대규모 병렬 | 세션 수 감소 | Yes |

### 6.2 Retry Policy

```yaml
retry_policy:
  default:
    max_attempts: 3
    backoff: "exponential"
    initial_delay_seconds: 30

  rate_limit:
    max_attempts: 5
    backoff: "exponential"
    initial_delay_seconds: 60

  timeout:
    max_attempts: 3
    backoff: "linear"
    delay_increment_seconds: 30
```

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 세션 실패 | 체크포인트에서 재시작 | Batch |
| 특정 Feature 실패 | 재시도 큐에 추가 | Feature |
| 전체 실패 | 처음부터 재실행 | Phase |

---

## 7. Examples

### 7.1 Sample Batch Dispatch

**Input (Batch B001):**
```yaml
batch:
  batch_id: "B001"
  priority: "P2"
  domain: "PA"
  features:
    - "FEAT-PA-001"
    - "FEAT-PA-002"
    - "FEAT-PA-003"
  session_id: "S1"
```

**Task Dispatch:**
```
Task tool invocation:
- subagent_type: "general-purpose"
- prompt: "Generate code for batch B001, domain PA, 3 features..."
```

### 7.2 Sample Progress Update

**During Execution:**
```yaml
# Intermediate progress
summary:
  total_features: 700
  completed: 350
  failed: 2
  in_progress: 48
  completion_percentage: 50.0

current_sessions:
  S1: { domain: "PA", batch: "B008", progress: "45/50" }
  S2: { domain: "MM", batch: "B012", progress: "32/50" }
  # ...
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| PA 대형 도메인 | 443 features | 9 batches, 세션 affinity 유지 |
| Feature 실패 | 템플릿 불일치 | 재시도 큐, 나머지 계속 |
| 세션 크래시 | 중간 실패 | 체크포인트에서 재개 |

---

## Version History

### v1.2.0 (2026-01-15)
- Section 3.1.1: Execution Modes 추가
- `full_batch` / `incremental_batch` 모드 선택 지원
- Decision Point로 사용자 범위 선택 가능
- 점진적 검증 워크플로우 공식 지원

### v1.1.0 (2026-01-08)
- Step 7: Schema Validation 추가
- s4-03-domain-batch.schema.yaml 스키마 참조
- 10개 검증 규칙 적용 (V001-V010)

### v1.0.0 (2026-01-07)
- Initial version
- 10 병렬 세션 지원
- Priority 기반 배치 전략
- Phase 4.4와 병렬 조율
