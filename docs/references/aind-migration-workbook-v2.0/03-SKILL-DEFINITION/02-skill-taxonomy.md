# Skill Taxonomy

**Version**: 2.0.0
**Last Updated**: 2026-01-07
**Purpose**: AI-Driven Migration 프로젝트를 위한 범용 Skill 분류 체계

---

## 1. Overview

이 문서는 AI-Driven Migration 프로젝트에서 사용되는 Skill의 분류 체계를 정의합니다. 특정 프로젝트에 의존하지 않는 범용적인 분류를 제공하여, 다양한 Migration 시나리오에 적용할 수 있습니다.

---

## 2. Stage-Based Classification

### 2.1 Five-Stage Model

AI-Driven Migration은 5개의 Stage와 1개의 Cross-cutting Stage로 구성됩니다.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FIVE-STAGE MODEL                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   STAGE 1          STAGE 2          STAGE 3          STAGE 4           │
│   DISCOVERY        VALIDATION       PREPARATION      GENERATION         │
│   (발견)            (검증)            (준비)            (생성)             │
│                                                                         │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐          │
│   │ What    │────▶│ Is it   │────▶│ How to  │────▶│ Build   │          │
│   │ exists? │     │ correct?│     │ build?  │     │ it!     │          │
│   └─────────┘     └─────────┘     └─────────┘     └─────────┘          │
│                                                                         │
│                               ↓                                         │
│                                                                         │
│                           STAGE 5          CROSS-CUTTING                │
│                           ASSURANCE        ORCHESTRATION                │
│                           (보증)            (조율)                        │
│                                                                         │
│                        ┌─────────┐       ┌─────────┐                    │
│                        │ Does it │       │ Control │                    │
│                        │ work?   │       │ flow    │                    │
│                        └─────────┘       └─────────┘                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Stage Descriptions

| Stage | Name | Question | Goal |
|-------|------|----------|------|
| **1** | Discovery | "What exists?" | Legacy 시스템의 완전한 이해와 문서화 |
| **2** | Validation | "Is it correct?" | Stage 1 명세의 정확성 검증 |
| **3** | Preparation | "How to build?" | 아키텍처 설계 및 코드 생성 명세 |
| **4** | Generation | "Build it!" | AI 기반 코드 생성 |
| **5** | Assurance | "Does it work?" | 생성된 코드의 품질 검증 |
| **X** | Orchestration | "Control flow" | 작업 흐름 제어 및 조율 |

---

## 3. Skill Categories by Stage

### 3.1 Stage 1: Discovery Skills

**목적**: Legacy 시스템을 분석하여 구조화된 명세 생성

```yaml
discovery_skills:
  categories:
    inventory:
      purpose: "대상 시스템의 구성 요소 목록화"
      typical_skills:
        - name: "feature-inventory"
          description: "API 엔드포인트/기능 목록 추출"
          type: "analysis"
          parallel: true
          batch_unit: "domain"

    protocol_analysis:
      purpose: "통신 프로토콜 및 데이터 형식 분석"
      typical_skills:
        - name: "protocol-analysis"
          description: "Request/Response 스키마 분석"
          type: "analysis"
          parallel: true
          batch_unit: "domain"

    deep_analysis:
      purpose: "다계층 코드 추적 분석"
      typical_skills:
        - name: "deep-analysis"
          description: "N-Layer 계층 추적 (Controller→Service→DAO→SQL→Model)"
          type: "analysis"
          parallel: true
          batch_unit: "feature"

    spec_generation:
      purpose: "분석 결과를 구조화된 명세로 변환"
      typical_skills:
        - name: "spec-generation"
          description: "YAML/JSON 명세 문서 생성"
          type: "generation"
          parallel: true
          batch_unit: "feature"
```

### 3.2 Stage 2: Validation Skills

**목적**: Stage 1 명세의 완전성과 정확성 검증

```yaml
validation_skills:
  categories:
    source_truth:
      purpose: "Ground Truth 수집 (Stage 1과 독립적)"
      typical_skills:
        - name: "source-inventory"
          description: "소스코드 기반 독립적 목록 생성"
          type: "analysis"
          parallel: true
          batch_unit: "domain"

    comparison:
      purpose: "명세와 Ground Truth 비교"
      typical_skills:
        - name: "structural-comparison"
          description: "구조적 일치성 비교 및 커버리지 측정"
          type: "validation"
          parallel: true
          batch_unit: "domain"

    gap_analysis:
      purpose: "누락/불일치 항목 분석"
      typical_skills:
        - name: "gap-analysis"
          description: "Gap 식별, 분류, 심각도 평가"
          type: "analysis"
          parallel: true
          batch_unit: "domain"

    completion:
      purpose: "Gap 해소 및 명세 보완"
      typical_skills:
        - name: "spec-completion"
          description: "누락된 명세 생성 및 병합"
          type: "generation"
          parallel: true
          batch_unit: "feature"
```

### 3.3 Stage 3: Preparation Skills

**목적**: 코드 생성을 위한 아키텍처 설계 및 명세 준비

```yaml
preparation_skills:
  categories:
    dependency_analysis:
      purpose: "시스템 의존성 분석"
      typical_skills:
        - name: "dependency-graph"
          description: "Inter-module/domain 의존성 그래프 구축"
          type: "analysis"
          parallel: false  # 전체 그림 필요
          batch_unit: "none"

    interface_design:
      purpose: "모듈 간 인터페이스 설계"
      typical_skills:
        - name: "interface-extraction"
          description: "순환 의존성 해소를 위한 인터페이스 설계"
          type: "generation"
          parallel: true
          batch_unit: "dependency_chain"

    technical_debt:
      purpose: "기술 부채 식별 및 문서화"
      typical_skills:
        - name: "technical-debt"
          description: "기술 부채 패턴 식별 및 처리 방안 정의"
          type: "analysis"
          parallel: true
          batch_unit: "domain"

    architecture_design:
      purpose: "Target 아키텍처 설계"
      typical_skills:
        - name: "architecture-design"
          description: "모듈 구조, 패키지, 계층 설계"
          type: "generation"
          parallel: false  # Human approval 필요
          batch_unit: "none"
          human_approval: true

    generation_spec:
      purpose: "코드 생성 명세 정의"
      typical_skills:
        - name: "generation-spec"
          description: "코드 생성 템플릿 및 규칙 정의"
          type: "generation"
          parallel: true
          batch_unit: "template_type"
```

### 3.4 Stage 4: Generation Skills

**목적**: AI 기반 코드 및 테스트 생성

```yaml
generation_skills:
  categories:
    scaffold:
      purpose: "프로젝트 초기 구조 생성"
      typical_skills:
        - name: "project-scaffold"
          description: "빌드 설정, 공통 모듈, 인프라 코드 생성"
          type: "generation"
          parallel: false  # 1회성
          batch_unit: "none"

    pilot:
      purpose: "파일럿 생성 및 패턴 검증"
      typical_skills:
        - name: "mini-pilot"
          description: "대표 feature 생성 및 패턴 검증"
          type: "generation"
          parallel: false  # 피드백 루프
          batch_unit: "none"

    batch_generation:
      purpose: "배치 코드 생성"
      typical_skills:
        - name: "domain-batch"
          description: "도메인별 배치 코드 생성"
          type: "generation"
          parallel: true
          batch_unit: "feature"

    test_generation:
      purpose: "테스트 코드 생성"
      typical_skills:
        - name: "test-generation"
          description: "Unit/Integration 테스트 생성"
          type: "generation"
          parallel: true
          batch_unit: "feature"

    build:
      purpose: "통합 빌드 및 아티팩트 생성"
      typical_skills:
        - name: "integration-build"
          description: "전체 코드 통합 및 빌드 검증"
          type: "validation"
          parallel: false
          batch_unit: "none"
```

### 3.5 Stage 5: Assurance Skills

**목적**: 생성된 코드의 품질 보증

```yaml
assurance_skills:
  categories:
    structural_check:
      purpose: "구조적 표준 준수 검증"
      typical_skills:
        - name: "structural-check"
          description: "코딩 컨벤션, 패키지 구조 검증"
          type: "validation"
          parallel: true
          batch_unit: "feature"

    functional_validation:
      purpose: "기능적 일치성 검증"
      typical_skills:
        - name: "functional-validation"
          description: "생성 코드 ↔ 명세 양방향 검증"
          type: "validation"
          parallel: true
          batch_unit: "feature"

    contract_test:
      purpose: "API 계약 검증"
      typical_skills:
        - name: "api-contract-test"
          description: "OpenAPI/프로토콜 호환성 검증"
          type: "validation"
          parallel: true
          batch_unit: "domain"

    performance:
      purpose: "성능 기준선 측정"
      typical_skills:
        - name: "performance-baseline"
          description: "N+1 쿼리 탐지, 성능 분석"
          type: "analysis"
          parallel: true
          batch_unit: "feature"

    quality_gate:
      purpose: "최종 품질 판정"
      typical_skills:
        - name: "quality-gate"
          description: "품질 게이트 통과/실패 판정"
          type: "validation"
          parallel: false  # Human approval 필요
          batch_unit: "none"
          human_approval: true
```

### 3.6 Cross-Cutting: Orchestration Skills

**목적**: 작업 흐름 제어 및 조율

```yaml
orchestration_skills:
  categories:
    gate_control:
      purpose: "게이트 검증 및 전환 판정"
      typical_skills:
        - name: "phase-gate"
          description: "Phase 완료 조건 검증"
          type: "orchestration"
          parallel: false
          batch_unit: "none"

        - name: "stage-gate"
          description: "Stage 전환 조건 검증"
          type: "orchestration"
          parallel: false
          batch_unit: "none"

    dispatch:
      purpose: "작업 배분 및 병렬 실행 관리"
      typical_skills:
        - name: "task-dispatch"
          description: "Task 생성, 배정, 병렬 실행 관리"
          type: "orchestration"
          parallel: false  # 제어 역할
          batch_unit: "none"

    tracking:
      purpose: "진행 상황 추적"
      typical_skills:
        - name: "progress-tracker"
          description: "진행률 추적 및 리포팅"
          type: "orchestration"
          parallel: false
          batch_unit: "none"

    recovery:
      purpose: "실패 시 복구"
      typical_skills:
        - name: "rollback"
          description: "Phase/Stage/Wave 레벨 롤백"
          type: "orchestration"
          parallel: false
          batch_unit: "none"
```

---

## 4. Type-Based Classification

### 4.1 Skill Type Matrix

| Type | Purpose | I/O Pattern | Stage Distribution |
|------|---------|-------------|-------------------|
| **Analysis** | 정보 추출 | Source → Structured Data | S1, S2, S3, S5 |
| **Generation** | 산출물 생성 | Data + Template → Artifact | S1, S3, S4 |
| **Validation** | 검증 | A + B → Report + Score | S2, S4, S5 |
| **Transformation** | 형식 변환 | Format A → Format B | S2, S5 |
| **Orchestration** | 흐름 제어 | State → Decision | Cross-cutting |

### 4.2 Type Distribution

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SKILL TYPE DISTRIBUTION                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Analysis      ████████████████████  (40%)                          │
│  Generation    ██████████████        (30%)                          │
│  Validation    ████████              (20%)                          │
│  Transform.    ██                    (5%)                           │
│  Orchestr.     ██                    (5%)                           │
│                                                                     │
│  Typical project: 25-30 skills total                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Execution Characteristics

### 5.1 Parallelization Categories

| Category | Max Sessions | Batch Unit | Typical Skills |
|----------|--------------|------------|----------------|
| **Feature-level** | 10 | 50 features/batch | deep-analysis, spec-generation, domain-batch |
| **Domain-level** | 10 | 1 domain/session | feature-inventory, source-inventory |
| **Limited** | 3-5 | Varies | interface-extraction, performance-baseline |
| **Sequential** | 1 | N/A | dependency-graph, architecture-design, quality-gate |

### 5.2 Human Approval Points

| Skill | Stage | Approval Required By |
|-------|-------|---------------------|
| `architecture-design` | S3 | Tech Lead + Architect |
| `quality-gate` | S5 | Tech Lead + Architect |

---

## 6. Skill Selection Guide

### 6.1 When to Create New Skills

새로운 Skill 생성이 필요한 경우:

```yaml
new_skill_triggers:
  - trigger: "기존 Skill이 커버하지 못하는 새로운 분석 대상"
    example: "특수한 프레임워크(MiPlatform, SAP 등) 분석"

  - trigger: "새로운 출력 형식 필요"
    example: "OpenAPI 3.0 명세 생성"

  - trigger: "프로젝트 특화 검증 요구사항"
    example: "특정 코딩 컨벤션 검증"
```

### 6.2 Skill Composition

기존 Skill 조합으로 해결 가능한 경우:

```yaml
skill_composition:
  pattern: "Pipeline"
  example:
    - skill: "feature-inventory"
    - skill: "deep-analysis"
      depends_on: "feature-inventory"
    - skill: "spec-generation"
      depends_on: "deep-analysis"
```

---

## 7. Quick Reference Table

### 7.1 Complete Skill Taxonomy

| Stage | Category | Skill | Type | Parallel | Batch |
|-------|----------|-------|------|----------|-------|
| S1 | Inventory | feature-inventory | Analysis | ✅ | Domain |
| S1 | Protocol | protocol-analysis | Analysis | ✅ | Domain |
| S1 | Analysis | deep-analysis | Analysis | ✅ | Feature |
| S1 | Spec | spec-generation | Generation | ✅ | Feature |
| S2 | Truth | source-inventory | Analysis | ✅ | Domain |
| S2 | Compare | structural-comparison | Validation | ✅ | Domain |
| S2 | Gap | gap-analysis | Analysis | ✅ | Domain |
| S2 | Complete | spec-completion | Generation | ✅ | Feature |
| S3 | Dependency | dependency-graph | Analysis | ❌ | - |
| S3 | Interface | interface-extraction | Generation | ✅ | Chain |
| S3 | Debt | technical-debt | Analysis | ✅ | Domain |
| S3 | Architecture | architecture-design | Generation | ❌ | - |
| S3 | GenSpec | generation-spec | Generation | ✅ | Type |
| S4 | Scaffold | project-scaffold | Generation | ❌ | - |
| S4 | Pilot | mini-pilot | Generation | ❌ | - |
| S4 | Batch | domain-batch | Generation | ✅ | Feature |
| S4 | Test | test-generation | Generation | ✅ | Feature |
| S4 | Build | integration-build | Validation | ❌ | - |
| S5 | Structure | structural-check | Validation | ✅ | Feature |
| S5 | Function | functional-validation | Validation | ✅ | Feature |
| S5 | Contract | api-contract-test | Validation | ✅ | Domain |
| S5 | Performance | performance-baseline | Analysis | ✅ | Feature |
| S5 | Gate | quality-gate | Validation | ❌ | - |
| X | Gate | phase-gate | Orchestration | ❌ | - |
| X | Gate | stage-gate | Orchestration | ❌ | - |
| X | Dispatch | task-dispatch | Orchestration | ❌ | - |
| X | Track | progress-tracker | Orchestration | ❌ | - |
| X | Recovery | rollback | Orchestration | ❌ | - |

---

## 8. Customization Guidelines

### 8.1 Project-Specific Extensions

프로젝트별로 추가될 수 있는 Skill 예시:

```yaml
project_extensions:
  legacy_framework_specific:
    - "struts-analysis"      # Struts 프레임워크 분석
    - "miplatform-protocol"  # MiPlatform RIA 프로토콜
    - "sap-interface"        # SAP 인터페이스 분석

  target_technology_specific:
    - "graphql-generation"   # GraphQL API 생성
    - "grpc-contract"        # gRPC 계약 검증
    - "kubernetes-manifest"  # K8s 매니페스트 생성

  domain_specific:
    - "financial-validation" # 금융 규정 검증
    - "healthcare-compliance" # 의료 규정 준수
```

### 8.2 Skill Naming for Extensions

> **권장 명명 규칙**: `s{stage}-{phase}-{workflow}-{action}`

```yaml
extension_naming:
  pattern: "s{stage}-{phase}-{workflow}-{specific}"
  examples:
    - "s1-02-discovery-miplatform-protocol"
    - "s4-03-generation-api-graphql"
    - "s5-03-assurance-compliance-hipaa"
```

---

## 9. Claude Code Skill Type Mapping

### 9.1 두 가지 분류 체계

**Migration Domain 분류** (이 문서):
| Type | Purpose |
|------|---------|
| Analysis | 소스코드/데이터 분석 |
| Generation | 산출물 생성 |
| Validation | 품질 검증 |
| Transformation | 형식 변환 |
| Orchestration | 작업 흐름 제어 |

**Claude Code 표준 분류** (`superpowers:writing-skills`):
| Type | Purpose | 특징 |
|------|---------|------|
| **Technique** | 따라야 할 구체적 단계가 있는 방법 | Rigid: 정확히 따라야 함 |
| **Pattern** | 문제에 대한 사고 방식 | Flexible: 원칙을 상황에 맞게 적용 |
| **Reference** | API 문서, 구문 가이드, 도구 문서 | Lookup: 필요 시 참조 |

### 9.2 Type Mapping Matrix

| Migration Type | Claude Code Type | Rationale |
|----------------|------------------|-----------|
| Analysis | **Technique** | 구체적 스캔/추출 단계 존재 |
| Generation | **Technique** | 템플릿 기반 생성 단계 존재 |
| Validation | **Technique** | 비교/검증 단계 존재 |
| Transformation | **Technique** | 변환 단계 존재 |
| Orchestration | **Technique** + **Pattern** | 제어 로직은 Technique, 판단 기준은 Pattern |

### 9.3 Mapping 가이드라인

**Technique으로 분류할 때:**
- 명시적인 단계별 프로세스가 있는 경우
- 동일 입력 → 일관된 출력이 필요한 경우
- 에이전트가 정확히 따라야 하는 경우

**Pattern으로 분류할 때:**
- 상황에 따라 적용 방식이 달라지는 경우
- 원칙/사고방식을 제공하는 경우
- 에이전트가 판단하여 적용해야 하는 경우

**Reference로 분류할 때:**
- API 문서, 명령어 참조인 경우
- 100+ 줄의 상세 정보인 경우
- 필요 시에만 참조하는 경우

### 9.4 예시

```yaml
# Analysis Skill → Technique
# 이유: 명시적인 스캔-추출-분류 단계가 있음
s1-01-discovery-feature-inventory:
  migration_type: analysis
  claude_code_type: technique
  rationale: "Controller 스캔 → RequestMapping 추출 → Feature 분류 단계 존재"

# Orchestration Skill → Technique + Pattern
# 이유: Gate 로직은 Technique, 판정 기준은 Pattern
x-01-orchestration-phase-gate:
  migration_type: orchestration
  claude_code_types:
    - technique: "Gate 평가 → 결정 → 실행 단계"
    - pattern: "Pass/Conditional/Fail 판정 기준"
```

---

**Previous**: [01-skill-framework.md](01-skill-framework.md)
**Next**: [03-skill-authoring-guide.md](03-skill-authoring-guide.md)
