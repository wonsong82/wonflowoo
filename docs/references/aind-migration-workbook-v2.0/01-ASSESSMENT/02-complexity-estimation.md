# Complexity Estimation

## Overview

이 문서는 Legacy Feature의 복잡도를 체계적으로 평가하는 방법을 정의합니다. 복잡도 평가는 AI 모델 선택, 작업 우선순위, 리소스 할당의 기초가 됩니다.

---

## 1. Complexity Tiers

### 1.1 Three-Tier Classification

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       COMPLEXITY CLASSIFICATION                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   HIGH                    MEDIUM                   LOW                  │
│   ────                    ──────                   ───                  │
│                                                                         │
│   • Stored Procedures     • Standard CRUD         • Simple Query        │
│   • Complex Workflows     • Moderate Logic        • Read-Only           │
│   • 20+ Endpoints         • 2-19 Endpoints        • 1 Endpoint          │
│   • Multi-table Joins     • Basic Joins           • Single Table        │
│   • Dynamic SQL           • Simple Conditions     • No Conditions       │
│                                                                         │
│   AI Model: Opus          AI Model: Sonnet        AI Model: Haiku       │
│   Time: 2-4 hours         Time: 30-60 min         Time: 10-20 min       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tier Definitions

```yaml
complexity_tiers:
  HIGH:
    tier_id: "HIGH"
    description: "복잡한 비즈니스 로직, 다단계 처리"
    indicators:
      - "Stored Procedure 사용"
      - "20개 이상 엔드포인트"
      - "복잡한 상태 전이"
      - "다단계 트랜잭션"
      - "외부 시스템 연동"
    ai_model: "claude-opus-4"
    estimated_time: "2-4 hours per feature"
    human_review: "Required"

  MEDIUM:
    tier_id: "MEDIUM"
    description: "표준 CRUD + 비즈니스 검증"
    indicators:
      - "2-19개 엔드포인트"
      - "기본 검증 로직"
      - "단순 조인 쿼리"
      - "표준 트랜잭션"
    ai_model: "claude-sonnet-4"
    estimated_time: "30-60 minutes per feature"
    human_review: "Sampling"

  LOW:
    tier_id: "LOW"
    description: "단순 조회, 설정성 기능"
    indicators:
      - "1개 엔드포인트"
      - "단순 SELECT"
      - "비즈니스 로직 없음"
      - "Master 데이터 조회"
    ai_model: "claude-haiku-4"
    estimated_time: "10-20 minutes per feature"
    human_review: "Random"
```

---

## 2. Complexity Scoring Model

### 2.1 Scoring Dimensions

복잡도는 다음 5개 차원에서 평가됩니다:

```yaml
scoring_dimensions:
  - dimension: "endpoint_complexity"
    weight: 25
    factors:
      - "Endpoint count"
      - "HTTP method variety"
      - "Parameter complexity"

  - dimension: "data_access_complexity"
    weight: 25
    factors:
      - "Stored procedure usage"
      - "Dynamic SQL"
      - "Multi-table joins"
      - "Subquery depth"

  - dimension: "business_logic_complexity"
    weight: 25
    factors:
      - "Validation rules"
      - "Calculation logic"
      - "Workflow steps"
      - "State transitions"

  - dimension: "integration_complexity"
    weight: 15
    factors:
      - "External system calls"
      - "Message queue usage"
      - "File processing"

  - dimension: "data_model_complexity"
    weight: 10
    factors:
      - "VO/DTO count"
      - "Field count"
      - "Inheritance depth"
```

### 2.2 Scoring Rubric

#### Endpoint Complexity (0-25 points)

| 점수 | 기준 |
|------|------|
| 0-5 | 1 endpoint, 단순 GET |
| 6-10 | 2-5 endpoints, GET/POST |
| 11-15 | 6-10 endpoints, CRUD 완전 |
| 16-20 | 11-19 endpoints, 복잡한 파라미터 |
| 21-25 | 20+ endpoints, 다중 화면 |

#### Data Access Complexity (0-25 points)

| 점수 | 기준 |
|------|------|
| 0-5 | 단순 SELECT, 단일 테이블 |
| 6-10 | 기본 CRUD, 1-2 조인 |
| 11-15 | 동적 SQL, 3-5 조인 |
| 16-20 | 서브쿼리, 복잡한 조건 |
| 21-25 | Stored Procedure, 6+ 조인 |

#### Business Logic Complexity (0-25 points)

| 점수 | 기준 |
|------|------|
| 0-5 | 비즈니스 로직 없음 |
| 6-10 | 단순 검증 (null check, format) |
| 11-15 | 비즈니스 규칙 검증 |
| 16-20 | 계산 로직, 상태 관리 |
| 21-25 | 복잡한 워크플로우, 다단계 처리 |

#### Integration Complexity (0-15 points)

| 점수 | 기준 |
|------|------|
| 0-3 | 외부 연동 없음 |
| 4-7 | 내부 서비스 호출 |
| 8-11 | 단일 외부 시스템 연동 |
| 12-15 | 다중 외부 시스템, 비동기 처리 |

#### Data Model Complexity (0-10 points)

| 점수 | 기준 |
|------|------|
| 0-2 | 1 VO, 5개 이하 필드 |
| 3-5 | 2-3 VO, 10-20 필드 |
| 6-8 | 4-6 VO, 상속 구조 |
| 9-10 | 7+ VO, 복잡한 관계 |

### 2.3 Total Score to Tier Mapping

```
Total Score (0-100)
────────────────────────────────────────────────────────

0         25        50        65        80       100
├─────────┼─────────┼─────────┼─────────┼─────────┤
│   LOW   │  LOW    │  MEDIUM │  MEDIUM │   HIGH  │
│         │         │         │         │         │
└─────────┴─────────┴─────────┴─────────┴─────────┘

Score Range:
  • 0-49:   LOW
  • 50-79:  MEDIUM
  • 80-100: HIGH
```

---

## 3. Automated Complexity Estimation

### 3.1 Evidence Collection

AI가 복잡도를 추정하기 위해 수집하는 증거:

```yaml
evidence_collection:
  source_analysis:
    - controller_file_scan:
        pattern: "@RequestMapping"
        extract: "endpoint_count"

    - service_file_scan:
        patterns:
          - "if.*else"
          - "for.*each"
          - "switch.*case"
        extract: "logic_complexity"

    - mapper_file_scan:
        patterns:
          - "{call"  # Stored Procedure
          - "<if"    # Dynamic SQL
          - "JOIN"   # Table joins
        extract: "sql_complexity"

  structural_analysis:
    - file_count:
        per_layer: true
        extract: "component_count"

    - import_analysis:
        external_packages: true
        extract: "dependency_count"
```

### 3.2 Estimation Algorithm

```python
def estimate_complexity(feature_id: str, source_path: str) -> dict:
    """
    Feature 복잡도 자동 추정

    Returns:
        {
            "tier": "HIGH|MEDIUM|LOW",
            "score": 0-100,
            "reasoning": "...",
            "evidence": {...}
        }
    """
    evidence = collect_evidence(feature_id, source_path)

    # Rule-based overrides
    if evidence.has_stored_procedures:
        return {"tier": "HIGH", "reason": "Stored procedure detected"}

    if evidence.endpoint_count >= 20:
        return {"tier": "HIGH", "reason": "20+ endpoints"}

    if evidence.endpoint_count <= 1:
        if not evidence.has_complex_logic:
            return {"tier": "LOW", "reason": "Single simple endpoint"}

    # Score-based calculation
    scores = {
        "endpoint": calculate_endpoint_score(evidence),
        "data_access": calculate_data_access_score(evidence),
        "business_logic": calculate_logic_score(evidence),
        "integration": calculate_integration_score(evidence),
        "data_model": calculate_model_score(evidence),
    }

    total_score = sum(scores.values())

    if total_score >= 80:
        tier = "HIGH"
    elif total_score >= 50:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    return {
        "tier": tier,
        "score": total_score,
        "scores": scores,
        "evidence": evidence.to_dict(),
        "reasoning": generate_reasoning(tier, scores, evidence)
    }
```

### 3.3 Evidence Schema

```yaml
# Complexity Evidence Schema
evidence:
  feature_id: "FEAT-XX-NNN"
  timestamp: "2025-01-01T00:00:00Z"

  metrics:
    endpoint_count: 0
    controller_files: 0
    service_files: 0
    mapper_files: 0
    vo_files: 0

  patterns:
    has_stored_procedures: false
    has_dynamic_sql: false
    has_external_integration: false
    has_workflow: false

  sql_analysis:
    total_statements: 0
    select_count: 0
    insert_count: 0
    update_count: 0
    delete_count: 0
    max_join_count: 0
    subquery_count: 0

  logic_analysis:
    conditional_depth: 0
    loop_count: 0
    validation_rules: 0
    calculation_blocks: 0
```

---

## 4. Override Rules

### 4.1 Force HIGH Complexity

특정 조건이 감지되면 점수와 무관하게 HIGH로 분류:

```yaml
force_high_rules:
  - rule_id: "SP_DETECTED"
    condition: "has_stored_procedures == true"
    reason: "Stored Procedure는 항상 HIGH 복잡도"

  - rule_id: "MANY_ENDPOINTS"
    condition: "endpoint_count >= 20"
    reason: "20개 이상 엔드포인트는 HIGH 복잡도"

  - rule_id: "COMPLEX_WORKFLOW"
    condition: "workflow_steps >= 5"
    reason: "5단계 이상 워크플로우는 HIGH 복잡도"

  - rule_id: "EXTERNAL_INTEGRATION"
    condition: "external_system_count >= 3"
    reason: "3개 이상 외부 연동은 HIGH 복잡도"
```

### 4.2 Force LOW Complexity

특정 조건이 감지되면 점수와 무관하게 LOW로 분류:

```yaml
force_low_rules:
  - rule_id: "SINGLE_ENDPOINT"
    condition: "endpoint_count == 1 AND has_stored_procedures == false"
    reason: "단일 엔드포인트, SP 없음"

  - rule_id: "READ_ONLY"
    condition: "insert_count == 0 AND update_count == 0 AND delete_count == 0"
    reason: "조회 전용 기능"

  - rule_id: "SIMPLE_CRUD"
    condition: "endpoint_count <= 4 AND max_join_count <= 1"
    reason: "단순 CRUD, 복잡한 조인 없음"
```

---

## 5. Model Selection Based on Complexity

### 5.1 Model Mapping

```yaml
model_selection:
  high_complexity:
    tier: "HIGH"
    model: "opus"
    model_id: "claude-opus-4-20250514"
    reasoning: "복잡한 비즈니스 로직 분석에 최대 추론 능력 필요"
    use_cases:
      - "Stored Procedure 분석"
      - "복잡한 워크플로우 추적"
      - "다중 시스템 통합"

  medium_complexity:
    tier: "MEDIUM"
    model: "sonnet"
    model_id: "claude-sonnet-4-20250514"
    reasoning: "표준 패턴 인식 및 코드 생성에 적합"
    use_cases:
      - "표준 CRUD 분석"
      - "일반 비즈니스 로직"
      - "단순 조인 쿼리"

  low_complexity:
    tier: "LOW"
    model: "haiku"
    model_id: "claude-haiku-4-20250514"
    reasoning: "단순 작업에 비용 효율적"
    use_cases:
      - "단순 조회 기능"
      - "설정 데이터 조회"
      - "기본 CRUD"
```

### 5.2 Cost-Quality Tradeoff

```
Complexity vs Cost vs Quality Matrix
────────────────────────────────────────────────────────

                │ Cost per Feature │ Quality Risk │ Speed
────────────────┼──────────────────┼──────────────┼────────
HIGH + Opus     │       $$$        │     Low      │  Slow
HIGH + Sonnet   │       $$         │    Medium    │ Medium
HIGH + Haiku    │       $          │     HIGH     │  Fast   ← Not Recommended
────────────────┼──────────────────┼──────────────┼────────
MEDIUM + Opus   │       $$$        │    Very Low  │  Slow   ← Over-engineered
MEDIUM + Sonnet │       $$         │     Low      │ Medium  ← Optimal
MEDIUM + Haiku  │       $          │    Medium    │  Fast
────────────────┼──────────────────┼──────────────┼────────
LOW + Opus      │       $$$        │    Very Low  │  Slow   ← Over-engineered
LOW + Sonnet    │       $$         │    Very Low  │ Medium
LOW + Haiku     │       $          │     Low      │  Fast   ← Optimal
────────────────┴──────────────────┴──────────────┴────────
```

---

## 6. Complexity Estimation Output

### 6.1 Per-Feature Report

```yaml
# feature-complexity-report.yaml
feature_id: "FEAT-PA-205"
domain: "PA"
screen_id: "PA0205030M"

complexity:
  tier: "HIGH"
  score: 85
  model_assigned: "claude-opus-4-20250514"

scoring_breakdown:
  endpoint_complexity:
    score: 22
    details: "23 endpoints detected"
  data_access_complexity:
    score: 25
    details: "Stored procedures detected, 8 table joins"
  business_logic_complexity:
    score: 20
    details: "Complex workflow with state transitions"
  integration_complexity:
    score: 10
    details: "No external integration"
  data_model_complexity:
    score: 8
    details: "6 VOs with inheritance"

evidence:
  endpoint_count: 23
  has_stored_procedures: true
  stored_procedure_list:
    - "EPA_PA_PKG.SELECT_LIST"
    - "EPA_PA_PKG.PROCESS_SAVE"
  max_join_count: 8
  dynamic_sql_blocks: 15
  vo_count: 6

override_applied: "SP_DETECTED"
override_reason: "Stored Procedure detected - forced HIGH"
```

### 6.2 Domain Summary

```yaml
# domain-complexity-summary.yaml
domain: "PA"
assessment_date: "2025-01-01"

distribution:
  HIGH: 45
  MEDIUM: 180
  LOW: 84
  total: 309

high_complexity_features:
  - feature_id: "FEAT-PA-205"
    score: 85
    reason: "Stored procedures, 23 endpoints"
  - feature_id: "FEAT-PA-178"
    score: 82
    reason: "Complex workflow, external integration"
  # ... more

model_allocation:
  opus_tasks: 45
  sonnet_tasks: 180
  haiku_tasks: 84

estimated_effort:
  total_hours: 450
  high_features_hours: 180
  medium_features_hours: 180
  low_features_hours: 90
```

---

## 7. Best Practices

### 7.1 Estimation Guidelines

```yaml
guidelines:
  - rule: "When in doubt, estimate higher"
    rationale: "Under-estimation leads to quality issues"

  - rule: "Review HIGH estimates manually"
    rationale: "HIGH features consume most resources"

  - rule: "Re-estimate after pilot phase"
    rationale: "Actual complexity may differ from estimate"

  - rule: "Track estimation accuracy"
    rationale: "Improve estimation model over time"
```

### 7.2 Common Pitfalls

| 함정 | 설명 | 해결책 |
|------|------|--------|
| **과소 추정** | 간단해 보이지만 숨겨진 복잡성 | Override rules 적용 |
| **과대 추정** | 파일 수가 많지만 단순 반복 | 패턴 분석으로 보정 |
| **일관성 부족** | 평가자마다 다른 기준 | 자동화된 점수 체계 |
| **컨텍스트 무시** | 도메인 특성 미반영 | 도메인별 보정 계수 |

---

## Next Steps

Complexity Estimation 완료 후:

1. **Feasibility Matrix** → [03-feasibility-matrix.md](03-feasibility-matrix.md)
2. **Workflow Design** → [../02-WORKFLOW-DESIGN/](../02-WORKFLOW-DESIGN/)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-15
