# Phase Gate Criteria

**Version**: 1.0.0
**Last Updated**: 2025-12-15

---

## 1. Overview

각 Phase 완료 시점에서 다음 Phase로 진행하기 위한 품질 기준을 정의합니다.

### 1.1 Phase Gate Purpose

```yaml
phase_gate_purpose:
  quality_assurance:
    - "누적 품질 문제 방지"
    - "조기 문제 발견"

  progress_control:
    - "체계적 진행 관리"
    - "의존성 순서 보장"

  risk_management:
    - "단계별 위험 평가"
    - "복구 지점 확보"
```

### 1.2 Gate Decision Types

```yaml
gate_decisions:
  PASS:
    description: "모든 조건 충족, 다음 Phase 진행"
    action: "Immediate proceed"
    documentation: "Success log"

  CONDITIONAL_PASS:
    description: "주요 조건 충족, 부수적 이슈 존재"
    action: "Proceed with tracked issues"
    documentation: "Issue backlog"
    followup: "Remediation in parallel"

  FAIL:
    description: "필수 조건 미충족"
    action: "Block until resolved"
    documentation: "Failure report"
    followup: "Remediation required"
```

---

## 2. Stage 1 Phase Gates

### 2.1 Phase 1: Feature Inventory Gate

```yaml
stage1_phase1_gate:
  name: "Feature Inventory Gate"

  mandatory_conditions:
    output_files:
      required:
        - "api-endpoints-raw.txt"
        - "feature-inventory.yaml"
        - "feature-priorities.yaml"
      validation: "Files exist and non-empty"

    completeness:
      metric: "endpoint_count"
      expected: ">= 5,600"
      validation: "Count extracted endpoints"

    structure:
      metric: "feature_grouping"
      expected: ">= 900 features"
      validation: "Screen ID grouping complete"

  quality_metrics:
    coverage:
      target: ">= 95%"
      formula: "extracted_endpoints / expected_endpoints"

  decision_matrix:
    PASS: "All mandatory + coverage >= 95%"
    CONDITIONAL_PASS: "All mandatory + coverage 90-94%"
    FAIL: "Missing mandatory OR coverage < 90%"
```

### 2.2 Phase 2: Deep Analysis Gate

```yaml
stage1_phase2_gate:
  name: "Deep Analysis Gate"

  mandatory_conditions:
    per_feature_outputs:
      required:
        - "summary.yaml"
        - "api-endpoints/"
        - "business-logic/"
      validation: "Each analyzed feature has required files"

    layer_coverage:
      metric: "5_layer_trace"
      expected: ">= 95%"
      validation: "Controller → TS → ES → MyBatis → VO"

    miplatform_docs:
      metric: "protocol_documented"
      expected: "100%"
      validation: "Request/Response datasets defined"

  quality_metrics:
    analysis_depth:
      target: "All business logic captured"
      validation: "Spot check sampling"

  decision_matrix:
    PASS: "All mandatory + layer coverage >= 95%"
    CONDITIONAL_PASS: "All mandatory + layer coverage 90-94%"
    FAIL: "Missing mandatory OR layer coverage < 90%"
```

### 2.3 Phase 3: Spec Generation Gate

```yaml
stage1_phase3_gate:
  name: "Spec Generation Gate"

  mandatory_conditions:
    file_generation:
      success_rate: ">= 99%"
      validation: "Write operations succeeded"

    file_size:
      constraint: "< 300 lines per file"
      validation: "No oversized files"

    yaml_validity:
      error_rate: "< 1%"
      validation: "YAML syntax check"

  quality_metrics:
    spec_validation_score:
      target: ">= 95 points"
      source: "stage2-spec-validation"

    completeness:
      metric: "all_layers_present"
      target: "100%"

  decision_matrix:
    PASS: "success >= 99% + size OK + yaml OK + score >= 95"
    CONDITIONAL_PASS: "success >= 95% + minor issues"
    FAIL: "success < 95% OR score < 85"
```

---

## 3. Stage 2 Phase Gates

### 3.1 Phase 1: Source Inventory Gate

```yaml
stage2_phase1_gate:
  name: "Source Inventory Gate"

  mandatory_conditions:
    inventory_files:
      required:
        - "inventory/controllers.json"
        - "inventory/mybatis_statements.json"
      validation: "Files generated successfully"

    extraction_count:
      endpoints: ">= 5,600"
      mybatis: ">= 10,000"
      validation: "Count matches expected"

  quality_metrics:
    automation_rate:
      target: "100%"
      validation: "All extraction automated"

  decision_matrix:
    PASS: "All counts met + 100% automation"
    FAIL: "Missing files OR counts below threshold"
```

### 3.2 Phase 3: Structural Comparison Gate

```yaml
stage2_phase3_gate:
  name: "Structural Comparison Gate"

  mandatory_conditions:
    comparison_complete:
      validation: "All endpoints compared"

    missing_rate:
      metric: "endpoints_missing_in_specs / total_endpoints"
      threshold: "< 10%"

  quality_metrics:
    coverage:
      excellent: ">= 99%"
      acceptable: "95-98%"
      warning: "90-94%"

  decision_matrix:
    PASS: "missing_rate < 1%"
    CONDITIONAL_PASS: "missing_rate 1-5%"
    FAIL: "missing_rate >= 10%"

  special_action:
    if_fail: "Return to Stage 1 for re-analysis"
```

### 3.3 Phase 5: Spec Completion Gate

```yaml
stage2_phase5_gate:
  name: "Spec Completion Gate"

  mandatory_conditions:
    final_coverage:
      target: ">= 99.5%"
      validation: "All gaps addressed"

    merge_success:
      target: "100%"
      validation: "All new specs merged"

  quality_metrics:
    gap_resolution:
      target: "100%"
      validation: "All identified gaps resolved"

  decision_matrix:
    PASS: "coverage >= 99.5% + all gaps resolved"
    CONDITIONAL_PASS: "coverage >= 99% + minor gaps remaining"
    FAIL: "coverage < 99% OR critical gaps remaining"
```

---

## 4. Stage 4 Phase Gates

### 4.1 Phase 2: Mini-Pilot Gate

```yaml
stage4_phase2_gate:
  name: "Mini-Pilot Gate"

  mandatory_conditions:
    sample_completion:
      high_complexity: "2 features complete"
      medium_complexity: "2 features complete"
      low_complexity: "2 features complete"

    build_success:
      target: "100%"
      validation: "All 6 features compile"

    test_success:
      target: ">= 80%"
      validation: "Unit tests pass"

  quality_metrics:
    retrospective:
      required: true
      content: "Lessons learned documented"

  decision_matrix:
    PASS: "All samples complete + build OK + tests >= 80%"
    CONDITIONAL_PASS: "All samples complete + minor test failures"
    FAIL: "Incomplete samples OR build failure"

  gate_approval: "Manual review required"
```

### 4.2 Phase 3: Code Generation Gate

```yaml
stage4_phase3_gate:
  name: "Domain Execution Gate"
  scope: "Per domain"

  mandatory_conditions:
    generation_complete:
      target: "100% features in domain"
      validation: "All features generated"

    compile_success:
      target: "100%"
      validation: "Domain code compiles"

  quality_metrics:
    generation_quality:
      metric: "error_free_rate"
      target: ">= 95%"

  decision_matrix:
    PASS: "100% complete + compile OK + quality >= 95%"
    CONDITIONAL_PASS: "100% complete + minor issues"
    FAIL: "Incomplete OR compile failure"
```

### 4.3 Phase 4: Integration Gate

```yaml
stage4_phase4_gate:
  name: "Integration Gate"

  mandatory_conditions:
    full_build:
      target: "SUCCESS"
      validation: "Entire project builds"

    test_execution:
      target: ">= 80% pass"
      validation: "All tests executed"

    quality_checks:
      spotbugs: "No high/critical issues"
      checkstyle: "Violations < threshold"

  decision_matrix:
    PASS: "Build OK + Tests >= 80% + Quality OK"
    CONDITIONAL_PASS: "Build OK + Tests >= 70% + Minor quality issues"
    FAIL: "Build failure OR Tests < 70%"
```

---

## 5. Stage 5 Phase Gates

### 5.1 Phase 1: Structural Standardization Gate

```yaml
stage5_phase1_gate:
  name: "Structural Standardization Gate"
  scope: "Per feature"

  mandatory_conditions:
    naming_compliance:
      target: "100%"
      validation: "All names follow convention"

    url_pattern_compliance:
      target: "100%"
      validation: "All URLs follow pattern"

    package_compliance:
      target: "100%"
      validation: "Correct package structure"

    import_cleanup:
      target: "100%"
      validation: "No wildcard, no unused"

  decision_matrix:
    PASS: "All compliance 100%"
    FAIL: "Any compliance < 100%"
    action: "Auto-fix applied, re-check"
```

### 5.2 Phase 2: Functional Validation Gate

```yaml
stage5_phase2_gate:
  name: "Functional Validation Gate"
  scope: "Per feature"

  mandatory_conditions:
    validation_score:
      target: ">= 70"
      validation: "Weighted score calculation"

    critical_issues:
      target: "0"
      validation: "No critical issues"

  quality_metrics:
    sql_equivalence:
      weight: 40
      target: ">= 35"
      critical: true

    endpoint_equivalence:
      weight: 25
      target: ">= 20"

    business_logic:
      weight: 20
      target: ">= 15"

    data_model:
      weight: 15
      target: ">= 10"

  decision_matrix:
    PASS: "score >= 70 AND critical = 0"
    CONDITIONAL_PASS: "score >= 60 AND critical = 0 AND sql >= 30"
    FAIL: "score < 60 OR critical > 0 OR sql < 25"
```

### 5.3 Phase 3: Quality Standardization Gate

```yaml
stage5_phase3_gate:
  name: "Quality Standardization Gate"
  scope: "Per feature"

  mandatory_conditions:
    code_style:
      target: "Compliant"
      validation: "Style checks pass"

    javadoc:
      target: "All public methods documented"
      validation: "Javadoc coverage"

    logging:
      target: "@Slf4j present"
      validation: "Logging configured"

    exception_handling:
      target: "BusinessException used"
      validation: "Exception pattern correct"

  decision_matrix:
    PASS: "All standards applied"
    FAIL: "Any standard not applied"
    action: "Auto-apply standards, re-check"
```

### 5.4 Phase 4: Integration Validation Gate

```yaml
stage5_phase4_gate:
  name: "Integration Validation Gate"
  scope: "System level"
  trigger: "All features complete Phase 3"

  mandatory_conditions:
    build_validation:
      weight: 70
      checks:
        - "Full project compiles"
        - "No dependency conflicts"
        - "Resources load correctly"
      target: ">= 60 / 70"

    dependency_validation:
      weight: 30
      checks:
        - "No circular dependencies"
        - "All modules resolve"
      target: ">= 25 / 30"

  quality_metrics:
    cross_feature:
      weight: 75
      checks:
        - "Common component compatibility"
        - "Interface consistency"
        - "Data model alignment"
      target: ">= 60 / 75"

    runtime:
      weight: 30
      optional: true
      checks:
        - "Application starts"
        - "Health check responds"

  total_possible: 205
  minimum_required: 150

  decision_matrix:
    PASS: "score >= 175"
    CONDITIONAL_PASS: "score >= 150"
    FAIL: "score < 150"
```

### 5.5 Phase 5: Quality Gate (Final)

```yaml
stage5_phase5_gate:
  name: "Final Quality Gate"
  scope: "System level"
  criticality: "HIGHEST"

  aggregated_metrics:
    overall_pass_rate:
      source: "All Phase 2 validations"
      target: ">= 90%"

    average_score:
      source: "All Phase 2 scores"
      target: ">= 75"

    issue_summary:
      blocker_count: "Must be 0"
      critical_count: "< 5"

  decision_matrix:
    APPROVED:
      conditions:
        blocker: "= 0"
        critical: "< 5"
        score: ">= 85%"
      action: "Ready for deployment"

    CONDITIONALLY_APPROVED:
      conditions:
        blocker: "= 0"
        critical: "5-15"
        score: "70-84%"
      action: "Deploy with known issues tracked"
      followup: "Remediation plan required"

    REJECTED:
      conditions:
        blocker: "> 0"
        or_critical: "> 15"
        or_score: "< 70%"
      action: "Return for remediation"
      followup: "Root cause analysis required"
```

---

## 6. Gate Execution Process

### 6.1 Gate Check Procedure

```yaml
gate_check_procedure:
  1_collect:
    action: "Gather all outputs and metrics"
    source: "Phase output directory"

  2_validate:
    action: "Run validation checks"
    method: "Automated + Manual"

  3_calculate:
    action: "Compute scores and metrics"
    output: "gate-result.yaml"

  4_decide:
    action: "Apply decision matrix"
    output: "PASS | CONDITIONAL_PASS | FAIL"

  5_document:
    action: "Record decision and rationale"
    output: "gate-report.md"

  6_act:
    PASS: "Unlock next phase"
    CONDITIONAL_PASS: "Unlock with issues logged"
    FAIL: "Block and trigger remediation"
```

### 6.2 Gate Override

```yaml
gate_override:
  authorization:
    required: "Project Lead approval"
    documentation: "Override justification"

  valid_reasons:
    - "Known issue with documented workaround"
    - "Time-critical with acceptance of risk"
    - "False positive in automated check"

  invalid_reasons:
    - "Convenience"
    - "Undocumented assumption"

  tracking:
    log: "All overrides recorded"
    review: "Weekly override review"
```

---

## 7. Gate Metrics Dashboard

### 7.1 Gate Status Overview

```yaml
gate_dashboard:
  real_time:
    - "Current phase gate status"
    - "Pending gate checks"
    - "Recent gate decisions"

  historical:
    - "Pass rate by stage/phase"
    - "Average time to pass gate"
    - "Override frequency"

  alerts:
    - "Gate failure"
    - "Stalled at gate"
    - "Multiple failures"
```

### 7.2 Gate Report Template

```markdown
# Phase Gate Report

**Gate**: {Stage X Phase Y Gate Name}
**Feature/Domain**: {identifier}
**Checked At**: {timestamp}

## Decision: {PASS | CONDITIONAL_PASS | FAIL}

## Condition Results

| Condition | Required | Actual | Status |
|-----------|----------|--------|--------|
| {condition} | {value} | {value} | ✓/✗ |

## Quality Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| {metric} | {value} | {value} | ✓/✗ |

## Issues (if any)

| Severity | Description | Resolution |
|----------|-------------|------------|
| {level} | {desc} | {action} |

## Next Actions

- {action 1}
- {action 2}

## Approvals

- Checked by: {system/human}
- Approved by: {approver} (if override)
```

---

**Next**: [03-remediation-procedures.md](03-remediation-procedures.md)
