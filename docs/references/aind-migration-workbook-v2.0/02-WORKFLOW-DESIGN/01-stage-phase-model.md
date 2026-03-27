# Stage-Phase Model

## Overview

이 문서는 Legacy Migration Framework의 핵심인 Stage-Phase 계층 모델을 정의합니다. 이 모델은 마이그레이션 작업을 체계적으로 분해하고 관리하기 위한 구조적 프레임워크입니다.

---

## 1. Model Architecture

### 1.1 Hierarchical Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       STAGE-PHASE HIERARCHY                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   PROJECT                                                               │
│   └── STAGE (목적 단위)                                                  │
│       └── PHASE (작업 단위)                                              │
│           └── TASK (실행 단위)                                           │
│               └── SKILL (AI 지시사항)                                    │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Example:                                                              │
│                                                                         │
│   hallain_tft Migration Project                                         │
│   └── STAGE 1: Discovery                                                │
│       └── Phase 1: Feature Inventory                                    │
│           └── Task: FEAT-PA-205                                         │
│               └── Skill: stage1-phase1-feature-inventory                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Level Definitions

| Level | 정의 | 특성 | 예시 |
|-------|------|------|------|
| **Project** | 전체 마이그레이션 프로젝트 | 단일 인스턴스 | hallain_tft Migration |
| **Stage** | 마이그레이션의 주요 목적 단위 | 5개 표준 Stage | Discovery, Validation, Preparation, Generation, Assurance |
| **Phase** | Stage 내 순차적 작업 단위 | Stage당 3-6개 | Inventory, Analysis, Spec Generation |
| **Task** | 병렬 처리 가능한 개별 작업 | Feature 단위 | FEAT-PA-205, FEAT-PA-206 |
| **Skill** | AI가 실행하는 지시사항 | Phase별 정의 | stage1-phase2-deep-analysis |

---

## 2. Standard Five-Stage Model

### 2.1 Stage Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                         FIVE-STAGE MODEL                               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   STAGE 1           STAGE 2           STAGE 3           STAGE 4        │
│   DISCOVERY         VALIDATION        PREPARATION       GENERATION     │
│   (이해)            (검증)            (준비)            (생성)              │
│                                                                        │
│   ┌─────────┐       ┌─────────┐       ┌─────────┐       ┌─────────┐    │
│   │ What    │ ───→  │ Is it   │ ───→  │ How to  │ ───→  │ Build   │    │
│   │ exists? │       │ complete?│      │ build?  │       │ it!     │    │
│   └─────────┘       └─────────┘       └─────────┘       └─────────┘    │
│                                                                        │
│                              ↓                                         │
│                                                                        │
│                          STAGE 5                                       │
│                          ASSURANCE                                     │
│                          (보증)                                         │
│                                                                        │
│                       ┌─────────┐                                      │
│                       │ Does it │                                      │
│                       │ work?   │                                      │
│                       └─────────┘                                      │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Stage Definitions

```yaml
stages:
  stage_1_discovery:
    name: "Discovery"
    korean: "발견/이해"
    purpose: "Legacy 시스템의 완전한 이해와 문서화"
    question: "What exists in the legacy system?"
    outputs:
      - "Feature Inventory"
      - "Deep Analysis Reports"
      - "Technical Specifications"
    phases:
      - "Phase 1: Feature Inventory"
      - "Phase 2: Deep Analysis"
      - "Phase 3: Spec Generation"
    success_criteria:
      - "100% Feature 식별"
      - "100% Endpoint 문서화"
      - "Spec 파일 생성 완료"

  stage_2_validation:
    name: "Validation"
    korean: "검증"
    purpose: "Stage 1 산출물의 완전성 검증"
    question: "Is the specification complete?"
    outputs:
      - "Source Inventory (Ground Truth)"
      - "Gap Analysis Report"
      - "Completed Specifications"
    phases:
      - "Phase 1: Source Inventory"
      - "Phase 2: Structural Comparison"
      - "Phase 3: Gap Analysis"
      - "Phase 4: Spec Completion"
    success_criteria:
      - "Coverage >= 99%"
      - "Critical gaps 해소"
      - "Spec Validation 통과"

  stage_3_preparation:
    name: "Preparation"
    korean: "준비"
    purpose: "구현을 위한 설계 및 계획 수립"
    question: "How should we build it?"
    outputs:
      - "Dependency Graph"
      - "Architecture Design"
      - "Implementation Plan"
    phases:
      - "Phase 1: Dependency Analysis"
      - "Phase 2: System Integration"
      - "Phase 3: Technical Debt Analysis"
      - "Phase 4: Architecture Design"
      - "Phase 5: Code Generation Spec"
      - "Phase 6: Implementation Planning"
    success_criteria:
      - "아키텍처 승인"
      - "구현 계획 확정"
      - "리소스 할당 완료"

  stage_4_generation:
    name: "Generation"
    korean: "생성"
    purpose: "AI를 활용한 코드 생성"
    question: "Build the new system!"
    outputs:
      - "Generated Source Code"
      - "Unit Tests"
      - "Build Artifacts"
    phases:
      - "Phase 1: System Setup"
      - "Phase 2: Mini-Pilot"
      - "Phase 3: Domain Execution (2-Phase 분리)"
      - "Phase 4: Integration"
    success_criteria:
      - "Build 성공"
      - "Unit Test 통과"
      - "코드 커버리지 기준 충족"

    # QUERY-FIRST 전략 (REHOSTING/REPLATFORMING 필수)
    query_first_strategy:
      applicable: "REHOSTING, REPLATFORMING"
      phase_3_modification:
        description: "Phase 3 Domain Execution을 2-Phase로 분리"
        phase_3a_query_migration:
          name: "Query 전체 이관"
          scope: "전체 sqlmap 파일 (Mapper XML)"
          gate: "Query Fidelity Gate (100%)"
        phase_3b_java_generation:
          name: "Java 코드 생성"
          precondition: "Phase 3A Gate PASS"
          scope: "Controller, Service, DTO, Entity"

  stage_5_assurance:
    name: "Assurance"
    korean: "보증"
    purpose: "생성된 코드의 품질 검증"
    question: "Does it work correctly?"
    outputs:
      - "Validation Reports"
      - "Remediation Logs"
      - "Quality Certification"
    phases:
      - "Phase 1: Structural Standardization"
      - "Phase 2: Functional Validation"
      - "Phase 3: Quality Standardization"
      - "Phase 4: Integration Validation"
      - "Phase 5: Quality Gate"
    success_criteria:
      - "Functional Validation >= 90%"
      - "Quality Gate 통과"
      - "Production 배포 승인"
```

---

## 3. Phase Design Patterns

### 3.1 Phase Types

```yaml
phase_types:
  inventory_phase:
    pattern: "Discovery/Collection"
    characteristics:
      - "자동화 가능"
      - "전수 조사"
      - "메타데이터 수집"
    examples:
      - "Feature Inventory"
      - "Source Inventory"
      - "Dependency Scan"

  analysis_phase:
    pattern: "Deep Dive"
    characteristics:
      - "AI 추론 필요"
      - "상세 분석"
      - "문서화"
    examples:
      - "Deep Analysis"
      - "Gap Analysis"
      - "Complexity Assessment"

  generation_phase:
    pattern: "Creation"
    characteristics:
      - "산출물 생성"
      - "품질 기준 적용"
      - "검증 필요"
    examples:
      - "Spec Generation"
      - "Code Generation"
      - "Test Generation"

  validation_phase:
    pattern: "Verification"
    characteristics:
      - "비교/검증"
      - "Pass/Fail 판정"
      - "Remediation 트리거"
    examples:
      - "Structural Comparison"
      - "Functional Validation"
      - "Quality Gate"

  integration_phase:
    pattern: "Consolidation"
    characteristics:
      - "여러 산출물 통합"
      - "시스템 레벨 검증"
      - "최종 확정"
    examples:
      - "System Integration"
      - "Integration Validation"
      - "Build Integration"
```

### 3.2 Phase Sequencing Rules

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PHASE SEQUENCING RULES                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Rule 1: Sequential within Stage                                       │
│   ──────────────────────────────                                        │
│   Phase N must complete before Phase N+1 starts                         │
│                                                                         │
│       Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ ...                           │
│                                                                         │
│   Rule 2: Stage Gate between Stages                                     │
│   ─────────────────────────────────                                     │
│   All phases in Stage N must complete before Stage N+1                  │
│                                                                         │
│       Stage 1 ═══[Gate]═══→ Stage 2 ═══[Gate]═══→ Stage 3               │
│                                                                         │
│   Rule 3: Parallel Tasks within Phase                                   │
│   ────────────────────────────────────                                  │
│   Multiple tasks in same phase can run in parallel                      │
│                                                                         │
│       Phase 2: ┬─ Task A ─┬                                             │
│                ├─ Task B ─┤                                             │
│                └─ Task C ─┘                                             │
│                                                                         │
│   Rule 4: Phase Gate before Advance                                     │
│   ──────────────────────────────────                                    │
│   All tasks must pass Phase Gate to advance                             │
│                                                                         │
│       Task A ─┬─ [Phase Gate] ─→ Task A (Phase N+1)                     │
│       Task B ─┤                                                         │
│       Task C ─┘                                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Task Design

### 4.1 Task Granularity

```yaml
task_granularity:
  definition: "Task는 Feature 단위로 정의"

  feature_definition:
    primary_grouping: "Screen ID 기반"
    naming_pattern: "FEAT-{DOMAIN}-{NUMBER}"
    examples:
      - "FEAT-PA-205 (PA0205030M 화면)"
      - "FEAT-CM-001 (CM0101010M 화면)"

  task_characteristics:
    independence: "다른 Task와 독립적으로 실행 가능"
    atomicity: "성공 또는 실패, 부분 완료 없음"
    traceability: "입력/출력 추적 가능"
    reproducibility: "동일 입력 → 동일 출력"
```

### 4.2 Task Lifecycle

```
┌───────────────────────────────────────────────────────────────────────┐
│                         TASK LIFECYCLE                                │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   PENDING ──→ ASSIGNED ──→ IN_PROGRESS ──→ VALIDATING ──→ COMPLETED   │
│      │            │              │              │                     │
│      │            │              │              │                     │
│      │            ▼              ▼              ▼                     │
│      │        TIMEOUT        FAILED        REJECTED                   │
│      │            │              │              │                     │
│      │            └──────────────┴──────────────┘                     │
│      │                           │                                    │
│      │                           ▼                                    │
│      │                       RETRYING                                 │
│      │                           │                                    │
│      └───────────────────────────┘                                    │
│                                                                       │
│   States:                                                             │
│   • PENDING: 실행 대기                                                  │
│   • ASSIGNED: 세션에 할당됨                                              │
│   • IN_PROGRESS: 실행 중                                               │
│   • VALIDATING: Phase Gate 검증 중                                     │
│   • COMPLETED: 성공적 완료                                              │
│   • FAILED: 실행 실패                                                  │
│   • REJECTED: Phase Gate 실패                                         │
│   • RETRYING: 재시도 중                                                │
│   • TIMEOUT: 시간 초과                                                 │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 5. Phase Gate Control

### 5.1 Phase Gate Concept

```yaml
phase_gate:
  definition: "Phase 완료 전 품질 검증 체크포인트"

  purpose:
    - "불완전한 산출물 방지"
    - "품질 기준 강제"
    - "조기 문제 발견"

  components:
    validation_rules: "산출물 검증 규칙"
    minimum_requirements: "최소 요구사항"
    quality_metrics: "품질 메트릭"

  enforcement:
    blocking: "Gate 미통과 시 다음 Phase 진입 불가"
    auto_commit: "통과 시 자동 커밋"
```

### 5.2 Phase Gate Rules by Phase

```yaml
phase_gate_rules:
  phase1_inventory:
    name: "Inventory Gate"
    rules:
      - "All controllers scanned"
      - "Endpoint list generated"
      - "Feature grouping complete"
    minimum:
      endpoints_extracted: ">= 90% of expected"
      features_identified: ">= 90% of expected"

  phase2_analysis:
    name: "Analysis Gate"
    rules:
      - "All layers traced"
      - "Business logic documented"
      - "MiPlatform protocol captured"
    minimum:
      files_generated: ">= 3 YAML files per feature"
      coverage: "5-layer complete"

  phase3_generation:
    name: "Generation Gate"
    rules:
      - "Spec structure valid"
      - "All sections present"
      - "File size limits respected"
    minimum:
      main_yaml_size: ">= 500 bytes"
      required_directories: ">= 2"
      max_file_size: "<= 300 lines"

  validation_phase:
    name: "Validation Gate"
    rules:
      - "Score threshold met"
      - "No critical issues"
      - "Remediation complete"
    minimum:
      score: ">= 70"
      critical_issues: "0"
      blocking_issues: "0"
```

### 5.3 Gate Enforcement Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     PHASE GATE ENFORCEMENT                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Task Completion Request                                               │
│            │                                                            │
│            ▼                                                            │
│   ┌─────────────────┐                                                   │
│   │ 1. File Check   │ ──→ Missing files? ──→ REJECT                     │
│   └────────┬────────┘                                                   │
│            │ Pass                                                       │
│            ▼                                                            │
│   ┌─────────────────┐                                                   │
│   │ 2. Structure    │ ──→ Invalid structure? ──→ REJECT                 │
│   │    Validation   │                                                   │
│   └────────┬────────┘                                                   │
│            │ Pass                                                       │
│            ▼                                                            │
│   ┌─────────────────┐                                                   │
│   │ 3. Schema       │ ──→ Schema violation? ──→ REJECT                  │
│   │    Validation   │     (validation-errors.yaml)                      │
│   └────────┬────────┘                                                   │
│            │ Pass                                                       │
│            ▼                                                            │
│   ┌─────────────────┐                                                   │
│   │ 4. Size Check   │ ──→ Too small/large? ──→ REJECT                   │
│   └────────┬────────┘                                                   │
│            │ Pass                                                       │
│            ▼                                                            │
│   ┌─────────────────┐                                                   │
│   │ 5. Auto Commit  │ ──→ Commit changes                                │
│   └────────┬────────┘                                                   │
│            │                                                            │
│            ▼                                                            │
│   ┌─────────────────┐                                                   │
│   │ 6. State Update │ ──→ Mark as COMPLETED                             │
│   └─────────────────┘                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Schema Validation**: 각 Skill에 소속된 스키마(`.claude/skills/{skill}/output.schema.yaml`)에 대해 산출물을 검증합니다. 공통 타입은 `.claude/skills/common/types.schema.yaml`에 정의됩니다. 검증 실패 시 `validation-errors.yaml` 파일이 생성되며 Phase Gate가 blocking됩니다.

---

## 6. Output Structure

### 6.1 Directory Organization

```
{project_root}/
├── {specs_root}/                          # 산출물 루트 (config.yaml에서 정의)
│   ├── stage1-outputs/
│   │   ├── phase1/                        # Feature Inventory
│   │   │   ├── feature-inventory.yaml
│   │   │   └── api-endpoints-raw.txt
│   │   ├── phase2/                        # Deep Analysis
│   │   │   └── {Priority}/{Domain}-domain/FEAT-XX-NNN/
│   │   │       ├── summary.yaml
│   │   │       ├── api-endpoints/
│   │   │       └── business-logic/
│   │   └── phase3/                        # Spec Generation
│   │       └── {Priority}/{Domain}-domain/FEAT-XX-NNN/
│   │           ├── main.yaml
│   │           ├── api-specs/
│   │           ├── business-logic/
│   │           └── data-model/
│   │
│   ├── stage2-outputs/
│   │   ├── phase1/                        # Source Inventory
│   │   ├── phase2/                        # Structural Comparison
│   │   ├── phase3/                        # Gap Analysis
│   │   └── phase4/                        # Spec Completion
│   │
│   ├── stage3-outputs/                    # Preparation outputs
│   ├── stage4-outputs/                    # Generation outputs
│   └── stage5-outputs/                    # Assurance outputs
│
└── backend/                               # Generated code (Stage 4)
    └── src/main/java/...
```

### 6.2 Priority-Based Grouping

```yaml
priority_structure:
  P0-Foundation:
    description: "공통 프레임워크, 유틸리티"
    domains: ["common", "framework"]
    order: 1

  P1-Hub:
    description: "중앙 허브 도메인"
    domains: ["CM"]
    order: 2

  P2-Core:
    description: "핵심 비즈니스 도메인"
    domains: ["PA", "MM", "SC", "SM", "EA", "SA"]
    order: 3

  P3-Supporting:
    description: "지원 도메인"
    domains: ["PE", "EB", "BS", "QM"]
    order: 4

  path_pattern: "{specs_root}/{stage}-outputs/{phase}/{Priority}/{Domain}-domain/FEAT-{Domain}-{NNN}/"
```

---

## 7. Customization Points

### 7.1 Stage Customization

```yaml
customization_options:
  add_stages:
    when: "표준 5단계로 불충분할 때"
    example:
      - "Stage 6: Deployment (배포 자동화)"
      - "Stage 7: Monitoring (운영 모니터링)"

  merge_stages:
    when: "소규모 프로젝트"
    example:
      - "Stage 1+2: Discovery & Validation 통합"

  skip_stages:
    when: "특정 Stage 불필요"
    example:
      - "Rehosting의 경우 Stage 4 불필요"

  reorder_phases:
    when: "프로젝트 특성에 맞게 조정"
    constraint: "Stage 내 순서만 변경 가능"

  query_first_strategy:
    when: "REHOSTING 또는 REPLATFORMING 마이그레이션"
    required: true
    description: "Stage 4 Phase 3을 2-Phase로 분리"
    reference: "02-customization-guide.md#2.3"
```

### 7.2 Phase Customization

```yaml
phase_customization:
  add_phases:
    example:
      - "Stage 4 Phase 2.5: Security Review"
      - "Stage 5 Phase 2.5: Performance Testing"

  modify_gate_rules:
    example:
      - "Score threshold 변경: 70 → 80"
      - "Minimum files 변경: 3 → 5"

  parallel_vs_sequential:
    default: "Phase 내 Task는 병렬"
    customizable: "의존성 있는 Task는 순차"
```

---

## 8. Configuration Example

```yaml
# .choisor/config.yaml

project:
  name: "legacy-migration-project"
  specs_root: "work/specs"

stages:
  enabled: [1, 2, 3, 4, 5]  # All stages enabled

stage_config:
  stage1:
    phases: [1, 2, 3]
    max_parallel_tasks: 10

  stage2:
    phases: [1, 2, 3, 4]
    max_parallel_tasks: 10

  stage3:
    phases: [1, 2, 3, 4, 5, 6]
    max_parallel_tasks: 5

  stage4:
    phases: [1, 2, 3, 4]
    max_parallel_tasks: 10

  stage5:
    phases: [1, 2, 3, 4, 5]
    max_parallel_tasks: 10

phase_gates:
  enabled: true
  auto_commit: true
  strict_mode: true  # Block on any gate failure

execution:
  auto_to_max: true  # Auto-advance through phases
  retry_on_failure: 3
  timeout_minutes: 60
```

---

## Next Steps

Stage-Phase Model 이해 후:

1. **Customization Guide** → [02-customization-guide.md](02-customization-guide.md)
2. **Decision Trees** → [03-decision-trees.md](03-decision-trees.md)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-15
