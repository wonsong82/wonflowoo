# Orchestration Patterns

**Version**: 1.0.0
**Last Updated**: 2026-01-07
**Purpose**: AI-Driven Migration의 작업 흐름 제어 및 조율 패턴

---

## 1. Overview

Orchestration Patterns은 Migration 프로젝트의 작업 흐름을 제어하고 조율하는 패턴을 정의합니다. 이 패턴들은 Cross-cutting 관심사로, 모든 Stage에 걸쳐 적용됩니다.

### 1.1 Orchestration Skill Categories

| Category | Skills | Purpose |
|----------|--------|---------|
| **Gate Control** | phase-gate, stage-gate | 진행 조건 검증 |
| **Task Management** | task-dispatch | 작업 배분 및 병렬 실행 |
| **Monitoring** | progress-tracker | 진행 상황 추적 |
| **Recovery** | rollback | 실패 시 복구 |

### 1.2 Orchestration Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATION FLOW                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────┐                                                  │
│   │ Task Queue   │◀────────────────────────────────┐               │
│   └──────┬───────┘                                 │               │
│          │                                         │               │
│          ▼                                         │               │
│   ┌──────────────┐     ┌──────────────┐           │               │
│   │task-dispatch │────▶│ AI Sessions  │           │               │
│   └──────┬───────┘     │ (Parallel)   │           │               │
│          │             └──────┬───────┘           │               │
│          │                    │                   │               │
│          ▼                    ▼                   │               │
│   ┌──────────────┐     ┌──────────────┐          │               │
│   │progress-     │◀────│ Task Results │          │               │
│   │tracker       │     └──────┬───────┘          │               │
│   └──────┬───────┘            │                  │               │
│          │                    ▼                  │               │
│          │             ┌──────────────┐          │               │
│          └────────────▶│ phase-gate   │          │               │
│                        └──────┬───────┘          │               │
│                               │                  │               │
│              ┌────────────────┼────────────────┐ │               │
│              │                │                │ │               │
│              ▼                ▼                ▼ │               │
│         ┌────────┐      ┌────────┐      ┌────────┐               │
│         │  PASS  │      │ COND.  │      │  FAIL  │               │
│         └────┬───┘      └────┬───┘      └────┬───┘               │
│              │               │               │                   │
│              ▼               ▼               ▼                   │
│         stage-gate      Remediation      rollback ───────────────┘
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Phase Gate Pattern

### 2.1 Intent

Phase 완료 조건을 검증하고, 다음 Phase로의 진행 여부를 판정합니다.

### 2.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE GATE PATTERN                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Gate Criteria Collection             │      │
│  │  - Automated checks results                      │      │
│  │  - Coverage metrics                              │      │
│  │  - Quality scores                                │      │
│  │  - Blocker/Critical counts                       │      │
│  └──────────────────────┬───────────────────────────┘      │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Threshold Evaluation                 │      │
│  │  if (all_criteria_met):                          │      │
│  │      return PASS                                 │      │
│  │  elif (conditional_criteria_met):                │      │
│  │      return CONDITIONAL_PASS                     │      │
│  │  else:                                           │      │
│  │      return FAIL                                 │      │
│  └──────────────────────┬───────────────────────────┘      │
│                         │                                   │
│         ┌───────────────┼───────────────┐                  │
│         │               │               │                  │
│         ▼               ▼               ▼                  │
│     ┌───────┐     ┌───────────┐    ┌───────┐              │
│     │ PASS  │     │CONDITIONAL│    │ FAIL  │              │
│     │       │     │   PASS    │    │       │              │
│     └───┬───┘     └─────┬─────┘    └───┬───┘              │
│         │               │              │                   │
│         ▼               ▼              ▼                   │
│     Next Phase    Next Phase +    Re-execute              │
│                   Remediation     Phase                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Implementation

```yaml
phase_gate_pattern:
  skill_definition:
    name: "phase-gate"
    type: "orchestration"
    parallel: false
    triggers:
      - "All tasks in phase completed"
      - "Manual trigger"

  gate_criteria:
    mandatory:
      - criterion: "all_tasks_completed"
        check: "task_status != PENDING AND task_status != IN_PROGRESS"
        blocking: true

      - criterion: "no_failed_tasks"
        check: "count(task_status == FAILED) == 0"
        blocking: true

    threshold_based:
      - criterion: "coverage_threshold"
        metric: "coverage_percentage"
        threshold: 90
        weight: 0.3

      - criterion: "quality_threshold"
        metric: "quality_score"
        threshold: 70
        weight: 0.4

      - criterion: "blocker_count"
        metric: "blocker_issues"
        threshold: 0
        weight: 0.3

  decision_logic:
    pass:
      conditions:
        - "all mandatory criteria met"
        - "weighted_score >= threshold"
      action: "auto_advance"

    conditional_pass:
      conditions:
        - "all mandatory criteria met"
        - "weighted_score >= (threshold - 20)"
        - "weighted_score < threshold"
      action: "advance_with_remediation"
      remediation_required: true

    fail:
      conditions:
        - "any mandatory criteria not met"
        - "OR weighted_score < (threshold - 20)"
      action: "re_execute_phase"

  outputs:
    - "gate-result.yaml"
    - "gate-report.md"

  example_output:
    gate_id: "G-S1-P3"
    phase: "Stage 1 Phase 3"
    result: "PASS"
    score: 92.5
    criteria_results:
      - criterion: "all_tasks_completed"
        result: true
      - criterion: "coverage_threshold"
        value: 95.2
        threshold: 90
        result: true
    timestamp: "2026-01-07T15:30:00Z"
```

---

## 3. Stage Gate Pattern

### 3.1 Intent

Stage 완료 조건을 검증하고, 다음 Stage로의 전환 여부를 판정합니다. Phase Gate보다 상위 레벨의 검증입니다.

### 3.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    STAGE GATE PATTERN                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Phase Gate Results                      │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐           │   │
│  │  │P1.1 │ │P1.2 │ │P1.3 │ │P1.4 │ │ ... │           │   │
│  │  │PASS │ │PASS │ │PASS │ │PASS │ │     │           │   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘           │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Stage Criteria Aggregation              │   │
│  │  - All phase gates passed                           │   │
│  │  - Stage-level metrics                              │   │
│  │  - Cross-phase dependencies resolved                │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Human Approval Check                    │   │
│  │  (Required for S3→S4, S5 completion)                │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                 │
│           ┌───────────────┼───────────────┐                │
│           │               │               │                │
│           ▼               ▼               ▼                │
│       ┌───────┐     ┌───────────┐    ┌───────┐            │
│       │ PASS  │     │  PENDING  │    │ FAIL  │            │
│       │       │     │ APPROVAL  │    │       │            │
│       └───┬───┘     └─────┬─────┘    └───┬───┘            │
│           │               │              │                 │
│           ▼               ▼              ▼                 │
│       Next Stage    Wait for       Rollback to            │
│                     Human OK       Previous Phase          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Implementation

```yaml
stage_gate_pattern:
  skill_definition:
    name: "stage-gate"
    type: "orchestration"
    parallel: false
    triggers:
      - "All phases in stage completed"
      - "All phase gates passed"

  prerequisites:
    - "All phase gates in current stage: PASS or CONDITIONAL_PASS"

  stage_criteria:
    - stage: "S1 → S2"
      name: "Discovery Complete"
      auto_advance: true
      criteria:
        - "100% features inventoried"
        - "All phase gates passed"
        - "Spec generation complete"

    - stage: "S2 → S3"
      name: "Validation Complete"
      auto_advance: true
      criteria:
        - "Coverage >= 99%"
        - "Critical gaps = 0"
        - "All specs validated"

    - stage: "S3 → S4"
      name: "Preparation Complete"
      auto_advance: false
      human_approval_required: true
      approvers:
        - "tech_lead"
        - "architect"
      criteria:
        - "Architecture approved"
        - "Generation spec ready"
        - "Dependencies resolved"

    - stage: "S4 → S5"
      name: "Generation Complete"
      auto_advance: true
      criteria:
        - "Build successful"
        - "Test coverage >= 80%"
        - "No compilation errors"

    - stage: "S5 → Deploy"
      name: "Assurance Complete"
      auto_advance: false
      human_approval_required: true
      approvers:
        - "tech_lead"
        - "architect"
      criteria:
        - "Quality gate passed"
        - "Blocker = 0"
        - "Critical < 5"

  outputs:
    - "stage-gate-result.yaml"
    - "approval-record.yaml" (if human approval required)
```

---

## 4. Task Dispatch Pattern

### 4.1 Intent

작업을 생성하고, 가용 세션에 배정하며, 병렬 실행을 관리합니다.

### 4.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│                  TASK DISPATCH PATTERN                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Task Generation                      │      │
│  │  - From feature list                             │      │
│  │  - With priority ordering                        │      │
│  │  - With batch grouping                           │      │
│  └──────────────────────┬───────────────────────────┘      │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Task Queue                           │      │
│  │  ┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐            │      │
│  │  │ T1  ││ T2  ││ T3  ││ T4  ││ ... │ (PENDING)  │      │
│  │  └─────┘└─────┘└─────┘└─────┘└─────┘            │      │
│  └──────────────────────┬───────────────────────────┘      │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Session Pool                         │      │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐            │      │
│  │  │Session 1│ │Session 2│ │Session N│ (max 10)   │      │
│  │  │ IDLE    │ │ BUSY    │ │ IDLE    │            │      │
│  │  └────┬────┘ └─────────┘ └────┬────┘            │      │
│  │       │                       │                  │      │
│  └───────┼───────────────────────┼──────────────────┘      │
│          │                       │                          │
│          ▼                       ▼                          │
│     ┌─────────┐            ┌─────────┐                     │
│     │ Assign  │            │ Assign  │                     │
│     │ T1→S1   │            │ T3→SN   │                     │
│     └─────────┘            └─────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Implementation

```yaml
task_dispatch_pattern:
  skill_definition:
    name: "task-dispatch"
    type: "orchestration"
    parallel: false  # Dispatcher itself is sequential

  configuration:
    session_pool:
      max_sessions: 10
      session_timeout_minutes: 60
      idle_timeout_minutes: 5

    batching:
      default_batch_size: 50
      priority_order: ["P0", "P1", "P2", "P3"]

    assignment_strategy: "round_robin"  # or "least_loaded"

  task_lifecycle:
    states:
      - name: "PENDING"
        description: "대기 중"
        transitions: ["ASSIGNED"]

      - name: "ASSIGNED"
        description: "세션에 배정됨"
        timeout_minutes: 5
        transitions: ["IN_PROGRESS", "PENDING"]

      - name: "IN_PROGRESS"
        description: "실행 중"
        timeout_minutes: 60
        transitions: ["VALIDATING", "FAILED"]

      - name: "VALIDATING"
        description: "검증 중"
        timeout_minutes: 10
        transitions: ["COMPLETED", "REJECTED"]

      - name: "COMPLETED"
        description: "완료"
        final: true

      - name: "FAILED"
        description: "실패"
        retry_eligible: true
        transitions: ["PENDING", "ESCALATED"]

      - name: "REJECTED"
        description: "검증 실패"
        retry_eligible: true
        transitions: ["PENDING", "ESCALATED"]

      - name: "ESCALATED"
        description: "에스컬레이션"
        final: true
        requires_human: true

  task_naming:
    patterns:
      feature_task: "FEAT-{DOMAIN}-{NNN}"
      batch_task: "BATCH-S{N}-P{P}-{DOMAIN}-{NNNN}"
      generation_task: "GEN-{FEAT_ID}"
      test_task: "TEST-{FEAT_ID}"

  dispatch_algorithm:
    steps:
      - step: 1
        name: "Get pending tasks"
        query: "status == PENDING ORDER BY priority, created_at"

      - step: 2
        name: "Get available sessions"
        query: "status == IDLE ORDER BY last_used"

      - step: 3
        name: "Batch tasks by unit"
        logic: "GROUP BY batch_unit LIMIT batch_size"

      - step: 4
        name: "Assign to sessions"
        logic: "WHILE available_sessions AND pending_batches"

  outputs:
    - "dispatch-log.yaml"
    - "session-status.yaml"
    - "task-progress.yaml"
```

---

## 5. Progress Tracker Pattern

### 5.1 Intent

전체 프로젝트 및 각 Stage/Phase의 진행 상황을 실시간으로 추적하고 리포팅합니다.

### 5.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│                PROGRESS TRACKER PATTERN                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Event Collection                     │      │
│  │  - Task state changes                            │      │
│  │  - Gate results                                  │      │
│  │  - Error occurrences                             │      │
│  └──────────────────────┬───────────────────────────┘      │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Metrics Aggregation                  │      │
│  │  - Completion rates                              │      │
│  │  - Pass/Fail ratios                              │      │
│  │  - Time metrics                                  │      │
│  └──────────────────────┬───────────────────────────┘      │
│                         │                                   │
│         ┌───────────────┼───────────────┐                  │
│         │               │               │                  │
│         ▼               ▼               ▼                  │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐              │
│   │ Dashboard│   │  Report  │   │  Alert   │              │
│   │  Update  │   │ Generate │   │  Trigger │              │
│   └──────────┘   └──────────┘   └──────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Implementation

```yaml
progress_tracker_pattern:
  skill_definition:
    name: "progress-tracker"
    type: "orchestration"
    parallel: false
    update_frequency: "per_task_completion"

  tracked_metrics:
    project_level:
      - metric: "overall_progress"
        formula: "completed_tasks / total_tasks * 100"
        display: "percentage"

      - metric: "estimated_completion"
        formula: "average_task_duration * remaining_tasks"
        display: "datetime"

    stage_level:
      - metric: "stage_progress"
        formula: "completed_phases / total_phases * 100"

      - metric: "stage_quality_score"
        formula: "average(phase_quality_scores)"

    phase_level:
      - metric: "phase_progress"
        formula: "completed_tasks / total_tasks * 100"

      - metric: "phase_pass_rate"
        formula: "passed_tasks / validated_tasks * 100"

    task_level:
      - metric: "task_duration"
        formula: "completed_at - started_at"

      - metric: "retry_count"
        formula: "count(task_attempts)"

  alerts:
    - alert: "high_failure_rate"
      condition: "failure_rate > 20%"
      severity: "warning"
      action: "notify_team"

    - alert: "stuck_task"
      condition: "task_duration > 2 * average_duration"
      severity: "warning"
      action: "investigate"

    - alert: "budget_exceeded"
      condition: "accumulated_cost > daily_budget"
      severity: "critical"
      action: "pause_and_notify"

  cost_tracking:
    model_costs:
      opus: 0.015  # per 1K tokens (example)
    daily_budget: 500
    weekly_budget: 2500
    cumulative_alert: 10000

  outputs:
    - "progress-dashboard.yaml"
    - "daily-report.md"
    - "cost-report.yaml"

  dashboard_example:
    project: "hallain_tft Migration"
    updated_at: "2026-01-07T16:00:00Z"
    overall_progress: 23.5%
    stages:
      - stage: "S1: Discovery"
        status: "COMPLETED"
        progress: 100%
      - stage: "S2: Validation"
        status: "IN_PROGRESS"
        progress: 67.3%
      - stage: "S3: Preparation"
        status: "PENDING"
        progress: 0%
    current_phase:
      name: "S2-P3: Structural Comparison"
      tasks_total: 450
      tasks_completed: 302
      tasks_in_progress: 10
      tasks_failed: 3
    cost:
      today: 124.50
      this_week: 856.20
      total: 3420.80
```

---

## 6. Rollback Pattern

### 6.1 Intent

실패 상황에서 적절한 레벨로 롤백하여 안정적인 상태로 복구합니다.

### 6.2 Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    ROLLBACK PATTERN                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Failure Detection                    │      │
│  │  - Gate failure                                  │      │
│  │  - Task failure (max retries)                    │      │
│  │  - Quality threshold breach                      │      │
│  └──────────────────────┬───────────────────────────┘      │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Rollback Level Decision             │      │
│  │  Based on: failure_type, impact_scope            │      │
│  └──────────────────────┬───────────────────────────┘      │
│                         │                                   │
│         ┌───────────────┼───────────────┐                  │
│         │               │               │                  │
│         ▼               ▼               ▼                  │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐              │
│   │  Phase   │   │  Stage   │   │  Wave    │              │
│   │ Rollback │   │ Rollback │   │ Rollback │              │
│   └────┬─────┘   └────┬─────┘   └────┬─────┘              │
│        │              │              │                     │
│        ▼              ▼              ▼                     │
│   Re-execute     Return to      Human                      │
│   Phase          Stage start    intervention               │
│   (hours)        (1-2 days)     (1-2 weeks)               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Implementation

```yaml
rollback_pattern:
  skill_definition:
    name: "rollback"
    type: "orchestration"
    parallel: false
    triggers:
      - "Gate failure"
      - "Quality threshold breach"
      - "Human decision"

  rollback_levels:
    - level: "PHASE"
      trigger_conditions:
        - "Phase gate failure"
        - "High failure rate in phase"
      approval: "auto"
      time_impact: "hours"
      actions:
        - "Mark phase tasks as PENDING"
        - "Clear phase outputs"
        - "Re-execute from phase start"

    - level: "STAGE"
      trigger_conditions:
        - "Stage gate rejection"
        - "Critical quality issues"
      approval: "auto"
      time_impact: "1-2 days"
      actions:
        - "Return to stage start"
        - "Preserve completed outputs"
        - "Re-analyze failed areas"

    - level: "WAVE"
      trigger_conditions:
        - "Architecture flaw discovered"
        - "Fundamental approach issue"
      approval: "human"
      approvers:
        - "tech_lead"
        - "architect"
      time_impact: "1-2 weeks"
      actions:
        - "Pause all activities"
        - "Review and revise approach"
        - "Re-plan affected phases"

    - level: "FULL"
      trigger_conditions:
        - "Go/No-Go reversal"
        - "Project cancellation"
      approval: "stakeholder"
      time_impact: "project halt"
      actions:
        - "Stop all activities"
        - "Archive outputs"
        - "Document lessons learned"

  rollback_procedure:
    steps:
      - step: 1
        name: "Identify failure scope"
        actions:
          - "Determine affected tasks/phases"
          - "Calculate impact"

      - step: 2
        name: "Select rollback level"
        actions:
          - "Apply decision tree"
          - "Get approval if required"

      - step: 3
        name: "Execute rollback"
        actions:
          - "Revert state to checkpoint"
          - "Clear affected outputs"
          - "Update task statuses"

      - step: 4
        name: "Prepare for re-execution"
        actions:
          - "Document failure cause"
          - "Apply fixes/improvements"
          - "Reset tracking"

  checkpoint_management:
    checkpoint_creation:
      - "Phase gate pass"
      - "Stage gate pass"
      - "Batch completion"
    checkpoint_retention:
      - "Keep last 3 phase checkpoints"
      - "Keep all stage checkpoints"

  outputs:
    - "rollback-log.yaml"
    - "rollback-report.md"

  decision_tree:
    start: "failure_detected"
    nodes:
      - id: "failure_detected"
        question: "Is it a task failure?"
        yes: "check_retry_count"
        no: "check_gate_failure"

      - id: "check_retry_count"
        question: "Retry count < max?"
        yes: "retry_task"
        no: "phase_rollback"

      - id: "check_gate_failure"
        question: "Is it a gate failure?"
        yes: "check_gate_type"
        no: "check_quality_breach"

      - id: "check_gate_type"
        question: "Phase gate or Stage gate?"
        phase: "phase_rollback"
        stage: "stage_rollback"

      - id: "check_quality_breach"
        question: "Severity?"
        critical: "wave_rollback"
        major: "stage_rollback"
        minor: "phase_rollback"
```

---

## 7. Pattern Integration

### 7.1 Orchestration Flow Integration

```yaml
orchestration_integration:
  typical_flow:
    - step: 1
      skill: "task-dispatch"
      action: "Generate and assign tasks"

    - step: 2
      skill: "progress-tracker"
      action: "Monitor execution"
      parallel_with: "task execution"

    - step: 3
      skill: "phase-gate"
      action: "Validate phase completion"
      triggers_on: "all tasks completed"

    - step: 4a
      condition: "gate PASS"
      skill: "task-dispatch"
      action: "Start next phase"

    - step: 4b
      condition: "gate FAIL"
      skill: "rollback"
      action: "Execute rollback"

    - step: 5
      skill: "stage-gate"
      action: "Validate stage completion"
      triggers_on: "all phases completed"

  event_flow:
    task_completed:
      - "Update progress-tracker"
      - "Check if phase complete"

    phase_completed:
      - "Trigger phase-gate"
      - "Generate phase report"

    gate_failed:
      - "Trigger rollback"
      - "Alert team"

    stage_completed:
      - "Trigger stage-gate"
      - "Request approval if needed"
```

### 7.2 Human Approval Integration

```yaml
human_approval_points:
  - gate: "S3-P4 (Architecture Design)"
    approvers: ["tech_lead", "architect"]
    criteria:
      - "Package structure defined"
      - "All layers specified"
      - "Common components designed"
    timeout_days: 3

  - gate: "S5-P5 (Quality Gate)"
    approvers: ["tech_lead", "architect"]
    criteria:
      - "Blocker = 0"
      - "Critical < 5"
      - "Score >= 85%"
    timeout_days: 3

  approval_workflow:
    - step: "Request submitted"
    - step: "Notify approvers"
    - step: "Wait for responses"
    - step: "Aggregate decisions"
    - step: "Record approval/rejection"
```

---

## 8. Quick Reference

### 8.1 Orchestration Skills Summary

| Skill | Purpose | Trigger | Output |
|-------|---------|---------|--------|
| `phase-gate` | Phase 완료 검증 | All tasks done | gate-result.yaml |
| `stage-gate` | Stage 전환 판정 | All phases done | stage-gate-result.yaml |
| `task-dispatch` | 작업 배분/병렬화 | Continuous | task-progress.yaml |
| `progress-tracker` | 진행 추적 | Per task | dashboard, reports |
| `rollback` | 실패 복구 | Failure detected | rollback-log.yaml |

### 8.2 Gate Thresholds Quick Reference

| Gate Type | Threshold | Applies To |
|-----------|-----------|------------|
| Phase Gate | >= 70 | All phases |
| Validation Gate | >= 90 | S2-P4, S5-P2 |
| Quality Gate | >= 85 | S5-P5 |

---

**Previous**: [04-skill-patterns.md](04-skill-patterns.md)
**Next**: [templates/](templates/)
