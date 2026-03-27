---
name: {skill-name-with-hyphens}
description: Use when {검증이 필요한 상황/증상 - 트리거 조건만}
---

# {Validation Skill Name}

> **CRITICAL - 파일 위치**: `.claude/skills/{name}/SKILL.md` 경로에 저장 필수.
> 디렉토리명 = `name` 필드 (정확히 일치). 중첩 구조 금지.

> **CRITICAL**: Frontmatter(위 `---` 블록)는 반드시 파일 맨 처음에 raw YAML로 시작해야 합니다.
> 코드 블록(` ```yaml `)으로 감싸면 Claude Code가 인식하지 못합니다.

> **Skill Type**: Validation (품질 검증 및 일치성 확인)

## 1. Overview

### 1.1 Purpose

{검증 목적과 대상을 명확하게 기술}

**검증 대상:**
- Source A: {비교 대상 A}
- Source B: {비교 대상 B}

**검증 항목:**
- {검증 항목 1}
- {검증 항목 2}

### 1.2 Validation Scope

| Dimension | Weight | Match Criteria |
|-----------|--------|----------------|
| {차원 1} | {0.0-1.0} | {일치 기준} |
| {차원 2} | {0.0-1.0} | {일치 기준} |

---

## 2. Prerequisites

### 2.1 Comparison Sources

```yaml
comparison_sources:
  source_a:
    name: "{Source A 이름}"
    location: "{경로}"
    type: "spec|code|data"

  source_b:
    name: "{Source B 이름}"
    location: "{경로}"
    type: "spec|code|data"
```

### 2.2 Normalization Rules

| Source | Field | Normalization |
|--------|-------|---------------|
| A | {필드} | {정규화 방법} |
| B | {필드} | {정규화 방법} |

---

## 3. Methodology

### 3.1 Validation Pipeline

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Source A │────▶│ Normalize│────▶│ Compare  │────▶│  Score   │
│ Source B │────▶│  & Align │────▶│ & Match  │────▶│ & Report │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

### 3.2 Comparison Strategy

```yaml
comparison_strategy:
  direction: "bidirectional"  # or "unidirectional"

  forward_check:
    name: "A → B"
    purpose: "A의 모든 항목이 B에 있는지"
    identifies: "Over-specification"

  backward_check:
    name: "B → A"
    purpose: "B의 모든 항목이 A에 있는지"
    identifies: "Under-specification"
```

### 3.3 Matching Rules

| Field | Match Type | Tolerance |
|-------|------------|-----------|
| {필드 1} | exact | - |
| {필드 2} | fuzzy | {허용치} |
| {필드 3} | semantic | {유사도} |

---

## 4. Outputs

### 4.1 Validation Report

```yaml
validation_report:
  file: "validation-report.yaml"
  sections:
    - summary
    - forward_results
    - backward_results
    - gaps
    - score
```

### 4.2 Score Calculation

```yaml
score_calculation:
  formula: "Σ(dimension_weight × dimension_score)"

  dimensions:
    - name: "{차원 1}"
      weight: {0.0-1.0}
      score: "matched / total * 100"

  thresholds:
    pass: ">= {threshold}"
    conditional: ">= {threshold - 20}"
    fail: "< {threshold - 20}"
```

### 4.3 Output Schema

```yaml
# validation-report.yaml
metadata:
  skill: "${SKILL_NAME}"
  timestamp: "${TIMESTAMP}"
  sources:
    a: "{source_a_path}"
    b: "{source_b_path}"

summary:
  total_items_a: {count}
  total_items_b: {count}
  matched: {count}
  mismatched: {count}
  score: {percentage}

forward_check:
  coverage: {percentage}
  missing_in_b:
    - {item}

backward_check:
  coverage: {percentage}
  missing_in_a:
    - {item}

gaps:
  - item: "{item_id}"
    type: "missing|mismatch"
    severity: "critical|major|minor"
    details: "{상세 내용}"

result: "PASS|CONDITIONAL|FAIL"
```

---

## 5. Quality Checks

### 5.1 Validation Accuracy

| Check | Criteria |
|-------|----------|
| False positive rate | < 5% |
| False negative rate | < 1% |

### 5.2 Coverage Requirements

| Metric | Target |
|--------|--------|
| Source A coverage | 100% |
| Source B coverage | 100% |
| Comparison coverage | >= 99% |

---

## 6. Error Handling

### 6.1 Comparison Errors

| Error Type | Handling |
|------------|----------|
| Missing source | FAIL immediately |
| Parse error | Skip item, log warning |
| Timeout | Retry once |

### 6.2 Gap Classification

| Severity | Criteria | Action |
|----------|----------|--------|
| Critical | {기준} | Must fix |
| Major | {기준} | Should fix |
| Minor | {기준} | May defer |
| False Positive | {기준} | Mark and skip |

---

## 7. Examples

### 7.1 Sample Comparison

**Source A (Spec):**
```yaml
endpoints:
  - path: "/api/sample/list"
    method: "POST"
```

**Source B (Ground Truth):**
```yaml
endpoints:
  - path: "/api/sample/list"
    method: "POST"
  - path: "/api/sample/detail"
    method: "GET"
```

### 7.2 Sample Output

```yaml
validation_report:
  forward_check:
    coverage: 100%
    missing_in_b: []

  backward_check:
    coverage: 50%
    missing_in_a:
      - path: "/api/sample/detail"

  gaps:
    - item: "/api/sample/detail"
      type: "missing"
      severity: "major"
      details: "Endpoint exists in source but not in spec"

  score: 75%
  result: "CONDITIONAL"
```
