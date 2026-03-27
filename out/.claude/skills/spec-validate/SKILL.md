---
name: spec-validate
description: "Use to verify specs and codebase are synchronized. Bidirectional validation: forward (spec→code) and backward (code→spec). Run after implementation, periodically, or when drift is suspected."
allowed-tools: Read, Grep, Glob, Bash
---

# Skill: Bidirectional Spec Validation (Spec System Drift Control)

Use this skill to verify that specs and codebase remain synchronized in both directions.

## Goal

Detect and report drift using structural, content, and metric validation tiers with forward and backward checks.

## Why Bidirectional

Forward-only validation is insufficient — Choisor migration data showed forward-only extraction missed 4.7% of endpoints. Both directions are mandatory.

- Forward (spec -> code) catches over-specification and stale entries.
- Backward (code -> spec) catches missing documentation of implemented reality.

Both directions are required for reliable coverage.

## When to Run

- Post-implementation (before task closure)
- Periodically in automation/CI to detect drift
- On merge conflict or disagreement about behavior
- After bootstrap completion and after major refactors/migrations

## Inputs

- `.wonflowoo/workspace/specs/_system.yml`
- `.wonflowoo/workspace/specs/*.yml` feature specs
- Current source code tree
- Optional architecture conventions for naming/type validation

## Validation Tiers

### Tier 1: Structural Validation

Mechanical checks for file shape and required schema.

Checks:

- YAML parses successfully
- Required top-level fields present (`name`, `source_paths`, `interfaces`, `logic`, `data`, `dependencies`)
- Layer presence and expected field types
- `_system.yml` required sections exist (`modules`, `dependency_graph`, `data_ownership`, etc.)

Failure class examples:

- `yaml_parse_error`
- `missing_required_field`
- `invalid_field_type`
- `missing_layer`

### Tier 2: Content Validation

Semantic consistency and reference integrity.

Checks:

- Names are consistent across files and layers
- Interface types and direction values are valid
- `file:` anchors point to real source files
- `source_paths` files exist
- Internal dependency references resolve to existing modules/specs
- `_system.yml` module names map to real feature spec files

Failure class examples:

- `unresolved_source_path`
- `invalid_interface_type`
- `dangling_module_reference`
- `name_mismatch`

### Tier 3: Metric Validation

Quantitative cross-checks between code and specs.

Checks:

- Endpoint/topic/job counts align (within defined tolerance)
- No orphan dependencies (declared but unused or used but undeclared)
- No orphan modules in `_system.yml`
- File coverage ratio from code to specs
- Drift trends from prior run (optional but recommended)

Coverage ratio definition:
- `file_coverage_ratio = files_with_spec_entries / total_significant_source_files`
- Target: 100%
- Acceptable floor: 95%+ only with documented exceptions

Failure class examples:

- `count_mismatch`
- `orphan_dependency`
- `orphan_module`
- `coverage_gap`

---

## Forward Validation (Spec -> Code)

Question: Does everything declared in spec exist in code?

Procedure:

1. Iterate each feature spec and enumerate declared interfaces, flows, data entities, dependencies.
2. Resolve each declaration to concrete code artifact:
   - REST path/method in route definitions
   - Event topic/job handler in subscriber/worker code
   - Data tables/keys in ORM/repository/migrations
   - Dependency usage in imports/runtime clients
3. Record unmatched declarations as stale/over-specified entries.
4. Validate `_system.yml` references to modules and ownership links.

Typical flags:

- Interface declared but route/topic/job absent
- Flow declared with no implementation file anchor
- Data table listed but never referenced by module
- Dependency edge listed but module/package not used

## Backward Validation (Code -> Spec)

Question: Does everything implemented in code exist in specs?

Procedure:

1. Enumerate implemented interfaces, data touchpoints, dependencies from code.
2. Map each artifact to owning feature spec via `source_paths` and `file:` anchors.
3. Flag artifacts with no corresponding spec entries.
4. Ensure `_system.yml` includes all modules represented by feature specs.

Typical flags:

- New endpoint/topic/job implemented but missing in interfaces
- New flow in service code missing in logic layer
- New table/cache key usage missing in data layer
- New internal/external dependency missing in dependencies layer

Backward validation is mandatory to catch under-specification.

---

## Gap Classification and Reporting

Report all findings in a structured artifact:

```yaml
validation_report:
  timestamp: <iso8601>
  summary:
    structural_failures: <int>
    content_failures: <int>
    metric_failures: <int>
    forward_gaps: <int>
    backward_gaps: <int>
  gaps:
    - id: GAP-001
      tier: content
      direction: backward
      feature: auth
      type: missing_interface
      spec_path: .wonflowoo/workspace/specs/auth.yml
      code_path: src/routes/auth.routes.ts
      detail: "POST /api/auth/logout exists in code but not in spec"
      severity: high
      recommended_fix: "Add endpoint to interfaces with file anchor"
```

Severity guidance:

- High: behavior missing/misrepresented in spec
- Medium: reference inconsistency with low runtime risk
- Low: formatting/convention drift without semantic loss

Metric mismatch severity:
- High severity when the mismatch is a backward gap (implemented behavior missing from spec)
- Medium severity when the mismatch is a forward gap (over-specification)

## Remediation Workflow

1. Fix structural blockers first (unparseable/invalid files).
2. Resolve content reference errors.
3. Reconcile metric mismatches.
4. Re-run full bidirectional validation.
5. Repeat until no blocking gaps remain.

Do NOT close implementation tasks while high-severity backward gaps remain. Backward gaps indicate missing spec documentation of implemented behavior.

## Output Expectations

Validation run must produce:

- Pass/fail status per tier
- Pass/fail status per direction (forward/backward)
- Gap list with severity and actionable fix suggestions
- Coverage summary (spec -> code and code -> spec)

## Done Criteria

- Structural tier clean
- No unresolved content references
- Metric mismatches either resolved or explicitly accepted with rationale
- Forward and backward checks both pass for target scope
