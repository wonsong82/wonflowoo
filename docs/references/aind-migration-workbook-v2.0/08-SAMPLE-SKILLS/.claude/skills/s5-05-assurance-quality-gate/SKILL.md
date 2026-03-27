---
name: s5-05-assurance-quality-gate
description: Use when making final quality gate decisions for wave completion, aggregating all validation results, or requiring human approval for production readiness (project)
---

# Quality Gate

> **Skill ID**: S5-05
> **Skill Type**: Validation (Sequential - Singleton)
> **Stage**: 5 - Assurance
> **Phase**: 5.5 - Quality Gate
> **Parallelization**: None (Sequential, Wave-level)
> **Human Approval**: REQUIRED

## 1. Overview

### 1.1 Purpose

모든 Assurance 검증 결과를 종합하여 **최종 품질 판정**을 수행합니다. 이 Phase는 **Human Approval이 필수**이며, Wave 완료 및 Production 배포 가능 여부를 결정합니다.

**판정 결과:**
- **APPROVED**: 모든 기준 충족, Production 배포 가능
- **CONDITIONAL**: 경미한 이슈, 기한 내 수정 조건 배포
- **REJECTED**: 심각한 이슈, Stage 4 재작업 필요

**종합 대상:**
- S5-01: Structural Check 결과
- S5-02: Functional Validation 결과
- S5-03: API Contract Test 결과
- S5-04: Performance Baseline 결과
- S4 Build/Test 결과

### 1.2 Scope

**In Scope:**
- 전 Phase 검증 결과 종합
- 품질 점수 계산
- Issue 분류 및 집계
- Human Approval 요청
- 최종 판정 기록

**Out of Scope:**
- 개별 검증 수행 (-> S5-01~04)
- 수정 작업 (-> Remediation)
- 배포 실행 (-> DevOps)

### 1.3 Decision Matrix

| Condition | Decision | Action |
|-----------|----------|--------|
| Blocker = 0, Critical < 5, Score >= 85 | **APPROVED** | Proceed to deployment |
| Blocker = 0, Critical 5-14, Score 70-84 | **CONDITIONAL** | Proceed with remediation plan |
| Blocker >= 1 OR Critical >= 15 OR Score < 70 | **REJECTED** | Return to Stage 4 |

### 1.4 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Human in Loop** | 최종 결정은 Human | 책임 소재 명확화 |
| **Evidence-Based** | 데이터 기반 판정 | 객관적 품질 평가 |
| **Traceable** | 모든 판정 기록 | 감사 추적 가능 |
| **Threshold-Based** | 정량적 기준 적용 | 일관된 품질 보장 |

### 1.5 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S5-05는 최종 품질 게이트이며, **SQL Fidelity 검증 결과가 품질 점수에 반영**

### 1.6 Relationships

**Predecessors:**
| Skill | Reason | Input |
|-------|--------|-------|
| `s5-01-assurance-structural-check` | 구조 검증 결과 | structural-report.yaml |
| `s5-02-assurance-functional-validation` | 기능 검증 결과 | validation-summary.yaml |
| `s5-03-assurance-api-contract-test` | 계약 검증 결과 | contract-validation.yaml |
| `s5-04-assurance-performance-baseline` | 성능 분석 결과 | performance-analysis.yaml |

**Successors:**
| Skill | Reason |
|-------|--------|
| Wave Deployment | APPROVED/CONDITIONAL 시 |
| Rollback | REJECTED 시 Stage 4 재작업 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S5-01"
    skill_name: "s5-01-assurance-structural-check"
    status: "completed"
    artifacts:
      - "structural-report.yaml"

  - skill_id: "S5-02"
    skill_name: "s5-02-assurance-functional-validation"
    status: "completed"
    artifacts:
      - "validation-summary.yaml"

  - skill_id: "S5-03"
    skill_name: "s5-03-assurance-api-contract-test"
    status: "completed"
    artifacts:
      - "contract-validation.yaml"
      - "miplatform-compatibility.yaml"

  - skill_id: "S5-04"
    skill_name: "s5-04-assurance-performance-baseline"
    status: "completed"
    artifacts:
      - "performance-analysis.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| structural_report | file | `work/specs/stage5-outputs/phase1/structural-report.yaml` | YAML | Yes |
| functional_validation | file | `work/specs/stage5-outputs/phase2/validation-summary.yaml` | YAML | Yes |
| contract_validation | file | `work/specs/stage5-outputs/phase3/contract-validation.yaml` | YAML | Yes |
| performance_analysis | file | `work/specs/stage5-outputs/phase4/performance-analysis.yaml` | YAML | Yes |
| build_reports | directory | `next-hallain/build/reports/` | Various | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Read | - | 리포트 읽기 |
| Write | - | 최종 리포트 생성 |

**Human Approvers:**
| Role | Responsibility |
|------|----------------|
| Tech Lead | 기술적 품질 승인 |
| Architect | 아키텍처 준수 승인 |

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: sequential
  unit: wave
  parallelization:
    enabled: false
  lifecycle:
    timeout_minutes: 120
    retry_on_failure: 1

task:
  naming_pattern: "QGATE-{WAVE}"
  granularity: wave
```

### 3.2 Quality Gate Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       QUALITY GATE PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│   │ S5-01       │  │ S5-02       │  │ S5-03       │  │ S5-04       │   │
│   │ Structural  │  │ Functional  │  │ Contract    │  │ Performance │   │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│          │                │                │                │          │
│          └────────────────┴────────────────┴────────────────┘          │
│                                    │                                    │
│                                    ▼                                    │
│                    ┌──────────────────────────────┐                    │
│                    │     Result Aggregation       │                    │
│                    └──────────────┬───────────────┘                    │
│                                   │                                     │
│                                   ▼                                     │
│                    ┌──────────────────────────────┐                    │
│                    │      Issue Classification    │                    │
│                    │   (Blocker/Critical/Major)   │                    │
│                    └──────────────┬───────────────┘                    │
│                                   │                                     │
│                                   ▼                                     │
│                    ┌──────────────────────────────┐                    │
│                    │      Score Calculation       │                    │
│                    └──────────────┬───────────────┘                    │
│                                   │                                     │
│                                   ▼                                     │
│                    ┌──────────────────────────────┐                    │
│                    │     Decision Matrix          │                    │
│                    │   Apply APPROVED/COND/REJ    │                    │
│                    └──────────────┬───────────────┘                    │
│                                   │                                     │
│                                   ▼                                     │
│                    ┌──────────────────────────────┐                    │
│                    │     HUMAN APPROVAL           │                    │
│                    │     (Tech Lead + Architect)  │                    │
│                    └──────────────┬───────────────┘                    │
│                                   │                                     │
│                                   ▼                                     │
│                    ┌──────────────────────────────┐                    │
│                    │      Final Report            │                    │
│                    │      & Git Tag               │                    │
│                    └──────────────────────────────┘                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Issue Severity Classification

```yaml
issue_severity:
  blocker:
    description: "배포 불가능한 심각한 결함"
    criteria:
      - "Build failure"
      - "Critical security vulnerability"
      - "Data corruption risk"
      - "Core functionality broken"
    threshold: 0  # Must be zero

  critical:
    description: "주요 기능에 영향을 미치는 결함"
    criteria:
      - "Major feature not working"
      - "Significant performance issue"
      - "API contract violation"
      - "Missing required endpoint"
    threshold: "< 5 for APPROVED, < 15 for CONDITIONAL"

  major:
    description: "기능에 영향을 미치지만 우회 가능"
    criteria:
      - "Minor feature issue"
      - "Non-critical performance warning"
      - "Documentation gap"
    threshold: "No limit (tracked)"

  minor:
    description: "품질 개선 권장 사항"
    criteria:
      - "Code style issues"
      - "Missing optimization"
      - "Enhancement suggestions"
    threshold: "No limit (tracked)"
```

### 3.4 Score Calculation

```yaml
score_calculation:
  components:
    structural:
      weight: 0.20
      source: "structural-report.yaml -> gate_score"

    functional:
      weight: 0.35
      source: "validation-summary.yaml -> average_score"

    contract:
      weight: 0.25
      source: "contract-validation.yaml -> gate_score"

    build_test:
      weight: 0.20
      sources:
        - "Test pass rate"
        - "Code coverage"
        - "Build success"

  formula: |
    overall_score = (
        structural_score * 0.20 +
        functional_score * 0.35 +
        contract_score * 0.25 +
        build_test_score * 0.20
    )

  thresholds:
    approved: ">= 85"
    conditional: ">= 70"
    rejected: "< 70"
```

### 3.5 Process Steps

#### Step 1: Aggregate Phase Results

**Description:** 모든 S5 Phase 결과 수집 및 종합

**Sub-steps:**
1. S5-01 structural-report.yaml 로드
2. S5-02 validation-summary.yaml 로드
3. S5-03 contract-validation.yaml 로드
4. S5-04 performance-analysis.yaml 로드
5. Build reports 로드

**Aggregation:**
```yaml
aggregation:
  - phase: "S5-01"
    file: "structural-report.yaml"
    extract:
      - gate_score
      - total_violations
      - result

  - phase: "S5-02"
    file: "validation-summary.yaml"
    extract:
      - average_score
      - pass_rate
      - failed_features

  - phase: "S5-03"
    file: "contract-validation.yaml"
    extract:
      - gate_score
      - match_rate
      - compatibility_issues

  - phase: "S5-04"
    file: "performance-analysis.yaml"
    extract:
      - n_plus_1_count
      - risk_level
      - technical_debt_items
```

**Validation:** 모든 Phase 결과 로드 완료

---

#### Step 2: Classify Issues

**Description:** 모든 이슈를 심각도별로 분류

**Sub-steps:**
1. 각 Phase에서 이슈 추출
2. 심각도 기준에 따라 분류
3. Blocker/Critical/Major/Minor 집계
4. 중복 제거

**Classification Rules:**
```yaml
classification_rules:
  blocker:
    from_structural: "errors > 0"
    from_functional: "score < 50"
    from_contract: "critical compatibility issue"
    from_build: "build failure"

  critical:
    from_structural: "critical violations"
    from_functional: "failed features with score < 70"
    from_contract: "contract mismatch > 5%"
    from_performance: "high severity N+1 > 5"

  major:
    from_structural: "warnings > 10"
    from_functional: "conditional features"
    from_contract: "minor compatibility issues"
    from_performance: "medium severity issues"
```

**Validation:** Issue 분류 완료

---

#### Step 3: Calculate Overall Score

**Description:** 가중 평균으로 전체 품질 점수 계산

**Sub-steps:**
1. 각 컴포넌트 점수 추출
2. 가중치 적용
3. 전체 점수 계산
4. 임계값과 비교

**Score Calculation Example:**
```yaml
score_calculation:
  structural_score: 85  # from S5-01
  functional_score: 88  # from S5-02
  contract_score: 95    # from S5-03
  build_test_score: 90  # from build reports

  weighted_calculation:
    structural: 85 * 0.20 = 17.0
    functional: 88 * 0.35 = 30.8
    contract: 95 * 0.25 = 23.75
    build_test: 90 * 0.20 = 18.0

  overall_score: 89.55
```

**Validation:** 점수 계산 완료

---

#### Step 4: Apply Decision Matrix

**Description:** 조건에 따라 판정 결과 도출

**Sub-steps:**
1. Blocker 수 확인
2. Critical 수 확인
3. Overall score 확인
4. Decision matrix 적용

**Decision Logic:**
```python
def determine_decision(blocker, critical, score):
    if blocker > 0:
        return "REJECTED"
    elif critical >= 15:
        return "REJECTED"
    elif score < 70:
        return "REJECTED"
    elif critical >= 5 or score < 85:
        return "CONDITIONAL"
    else:
        return "APPROVED"
```

**Validation:** 판정 결과 도출

---

#### Step 5: Prepare Human Approval Request

**Description:** Human Approval을 위한 리포트 준비

**Sub-steps:**
1. Executive Summary 작성
2. Issue 목록 정리
3. 권장 조치 작성
4. Approval 양식 준비

**Approval Request Contents:**
```yaml
approval_request:
  sections:
    - executive_summary
    - wave_scope
    - quality_scores
    - issue_summary
    - risk_assessment
    - recommendation
    - approval_form

  required_approvers:
    - role: "Tech Lead"
      responsibility: "Technical quality"
    - role: "Architect"
      responsibility: "Architecture compliance"
```

**Validation:** Approval 요청 준비 완료

---

#### Step 6: Request Human Approval

**Description:** Human Approval 요청 및 대기

**CRITICAL: This step requires human interaction**

**Sub-steps:**
1. Approval 요청 발송
2. Approver 응답 대기
3. 승인/거부 기록
4. 조건부 승인 시 조건 기록

**Approval Options:**
```yaml
approval_options:
  approve:
    action: "Proceed to deployment"
    output: "quality-gate-approved.yaml"

  conditional:
    action: "Proceed with remediation plan"
    requires: "Remediation deadline"
    output: "quality-gate-conditional.yaml"

  reject:
    action: "Return to Stage 4"
    requires: "Rejection reason"
    output: "quality-gate-rejected.yaml"
```

**Validation:** Human Approval 완료

---

#### Step 7: Generate Final Report

**Description:** 최종 품질 게이트 리포트 생성

**Sub-steps:**
1. 모든 결과 종합
2. 최종 리포트 작성
3. Git commit 및 tag
4. 알림 발송

**Final Actions:**
```yaml
final_actions:
  approved:
    - commit_message: "release: Wave {N} complete - Quality gate APPROVED"
    - tag: "wave-{N}-release"
    - artifacts: ["Release notes", "Quality report"]

  conditional:
    - commit_message: "release: Wave {N} - Quality gate CONDITIONAL"
    - remediation_deadline: "7 days"
    - follow_up_required: true

  rejected:
    - commit_message: "quality: Wave {N} - Quality gate REJECTED"
    - rollback_to: "Stage 4"
    - root_cause_analysis: true
```

**Validation:** 최종 리포트 생성 완료

---

### 3.6 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | All phases complete | Aggregate | Wait/Error |
| DP-2 | Blocker = 0 | Continue | REJECT |
| DP-3 | Score >= 85 & Critical < 5 | APPROVE proposal | CONDITIONAL proposal |
| DP-4 | Human approves | Record approval | Record rejection |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage5-outputs/phase5/"

  artifacts:
    - name: "quality-gate-report.yaml"
      required: true
    - name: "issue-list.yaml"
      required: true
    - name: "remediation-plan.yaml"
      required: false  # Only if CONDITIONAL
    - name: "approval-record.yaml"
      required: true
```

### 4.2 Output Files Summary

```
work/specs/stage5-outputs/phase5/
├── quality-gate-report.yaml    # 전체 품질 게이트 리포트
├── issue-list.yaml             # 분류된 이슈 목록
├── remediation-plan.yaml       # 수정 계획 (CONDITIONAL 시)
└── approval-record.yaml        # Human Approval 기록
```

### 4.3 Quality Gate Report Schema

```yaml
# quality-gate-report.yaml
metadata:
  generated_by: "s5-05-assurance-quality-gate"
  generated_at: "${TIMESTAMP}"
  wave: "${WAVE_NUMBER}"
  domains: ["PA", "MM", "SC"]

executive_summary:
  decision: "APPROVED"  # APPROVED | CONDITIONAL | REJECTED
  overall_score: 89.5
  blocker_issues: 0
  critical_issues: 3
  recommendation: "Proceed to production deployment"

wave_scope:
  domains: 3
  features: 350
  endpoints: 580
  services: 120
  tests: 1200

phase_results:
  s5_01_structural:
    status: "PASS"
    score: 85
    errors: 0
    warnings: 15

  s5_02_functional:
    status: "PASS"
    score: 88
    pass_rate: 92%
    failed_features: 28

  s5_03_contract:
    status: "PASS"
    score: 95
    match_rate: 96%
    compatibility: 99%

  s5_04_performance:
    status: "WARNING"
    risk_level: "MEDIUM"
    n_plus_1_count: 8
    technical_debt: 12

  build_test:
    build_status: "SUCCESS"
    test_pass_rate: 91%
    code_coverage: 82%

score_breakdown:
  components:
    structural:
      raw_score: 85
      weight: 0.20
      weighted: 17.0
    functional:
      raw_score: 88
      weight: 0.35
      weighted: 30.8
    contract:
      raw_score: 95
      weight: 0.25
      weighted: 23.75
    build_test:
      raw_score: 90
      weight: 0.20
      weighted: 18.0
  total: 89.55

issue_summary:
  total: 48
  by_severity:
    blocker: 0
    critical: 3
    major: 15
    minor: 30
  by_phase:
    s5_01: 15
    s5_02: 20
    s5_03: 5
    s5_04: 8

decision_rationale:
  blocker_check: "PASS (0 blockers)"
  critical_check: "PASS (3 < 5)"
  score_check: "PASS (89.5 >= 85)"
  final_decision: "APPROVED"

approval:
  status: "APPROVED"
  approvers:
    - name: "Tech Lead"
      approved_at: "2026-01-07T16:30:00Z"
      comment: "Technical quality meets standards"
    - name: "Architect"
      approved_at: "2026-01-07T16:45:00Z"
      comment: "Architecture compliance verified"

next_steps:
  - "Proceed to staging deployment"
  - "Execute E2E tests"
  - "Production deployment"

artifacts:
  release_notes: "RELEASE-NOTES-Wave{N}.md"
  quality_report: "quality-gate-report.yaml"
  known_issues: "issue-list.yaml"
```

### 4.4 Issue List Schema

```yaml
# issue-list.yaml
metadata:
  generated_by: "s5-05-assurance-quality-gate"
  generated_at: "${TIMESTAMP}"

summary:
  total: 48
  blocker: 0
  critical: 3
  major: 15
  minor: 30

issues:
  critical:
    - id: "ISS-001"
      phase: "S5-02"
      domain: "PA"
      feature: "FEAT-PA-123"
      title: "Missing delete functionality"
      description: "Delete endpoint not implemented"
      impact: "User cannot delete records"
      resolution: "Implement delete endpoint"
      assigned_to: "TBD"
      status: "OPEN"

    - id: "ISS-002"
      phase: "S5-03"
      domain: "MM"
      title: "API contract mismatch"
      description: "Response schema differs from spec"
      impact: "Client integration may fail"
      resolution: "Update response DTO"
      status: "OPEN"

  major:
    - id: "ISS-003"
      phase: "S5-01"
      domain: "PA"
      title: "Naming convention violation"
      description: "5 services with incorrect naming"
      impact: "Code consistency"
      resolution: "Rename services"
      status: "OPEN"

  minor:
    - id: "ISS-004"
      phase: "S5-04"
      domain: "SC"
      title: "N+1 query pattern"
      description: "Loop-based query in SC02001Service"
      impact: "Performance under load"
      resolution: "Optimize query"
      status: "DEFERRED"
```

### 4.5 Approval Record Schema

```yaml
# approval-record.yaml
metadata:
  wave: "${WAVE_NUMBER}"
  gate_id: "G5.5"

request:
  submitted_at: "2026-01-07T15:00:00Z"
  submitted_by: "AI Migration Agent"
  decision_proposed: "APPROVED"
  score: 89.5

approvals:
  - approver:
      role: "Tech Lead"
      name: "John Doe"
    decision: "APPROVED"
    timestamp: "2026-01-07T16:30:00Z"
    comments: |
      - Technical quality meets our standards
      - Minor issues can be addressed post-deployment
      - Recommend proceeding

  - approver:
      role: "Architect"
      name: "Jane Smith"
    decision: "APPROVED"
    timestamp: "2026-01-07T16:45:00Z"
    comments: |
      - Architecture patterns are correctly applied
      - Performance issues are documented as tech debt
      - Approved for production

final_decision:
  status: "APPROVED"
  effective_at: "2026-01-07T16:45:00Z"
  conditions: []

signatures:
  - role: "Tech Lead"
    signature: "APPROVED"
  - role: "Architect"
    signature: "APPROVED"
```

---

## 5. Quality Checks

### 5.1 Gate Criteria

```yaml
gate_criteria:
  id: "G5.5"
  name: "Final Quality Gate"
  threshold: 85
  human_approval_required: true

  mandatory_checks:
    - check: "blocker_zero"
      rule: "blocker_issues == 0"
      blocking: true

    - check: "critical_limited"
      rule: "critical_issues < 5"
      blocking: true

    - check: "quality_score"
      rule: "overall_score >= 85"
      blocking: true

    - check: "test_coverage"
      rule: "line_coverage >= 80%"
      blocking: true

    - check: "human_approval"
      rule: "Tech lead AND architect sign-off"
      type: "human_approval"
      approvers: ["tech_lead", "architect"]
      blocking: true
```

### 5.2 Decision Outcomes

```yaml
decision_outcomes:
  approved:
    conditions:
      - "blocker: 0"
      - "critical: < 5"
      - "score: >= 85"
      - "human_approval: granted"
    actions:
      - "Create release tag"
      - "Generate release notes"
      - "Notify stakeholders"
      - "Proceed to deployment"

  conditional:
    conditions:
      - "blocker: 0"
      - "critical: 5-14"
      - "score: 70-84"
      - "human_approval: conditional"
    actions:
      - "Create remediation plan"
      - "Set deadline (1 week)"
      - "Proceed with monitoring"
      - "Schedule follow-up review"

  rejected:
    conditions:
      - "blocker: >= 1"
      - "OR critical: >= 15"
      - "OR score: < 70"
      - "OR human_approval: denied"
    actions:
      - "Document rejection reason"
      - "Return to Stage 4"
      - "Root cause analysis"
      - "Re-plan wave"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Missing phase result | File not found | Phase incomplete | Complete phase | No |
| Score calculation error | Invalid score | Null values | Default handling | Yes |
| Approval timeout | No response | Approver unavailable | Escalate | No |

### 6.2 Escalation

| Condition | Action | Notify |
|-----------|--------|--------|
| Blocker found | Immediate escalation | All stakeholders |
| Approval timeout (24h) | Escalate to management | Manager |
| Rejection | Root cause analysis | Tech Lead + Architect |

### 6.3 Rollback Procedures

```yaml
rollback_procedures:
  on_rejection:
    steps:
      - "Document rejection reason"
      - "Identify affected components"
      - "Create rollback plan"
      - "Execute rollback to Stage 4"
      - "Schedule re-work"

  rollback_levels:
    - level: "Phase"
      trigger: "Single phase failure"
      impact: "Hours"
    - level: "Stage"
      trigger: "Quality gate rejection"
      impact: "1-2 days"
    - level: "Wave"
      trigger: "Architecture flaw"
      impact: "1-2 weeks"
```

---

## 7. Examples

### 7.1 APPROVED Example

```yaml
# Scenario: All criteria met
input:
  structural_score: 90
  functional_score: 92
  contract_score: 98
  build_test_score: 88
  blocker: 0
  critical: 2

calculation:
  overall_score: 92.3

decision:
  status: "APPROVED"
  rationale: "All criteria exceeded"

output:
  commit: "release: Wave 3 complete - Quality gate APPROVED"
  tag: "wave-3-release"
```

### 7.2 CONDITIONAL Example

```yaml
# Scenario: Minor issues, acceptable risk
input:
  structural_score: 78
  functional_score: 85
  contract_score: 90
  build_test_score: 82
  blocker: 0
  critical: 8

calculation:
  overall_score: 83.5

decision:
  status: "CONDITIONAL"
  rationale: "Score below threshold, critical issues present"
  conditions:
    - "Fix 8 critical issues within 1 week"
    - "Achieve score >= 85 in follow-up"

output:
  commit: "release: Wave 3 - Quality gate CONDITIONAL"
  remediation_deadline: "2026-01-14"
```

### 7.3 REJECTED Example

```yaml
# Scenario: Blocker found
input:
  structural_score: 85
  functional_score: 65  # Below threshold
  contract_score: 80
  build_test_score: 70
  blocker: 1  # Build failure
  critical: 12

calculation:
  overall_score: 72.25

decision:
  status: "REJECTED"
  rationale: "Blocker present, score below minimum"
  rejection_reasons:
    - "Build failure (blocker)"
    - "Functional validation score too low"

output:
  commit: "quality: Wave 3 - Quality gate REJECTED"
  action: "Return to Stage 4"
  root_cause_required: true
```

---

## 8. Approval Automation

### 8.1 Approval Hierarchy

```yaml
approval_hierarchy:
  level_1_primary:
    name: "Primary Approvers"
    required: true
    approvers:
      - role: "Tech Lead"
        responsibility: "Technical quality"
        mandatory: true
      - role: "Architect"
        responsibility: "Architecture compliance"
        mandatory: true
    quorum: "ALL"

  level_2_delegate:
    name: "Delegate Approvers"
    trigger: "Primary unavailable for > 4 hours"
    approvers:
      - role: "Senior Developer"
        conditions: ["Experience >= 5 years", "Domain expertise"]
      - role: "Tech Lead (Other Team)"
    quorum: "ANY_2"

  level_3_escalation:
    name: "Escalation Approvers"
    trigger: "Delegate unavailable for > 8 hours"
    approvers:
      - role: "Engineering Manager"
      - role: "CTO"
    quorum: "ANY_1"
    notification: "Mandatory"
```

### 8.2 Auto-Approval Conditions

```yaml
auto_approval:
  enabled: true

  conditions:
    score_threshold:
      overall_score: ">= 95"
      structural_score: ">= 95"
      functional_score: ">= 95"
      contract_score: ">= 98"

    issue_threshold:
      blocker: 0
      critical: 0
      major: "<= 5"

    test_threshold:
      pass_rate: ">= 98%"
      coverage: ">= 85%"

    history_condition:
      consecutive_passes: ">= 3"
      no_production_incidents: true

    scope_condition:
      feature_count: "<= 50"
      is_hotfix: false

  notification:
    on_auto_approve:
      - channel: "slack"
        message: "Wave {N} auto-approved (score: {score})"
        mention: ["@tech-lead", "@architect"]
      - channel: "email"
        recipients: ["tech-lead", "architect"]

  audit:
    log_reason: true
    require_post_review: true  # Within 24h

  override:
    allow_manual_block: true
    block_keywords: ["security", "data-migration", "breaking-change"]
```

### 8.3 Workflow Automation

```yaml
approval_workflow:
  stages:
    stage_1_preparation:
      name: "Prepare Approval Request"
      automated: true
      actions:
        - aggregate_results
        - calculate_score
        - classify_issues
        - generate_report

    stage_2_auto_check:
      name: "Auto-Approval Check"
      automated: true
      outcomes:
        - condition: "all_conditions_met AND no_block_keywords"
          action: "proceed_to_auto_approve"
        - condition: "else"
          action: "proceed_to_manual_approval"

    stage_3_request:
      name: "Request Approval"
      actions:
        manual:
          - notify_approvers (slack, email, teams)
          - create_approval_task (jira)
          - set_sla_timer:
              primary_sla: "4 hours"
              delegate_sla: "8 hours"
              escalation_sla: "12 hours"
        auto:
          - log_auto_approval
          - schedule_post_review: "24 hours"

    stage_4_collect:
      name: "Collect Decisions"
      actions:
        - monitor_responses (check every 15 min)
        - track_sla:
            at_50%: "reminder"
            at_75%: "escalation_warning"
            at_100%: "trigger_delegate"

    stage_5_finalize:
      name: "Finalize Decision"
      actions:
        - record_decision
        - update_status (jira, confluence)
        - trigger_next_phase
```

### 8.4 Notification Templates

```yaml
notification_templates:
  approval_request:
    slack:
      blocks:
        - type: "header"
          text: "Quality Gate Approval Required"
        - type: "section"
          fields:
            - "Wave: {wave_number}"
            - "Score: {overall_score}%"
            - "Domains: {domains}"
        - type: "section"
          text: |
            *Issue Summary*
            Blocker: {blocker_count}
            Critical: {critical_count}
        - type: "actions"
          elements:
            - type: "button"
              text: "View Report"
              url: "{report_url}"
            - type: "button"
              text: "Approve"
              style: "primary"
            - type: "button"
              text: "Reject"
              style: "danger"

    email:
      subject: "Quality Gate Approval: Wave {wave_number}"
      body: |
        A Quality Gate approval is required for Wave {wave_number}.

        **Summary**
        - Overall Score: {overall_score}%
        - Blocker: {blocker_count}
        - Critical: {critical_count}

        This request will escalate if not addressed within {sla_hours} hours.

  sla_reminder:
    slack:
      text: |
        Approval Reminder: Wave {wave_number} pending.
        Time remaining: {time_remaining}

  escalation_notice:
    slack:
      text: |
        Approval Escalation: Wave {wave_number} SLA exceeded.
        Escalating to delegate approvers.
```

### 8.5 Approval Dashboard

```yaml
approval_dashboard:
  components:
    pending_approvals:
      title: "Pending Approvals"
      columns: ["Wave", "Score", "Requested", "SLA Status", "Actions"]
      filters: ["My Approvals", "All Pending", "Overdue"]

    approval_history:
      title: "Approval History"
      columns: ["Wave", "Decision", "Score", "Approvers", "Duration"]
      filters: ["Last 7 days", "Last 30 days", "By Domain"]

    sla_metrics:
      title: "SLA Performance"
      charts:
        - type: "gauge"
          metric: "Current SLA compliance %"
        - type: "line"
          metric: "Avg approval time (days)"

    auto_approval_stats:
      title: "Auto-Approval Statistics"
      metrics:
        - "Auto-approved this month"
        - "Manual approvals"
        - "Auto-approval rate %"
```

### 8.6 External Integrations

```yaml
external_integrations:
  jira:
    enabled: true
    config:
      project_key: "MIGR"
      issue_type: "Approval"
      workflow:
        created: "Pending Approval"
        approved: "Approved"
        rejected: "Rejected"

  confluence:
    enabled: true
    config:
      space_key: "MIGRATION"
      template: "Quality Gate Report"
      auto_publish: true

  slack:
    enabled: true
    config:
      channel: "#migration-approvals"
      bot_name: "QualityGateBot"

  pagerduty:
    enabled: true
    config:
      service_id: "MIGRATION_GATE"
      trigger_on: ["SLA breach", "Blocker found"]
```

---

## Version History

### v1.1.0 (2026-01-07)
- **Approval Automation 추가** (Section 8)
  - Approval hierarchy (Primary → Delegate → Escalation)
  - Auto-approval conditions (Score >= 95, Critical = 0)
  - Workflow automation (5-stage process)
  - Notification templates (Slack, Email)
  - Approval dashboard design
  - External integrations (Jira, Confluence, Slack, PagerDuty)

### v1.0.0 (2026-01-07)
- Initial version
- Decision matrix (APPROVED/CONDITIONAL/REJECTED)
- Human approval workflow
- Score aggregation from all phases
- Issue classification system
- Rollback procedures
