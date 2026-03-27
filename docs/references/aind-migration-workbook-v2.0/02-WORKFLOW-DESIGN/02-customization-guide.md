# Workflow Customization Guide

**Version**: 1.0.0
**Last Updated**: 2025-12-15

---

## 1. Overview

이 가이드는 Legacy Migration Framework의 Stage-Phase 모델을 프로젝트 특성에 맞게 커스터마이징하는 방법을 설명합니다.

### 1.1 Customization Principles

```yaml
customization_principles:
  preserve_core:
    description: "핵심 검증 메커니즘 유지"
    mandatory_elements:
      - "Phase Gate control"
      - "Bidirectional validation"
      - "Quality metrics"

  adapt_structure:
    description: "구조는 프로젝트에 맞게 조정"
    adjustable_elements:
      - "Phase 수 및 구성"
      - "Task 병렬화 수준"
      - "검증 임계값"

  document_changes:
    description: "모든 커스터마이징 문서화"
    required_documentation:
      - "변경 사유"
      - "영향 분석"
      - "승인 기록"
```

---

## 2. Stage Customization

### 2.1 Stage 추가/제거

```yaml
stage_modification:
  adding_stage:
    when_needed:
      - "복잡한 외부 시스템 연동이 필요한 경우"
      - "규제 준수를 위한 별도 검증 단계 필요"
      - "특수 보안 요구사항 존재"

    procedure:
      1: "신규 Stage 목적 정의"
      2: "기존 Stage와의 의존성 분석"
      3: "Phase 구성 설계"
      4: "Phase Gate 조건 정의"
      5: "Skill 매핑"

    example:
      name: "Stage 2.5: Security Validation"
      purpose: "금융권 보안 규제 준수 검증"
      position: "Stage 2 (Validation) 후, Stage 3 (Preparation) 전"
      phases:
        - "Security Audit"
        - "Penetration Testing"
        - "Compliance Check"

  removing_stage:
    caution: "Stage 제거는 권장하지 않음"
    acceptable_cases:
      - "소규모 프로젝트 (Feature < 50)"
      - "단순 Rehosting 마이그레이션"

    prohibited_removals:
      - "Stage 1 (Discovery) - 스펙 추출 필수"
      - "Stage 5 (Assurance) - 품질 보증 필수"
```

### 2.3 QUERY-FIRST 전략 (REHOSTING/REPLATFORMING 필수)

> **CRITICAL**: REHOSTING 또는 REPLATFORMING 마이그레이션에서는 QUERY-FIRST 전략을 최우선으로 적용해야 합니다.

```yaml
query_first_strategy:
  applicable_to:
    - "REHOSTING (Lift & Shift)"
    - "REPLATFORMING (Lift & Reshape)"

  principle: "Query 이관이 어떤 Task보다 우선한다"
  rationale: "비즈니스 로직은 Query에 있다. Query가 변경되면 비즈니스가 변경된다."

  workflow_modification:
    before: # 기존 Feature별 작업
      pattern: "Feature 1: [Mapper XML → Controller → Service → DTO]"
      issue: "SQL 재생성 시 로직 변조 위험"

    after: # QUERY-FIRST 2-Phase 분리
      pattern: |
        PHASE 1: [Mapper XML 1] [Mapper XML 2] ... [Mapper XML N]
                              │
                              ▼
        GATE: Query Fidelity (100% PASS 필수)
                              │
                              ▼
        PHASE 2: Feature별 Java 코드 생성

  stage_4_modification:
    phase_3_domain_batch:
      original: "Feature별 6-Layer 생성"
      modified: |
        PHASE 1: Query 전체 이관 (Mapper XML)
        GATE: Query Fidelity (100%)
        PHASE 2: Java 코드 생성 (Query 검증 후)

  mandatory_gate:
    name: "Query Fidelity Gate"
    threshold: "100%"  # 99% 불가
    human_review: "REQUIRED"
    on_fail: "BLOCK - Java 코드 생성 불가"

  prohibited_changes:
    - "SQL 로직 재해석/재생성"
    - "컬럼명/테이블명 추측 또는 축약"
    - "리터럴 조건값 변경"
    - "JOIN 조건 수정"
    - "WHERE 절 IN/LIKE/= 값 변경"
    - "GROUP BY/ORDER BY/ROLLUP 구조 변경"
    - "DECODE/CASE/NVL 로직 간소화"
    - "서브쿼리/UNION 구조 변경"

  verification:
    method: "Line-by-Line 비교"
    scope: "전체 SQL Statement"
    criteria: "Legacy와 100% 일치"
```

#### 적용 시점 결정

```
마이그레이션 전략 결정
         │
         ├── REHOSTING ──→ QUERY-FIRST 적용 (MANDATORY)
         │                  └── Query 이관만 수행, Java 변경 없음
         │
         ├── REPLATFORMING ──→ QUERY-FIRST 적용 (MANDATORY)
         │                      └── Query 전체 선행 이관 → Java 생성
         │
         ├── REFACTORING ──→ QUERY-FIRST 검토 (OPTIONAL)
         │                    └── 아키텍처 변경으로 Query 재설계 가능
         │
         └── REWRITING ──→ QUERY-FIRST 불필요
                           └── 완전 재개발로 Query 재작성
```

### 2.2 Stage 병합

```yaml
stage_merging:
  allowed_merges:
    merge_2_3:
      name: "Validation + Preparation"
      condition: "Feature 수 < 100"
      merged_phases:
        - "Gap Analysis"
        - "Dependency Analysis"
        - "Architecture Design"

    merge_4_5:
      name: "Generation + Assurance"
      condition: "Mini-Pilot 성공 후 안정화된 파이프라인"
      approach: "Inline validation during generation"

  prohibited_merges:
    - merge: "Stage 1 + Stage 2"
      reason: "Forward/Backward 검증의 독립성 필수"
    - merge: "Stage 1 + any"
      reason: "스펙 추출은 독립 단계로 유지"
```

---

## 3. Phase Customization

### 3.1 Phase 구성 조정

```yaml
phase_customization:
  stage_1_phases:
    default:
      - "Feature Inventory"
      - "Deep Analysis"
      - "Spec Generation"

    simplified:
      condition: "단순 CRUD 시스템"
      phases:
        - "Feature Inventory + Analysis (통합)"
        - "Spec Generation"

    extended:
      condition: "복잡한 비즈니스 로직"
      phases:
        - "Feature Inventory"
        - "Architecture Analysis"
        - "Business Logic Analysis"
        - "Integration Analysis"
        - "Spec Generation"

  stage_2_phases:
    default:
      - "Source Inventory"
      - "Spec Standardization"
      - "Structural Comparison"
      - "Gap Analysis"
      - "Spec Completion"

    minimal:
      condition: "높은 Stage 1 정확도 (>95%)"
      phases:
        - "Source Inventory"
        - "Quick Comparison"
        - "Gap Remediation"
```

### 3.2 Phase 순서 변경

```yaml
phase_reordering:
  allowed:
    - description: "독립적인 Phase 간 순서 조정"
      example: "Stage 3 Phase 2,3 병렬 실행"

  prohibited:
    - description: "의존성 있는 Phase 순서 변경"
      example: "Gap Analysis를 Structural Comparison 전에 실행 불가"

  dependency_rules:
    stage_1:
      - "Inventory → Analysis → Generation (순차)"
    stage_2:
      - "Source Inventory → Comparison → Gap Analysis (순차)"
      - "Spec Standardization 병렬 가능"
    stage_3:
      - "Dependency Analysis → System Integration (순차)"
      - "Technical Debt 분석 병렬 가능"
```

---

## 4. Phase Gate Customization

### 4.1 Threshold 조정

```yaml
threshold_adjustment:
  coverage_thresholds:
    conservative:
      description: "금융/의료 등 고위험 시스템"
      endpoint_coverage: ">= 99.9%"
      spec_accuracy: ">= 95%"
      test_coverage: ">= 90%"

    standard:
      description: "일반 엔터프라이즈 시스템"
      endpoint_coverage: ">= 99%"
      spec_accuracy: ">= 90%"
      test_coverage: ">= 80%"

    agile:
      description: "빠른 검증이 필요한 PoC"
      endpoint_coverage: ">= 95%"
      spec_accuracy: ">= 85%"
      test_coverage: ">= 70%"

  validation_thresholds:
    functional_validation:
      pass: ">= 90 points"
      warning: "80-89 points"
      fail: "< 80 points"

    custom_example:
      project: "Simple CRUD Migration"
      pass: ">= 85 points"
      warning: "75-84 points"
      fail: "< 75 points"
```

### 4.2 Gate 조건 추가/제거

```yaml
gate_condition_modification:
  adding_conditions:
    example_security:
      gate: "Stage 4 Phase 4"
      new_condition:
        name: "security_scan_pass"
        type: "boolean"
        required: true
        validation: "OWASP ZAP scan with 0 high severity issues"

    example_performance:
      gate: "Stage 5 Phase 4"
      new_condition:
        name: "performance_baseline"
        type: "metric"
        required: true
        validation: "Response time <= legacy * 1.1"

  removing_conditions:
    prohibited:
      - "file_count_minimum (최소 산출물 검증)"
      - "structural_compliance (구조 검증)"

    allowed_with_justification:
      - "specific_metric_thresholds (프로젝트 특성에 따라 조정)"
```

---

## 5. Complexity Tier Customization

### 5.1 Tier 정의 조정

```yaml
complexity_customization:
  default_tiers:
    high: "score >= 70"
    medium: "40 <= score < 70"
    low: "score < 40"

  custom_tiers:
    four_tier_example:
      critical: "score >= 85"
      high: "70 <= score < 85"
      medium: "40 <= score < 70"
      low: "score < 40"

    binary_tier_example:
      complex: "score >= 50"
      simple: "score < 50"

  tier_to_model_mapping:
    default:
      high: "opus"
      medium: "sonnet"
      low: "haiku"

    cost_optimized:
      high: "sonnet"
      medium: "haiku"
      low: "haiku"

    quality_focused:
      high: "opus"
      medium: "opus"
      low: "sonnet"
```

### 5.2 Scoring Weight 조정

```yaml
scoring_customization:
  default_weights:
    endpoint_complexity: 25
    data_access_complexity: 25
    business_logic_complexity: 25
    integration_complexity: 15
    data_model_complexity: 10

  data_intensive_project:
    description: "데이터 처리 중심 시스템"
    weights:
      endpoint_complexity: 15
      data_access_complexity: 35
      business_logic_complexity: 20
      integration_complexity: 10
      data_model_complexity: 20

  integration_heavy_project:
    description: "외부 시스템 연동 중심"
    weights:
      endpoint_complexity: 20
      data_access_complexity: 20
      business_logic_complexity: 20
      integration_complexity: 30
      data_model_complexity: 10
```

---

## 6. Parallelization Customization

### 6.1 병렬화 수준 조정

```yaml
parallelization_levels:
  session_parallelism:
    conservative:
      max_sessions: 3
      reason: "리소스 제약 또는 안정성 우선"

    standard:
      max_sessions: 5
      reason: "일반적인 운영 환경"

    aggressive:
      max_sessions: 10
      reason: "충분한 리소스, 빠른 완료 필요"

  task_parallelism:
    within_phase:
      default: "같은 Priority 내 병렬 처리"
      custom: "Domain 간 의존성 없을 시 전체 병렬"

    cross_phase:
      default: "순차 실행"
      custom: "Stage 5 Phase 1-3 병렬 (Feature 단위)"
```

### 6.2 Batch Size 조정

```yaml
batch_customization:
  default_batch_sizes:
    stage_1_phase_2: "Domain 단위"
    stage_4_phase_3: "Feature 단위"
    stage_5_phases: "Feature 단위"

  custom_batch_strategies:
    large_domain:
      condition: "Feature > 100 in single domain"
      strategy: "Sub-domain batching (50 features per batch)"

    small_project:
      condition: "Total features < 100"
      strategy: "All features in single batch"
```

---

## 7. Output Structure Customization

### 7.1 Directory Structure

```yaml
directory_customization:
  default_structure:
    pattern: "stage{N}-outputs/phase{N}/"
    example: "stage1-outputs/phase2/"

  flat_structure:
    condition: "소규모 프로젝트"
    pattern: "outputs/stage{N}-phase{N}/"
    example: "outputs/stage1-phase2/"

  domain_first_structure:
    condition: "도메인별 독립 팀 운영"
    pattern: "{DOMAIN}/stage{N}/phase{N}/"
    example: "PA/stage1/phase2/"
```

### 7.2 File Naming Convention

```yaml
naming_customization:
  default:
    feature_spec: "FEAT-{DOMAIN}-{NNN}/main.yaml"
    api_spec: "api-specs/{endpoint}.yaml"

  verbose:
    feature_spec: "{DOMAIN}_{CATEGORY}_{FUNCTION}/feature-specification.yaml"
    api_spec: "api-specifications/{method}_{endpoint}.yaml"

  minimal:
    feature_spec: "{FEAT-ID}.yaml"
    api_spec: "{endpoint}.yaml"
```

---

## 8. Skill Customization

### 8.1 Skill 구조 조정

```yaml
skill_customization:
  extending_skill:
    approach: "기존 Skill 상속 + 추가 지시"
    example:
      base: "stage1-phase2-deep-analysis"
      extended: "stage1-phase2-deep-analysis-financial"
      additions:
        - "금융 규제 관련 코드 패턴 식별"
        - "거래 로그 추적 로직 분석"

  replacing_skill:
    caution: "전체 교체는 권장하지 않음"
    procedure:
      1: "기존 Skill 복사"
      2: "필요 부분만 수정"
      3: "원본 참조 유지"
      4: "테스트 실행"
```

### 8.2 Custom Skill 생성

```yaml
custom_skill_creation:
  template:
    location: ".claude/skills/custom-{name}/SKILL.md"
    structure:
      - "# Skill Name"
      - "## Objective"
      - "## Prerequisites"
      - "## Methodology"
      - "## Outputs"
      - "## Quality Checks"

  integration:
    skill_registry: ".claude/skills/registry.yaml"
    phase_mapping: "CLAUDE.md 업데이트"
```

---

## 9. Customization Documentation

### 9.1 변경 기록 템플릿

```yaml
customization_record:
  template:
    change_id: "CUSTOM-{NNN}"
    date: "YYYY-MM-DD"
    author: "{name}"

    change_type:
      - "stage_modification"
      - "phase_modification"
      - "threshold_adjustment"
      - "skill_customization"

    description: "{변경 내용 상세}"

    justification: "{변경 사유}"

    impact_analysis:
      affected_stages: []
      affected_phases: []
      affected_outputs: []

    approval:
      approver: "{name}"
      date: "YYYY-MM-DD"

    rollback_plan: "{복구 절차}"
```

### 9.2 Customization Registry

```yaml
customization_registry:
  location: "docs/customizations/registry.yaml"

  structure:
    project_name: "{프로젝트명}"
    base_framework_version: "1.0.0"

    customizations:
      - change_id: "CUSTOM-001"
        summary: "{요약}"
        status: "active | deprecated | reverted"
```

---

## 10. Validation of Customizations

### 10.1 Customization 검증

```yaml
customization_validation:
  pre_deployment:
    - check: "Phase Gate 무결성"
      validation: "모든 Gate가 정의되고 연결됨"

    - check: "의존성 일관성"
      validation: "순환 의존성 없음"

    - check: "Skill 매핑 완전성"
      validation: "모든 Phase에 Skill 할당됨"

  post_deployment:
    - check: "Pilot 실행"
      validation: "Sample Feature 전체 파이프라인 통과"

    - check: "Output 검증"
      validation: "기대 산출물 생성 확인"
```

---

## Appendix: Customization Checklist

### 시작 전 체크리스트

- [ ] 프로젝트 특성 분석 완료
- [ ] 기본 Framework 이해 완료
- [ ] 커스터마이징 범위 결정
- [ ] 이해관계자 승인

### 커스터마이징 체크리스트

- [ ] Stage 구조 결정
- [ ] Phase 구성 결정
- [ ] Phase Gate 조건 정의
- [ ] Complexity Tier 정의
- [ ] 병렬화 수준 결정
- [ ] Output 구조 정의
- [ ] Skill 매핑 완료

### 검증 체크리스트

- [ ] 변경 문서화 완료
- [ ] 영향 분석 완료
- [ ] Pilot 테스트 통과
- [ ] 승인 획득

---

**Next**: [03-decision-trees.md](03-decision-trees.md)
