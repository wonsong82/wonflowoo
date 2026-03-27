---
name: s2-03-validation-gap-analysis
description: Use when classifying specification gaps by severity, determining remediation strategies for discrepancies, or prioritizing spec completion work (project)
---

# Gap Analysis

> **Skill ID**: S2-03
> **Skill Type**: Validation (Gap 분류 및 심각도 평가)
> **Stage**: 2 - Validation
> **Phase**: 2.3 - Gap Analysis

## 1. Overview

### 1.1 Purpose

S2-02에서 식별된 모든 불일치(discrepancy)를 **심각도별로 분류**하고, 각 Gap에 대한 **remediation 전략**을 결정합니다. 이 분석 결과는 S2-04 Spec Completion의 우선순위 및 작업 범위를 결정합니다.

**주요 활동:**
| Activity | Description |
|----------|-------------|
| **분류** | 각 Gap의 심각도(critical/major/minor) 판정 |
| **원인 분석** | Gap 발생 원인 파악 (누락/오류/변경) |
| **영향 평가** | 마이그레이션에 미치는 영향도 산정 |
| **전략 수립** | 각 Gap에 대한 remediation 방법 결정 |

### 1.2 Gap Classification

| Severity | Score | Criteria | Remediation | Blocking |
|----------|-------|----------|-------------|----------|
| **critical** | 100 | 핵심 기능 누락, 데이터 불일치 | Immediate - Block until resolved | Yes |
| **major** | 70 | 주요 기능 누락, API 불일치 | Required - Resolve in P2.4 | No (but required) |
| **minor** | 30 | 부가 기능, 문서화 누락 | Optional - Document for future | No |
| **false_positive** | 0 | 실제 Gap 아님 | Document rationale | No |

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **완전성** | 모든 Gap 분류 필수 | 미분류 Gap은 리스크 |
| **일관성** | 동일 기준 적용 | 주관적 판단 최소화 |
| **실행가능성** | 구체적 remediation 제시 | S2-04 실행 가능해야 함 |
| **추적성** | 원본 위치 및 근거 기록 | 검증 및 감사 가능 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S2-03은 Gap을 분류하며, **SQL/Data 관련 Gap은 Data Integrity 영향으로 높은 심각도 부여**

### 1.5 Relationships

**Predecessors:**
| Skill | Input |
|-------|-------|
| `s2-02-validation-structural-comparison` | comparison-report.yaml, discrepancies |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s2-04-validation-spec-completion` | Gap별 remediation 실행 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "s2-02-validation-structural-comparison"
    relationship: "sequential"
    outputs_used:
      - "comparison-report.yaml"
      - "coverage-matrix.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| comparison_report | file | `work/specs/stage2-outputs/phase2/{Priority}/{Domain}/comparison-report.yaml` | YAML | Yes |
| legacy_source | directory | `${LEGACY_CODEBASE}/src/main/java/` | Java | Yes (추가 분석용) |
| stage1_specs | directory | `work/specs/stage1-outputs/phase4/{Priority}/{Domain}/` | YAML | Yes (context) |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Read | - | YAML/Java 파일 읽기 |
| Grep | - | 소스코드 패턴 검색 |
| Glob | - | 파일 패턴 매칭 |

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: parallel
  unit: domain
  parallelization:
    max_sessions: 10
    batch_unit: domain
    timeout_minutes: 180
    retry_on_failure: 3
```

### 3.2 Analysis Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Load Gaps    │────▶│ Classify     │────▶│ Determine    │────▶│ Generate     │
│ from Report  │     │ Severity     │     │ Remediation  │     │ Analysis     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 3.3 Process Steps

#### Step 1: Load Discrepancies

**Description:** S2-02 비교 결과에서 모든 불일치 항목 로드

**Sub-steps:**
1. comparison-report.yaml 로드 - **Large File Handling 적용** (v1.2.0)
2. discrepancies 섹션 파싱
3. over_specifications 및 under_specifications 분리
4. 총 Gap 수 집계

**Large File Reading (v1.2.0):**

> **⚠️ Read Tool Limit**: comparison-report.yaml은 256KB를 초과할 수 있음

```yaml
comparison_report_loading:
  step_1:
    name: "파일 크기 확인"
    action: "Bash: wc -c < comparison-report.yaml"

  step_2:
    name: "크기 기반 로딩"
    if_small: "전체 Read (< 200KB)"
    if_large:
      name: "offset/limit 청크 읽기"
      process: |
        1. total_lines=$(wc -l < comparison-report.yaml)
        2. for offset in 0, 1500, 3000, ...:
             Read(file, offset=offset, limit=1500)
             # YAML 파싱 및 누적
        3. 전체 데이터 조립

  threshold_kb: 200
  chunk_lines: 1500
```

**Validation:** 모든 discrepancy 로드 완료 (대용량 파일 지원)

---

#### Step 2: Classify Severity

**Description:** 각 Gap에 심각도 부여

**Classification Rules:**
```yaml
classification_rules:
  critical:
    - "핵심 비즈니스 로직 누락"
    - "데이터 무결성 영향"
    - "트랜잭션 경계 불일치 (critical 메서드)"
    - "인증/인가 관련"

  major:
    - "API 엔드포인트 누락"
    - "서비스 메서드 누락"
    - "SQL 쿼리 누락"
    - "주요 VO/DTO 필드 누락"
    # v1.2.0 추가
    - "메서드 시그니처 불일치 (signature_mismatch)"
    - "파라미터 타입/개수 불일치"
    - "반환 타입 불일치"

  minor:
    - "부가 유틸리티 메서드"
    - "로깅/모니터링 코드"
    - "deprecated 기능"
    - "문서화 수준 차이"
    # v1.2.0 추가
    - "필드 타입 불일치 (field_type_mismatch)"
    - "트랜잭션 어노테이션 불일치 (annotation_mismatch)"

  false_positive:
    - "테스트 전용 코드"
    - "개발자 도구"
    - "실행되지 않는 dead code"
    - "정규화 차이로 인한 오탐"
```

#### v1.2.0 추가: 신규 Gap 유형 분류

| Gap Type | Severity | Criteria | Remediation |
|----------|----------|----------|-------------|
| **signature_mismatch** | MAJOR | 메서드 시그니처 불일치 (파라미터/반환타입) | Spec 수정 또는 Source 확인 |
| **annotation_mismatch** | MINOR/WARNING | @Transactional 등 어노테이션 불일치 | Spec에 어노테이션 추가 |
| **field_type_mismatch** | MINOR | Entity 필드 타입 불일치 | 타입 매핑 확인 |

**시그니처 불일치 분류 기준:**
```yaml
signature_mismatch_classification:
  severity_determination:
    - condition: "파라미터 개수 불일치"
      severity: "major"
      reason: "API 호환성 문제 - 호출 실패 가능"
    - condition: "반환 타입 불일치"
      severity: "major"
      reason: "타입 캐스팅 오류 가능"
    - condition: "파라미터 타입 불일치"
      severity: "major"
      reason: "런타임 오류 가능"

  remediation_strategy: "correct_spec"
  effort: "low-medium"
```

**트랜잭션 어노테이션 분류 기준:**
```yaml
annotation_mismatch_classification:
  severity_determination:
    - condition: "데이터 변경 메서드에 @Transactional 누락"
      severity: "minor"
      impact: "데이터 무결성 위험 (롤백 불가)"
    - condition: "조회 메서드에 @Transactional(readOnly=true) 누락"
      severity: "minor"
      impact: "성능 최적화 누락"

  remediation_strategy: "add_to_spec"
  effort: "low"
```

**필드 타입 불일치 분류 기준:**
```yaml
field_type_mismatch_classification:
  severity_determination:
    - condition: "String ↔ Number 변환 필요"
      severity: "minor"
      impact: "형변환 로직 필요"
    - condition: "호환 가능한 타입 (Integer ↔ Long)"
      severity: "minor"
      impact: "자동 변환 가능"

  remediation_strategy: "normalize_spec"
  effort: "low"
```

**Sub-steps:**
1. Gap 유형 확인 (endpoint/service/sql/entity)
2. Gap 내용 분석 (소스코드 참조)
3. Classification rules 적용
4. 심각도 및 근거 기록

---

#### Step 3: Root Cause Analysis

**Description:** 각 Gap의 발생 원인 분석

**Root Cause Categories:**
| Category | Description | Example |
|----------|-------------|---------|
| **missing_in_spec** | Stage 1에서 누락 | 스캔 패턴 미적용 |
| **spec_error** | Spec 작성 오류 | 잘못된 URL 기록 |
| **source_change** | 소스 변경 미반영 | 최근 수정 코드 |
| **normalization_gap** | 정규화 문제 | 대소문자/패턴 차이 |
| **intentional_omit** | 의도적 제외 | deprecated 기능 |

**Sub-steps:**
1. Gap 상세 위치 확인
2. 소스코드 직접 검토
3. Stage 1 처리 이력 확인 (가능한 경우)
4. Root cause 판정

---

#### Step 4: Impact Assessment

**Description:** 각 Gap이 마이그레이션에 미치는 영향 평가

**Impact Dimensions:**
| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Functionality | 0.40 | 기능 동작에 영향 |
| Data Integrity | 0.30 | 데이터 정합성 영향 |
| Performance | 0.15 | 성능에 영향 |
| User Experience | 0.15 | 사용자 경험 영향 |

**Impact Levels:**
| Level | Score Range | Description |
|-------|-------------|-------------|
| High | 80-100 | 즉시 해결 필요 |
| Medium | 50-79 | Phase 2.4에서 해결 |
| Low | 20-49 | 선택적 해결 |
| None | 0-19 | 무시 가능 |

---

#### Step 5: Determine Remediation

**Description:** 각 Gap에 대한 해결 전략 수립

**Remediation Strategies:**
```yaml
remediation_strategies:
  add_to_spec:
    applicable: "under_specification"
    action: "S2-04에서 Spec에 추가"
    effort: "low-medium"

  remove_from_spec:
    applicable: "over_specification (dead code)"
    action: "Spec에서 제거"
    effort: "low"

  correct_spec:
    applicable: "spec_error"
    action: "Spec 수정"
    effort: "low"

  normalize_spec:
    applicable: "normalization_gap"
    action: "정규화 규칙 조정"
    effort: "low"

  defer:
    applicable: "minor gaps"
    action: "향후 처리로 연기"
    effort: "none"

  false_positive_mark:
    applicable: "false_positive"
    action: "오탐으로 기록"
    effort: "none"
```

---

#### Step 6: Feature-level Aggregation

**Description:** Gap을 Feature 단위로 그룹핑

**Sub-steps:**
1. 각 Gap을 Feature ID에 매핑
2. Feature별 Gap 집계
3. Feature별 심각도 요약
4. gap-by-feature.yaml 생성

---

#### Step 7: Generate Analysis Reports

**Description:** 분석 결과 보고서 생성

**Sub-steps:**
1. gap-analysis.yaml 생성
2. gap-by-feature.yaml 생성
3. 요약 통계 계산
4. YAML 문법 검증

---

#### Step 8: Schema Validation

**Description:** 생성된 gap-analysis.yaml 및 gap-by-feature.yaml이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | gap-analysis | 필수 키 존재 | ERROR | Yes |
| V002 | gap-by-feature | 필수 키 존재 | ERROR | Yes |
| V003 | metadata.generated_by | 정확히 일치 | ERROR | Yes |
| V004 | gaps[].severity | enum 검증 | ERROR | Yes |
| V005 | gaps[].type | enum 검증 | ERROR | Yes |
| V006 | gaps[].dimension | enum 검증 | ERROR | Yes |
| V007 | gaps[].id | GAP-{DOMAIN}-{NNN} 패턴 | ERROR | Yes |
| V008 | gate_evaluation.result | enum 검증 | ERROR | Yes |
| V009 | summary | severity 합계 일치 | WARNING | No |
| V010 | gaps | 모든 gap에 severity 할당 | ERROR | Yes |

**Sub-steps:**
1. gap-analysis.yaml 파일 로드
2. gap-by-feature.yaml 파일 로드
3. 스키마 파일 로드 및 검증 규칙 적용
4. 검증 실패 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재생성 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.4 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | Critical gap 발견 | 즉시 escalation | 정상 진행 |
| DP-2 | Critical > 0 at end | Gate FAIL | Gate evaluation |
| DP-3 | 애매한 분류 | conservative (higher severity) | 정상 분류 |
| DP-4 | False positive 의심 | 소스 직접 확인 | 정상 분류 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage2-outputs/phase3/"
    pattern: "{Priority}/{Domain}/"

  example: "work/specs/stage2-outputs/phase3/P2-Core/PA/"
```

### 4.2 Output Files

| File | Type | Purpose | Required |
|------|------|---------|----------|
| gap-analysis.yaml | YAML | 전체 Gap 분석 결과 | Yes |
| gap-by-feature.yaml | YAML | Feature별 Gap 그룹핑 | Yes |

### 4.3 File Header

```yaml
# Generated by: s2-03-validation-gap-analysis
# Stage: 2 - Validation
# Phase: 2.3 - Gap Analysis
# Domain: ${DOMAIN}
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
```

### 4.4 Output Schemas

#### gap-analysis.yaml

```yaml
# gap-analysis.yaml
metadata:
  generated_by: "s2-03-validation-gap-analysis"
  generated_at: "2026-01-07T12:00:00Z"
  domain: "PA"
  source_report: "work/specs/stage2-outputs/phase2/P2-Core/PA/comparison-report.yaml"

summary:
  total_gaps: 111
  by_severity:
    critical: 0
    major: 23
    minor: 45
    false_positive: 43
  by_type:
    under_specification: 68
    over_specification: 43
  by_root_cause:
    missing_in_spec: 45
    spec_error: 12
    source_change: 8
    normalization_gap: 3
    intentional_omit: 43

remediation_summary:
  add_to_spec: 45
  remove_from_spec: 0
  correct_spec: 12
  normalize_spec: 3
  defer: 8
  false_positive_mark: 43
  estimated_effort: "medium"

gaps:
  - id: "GAP-PA-001"
    discrepancy_id: "DISC-001"
    type: "under_specification"
    dimension: "endpoint"
    severity: "major"
    severity_score: 70

    location:
      source_file: "src/main/java/com/hallain/pa/controller/PA01005Controller.java"
      source_line: 45
      source_item: "PA01005Controller.getLegacyReport"

    analysis:
      root_cause: "missing_in_spec"
      root_cause_detail: "Stage 1 스캔 시 @GetMapping 패턴 누락"
      impact_score: 65
      impact_dimensions:
        functionality: 70
        data_integrity: 50
        performance: 20
        user_experience: 60

    remediation:
      strategy: "add_to_spec"
      action: "S2-04에서 해당 엔드포인트를 Spec에 추가"
      priority: 2
      effort: "low"
      target_files:
        - "api-specs/openapi-spec.yaml"

  - id: "GAP-PA-002"
    discrepancy_id: "DISC-015"
    type: "over_specification"
    dimension: "endpoint"
    severity: "false_positive"
    severity_score: 0

    location:
      spec_file: "api-specs/openapi-spec.yaml"
      spec_line: 234
      spec_item: "PA01099Controller.getArchiveList"

    analysis:
      root_cause: "intentional_omit"
      root_cause_detail: "테스트 전용 코드로 프로덕션에서 제외됨"
      impact_score: 0

    remediation:
      strategy: "false_positive_mark"
      action: "오탐으로 기록, Spec 유지 또는 제거 결정 필요"
      priority: 5
      effort: "none"

  # ... more gaps

gate_evaluation:
  criteria:
    all_classified: true
    critical_count: 0
    critical_remediation_planned: true  # N/A when critical=0
  result: "PASS"
```

#### gap-by-feature.yaml

```yaml
# gap-by-feature.yaml
metadata:
  generated_by: "s2-03-validation-gap-analysis"
  generated_at: "2026-01-07T12:00:00Z"
  domain: "PA"

summary:
  total_features: 443
  features_with_gaps: 45
  features_clean: 398

features:
  - feature_id: "FEAT-PA-005"
    screen_id: "PA01005"
    gap_summary:
      total: 3
      critical: 0
      major: 2
      minor: 1
      false_positive: 0
    gaps:
      - gap_id: "GAP-PA-001"
        severity: "major"
        type: "under_specification"
        item: "PA01005Controller.getLegacyReport"
        remediation: "add_to_spec"
      - gap_id: "GAP-PA-008"
        severity: "major"
        type: "under_specification"
        item: "PA01005Service.generateReport"
        remediation: "add_to_spec"
      - gap_id: "GAP-PA-015"
        severity: "minor"
        type: "under_specification"
        item: "PA01005VO.legacyField"
        remediation: "defer"
    overall_status: "needs_remediation"
    priority: 2

  - feature_id: "FEAT-PA-001"
    screen_id: "PA01001"
    gap_summary:
      total: 0
      critical: 0
      major: 0
      minor: 0
      false_positive: 0
    gaps: []
    overall_status: "clean"
    priority: null

  # ... more features

priority_order:
  - priority: 1
    reason: "Critical gaps"
    features: []
  - priority: 2
    reason: "Major gaps only"
    features: ["FEAT-PA-005", "FEAT-PA-023", "FEAT-PA-045"]
  - priority: 3
    reason: "Minor gaps only"
    features: ["FEAT-PA-012", "FEAT-PA-067"]
  - priority: 4
    reason: "Clean (no remediation needed)"
    features: ["FEAT-PA-001", "FEAT-PA-002", "..."]
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| files_exist | structural | 두 파일 모두 존재 | ERROR | Yes |
| yaml_syntax | structural | YAML 파싱 오류 없음 | ERROR | Yes |
| all_classified | completeness | 모든 discrepancy에 분류 있음 | ERROR | Yes |
| critical_reviewed | content | critical gap에 remediation plan | ERROR | Yes |

### 5.2 Classification Accuracy

| Check | Criteria |
|-------|----------|
| Severity distribution | 합리적 분포 (critical << major) |
| False positive ratio | < 50% (과도한 오탐 경고) |
| Unclassified | 0개 |

### 5.3 Gate Criteria

```yaml
gate_criteria:
  id: "G2.3"
  name: "Gap Analysis Gate"
  tier: "phase_gate"
  threshold: 70
  metrics:
    - metric: "file_exists"
      weight: 0.2
      target: "true"
      formula: "gap-analysis.yaml AND gap-by-feature.yaml exist"
    - metric: "all_classified"
      weight: 0.4
      target: "true"
      formula: "Every discrepancy has classification"
    - metric: "critical_reviewed"
      weight: 0.4
      target: "true"
      formula: "All critical gaps have remediation plan"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Missing input | 로드 실패 | S2-02 미완료 | S2-02 완료 후 재실행 | Yes |
| Source access error | 분석 불가 | 권한/경로 문제 | 경로 확인 | Yes |
| Classification conflict | 일관성 없음 | 규칙 모호 | conservative 적용 | Auto |
| Large gap count | timeout | 불일치 많음 | 병렬 처리 | Yes |
| **Large input file** (v1.3.0) | Read tool 256KB 초과 | 대형 도메인 comparison-report | offset/limit 청크 읽기 (Step 1) | Auto |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Critical gap 발견 | critical | 즉시 보고 | Tech Lead |
| Major > 50개 | major | WARNING 로그 | Orchestrator |
| 분류 불가 | minor | conservative 적용 | - |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 부분 분류 실패 | 해당 Gap만 재분석 | Gap |
| 전체 실패 | S2-02 결과 확인 후 재실행 | Phase |

---

## 7. Examples

### 7.1 Sample Classification

**Input (Discrepancy):**
```yaml
- id: "DISC-001"
  type: "missing_in_spec"
  dimension: "endpoint"
  source_item: "PA01005Controller.getLegacyReport"
  source_file: "PA01005Controller.java"
  source_line: 45
```

**Analysis Process:**
1. 소스코드 확인: `@GetMapping("/pa/PA01005/legacyReport")`
2. 기능 분석: 레거시 리포트 생성 - 비즈니스 기능
3. 사용 빈도 확인: 호출 로그 존재 (활성 기능)
4. Severity 판정: **major** (API 엔드포인트 누락)
5. Root cause: **missing_in_spec** (스캔 패턴 미적용)
6. Remediation: **add_to_spec** (Spec에 추가)

### 7.2 Sample Output

```yaml
- id: "GAP-PA-001"
  discrepancy_id: "DISC-001"
  type: "under_specification"
  dimension: "endpoint"
  severity: "major"
  severity_score: 70

  location:
    source_file: "PA01005Controller.java"
    source_line: 45
    source_item: "PA01005Controller.getLegacyReport"

  analysis:
    root_cause: "missing_in_spec"
    root_cause_detail: "Stage 1에서 @GetMapping 패턴 스캔 누락"
    impact_score: 65

  remediation:
    strategy: "add_to_spec"
    action: "해당 엔드포인트를 openapi-spec.yaml에 추가"
    priority: 2
    effort: "low"
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| 모든 Gap = false_positive | 43 false positives | total_gaps: 43, remediation: 0 |
| Critical gap 발견 | 트랜잭션 누락 | 즉시 escalation, Gate FAIL |
| 분류 경계 | 애매한 major/minor | conservative (major) 적용 |
| 0 gaps | 불일치 없음 | empty gaps[], PASS |

---

## Version History

### v1.3.0 (2026-01-13)
- **Large File Reading 추가**
  - Step 1: comparison-report.yaml 대용량 파일 읽기 지원
  - offset/limit 청크 읽기 전략 추가
  - Known Issues에 Large input file 추가

### v1.2.0 (2026-01-13)
- 신규 Gap 유형 추가: signature_mismatch, annotation_mismatch, field_type_mismatch
- Classification Rules 확장: major에 시그니처 불일치, minor에 어노테이션/필드타입 불일치
- 각 신규 Gap 유형별 분류 기준 및 remediation 전략 정의
- S2-02 v1.2.0 discrepancy 유형과 연계

### v1.1.0 (2026-01-08)
- Step 8: Schema Validation 추가
- s2-03-gap-analysis.schema.yaml 스키마 참조
- 10개 검증 규칙 적용 (V001-V010)

### v1.0.0 (2026-01-07)
- Initial version
- 4-tier severity classification
- Root cause analysis
- Feature-level aggregation
