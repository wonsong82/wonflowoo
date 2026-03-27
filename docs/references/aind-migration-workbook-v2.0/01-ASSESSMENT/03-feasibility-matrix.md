# Feasibility Matrix

## Overview

이 문서는 Legacy 마이그레이션 프로젝트의 실행 가능성을 평가하고, 적절한 마이그레이션 전략을 선택하기 위한 의사결정 프레임워크를 제공합니다.

---

## 1. Migration Strategy Options

### 1.1 Strategy Spectrum

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MIGRATION STRATEGY SPECTRUM                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   REHOSTING      REPLATFORMING     REFACTORING      REWRITING       │
│   (Lift & Shift)  (Lift & Reshape)  (Restructure)    (Rebuild)      │
│                                                                     │
│   ───────────────────────────────────────────────────────────────→  │
│   낮은 변경                                              높은 변경      │
│   빠른 실행                                              느린 실행      │
│   낮은 리스크                                            높은 리스크     │
│   기술 부채 유지                                         기술 부채 해소   │
└────────────────────────────────────────────────────────────────────┘
```

### 1.2 Strategy Definitions

```yaml
migration_strategies:
  REHOSTING:
    alias: "Lift & Shift"
    description: "인프라만 변경, 코드 수정 최소화"
    changes:
      infrastructure: "변경"
      application_code: "변경 없음"
      database: "변경 없음"
    use_cases:
      - "긴급 데이터센터 이전"
      - "클라우드 마이그레이션 (IaaS)"
    ai_framework_fit: "낮음"

  REPLATFORMING:
    alias: "Lift & Reshape"
    description: "프레임워크 변경, 비즈니스 로직 유지"
    changes:
      infrastructure: "변경"
      application_code: "프레임워크 교체"
      database: "유지 또는 최소 변경"
    use_cases:
      - "Spring MVC → Spring Boot"
      - "EJB → Spring"
      - "Oracle → PostgreSQL (SQL 호환 범위 내)"
    ai_framework_fit: "높음 (본 프레임워크 최적 대상)"

  REFACTORING:
    alias: "Restructure"
    description: "아키텍처 일부 재설계"
    changes:
      infrastructure: "변경"
      application_code: "상당 부분 재작성"
      database: "스키마 변경 가능"
    use_cases:
      - "모놀리스 → 모듈러 모놀리스"
      - "계층 구조 개선"
      - "성능 병목 해소"
    ai_framework_fit: "중간 (Spec 추출 후 설계 변경)"

  REWRITING:
    alias: "Rebuild"
    description: "완전 재개발"
    changes:
      infrastructure: "변경"
      application_code: "완전 재작성"
      database: "재설계 가능"
    use_cases:
      - "기술 스택 완전 교체"
      - "비즈니스 모델 변경"
      - "레거시 폐기"
    ai_framework_fit: "중간 (Spec 추출 후 설계 변경)"
```

---

## 2. Feasibility Assessment Criteria

### 2.1 Assessment Dimensions

```yaml
assessment_dimensions:
  - dimension: "technical_feasibility"
    weight: 30
    description: "기술적으로 마이그레이션 가능한가?"
    factors:
      - "코드 가독성 및 구조화 수준"
      - "프레임워크 호환성"
      - "데이터베이스 이식성"
      - "외부 연동 복잡성"

  - dimension: "business_feasibility"
    weight: 25
    description: "비즈니스 관점에서 가치가 있는가?"
    factors:
      - "비즈니스 로직 문서화 수준"
      - "도메인 전문가 접근성"
      - "운영 중단 허용 시간"
      - "비즈니스 연속성 요구사항"

  - dimension: "resource_feasibility"
    weight: 25
    description: "필요한 리소스를 확보할 수 있는가?"
    factors:
      - "예산"
      - "인력"
      - "시간"
      - "도구 및 인프라"

  - dimension: "risk_feasibility"
    weight: 20
    description: "리스크를 감당할 수 있는가?"
    factors:
      - "데이터 손실 리스크"
      - "기능 누락 리스크"
      - "운영 장애 리스크"
      - "롤백 가능성"
```

### 2.2 Scoring Rubric

#### Technical Feasibility (0-30 points)

| 점수 | 기준 |
|------|------|
| 25-30 | 잘 구조화된 코드, 표준 프레임워크, 문서화 양호 |
| 18-24 | 일반적인 레거시, 일부 복잡성 존재 |
| 10-17 | 복잡한 의존성, 커스텀 프레임워크 |
| 0-9 | 스파게티 코드, 문서 없음, 블랙박스 컴포넌트 |

#### Business Feasibility (0-25 points)

| 점수 | 기준 |
|------|------|
| 21-25 | 도메인 전문가 상주, 비즈니스 규칙 문서화 |
| 15-20 | 일부 전문가 접근 가능, 부분 문서화 |
| 8-14 | 제한적 전문가 접근, 암묵적 지식 다수 |
| 0-7 | 전문가 부재, 비즈니스 로직 불명확 |

#### Resource Feasibility (0-25 points)

| 점수 | 기준 |
|------|------|
| 21-25 | 충분한 예산, 전담 팀, 현실적 일정 |
| 15-20 | 적정 예산, 파트타임 인력, 촉박한 일정 |
| 8-14 | 제한된 예산, 부족한 인력, 무리한 일정 |
| 0-7 | 극히 제한된 리소스 |

#### Risk Feasibility (0-20 points)

| 점수 | 기준 |
|------|------|
| 17-20 | 롤백 계획 완비, 병렬 운영 가능, 낮은 영향도 |
| 12-16 | 기본 롤백, 제한적 병렬 운영, 중간 영향도 |
| 6-11 | 롤백 어려움, 빅뱅 전환, 높은 영향도 |
| 0-5 | 롤백 불가, 치명적 비즈니스 영향 |

---

## 3. Decision Matrix

### 3.1 Feasibility Score Interpretation

```
Total Score (0-100)
────────────────────────────────────────────────────────

0         30        50        70        90       100
├─────────┼─────────┼─────────┼─────────┼─────────┤
│  HIGH   │ MEDIUM  │   LOW   │  VERY   │ MINIMAL │
│  RISK   │  RISK   │  RISK   │  LOW    │  RISK   │
│         │         │         │  RISK   │         │
└─────────┴─────────┴─────────┴─────────┴─────────┘
   ↓          ↓          ↓          ↓          ↓
 재검토     신중히      진행       적극       즉시
 필요       진행       가능       진행       진행
```

### 3.2 Strategy Selection Matrix

```
┌────────────────────────────────────────────────────────────┐
│                      STRATEGY SELECTION MATRIX             │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                    │ 시간 제약 낮음   │ 시간 제약 높음     │      │
│                    │ (6개월+)       │ (3개월 이하)      │     │
│ ───────────────────┼────────────────┼────────────────┤     │
│ 기술 부채 높음        │  REFACTORING   │ REPLATFORMING  │     │
│ (구조적 문제)         │  or REWRITING  │                │     │
│ ───────────────────┼────────────────┼────────────────┤     │
│ 기술 부채 낮음        │ REPLATFORMING  │  REHOSTING     │     │
│ (양호한 구조)        │                │                │      │
│ ───────────────────┴────────────────┴────────────────┘     │
│                                                            │
│                    │ 예산 충분        │ 예산 제한         │     │
│ ───────────────────┼────────────────┼────────────────┤     │
│ 비즈니스 가치 높음      │  REFACTORING   │ REPLATFORMING  │     │
│ (장기 투자 가치)       │  or REWRITING  │                │     │
│ ───────────────────┼────────────────┼────────────────┤     │
│ 비즈니스 가치 낮음      │ REPLATFORMING  │  REHOSTING     │     │
│ (유지만 필요)         │                │  or 유지보수     │     │
│ ───────────────────┴────────────────┴────────────────┘     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 3.3 AI Framework Applicability

```yaml
ai_framework_applicability:
  optimal_fit:
    strategy: "REPLATFORMING"
    score_threshold: ">= 60"
    characteristics:
      - "비즈니스 로직 100% 보존 필요"
      - "프레임워크/런타임 현대화"
      - "데이터베이스 유지 또는 마이너 변경"
    framework_utilization:
      stage1_discovery: "Full"
      stage2_validation: "Full"
      stage3_preparation: "Full"
      stage4_generation: "Full"
      stage5_assurance: "Full"

  good_fit:
    strategy: "REFACTORING"
    score_threshold: ">= 50"
    characteristics:
      - "아키텍처 개선 필요"
      - "비즈니스 로직 대부분 보존"
      - "일부 재설계"
    framework_utilization:
      stage1_discovery: "Full"
      stage2_validation: "Full"
      stage3_preparation: "Customized"
      stage4_generation: "Partial"
      stage5_assurance: "Full"

  limited_fit:
    strategy: "REWRITING"
    score_threshold: "Any"
    characteristics:
      - "완전 재개발"
      - "비즈니스 로직 재해석"
      - "새로운 아키텍처"
    framework_utilization:
      stage1_discovery: "Full (지식 추출용)"
      stage2_validation: "Partial"
      stage3_preparation: "N/A (새 설계)"
      stage4_generation: "N/A"
      stage5_assurance: "Custom"

  not_applicable:
    strategy: "REHOSTING"
    characteristics:
      - "코드 변경 없음"
    framework_utilization: "None"
```

---

## 3.4 QUERY-FIRST 전략 (REHOSTING/REPLATFORMING 필수 고려)

> **CRITICAL**: REHOSTING 또는 REPLATFORMING 마이그레이션에서는 QUERY-FIRST 전략을 최우선으로 고려해야 합니다.

### 배경

Legacy 시스템 마이그레이션에서 가장 빈번하게 발생하는 문제는 **SQL 로직 변조**입니다:

```yaml
common_issues:
  sql_logic_corruption:
    description: "AI/자동화 도구가 SQL을 재해석하여 비즈니스 로직 변경"
    examples:
      - "컬럼명/테이블명 추측으로 인한 참조 오류"
      - "조건값 임의 변경 (리터럴 값 단순화)"
      - "복잡한 JOIN/서브쿼리 구조 간소화"
      - "DECODE/CASE 로직 재해석"
    impact:
      - "런타임 SQL 오류 (존재하지 않는 컬럼/테이블)"
      - "비즈니스 로직 변조 (잘못된 결과 반환)"
      - "데이터 정합성 파괴"

  root_cause:
    description: "스펙 기반 SQL 재생성"
    explanation: |
      AI가 Stage 1에서 추출한 스펙을 기반으로 SQL을 '새로 생성'하면,
      원본 SQL의 미묘한 비즈니스 로직이 손실되거나 변조됨
```

### QUERY-FIRST 원칙

```yaml
query_first_principle:
  rule: "Query 이관이 어떤 Task보다 우선한다"
  rationale: "비즈니스 로직은 Query에 있다. Query가 변경되면 비즈니스가 변경된다."

  applicable_strategies:
    - REHOSTING
    - REPLATFORMING

  not_applicable:
    - REFACTORING  # 아키텍처 재설계로 Query 변경 가능
    - REWRITING    # 완전 재개발로 Query 재작성 가능
```

### 2-Phase 분리 전략

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    QUERY-FIRST 전략 (전체 선행 이관)                      │
│                                                                         │
│  "Feature별 작업이 아닌, Query 전체를 먼저 이관한 후 Java 코드 생성"       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
┌────────────┐               ┌────────────┐               ┌────────────┐
│  PHASE 1   │               │   GATE     │               │  PHASE 2   │
│ Query 이관 │ ──────────▶  │ Fidelity   │ ──────────▶  │ Java 생성  │
│ (전체)     │   100% 완료   │ (100%)     │   PASS 후    │ (Feature별)│
└────────────┘               └────────────┘               └────────────┘
```

### REHOSTING/REPLATFORMING 적용 가이드

```yaml
application_guide:
  rehosting:
    description: "인프라만 변경, 코드 수정 최소화"
    query_first_requirement: "MANDATORY"
    rationale:
      - "비즈니스 로직 100% 보존 필수"
      - "Query 변경 = 비즈니스 변경 (허용 불가)"
    phase_1_scope: "전체 Query 이관 및 검증"
    phase_2_scope: "없음 (코드 변경 최소화)"

  replatforming:
    description: "프레임워크 변경, 비즈니스 로직 유지"
    query_first_requirement: "MANDATORY"
    rationale:
      - "비즈니스 로직 100% 보존 필수"
      - "프레임워크만 변경 (Spring MVC → Spring Boot)"
      - "Query는 반드시 원본 유지"
    phase_1_scope:
      - "iBatis → MyBatis 문법 변환"
      - "SQL 로직 100% 보존"
      - "Query Fidelity 검증"
    phase_2_scope:
      - "Java 코드 생성 (Controller, Service, DTO)"
      - "Query 검증 PASS 후에만 시작"

  refactoring:
    description: "아키텍처 일부 재설계"
    query_first_requirement: "OPTIONAL"
    rationale:
      - "아키텍처 변경으로 Query 재작성 가능"
      - "단, Legacy Query 참조는 필수"

  rewriting:
    description: "완전 재개발"
    query_first_requirement: "NOT_APPLICABLE"
    rationale:
      - "Query 재설계 예정"
      - "Legacy Query는 참조용으로만 사용"
```

### 허용/금지 변경 사항

```yaml
query_transformation:
  allowed_changes:
    description: "iBatis → MyBatis 문법 변환만 허용"
    items:
      - "#var# → #{var}"
      - "$var$ → ${var}"
      - "<isNotEmpty> → <if test>"
      - "parameterClass → parameterType"
      - "resultClass → resultType"
      - "namespace 변경"

  prohibited_changes:
    description: "SQL 로직 변경 금지"
    items:
      - "SQL 로직 재해석/재생성"
      - "컬럼명/테이블명 추측 또는 축약"
      - "리터럴 조건값 변경"
      - "JOIN 조건 수정"
      - "WHERE 절 IN/LIKE/= 값 변경"
      - "GROUP BY/ORDER BY/ROLLUP 구조 변경"
      - "DECODE/CASE/NVL 로직 간소화"
      - "서브쿼리/UNION 구조 변경"
    on_violation: "BLOCK - 생성 중단"
```

### 의사결정 트리

```
REHOSTING 또는 REPLATFORMING?
           │
           ├── YES ──→ QUERY-FIRST 전략 적용 (MANDATORY)
           │            │
           │            ├── PHASE 1: Query 전체 이관
           │            │
           │            ├── GATE: Query Fidelity (100%)
           │            │
           │            └── PHASE 2: Java 코드 생성
           │
           └── NO ──→ REFACTORING/REWRITING?
                        │
                        └── Query 재설계 검토 가능
```

### 워크플로우 적용

QUERY-FIRST 전략을 적용하려면 다음 워크플로우 커스터마이징이 필요합니다:

```yaml
workflow_customization:
  stage_4_generation:
    phase_3_domain_execution:
      modification: "2-Phase 분리"
      phase_3a: "Query 전체 이관 (Mapper XML)"
      gate: "Query Fidelity Gate (100%)"
      phase_3b: "Java 코드 생성 (Query 검증 후)"

  quality_gate:
    name: "Query Fidelity Gate"
    threshold: "100%"
    human_review: "REQUIRED"
    blocking: true

  validation:
    type: "Line-by-Line 비교"
    scope: "전체 SQL Statement"
    criteria: "Legacy와 100% 일치"
```

**상세 가이드**: [02-customization-guide.md](02-customization-guide.md)

---

## 4. Risk Assessment

### 4.1 Risk Categories

```yaml
risk_categories:
  technical_risks:
    - risk: "Hidden Complexity"
      description: "분석 단계에서 발견되지 않은 복잡성"
      mitigation: "Pilot phase로 조기 발견"
      probability: "Medium"
      impact: "High"

    - risk: "Framework Incompatibility"
      description: "Legacy 프레임워크 특성 재현 어려움"
      mitigation: "Protocol adapter 개발"
      probability: "Low"
      impact: "High"

    - risk: "Data Loss"
      description: "마이그레이션 중 데이터 손실"
      mitigation: "백업, 검증, 롤백 계획"
      probability: "Low"
      impact: "Critical"

  business_risks:
    - risk: "Feature Gap"
      description: "일부 기능 누락"
      mitigation: "양방향 검증 (Stage 2, 5)"
      probability: "Medium"
      impact: "High"

    - risk: "Performance Degradation"
      description: "성능 저하"
      mitigation: "성능 테스트, 튜닝"
      probability: "Medium"
      impact: "Medium"

    - risk: "Business Disruption"
      description: "운영 중단"
      mitigation: "병렬 운영, 단계적 전환"
      probability: "Low"
      impact: "Critical"

  project_risks:
    - risk: "Schedule Overrun"
      description: "일정 지연"
      mitigation: "버퍼, 점진적 배포"
      probability: "High"
      impact: "Medium"

    - risk: "Budget Overrun"
      description: "예산 초과"
      mitigation: "우선순위 기반 scope 조정"
      probability: "Medium"
      impact: "Medium"

    - risk: "Resource Turnover"
      description: "핵심 인력 이탈"
      mitigation: "문서화, 지식 공유"
      probability: "Medium"
      impact: "High"
```

### 4.2 Risk Mitigation Strategies

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      RISK MITIGATION STRATEGIES                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Risk Level   │ Strategy              │ Actions                        │
│ ───────────────┼───────────────────────┼─────────────────────────────── │
│   CRITICAL     │ Avoid / Transfer      │ • Insurance                    │
│                │                       │ • External expertise           │
│                │                       │ • Parallel systems             │
│ ───────────────┼───────────────────────┼─────────────────────────────── │
│   HIGH         │ Mitigate              │ • Pilot phase validation       │
│                │                       │ • Incremental rollout          │
│                │                       │ • Rollback plans               │
│ ───────────────┼───────────────────────┼─────────────────────────────── │
│   MEDIUM       │ Monitor               │ • Regular checkpoints          │
│                │                       │ • Early warning indicators     │
│                │                       │ • Contingency plans            │
│ ───────────────┼───────────────────────┼─────────────────────────────── │
│   LOW          │ Accept                │ • Document known risks         │
│                │                       │ • Reserve budget               │
│                │                       │ • Monitor during execution     │
│ ───────────────┴───────────────────────┴─────────────────────────────── │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Go/No-Go Decision Framework

### 5.1 Decision Criteria

```yaml
decision_criteria:
  mandatory_requirements:
    - criterion: "Source code access"
      type: "binary"
      pass: "Full access available"
      fail: "No access or partial access"

    - criterion: "Business sponsor"
      type: "binary"
      pass: "Executive sponsor identified"
      fail: "No sponsor"

    - criterion: "Minimum budget"
      type: "threshold"
      pass: "Budget >= 70% of estimate"
      fail: "Budget < 70% of estimate"

  weighted_criteria:
    - criterion: "Technical feasibility score"
      weight: 30
      threshold: ">= 15"

    - criterion: "Business feasibility score"
      weight: 25
      threshold: ">= 12"

    - criterion: "Resource feasibility score"
      weight: 25
      threshold: ">= 10"

    - criterion: "Risk feasibility score"
      weight: 20
      threshold: ">= 8"
```

### 5.2 Decision Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GO / NO-GO DECISION                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Mandatory Requirements    │    All Pass?                              │
│   ──────────────────────────┼───────────────────                         │
│                             │                                           │
│         YES ────────────────┼───→ Check Weighted Score                  │
│                             │                                           │
│         NO  ────────────────┼───→ NO-GO (Address gaps first)            │
│                             │                                           │
│   ──────────────────────────┴───────────────────────────────            │
│                                                                         │
│   Weighted Score            │    Decision                               │
│   ──────────────────────────┼───────────────────                         │
│                             │                                           │
│   >= 70                     │    GO (Proceed with confidence)           │
│   50 - 69                   │    CONDITIONAL GO (Address risks first)   │
│   30 - 49                   │    DEFER (Improve conditions)             │
│   < 30                      │    NO-GO (Not feasible at this time)      │
│                             │                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Feasibility Report Template

### 6.1 Executive Summary

```yaml
# feasibility-report.yaml

executive_summary:
  project_name: "{PROJECT_NAME}"
  assessment_date: "YYYY-MM-DD"
  recommendation: "GO | CONDITIONAL_GO | DEFER | NO_GO"
  recommended_strategy: "REPLATFORMING | REFACTORING | REWRITING"
  key_findings:
    strengths: []
    weaknesses: []
    opportunities: []
    threats: []

feasibility_scores:
  technical: 0  # /30
  business: 0   # /25
  resource: 0   # /25
  risk: 0       # /20
  total: 0      # /100

mandatory_checks:
  source_access: "PASS | FAIL"
  business_sponsor: "PASS | FAIL"
  minimum_budget: "PASS | FAIL"

risk_summary:
  critical_risks: 0
  high_risks: 0
  medium_risks: 0
  low_risks: 0
  total_risks: 0
```

### 6.2 Detailed Assessment

```yaml
# Detailed sections of feasibility report

technical_assessment:
  code_quality:
    score: 0
    findings: []
  architecture:
    pattern: ""
    layers: []
    complexity: ""
  frameworks:
    current: []
    target: []
    compatibility: ""
  database:
    vendor: ""
    complexity: ""
    migration_effort: ""

business_assessment:
  documentation:
    level: "HIGH | MEDIUM | LOW"
    gaps: []
  domain_expertise:
    availability: ""
    knowledge_transfer_plan: ""
  business_continuity:
    requirements: []
    constraints: []

resource_assessment:
  budget:
    estimated: 0
    allocated: 0
    gap: 0
  timeline:
    estimated_months: 0
    target_months: 0
    feasible: true
  team:
    required_roles: []
    current_availability: []
    gaps: []

risk_assessment:
  risks:
    - id: ""
      category: ""
      description: ""
      probability: ""
      impact: ""
      mitigation: ""
      owner: ""
```

---

## 7. Next Steps After Assessment

### 7.1 If GO

```yaml
go_next_steps:
  - step: "Finalize project charter"
    owner: "Project Manager"
    timeline: "Week 1"

  - step: "Assemble project team"
    owner: "Resource Manager"
    timeline: "Week 1-2"

  - step: "Setup development environment"
    owner: "DevOps"
    timeline: "Week 2"

  - step: "Begin Stage 1: Discovery"
    owner: "Tech Lead"
    timeline: "Week 3"
```

### 7.2 If CONDITIONAL GO

```yaml
conditional_go_next_steps:
  - step: "Address identified gaps"
    actions:
      - "Secure additional budget if needed"
      - "Identify and onboard missing expertise"
      - "Develop risk mitigation plans"
    timeline: "2-4 weeks"

  - step: "Re-assess after gap resolution"
    owner: "Assessment Team"
    timeline: "After gap resolution"
```

### 7.3 If DEFER or NO-GO

```yaml
defer_no_go_next_steps:
  - step: "Document assessment findings"
    owner: "Assessment Team"

  - step: "Identify improvement actions"
    owner: "Technical Lead"

  - step: "Set conditions for re-assessment"
    owner: "Project Sponsor"

  - step: "Schedule follow-up review"
    timeline: "3-6 months"
```

---

## Next Steps

Feasibility Assessment 완료 후:

1. **Workflow Design** → [../02-WORKFLOW-DESIGN/01-stage-phase-model.md](../02-WORKFLOW-DESIGN/01-stage-phase-model.md)
2. **Skill Definition** → [../03-SKILL-DEFINITION/](../03-SKILL-DEFINITION/)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-15
