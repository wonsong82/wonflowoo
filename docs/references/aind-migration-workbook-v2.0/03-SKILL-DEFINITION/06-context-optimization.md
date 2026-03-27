# Context Optimization Strategy

**Version**: 1.1.0
**Last Updated**: 2026-01-13
**Purpose**: AI-Driven Migration에서 대형 Context 처리 시 데이터 손실 방지 전략

---

## 1. Overview

### 1.1 Problem Statement

**두 가지 다른 제한 문제:**

| 문제 유형 | Root Cause | Symptom | 해결책 |
|----------|------------|---------|--------|
| **Output Token Limit** | LLM 출력 ~25-30K tokens | Summary 정상, 데이터 배열 중간 절단 | Sub-wave division (Section 2-5) |
| **Read Tool File Limit** | Claude Code Read 도구 256KB 제한 | 파일 읽기 실패 오류 | Chunked I/O (Section 2.4) |

**Impact:**
- Output Token Limit: 95%+ 데이터 손실 가능 (PA: 1.7%, EB: 2.1% 문서화 사례)
- Read Tool File Limit: 파일 읽기 완전 실패 (source-inventory.yaml 2.2MB → 읽기 불가)

### 1.2 Scope

**In Scope:**
- Input Context 최적화 (읽기)
- Output Context 최적화 (쓰기)
- Processing Context 최적화 (처리)
- Truncation 감지 및 복구

**Out of Scope:**
- LLM 모델 자체 튜닝
- Infrastructure 레벨 최적화

### 1.3 Core Principle

> **Context 누락은 허용되지 않는다.**
>
> 모든 데이터는 100% 보존되어야 하며, 손실 발생 시 즉시 감지하고 복구해야 한다.

---

## 2. 핵심 전략

### 2.1 Input Context 최적화 (읽기)

```
┌─────────────────────────────────────────────────────────────┐
│                INPUT CONTEXT OPTIMIZATION                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐│
│  │   Source     │────▶│   Filter     │────▶│  Essential   ││
│  │   Files      │     │   Rules      │     │   Data Only  ││
│  └──────────────┘     └──────────────┘     └──────────────┘│
│                                                             │
│  Techniques:                                                │
│  - Selective file loading (필요 파일만)                     │
│  - Header-only scanning (전체 파싱 회피)                    │
│  - Cross-reference (중복 로딩 방지)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Token Efficiency Guidelines:**

| 스킬 유형 | 목표 단어 수 | 비고 |
|----------|-------------|------|
| getting-started | <150 words | 모든 대화에 로드됨 |
| 자주 로드 스킬 | <200 words | 빈번하게 참조됨 |
| 일반 스킬 | <500 words | 필요 시 로드 |

**압축 기법:**
- 세부사항은 `--help` 참조로 대체
- 다른 스킬 cross-reference 활용
- 예시는 최소화 (1개의 좋은 예시 > 5개의 평범한 예시)
- 중복 제거

### 2.2 Output Context 최적화 (쓰기)

```
┌─────────────────────────────────────────────────────────────┐
│               OUTPUT CONTEXT OPTIMIZATION                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 0: Size Assessment                                    │
│  ┌──────────────────────────────────────────────────┐      │
│  │  controller_count > 100? endpoint_estimate > 200? │      │
│  └──────────────────────┬───────────────────────────┘      │
│                         │                                   │
│         ┌───────────────┴───────────────┐                  │
│         │ small                         │ large            │
│         ▼                               ▼                  │
│  ┌──────────────┐               ┌──────────────┐           │
│  │ Single Pass  │               │  Sub-Wave    │           │
│  │   Execute    │               │  Division    │           │
│  └──────────────┘               └──────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Lean Format 원칙:**
- Sub-wave 출력 시 compact format 사용
- Size reduction: 60-70%
- Omit: detailed column definitions
- Preserve: essential identifiers, standard response variables

### 2.3 Processing Context 최적화 (처리)

```
┌─────────────────────────────────────────────────────────────┐
│              PROCESSING CONTEXT OPTIMIZATION                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐│
│  │ Session Pool │────▶│   Batch      │────▶│ Checkpoint   ││
│  │   (max 10)   │     │ Processing   │     │  Manager     ││
│  └──────────────┘     └──────────────┘     └──────────────┘│
│                                                             │
│  Configuration:                                             │
│  - max_sessions: 10                                         │
│  - batch_size: 50                                           │
│  - checkpoint_frequency: per_task                           │
│  - session_timeout_minutes: 60                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.4 File Size Handling (v1.1.0 추가)

> **⚠️ Read Tool Limit**: Claude Code Read 도구는 256KB 제한. 이 제한을 초과하는 파일은 분할 I/O 필요

```
┌─────────────────────────────────────────────────────────────┐
│                 FILE SIZE HANDLING                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WRITE (저장 시)                     READ (읽기 시)         │
│  ┌────────────────────┐             ┌────────────────────┐ │
│  │ size < 200KB?      │             │ file/dir exists?   │ │
│  └─────────┬──────────┘             └─────────┬──────────┘ │
│      yes   │   no                       dir   │   file     │
│      ▼     ▼                            ▼     ▼            │
│  ┌──────┐ ┌──────────────┐       ┌──────────┐ ┌──────────┐│
│  │Single│ │Layer-based   │       │Manifest  │ │Size check││
│  │ file │ │ Split        │       │ + Chunks │ │ first    ││
│  └──────┘ └──────────────┘       └──────────┘ └──────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Threshold:**
| 조건 | 처리 방식 |
|------|----------|
| 예상 출력 < 200KB | 단일 파일 저장 |
| 예상 출력 >= 200KB | Layer별 분할 저장 (manifest + chunks) |

**Output Chunking (저장 시 분할):**

```yaml
chunked_output_structure:
  pattern: "{filename}/ 디렉토리"
  example: "source-inventory/"
  files:
    - "_manifest.yaml"    # metadata + summary + chunk 목록
    - "controllers.yaml"  # Layer별 분할 파일
    - "services.yaml"
    - "daos.yaml"
    - "sql_statements.yaml"
    - "entities.yaml"

manifest_schema:
  metadata: "원본과 동일"
  summary: "원본과 동일"
  chunks:
    - name: "controllers"
      file: "controllers.yaml"
      item_count: 124
    - name: "services"
      file: "services.yaml"
      item_count: 98
```

**Input Chunking (읽기 시 분할):**

```yaml
reading_strategy:
  step_1: "파일/디렉토리 존재 확인"
  step_2:
    if_directory: "manifest 기반 청크 읽기"
    if_file: "크기 확인 후 처리"

  step_3_for_file:
    check: "wc -c < file.yaml"
    if_small: "전체 Read (< 200KB)"
    if_large:
      method: "offset/limit 청크 읽기"
      chunk_lines: 1500
      process: |
        total_lines=$(wc -l < file.yaml)
        for offset in 0 1500 3000 ...; do
          Read(file, offset=offset, limit=1500)
          # YAML 파싱 및 데이터 누적
        done
```

**적용 스킬:**

| Skill | 유형 | 대상 파일 |
|-------|------|----------|
| s2-01 | Output | source-inventory.yaml (2.2MB 가능) |
| s2-02 | Input | source-inventory.yaml |
| s2-03 | Input | comparison-report.yaml |
| s2-04 | Input | gap-analysis.yaml |
| s1-02 | Input/Output | feature-inventory.yaml, miplatform-protocol.yaml |
| s1-03 | Input | feature-inventory.yaml, miplatform-protocol.yaml |

---

## 3. Size Thresholds (임계값)

### 3.1 Decision Matrix

| 항목 | Small | Large |
|------|-------|-------|
| Controllers | ≤100 | >100 |
| Endpoints | ≤200 | >200 |
| 처리 방식 | Single Pass | Sub-wave Division |

### 3.2 Threshold Rationale

```yaml
thresholds:
  small:
    max_controllers: 100
    max_endpoints: 200
    strategy: single_pass
    rationale: "LLM 출력 토큰 내 안전하게 처리 가능"

  large:
    min_controllers: 100
    min_endpoints: 200
    strategy: sub_wave_division
    rationale: "토큰 제한으로 인한 truncation 위험"
```

---

## 4. Sub-wave Division 전략

### 4.1 분할 기준

| 항목 | 값 |
|------|---|
| Target Size | 30-50 controllers per wave |
| Method | prefix_grouping |
| Output Format | lean_format (60-70% 압축) |

### 4.2 분할 예시

**PA Domain (462 controllers → 6 waves):**
```yaml
waves:
  - wave: 1
    prefix: "PA01, PA02"
    controllers: 26
  - wave: 2
    prefix: "PA03"
    controllers: 55
  - wave: 3
    prefix: "PA04"
    controllers: 118
  - wave: 4
    prefix: "PA05"
    controllers: 80
  - wave: 5
    prefix: "PA06"
    controllers: 139
  - wave: 6
    prefix: "PA07, PA08+"
    controllers: 44
```

**EB Domain (116 controllers → 3 waves):**
```yaml
waves:
  - wave: 1
    prefix: "EB01-03"
    controllers: 47
  - wave: 2
    prefix: "EB04-06"
    controllers: 33
  - wave: 3
    prefix: "EB07-12+"
    controllers: 36
```

### 4.3 병합 전략

```yaml
merge_strategy:
  tool: "Python YAML parser"
  handle_format_variations: true  # 다양한 YAML 형식 지원
  deduplication: "by primary key (endpoint_path)"

  steps:
    - step: 1
      action: "Load all wave outputs"
    - step: 2
      action: "Parse with format tolerance"
    - step: 3
      action: "Deduplicate by primary key"
    - step: 4
      action: "Merge into single output"
    - step: 5
      action: "Validate count consistency"
```

---

## 5. Truncation Detection & Recovery

### 5.1 감지 규칙

| ID | Name | Rule | Action |
|----|------|------|--------|
| TC-001 | Summary-Data Consistency | `summary.total_count == len(data_array)` | Re-execute with sub-wave |
| TC-002 | Coverage Threshold | `coverage >= 95%` | Investigate and supplement |

### 5.2 감지 증상

| 증상 | 원인 | 진단 방법 |
|------|------|----------|
| Summary 정상, 데이터 절단 | Output Token Limit 초과 | `summary.count != actual` |
| YAML 파싱 에러 | 중간 절단으로 문법 오류 | YAML validator |
| Coverage 급락 | 대부분 데이터 손실 | Coverage < 50% |

### 5.3 복구 절차

```
┌─────────────────────────────────────────────────────────────┐
│                  RECOVERY PROCEDURE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. DETECT                                                  │
│     ┌──────────────────────────────────────┐               │
│     │ summary.count != actual_data_count   │               │
│     └──────────────────┬───────────────────┘               │
│                        │                                    │
│  2. ANALYZE            ▼                                    │
│     ┌──────────────────────────────────────┐               │
│     │ Identify truncation point            │               │
│     │ Calculate missing data range         │               │
│     └──────────────────┬───────────────────┘               │
│                        │                                    │
│  3. RE-DIVIDE          ▼                                    │
│     ┌──────────────────────────────────────┐               │
│     │ Split into smaller sub-waves         │               │
│     │ Target: 30-50 controllers per wave   │               │
│     └──────────────────┬───────────────────┘               │
│                        │                                    │
│  4. RE-EXECUTE         ▼                                    │
│     ┌──────────────────────────────────────┐               │
│     │ Execute each sub-wave independently  │               │
│     └──────────────────┬───────────────────┘               │
│                        │                                    │
│  5. MERGE              ▼                                    │
│     ┌──────────────────────────────────────┐               │
│     │ Merge results (deduplicate)          │               │
│     │ Validate: summary.count == actual    │               │
│     └──────────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 검증된 결과

### 6.1 개선 효과

| Domain | Before | After | Improvement |
|--------|--------|-------|-------------|
| PA | 34 endpoints (1.7%) | 1,225 endpoints (61%) | **36x** |
| EB | 13 endpoints (2.1%) | 402 endpoints (65%) | **31x** |
| BS | 71 (100%) | 71 (100%) | Already optimal |
| QM | 57 (100%) | 57 (100%) | Already optimal |

### 6.2 Key Learnings

1. **Token Limit is Primary Cause**: Timeout (120min) 아님, Output token limit (~25-30K)
2. **Size Threshold**: 100 controllers 또는 200 endpoints 기준
3. **Wave Size**: 30-50 controllers가 안전한 범위
4. **Format Variations**: Sub-wave 병합 시 다양한 YAML 형식 처리 필요
5. **Proactive Division**: 사후 감지보다 사전 분할이 효율적

---

## 7. Applicable Skills

이 전략이 적용되는 스킬 목록:

### 7.1 Output Token Limit 대응 (Sub-wave Division)

| Skill | Stage | Context 위험도 |
|-------|-------|---------------|
| `s1-02-discovery-miplatform-protocol` | S1 | High |
| `s1-03-discovery-deep-analysis` | S1 | High |
| `s4-01-generation-domain-batch` | S4 | High |

### 7.2 Read Tool File Limit 대응 (File Size Handling) - v1.1.0

| Skill | Stage | 유형 | 대상 파일 | 잠재적 크기 |
|-------|-------|------|----------|------------|
| `s2-01-validation-source-inventory` | S2 | Output | source-inventory.yaml | 2.2MB |
| `s2-02-validation-structural-comparison` | S2 | Input | source-inventory.yaml | 2.2MB |
| `s2-03-validation-gap-analysis` | S2 | Input | comparison-report.yaml | 500KB+ |
| `s2-04-validation-spec-completion` | S2 | Input | gap-analysis.yaml | 300KB+ |
| `s1-02-discovery-miplatform-protocol` | S1 | Input/Output | feature-inventory.yaml, miplatform-protocol.yaml | 300KB+ |
| `s1-03-discovery-deep-analysis` | S1 | Input | feature-inventory.yaml, miplatform-protocol.yaml | 300KB+ |

---

## 8. Checklist

### 8.1 작업 시작 전

- [ ] 대상 크기 평가 (controllers/endpoints 수)
- [ ] Threshold 초과 여부 확인 (>100 controllers OR >200 endpoints)
- [ ] Threshold 초과 시 Sub-wave 계획 수립
- [ ] Wave당 30-50 controllers 목표로 분할

### 8.2 작업 진행 중

- [ ] Lean format으로 출력
- [ ] Wave별 독립 실행
- [ ] 각 wave 완료 시 즉시 저장

### 8.3 작업 완료 후

- [ ] Summary-Data Consistency 검증 (`summary.count == actual`)
- [ ] Coverage Threshold 확인 (≥95%)
- [ ] 불일치 감지 시 Sub-wave 재실행
- [ ] 최종 병합 및 deduplication

---

## 9. Quick Reference

### 9.1 Decision Flow

```
대상 크기 평가
    │
    ├─ controllers ≤ 100 AND endpoints ≤ 200
    │   └─→ Single Pass 실행
    │
    └─ controllers > 100 OR endpoints > 200
        └─→ Sub-wave Division
            │
            ├─ 30-50 controllers per wave로 분할
            ├─ Wave별 독립 실행
            ├─ 결과 병합 (deduplicate)
            └─ 검증: summary.count == actual
```

### 9.2 Thresholds Summary

| Metric | Threshold | Action |
|--------|-----------|--------|
| Controllers | >100 | Sub-wave division |
| Endpoints | >200 | Sub-wave division |
| Wave size | 30-50 | Safe range |
| Coverage | <95% | Investigate |

---

**Previous**: [05-orchestration-patterns.md](05-orchestration-patterns.md)
**Next**: [templates/](templates/)
