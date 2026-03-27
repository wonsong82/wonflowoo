---
name: {skill-name-with-hyphens}
description: Use when {작업 흐름 제어가 필요한 상황 - 트리거 조건만}
---

# {Orchestration Skill Name}

> **CRITICAL - 파일 위치**: `.claude/skills/{name}/SKILL.md` 경로에 저장 필수.
> 디렉토리명 = `name` 필드 (정확히 일치). 중첩 구조 금지.

> **CRITICAL**: Frontmatter(위 `---` 블록)는 반드시 파일 맨 처음에 raw YAML로 시작해야 합니다.
> 코드 블록(` ```yaml `)으로 감싸면 Claude Code가 인식하지 못합니다.

> **Skill Type**: Orchestration (작업 흐름 제어 및 조율)

## 1. Overview

### 1.1 Purpose

{작업 흐름 제어/조율 목적을 명확하게 기술}

**제어 대상:**
- {제어 대상 1}
- {제어 대상 2}

**트리거 조건:**
- {트리거 1}
- {트리거 2}

### 1.2 Orchestration Scope

| Aspect | Scope |
|--------|-------|
| Level | {phase|stage|wave|project} |
| Automation | {auto|semi-auto|manual} |
| Human Approval | {required|optional|none} |

---

## 2. Prerequisites

### 2.1 State Requirements

```yaml
state_requirements:
  - condition: "{상태 조건 1}"
    check: "{검증 방법}"
  - condition: "{상태 조건 2}"
    check: "{검증 방법}"
```

### 2.2 Input Signals

| Signal | Source | Format |
|--------|--------|--------|
| {신호 1} | {소스} | {형식} |
| {신호 2} | {소스} | {형식} |

---

## 3. Methodology

### 3.1 Control Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Trigger  │────▶│ Evaluate │────▶│ Decision │────▶│ Execute  │
│ Received │     │ Criteria │     │  Matrix  │     │  Action  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

### 3.2 Decision Matrix

| Condition | Result | Action |
|-----------|--------|--------|
| {조건 1} | PASS | {액션 1} |
| {조건 2} | CONDITIONAL | {액션 2} |
| {조건 3} | FAIL | {액션 3} |

### 3.3 Criteria Evaluation

```yaml
criteria_evaluation:
  mandatory_criteria:
    - criterion: "{필수 조건 1}"
      check: "{검증 로직}"
      blocking: true

  threshold_criteria:
    - criterion: "{임계값 조건 1}"
      metric: "{측정 지표}"
      threshold: {값}
      weight: {0.0-1.0}
```

---

## 4. Outputs

### 4.1 Decision Record

```yaml
decision_record:
  file: "{skill-name}-result.yaml"
  schema:
    id: "{decision_id}"
    timestamp: "${TIMESTAMP}"
    trigger: "{trigger_source}"
    criteria_results:
      - criterion: "{조건}"
        value: {측정값}
        threshold: {임계값}
        result: "PASS|FAIL"
    final_decision: "PASS|CONDITIONAL|FAIL"
    action_taken: "{실행된 액션}"
```

### 4.2 Audit Trail

```yaml
audit_trail:
  file: "{skill-name}-audit.yaml"
  records:
    - timestamp: "${TIMESTAMP}"
      actor: "system|human"
      action: "{액션}"
      reason: "{사유}"
```

---

## 5. Quality Checks

### 5.1 Decision Validation

| Check | Criteria |
|-------|----------|
| Criteria completeness | All mandatory criteria evaluated |
| Threshold accuracy | Correct calculation |
| Action consistency | Matches decision |

### 5.2 Audit Requirements

- [ ] All decisions logged
- [ ] Human approvals recorded
- [ ] Action results captured

---

## 6. Error Handling

### 6.1 Decision Errors

| Error Type | Handling |
|------------|----------|
| Incomplete data | Defer decision, request data |
| Conflict | Escalate to human |
| Timeout | Use default action |

### 6.2 Rollback Triggers

| Condition | Rollback Level |
|-----------|----------------|
| {조건 1} | Phase |
| {조건 2} | Stage |
| {조건 3} | Wave |

---

## 7. Examples

### 7.1 Sample Trigger

```yaml
trigger:
  type: "phase_completion"
  source: "S1-P3"
  data:
    total_tasks: 450
    completed_tasks: 450
    failed_tasks: 0
```

### 7.2 Sample Decision

```yaml
decision_record:
  id: "G-S1-P3-001"
  timestamp: "2026-01-07T15:30:00Z"
  trigger: "phase_completion"

  criteria_results:
    - criterion: "all_tasks_completed"
      value: true
      result: "PASS"
    - criterion: "coverage_threshold"
      value: 95.2
      threshold: 90
      result: "PASS"

  final_decision: "PASS"
  action_taken: "advance_to_next_phase"
```

---

## 8. Human Approval (If Required)

### 8.1 Approval Workflow

```yaml
approval_workflow:
  required_approvers:
    - role: "{역할 1}"
      count: 1
    - role: "{역할 2}"
      count: 1

  approval_criteria:
    - "{승인 기준 1}"
    - "{승인 기준 2}"

  timeout_days: 3
  escalation_on_timeout: "{에스컬레이션 대상}"
```

### 8.2 Approval Record

```yaml
approval_record:
  request_id: "{request_id}"
  requested_at: "${TIMESTAMP}"
  approvers:
    - name: "{이름}"
      role: "{역할}"
      decision: "approved|rejected"
      timestamp: "{시간}"
      comments: "{코멘트}"
  final_result: "approved|rejected|timeout"
```
