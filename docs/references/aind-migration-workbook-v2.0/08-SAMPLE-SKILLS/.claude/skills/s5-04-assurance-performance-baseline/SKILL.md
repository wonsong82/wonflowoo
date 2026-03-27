---
name: s5-04-assurance-performance-baseline
description: Use when establishing performance baselines for generated code, detecting N+1 query patterns, or analyzing potential performance issues before deployment (project)
---

# Performance Baseline

> **Skill ID**: S5-04
> **Skill Type**: Analysis (Limited Parallel)
> **Stage**: 5 - Assurance
> **Phase**: 5.4 - Performance Baseline
> **Parallelization**: Limited (max 3 sessions, batch 2 domains)
> **Gate Type**: Non-Blocking (Warning Only)

## 1. Overview

### 1.1 Purpose

생성된 코드의 **성능 기준선을 수립**하고 **잠재적 성능 이슈(N+1 쿼리 등)를 탐지**합니다. 이 Phase는 **Non-Blocking Gate**로, 심각한 이슈가 있어도 경고만 발생하고 다음 단계로 진행할 수 있습니다.

**분석 대상:**
- N+1 Query Pattern 탐지
- 대량 데이터 조회 패턴
- 트랜잭션 범위 분석
- Connection Pool 사용 패턴

**성능 지표:**
- 예상 응답 시간 (Estimated Response Time)
- 쿼리 복잡도 (Query Complexity)
- 메모리 사용 패턴 (Memory Usage Pattern)

### 1.2 Scope

**In Scope:**
- Static Analysis 기반 N+1 탐지
- MyBatis 쿼리 복잡도 분석
- Loop 내 DB 호출 탐지
- 대량 조회 패턴 분석

**Out of Scope:**
- 실제 부하 테스트 (-> 별도 Phase)
- 프로파일링 (-> Runtime Analysis)
- 인프라 성능 (-> DevOps)

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Static Analysis** | 코드 분석 기반 탐지 | 런타임 없이 조기 발견 |
| **Non-Blocking** | 경고만 발생 | 배포 지연 방지 |
| **Pattern-Based** | 알려진 안티패턴 탐지 | 효율적 분석 |
| **Documentative** | Technical Debt 기록 | 향후 개선 추적 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S5-04는 성능 기준을 설정하며, **N+1 쿼리 탐지 및 SQL 복잡도 분석이 핵심 검증 항목**

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s5-02-assurance-functional-validation` | 기능 검증 완료 필요 |
| `s4-04-generation-test-generation` | 테스트 코드 참조 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s5-05-assurance-quality-gate` | 성능 분석 결과 포함 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S5-02"
    skill_name: "s5-02-assurance-functional-validation"
    status: "completed"
    artifacts:
      - "validation-summary.yaml"

  - skill_id: "S4-04"
    skill_name: "s4-04-generation-test-generation"
    status: "completed"
    artifacts:
      - "test-progress.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| generated_project | directory | `next-hallain/` | Gradle Project | Yes |
| functional_validation | directory | `work/specs/stage5-outputs/phase2/` | YAML | Yes |
| mybatis_mappers | directory | `next-hallain/src/main/resources/mapper/` | XML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Grep | - | 패턴 검색 |
| Read | - | 코드 분석 |
| Bash | - | 빌드 명령 |

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: parallel
  unit: domain
  parallelization:
    enabled: true
    max_sessions: 3
    batch_size: 2
    session_timeout_minutes: 180
    retry_on_failure: 2

task:
  naming_pattern: "PERF-{DOMAIN}"
  granularity: domain
```

### 3.2 Performance Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE ANALYSIS PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────────┐     ┌──────────────────┐     ┌──────────────┐   │
│   │  N+1 Query       │     │  Query           │     │  Transaction │   │
│   │  Detection       │     │  Complexity      │     │  Analysis    │   │
│   └────────┬─────────┘     └────────┬─────────┘     └──────┬───────┘   │
│            │                         │                      │           │
│            ▼                         ▼                      ▼           │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Issue Aggregation                             │   │
│   └────────────────────────────────┬────────────────────────────────┘   │
│                                     │                                   │
│                                     ▼                                   │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Report Generation                             │   │
│   │              (Non-Blocking - Warning Only)                       │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 N+1 Query Detection

#### 3.3.1 Detection Patterns

```yaml
n_plus_1_patterns:
  pattern_1:
    name: "Loop-based Query"
    description: "For/While 루프 내에서 Mapper 호출"
    detection:
      - "for (.*) {" + "mapper\\.select"
      - "while (.*) {" + "mapper\\.select"
      - ".forEach(" + "mapper\\.select"
      - ".stream()" + ".map(" + "mapper\\.select"
    severity: "high"

  pattern_2:
    name: "Lazy Loading in List"
    description: "리스트 순회 시 연관 엔티티 조회"
    detection:
      - "getList().stream().map(e -> e.getRelated())"
    severity: "medium"

  pattern_3:
    name: "Multiple Single Queries"
    description: "단건 조회 반복"
    detection:
      - "selectById" in loop
      - "findOne" in loop
    severity: "high"
```

#### 3.3.2 N+1 Analysis Output

```yaml
n_plus_1_analysis:
  total_detections: 15
  by_severity:
    high: 5
    medium: 8
    low: 2

  detections:
    - id: "N1-001"
      file: "PA01001Service.java"
      line: 45
      method: "getListWithDetails"
      pattern: "Loop-based Query"
      code_snippet: |
        for (PA01001Entity item : list) {
            item.setDetails(detailMapper.selectByParentId(item.getId()));
        }
      severity: "high"
      recommendation: "Use JOIN query or batch select"
      estimated_queries: "N+1 (N = list size)"

    - id: "N1-002"
      file: "MM02001Service.java"
      line: 78
      pattern: "Stream map with query"
      severity: "medium"
      recommendation: "Prefetch related data"
```

### 3.4 Query Complexity Analysis

#### 3.4.1 Complexity Metrics

```yaml
query_complexity:
  metrics:
    - name: "join_count"
      description: "JOIN 절 개수"
      threshold:
        low: 0-2
        medium: 3-5
        high: "> 5"

    - name: "subquery_count"
      description: "서브쿼리 개수"
      threshold:
        low: 0
        medium: 1-2
        high: "> 2"

    - name: "condition_count"
      description: "WHERE 조건 개수"
      threshold:
        low: 0-5
        medium: 6-10
        high: "> 10"

    - name: "has_full_scan"
      description: "Full table scan 가능성"
      detection: "No WHERE clause on large table"
```

#### 3.4.2 Query Analysis Output

```yaml
query_analysis:
  total_queries: 500
  by_complexity:
    simple: 350
    moderate: 120
    complex: 30

  complex_queries:
    - id: "QRY-001"
      mapper: "PA03001Mapper"
      query_id: "selectComplexReport"
      complexity: "high"
      metrics:
        join_count: 7
        subquery_count: 2
        condition_count: 15
      recommendation: "Consider query optimization or caching"

    - id: "QRY-002"
      mapper: "SC02001Mapper"
      query_id: "selectAllWithoutWhere"
      complexity: "warning"
      issue: "Potential full table scan"
      recommendation: "Add pagination or WHERE clause"
```

### 3.5 SQL Complexity Deep Analysis (QUERY-FIRST 강화)

> **QUERY-FIRST 원칙에 따른 SQL 심층 분석**
> SQL 보존 100% 필수이므로, 성능 문제가 있더라도 SQL 변경이 아닌 인프라/캐싱으로 대응

#### 3.5.1 MyBatis Mapper XML 분석

```yaml
mybatis_sql_analysis:
  scan_target: "src/main/resources/mapper/**/*.xml"

  metrics:
    - name: "full_table_scan_risk"
      description: "Full table scan 위험도"
      detection:
        - "SELECT without WHERE clause"
        - "WHERE clause with only non-indexed columns"
        - "SELECT * from large table (> 10000 rows estimated)"
      severity: "warning"

    - name: "missing_index_hint"
      description: "인덱스 누락 가능성"
      detection:
        - "WHERE clause on non-PK columns without index hint"
        - "ORDER BY on non-indexed columns"
        - "JOIN on non-indexed foreign keys"
      severity: "info"

    - name: "complex_join"
      description: "복잡한 JOIN 패턴"
      detection:
        - "JOIN count >= 4"
        - "Self-join patterns"
        - "Cross-database joins (if applicable)"
      severity: "warning"

    - name: "dynamic_sql_risk"
      description: "동적 SQL 성능 위험"
      detection:
        - "<if> or <choose> without proper indexing consideration"
        - "Dynamic ORDER BY (SQL injection risk + performance)"
      severity: "info"
```

#### 3.5.2 SQL Pattern Detection Rules

```yaml
sql_pattern_rules:
  full_table_scan:
    patterns:
      - pattern: "SELECT .* FROM \\w+ WHERE 1=1$"
        description: "조건 없는 전체 조회"
        severity: "high"
        recommendation: "페이징 또는 필수 조건 추가 권장"

      - pattern: "SELECT \\* FROM"
        description: "SELECT * 사용"
        severity: "low"
        recommendation: "필요한 컬럼만 명시 권장"

      - pattern: "SELECT .* FROM \\w+\\s*$"
        description: "WHERE 절 없는 조회"
        severity: "high"
        recommendation: "조건 절 또는 LIMIT 추가 필요"

  missing_index:
    patterns:
      - pattern: "WHERE .*(LIKE '%|LIKE concat)"
        description: "LIKE 선행 와일드카드 (인덱스 무효화)"
        severity: "medium"
        recommendation: "Full-text search 또는 별도 검색 엔진 고려"

      - pattern: "ORDER BY .*(,.*){3,}"
        description: "다중 컬럼 정렬"
        severity: "low"
        recommendation: "복합 인덱스 확인 권장"

  complex_query:
    patterns:
      - pattern: "(LEFT|RIGHT|INNER|OUTER)\\s+JOIN.*\\1.*\\1.*\\1"
        description: "4개 이상 JOIN"
        severity: "medium"
        recommendation: "쿼리 분할 또는 뷰/인덱스 최적화 검토"

      - pattern: "SELECT.*\\(SELECT.*\\(SELECT"
        description: "중첩 서브쿼리 (depth >= 2)"
        severity: "high"
        recommendation: "서브쿼리를 JOIN으로 변환 검토"
```

#### 3.5.3 SQL Analysis Output

```yaml
sql_deep_analysis:
  summary:
    total_sql_statements: 500
    analyzed: 500
    issues_found: 45
    by_severity:
      high: 5
      medium: 15
      low: 25

  findings:
    # Full Table Scan Risks
    - id: "SQL-FTS-001"
      mapper: "PA03001Mapper.xml"
      query_id: "selectAllProducts"
      issue_type: "full_table_scan"
      sql_snippet: "SELECT * FROM TB_PRODUCT WHERE 1=1"
      severity: "high"
      table_estimated_size: "50,000+ rows"
      recommendation: "페이징 필수 적용"

    # Missing Index Hints
    - id: "SQL-IDX-001"
      mapper: "SC02001Mapper.xml"
      query_id: "selectByDateRange"
      issue_type: "missing_index"
      sql_snippet: "WHERE CREATE_DT BETWEEN ... ORDER BY UPDATE_DT"
      severity: "medium"
      columns_without_index: ["CREATE_DT", "UPDATE_DT"]
      recommendation: "복합 인덱스 (CREATE_DT, UPDATE_DT) 확인"

    # Complex Joins
    - id: "SQL-JOIN-001"
      mapper: "MM01001Mapper.xml"
      query_id: "selectInventoryReport"
      issue_type: "complex_join"
      severity: "medium"
      join_count: 6
      tables: ["TB_INVENTORY", "TB_PRODUCT", "TB_WAREHOUSE", "TB_SUPPLIER", "TB_ORDER", "TB_SHIPMENT"]
      recommendation: "리포트 전용 뷰 또는 캐싱 레이어 검토"

  # QUERY-FIRST 준수 확인
  query_first_compliance:
    status: "COMPLIANT"  # COMPLIANT/NON_COMPLIANT
    note: "모든 SQL은 원본 유지됨. 성능 이슈는 인프라 레벨에서 대응 권장."
    optimization_recommendations:
      - type: "infrastructure"
        items:
          - "Redis 캐시 레이어 추가 (자주 조회되는 마스터 데이터)"
          - "Read Replica 구성 (리포트 쿼리 분산)"
      - type: "application"
        items:
          - "Spring @Cacheable 적용 (코드성 데이터)"
          - "배치 처리 도입 (대량 조회 최적화)"
```

### 3.6 Transaction Analysis

```yaml
transaction_analysis:
  patterns:
    - name: "Long Transaction"
      description: "과도하게 긴 트랜잭션"
      detection: "@Transactional on method with multiple service calls"
      threshold: "> 5 operations"

    - name: "Missing Transaction"
      description: "트랜잭션 누락"
      detection: "Multiple writes without @Transactional"

    - name: "Read-Only Missing"
      description: "조회에 readOnly 누락"
      detection: "SELECT-only method without readOnly=true"
      recommendation: "Performance optimization"

  findings:
    - id: "TX-001"
      file: "PA05001Service.java"
      method: "processComplexBatch"
      issue: "Long transaction (8 operations)"
      severity: "medium"
      recommendation: "Consider breaking into smaller transactions"
```

### 3.6 Process Steps

#### Step 1: Scan Service Layer

**Description:** Service 클래스의 성능 관련 패턴 분석

**Sub-steps:**
1. Service 클래스 목록 수집
2. Mapper 호출 패턴 분석
3. 루프 내 DB 호출 탐지
4. 트랜잭션 어노테이션 분석

**Scan Targets:**
```yaml
scan_targets:
  service_files:
    pattern: "next-hallain/src/main/java/**/service/*.java"
    analysis:
      - "mapper_calls_in_loop"
      - "transaction_scope"
      - "batch_operations"
```

**Validation:** Service 스캔 완료

---

#### Step 2: Analyze MyBatis Queries

**Description:** MyBatis XML 쿼리의 복잡도 분석

**Sub-steps:**
1. Mapper XML 파일 파싱
2. 쿼리 복잡도 계산
3. 인덱스 힌트 확인
4. Full scan 가능성 탐지

**Query Analysis:**
```yaml
mybatis_analysis:
  xml_files: "next-hallain/src/main/resources/mapper/**/*.xml"
  extract:
    - select_statements
    - join_clauses
    - where_conditions
    - subqueries
```

**Validation:** 쿼리 분석 완료

---

#### Step 3: Detect N+1 Patterns

**Description:** N+1 쿼리 패턴 탐지

**Sub-steps:**
1. Loop + Mapper 패턴 검색
2. Stream + Query 패턴 검색
3. 연관 로딩 패턴 분석
4. 심각도 분류

**Detection Rules:**
```bash
# Pattern: for loop with mapper call
grep -n "for.*{" service/*.java | xargs grep -l "mapper\."

# Pattern: stream with query
grep -n "stream().*map.*mapper" service/*.java
```

**Validation:** N+1 패턴 탐지 완료

---

#### Step 4: Calculate Performance Estimates

**Description:** 성능 예측값 계산

**Sub-steps:**
1. 쿼리별 복잡도 점수 계산
2. N+1 영향도 계산
3. 전체 성능 위험도 산정

**Estimation Formula:**
```python
# Query complexity score
complexity_score = (
    join_count * 1.5 +
    subquery_count * 2.0 +
    condition_count * 0.5
)

# N+1 impact (for N records)
n_plus_1_impact = "O(N)" if n_plus_1_detected else "O(1)"

# Overall risk
risk_score = sum(complexity_scores) + n_plus_1_count * 10
```

**Validation:** 예측값 계산 완료

---

#### Step 5: Generate Report

**Description:** 성능 분석 리포트 생성

**Sub-steps:**
1. 분석 결과 집계
2. 권장사항 생성
3. Technical Debt 기록
4. 리포트 파일 생성

**Validation:** 리포트 생성 완료

---

#### Step 7: Schema Validation

**Description:** 생성된 performance-baseline.yaml이 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | root | metadata, summary, n_plus_1_analysis, query_complexity 필수 키 존재 | ERROR | Yes |
| V002 | metadata.generated_by | 정확히 "s5-04-assurance-performance-baseline" | ERROR | Yes |
| V003 | metadata.gate_type | 정확히 "non_blocking" | ERROR | Yes |
| V004 | summary.result | enum: PASS, WARNING, ALERT (FAIL 없음 - Non-blocking) | ERROR | Yes |
| V005 | n_plus_1_analysis.detections[].severity | enum: high, medium, low | ERROR | Yes |
| V006 | recommendations[].priority | enum: high, medium, low | ERROR | Yes |
| V007 | summary.risk_score | 범위: 0-100 | ERROR | Yes |
| V008 | n_plus_1_analysis | by_severity 합계 == total_detections | WARNING | No |
| V009 | query_complexity | complexity 합계 == total_queries | WARNING | No |
| V010 | result | ALERT 시 high severity > 10 | WARNING | No |

**Sub-steps:**
1. performance-baseline.yaml 스키마 검증
2. N+1 분석 결과 검증
3. Non-blocking Gate 특성 검증
4. 오류 발생 시 validation-errors.yaml 생성

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 재분석 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.7 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | N+1 High > 0 | 경고 발생 | 계속 |
| DP-2 | Complex Query > 10 | 권장사항 추가 | 계속 |
| DP-3 | 분석 완료 | 리포트 생성 | 재시도 |
| DP-4 | 리포트 완료 | Gate 통과 (Warning) | ERROR |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage5-outputs/phase4/"

  artifacts:
    - name: "performance-analysis.yaml"
      required: true
    - name: "performance-recommendations.md"
      required: false
    - name: "by-domain/"
      required: true
```

### 4.2 Output Files Summary

```
work/specs/stage5-outputs/phase4/
├── performance-analysis.yaml      # 전체 분석 결과
├── performance-recommendations.md # 권장사항 문서
└── by-domain/
    ├── PA-performance.yaml
    ├── MM-performance.yaml
    └── ...
```

### 4.3 Output Schema

```yaml
# performance-analysis.yaml
metadata:
  generated_by: "s5-04-assurance-performance-baseline"
  generated_at: "${TIMESTAMP}"
  analysis_type: "static"

summary:
  domains_analyzed: 12
  total_services: 200
  total_queries: 500

  n_plus_1:
    total_detections: 15
    high_severity: 5
    medium_severity: 8
    low_severity: 2

  query_complexity:
    simple: 350
    moderate: 120
    complex: 30

  transaction_issues:
    long_transactions: 8
    missing_transactions: 3
    missing_readonly: 45

  risk_level: "MEDIUM"  # LOW | MEDIUM | HIGH

n_plus_1_detections:
  - id: "N1-001"
    domain: "PA"
    service: "PA01001Service"
    method: "getListWithDetails"
    line: 45
    severity: "high"
    pattern: "Loop-based Query"
    estimated_impact: "N+1 queries (N = list.size())"
    recommendation: |
      Replace loop-based query with batch select:
      - Use IN clause: mapper.selectByIds(ids)
      - Or use JOIN in single query

complex_queries:
  - id: "QRY-001"
    domain: "PA"
    mapper: "PA03001Mapper"
    query_id: "selectComplexReport"
    file: "PA03001Mapper.xml"
    line: 150
    complexity_score: 12.5
    metrics:
      joins: 7
      subqueries: 2
      conditions: 15
    recommendation: "Consider query optimization"

transaction_findings:
  - id: "TX-001"
    domain: "PA"
    service: "PA05001Service"
    method: "processComplexBatch"
    issue: "Long transaction"
    operations_count: 8
    recommendation: "Break into smaller transactions"

performance_baselines:
  by_domain:
    PA:
      services: 45
      avg_complexity: 5.2
      n_plus_1_count: 5
      risk: "MEDIUM"
    MM:
      services: 20
      avg_complexity: 4.8
      n_plus_1_count: 3
      risk: "LOW"

technical_debt:
  items:
    - id: "TD-PERF-001"
      category: "performance"
      description: "N+1 queries in PA domain"
      severity: "medium"
      affected_files: 5
      effort_estimate: "2-3 days"
      priority: "P2"

recommendations:
  immediate:
    - "Fix high-severity N+1 patterns (5 occurrences)"
  short_term:
    - "Add readOnly=true to query-only transactions"
    - "Review complex queries for optimization"
  long_term:
    - "Implement query result caching"
    - "Add database indexes for frequent queries"

gate_result:
  status: "WARNING"  # PASS (no issues) | WARNING (issues found) | INFO
  blocking: false
  message: "Performance issues detected but not blocking"
  action: "Create technical debt tickets"
```

### 4.4 Recommendations Document

```markdown
# performance-recommendations.md

## Performance Analysis Summary

**Analysis Date**: 2026-01-07
**Domains Analyzed**: 12

### Critical Findings

#### 1. N+1 Query Patterns (5 High Severity)

| Service | Method | Impact | Fix |
|---------|--------|--------|-----|
| PA01001Service | getListWithDetails | O(N) queries | Use JOIN |
| MM02001Service | fetchWithChildren | O(N) queries | Batch select |

#### 2. Complex Queries (30 detected)

Queries with complexity score > 10 should be reviewed for optimization.

### Recommendations by Priority

#### P0 - Immediate (Before Production)
- None (no blocking issues)

#### P1 - High Priority (Within 1 sprint)
1. Fix high-severity N+1 patterns
2. Add pagination to unbounded queries

#### P2 - Medium Priority (Within 1 month)
1. Optimize complex queries
2. Add missing readOnly annotations

#### P3 - Low Priority (Backlog)
1. Implement query caching
2. Database index review
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| all_domains_analyzed | structural | 100% analyzed | ERROR | Yes |
| n_plus_1_documented | metric | All patterns logged | WARNING | No |
| baselines_recorded | metric | All services baselined | WARNING | No |
| high_severity_limited | metric | < 10 high severity | WARNING | No |

### 5.2 Gate Criteria

```yaml
gate_criteria:
  id: "G5.4"
  name: "Performance Baseline Gate"
  threshold: 70
  blocking: false  # Non-blocking gate

  metrics:
    - metric: "all_domains_analyzed"
      weight: 0.5
      target: "100%"
      blocking: true  # Only structural check is blocking

    - metric: "n_plus_1_documented"
      weight: 0.25
      target: "All patterns documented"
      blocking: false

    - metric: "high_severity_limited"
      weight: 0.25
      target: "< 10 high severity issues"
      blocking: false

  on_pass:
    auto_commit: true
    message: "feat(S5-P5.4): Performance baseline established"

  on_fail:
    action: "document_and_continue"
    create_tech_debt: true
    message: "Performance issues logged as technical debt"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Parse error | XML 파싱 실패 | 잘못된 XML | 파일 확인 | Yes |
| Pattern miss | 패턴 누락 | 새로운 코드 스타일 | 패턴 추가 | No |
| Timeout | 분석 시간 초과 | 대용량 코드 | 배치 축소 | Yes |

### 6.2 False Positive Handling

```yaml
false_positive_handling:
  whitelist:
    - pattern: "mapper call in intentional loop"
      condition: "// @SuppressWarnings(\"n-plus-1\")"
      action: "skip"

    - pattern: "complex query for reporting"
      condition: "query_id contains 'Report'"
      action: "lower severity"
```

### 6.3 Technical Debt Recording

| Severity | Action | Ticket Priority |
|----------|--------|-----------------|
| High | Create P1 ticket | 즉시 |
| Medium | Create P2 ticket | 스프린트 내 |
| Low | Backlog | 향후 |

---

## 7. Examples

### 7.1 N+1 Detection Example

**Problematic Code:**
```java
public List<PA01001Response> getListWithDetails(PA01001SearchRequest request) {
    List<PA01001Entity> list = mapper.selectList(request);

    // N+1 Pattern: Loop with individual queries
    for (PA01001Entity item : list) {
        List<PA01001Detail> details = detailMapper.selectByParentId(item.getId());
        item.setDetails(details);
    }

    return list.stream()
        .map(PA01001Response::from)
        .collect(Collectors.toList());
}
```

**Detection Output:**
```yaml
detection:
  id: "N1-001"
  severity: "high"
  pattern: "Loop-based Query"
  line: 5
  impact: "N+1 queries where N = list.size()"
```

**Recommended Fix:**
```java
public List<PA01001Response> getListWithDetails(PA01001SearchRequest request) {
    List<PA01001Entity> list = mapper.selectList(request);

    // Batch query: single query with IN clause
    List<String> ids = list.stream()
        .map(PA01001Entity::getId)
        .collect(Collectors.toList());

    Map<String, List<PA01001Detail>> detailsMap =
        detailMapper.selectByParentIds(ids).stream()
            .collect(Collectors.groupingBy(PA01001Detail::getParentId));

    list.forEach(item ->
        item.setDetails(detailsMap.getOrDefault(item.getId(), List.of()))
    );

    return list.stream()
        .map(PA01001Response::from)
        .collect(Collectors.toList());
}
```

### 7.2 Complex Query Example

**Complex Query:**
```xml
<select id="selectComplexReport" resultType="ReportDTO">
    SELECT
        a.col1, b.col2, c.col3, d.col4,
        (SELECT COUNT(*) FROM table_e WHERE e.fk = a.pk) as cnt
    FROM table_a a
    INNER JOIN table_b b ON a.fk1 = b.pk
    INNER JOIN table_c c ON b.fk2 = c.pk
    LEFT JOIN table_d d ON c.fk3 = d.pk
    LEFT JOIN table_f f ON d.fk4 = f.pk
    LEFT JOIN table_g g ON f.fk5 = g.pk
    LEFT JOIN table_h h ON g.fk6 = h.pk
    WHERE a.status = #{status}
      AND b.date BETWEEN #{startDate} AND #{endDate}
      AND c.type IN
        <foreach collection="types" item="type" open="(" separator="," close=")">
            #{type}
        </foreach>
    ORDER BY a.created_at DESC
</select>
```

**Analysis Output:**
```yaml
query_analysis:
  id: "QRY-001"
  complexity_score: 15.5
  metrics:
    joins: 7
    subqueries: 1
    conditions: 4
  recommendation: |
    - Consider splitting into multiple queries
    - Add appropriate indexes
    - Consider materialized view for reporting
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| 빈 프로젝트 | No services | 분석 스킵, INFO |
| Stored Procedure | SP 호출만 | SP 분석 제외 |
| Native Query | @Query 어노테이션 | 별도 분석 |
| Batch Operation | 대량 처리 | Batch 패턴 인식 |

---

## 8. Runtime Profiling Integration

### 8.1 Hybrid Analysis Architecture

```yaml
hybrid_analysis:
  phases:
    phase_1_static:
      name: "Static Analysis"
      timing: "Build time"
      tools: ["Pattern-based N+1 detection", "Query complexity scoring"]
      output: "performance-static.yaml"

    phase_2_runtime:
      name: "Runtime Profiling"
      timing: "Test execution time"
      tools: ["P6Spy", "Micrometer", "Custom interceptors"]
      output: "performance-runtime.yaml"

    phase_3_comparison:
      name: "Analysis Comparison"
      process: ["Compare predictions vs results", "Calibrate rules"]
      output: "performance-comparison.yaml"
```

### 8.2 Runtime Profiling Configuration

```yaml
runtime_profiling:
  p6spy:
    enabled: true
    config:
      log_format: "executionTime:%(executionTime)ms | sql:%(sqlSingleLine)"
      slow_query_threshold_ms: 1000
    output:
      file: "logs/sql-profiling.log"
      format: "json"
    metrics:
      - query_count
      - total_execution_time
      - avg_execution_time
      - slow_query_count

  micrometer:
    enabled: true
    metrics:
      - name: "sql.query.count"
        type: "counter"
        tags: ["query_type", "mapper", "method"]

      - name: "sql.query.duration"
        type: "timer"
        tags: ["query_type", "mapper", "method"]
        percentiles: [0.5, 0.9, 0.95, 0.99]

      - name: "n_plus_1.detected"
        type: "counter"
        tags: ["service", "method"]

  n_plus_1_detector:
    enabled: true
    request_scope: true
    threshold: 5  # Alert if same query > 5 times per request
```

### 8.3 SQL Interceptor Implementation

```java
@Component
public class SqlProfilingInterceptor implements Interceptor {

    private static final ThreadLocal<RequestSqlStats> requestStats =
        ThreadLocal.withInitial(RequestSqlStats::new);

    private final MeterRegistry meterRegistry;

    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        MappedStatement ms = (MappedStatement) invocation.getArgs()[0];
        String mapperId = ms.getId();
        String queryType = ms.getSqlCommandType().name();

        long startTime = System.currentTimeMillis();
        Object result = invocation.proceed();
        long duration = System.currentTimeMillis() - startTime;

        recordMetrics(mapperId, queryType, duration);
        detectNPlus1(mapperId);

        return result;
    }

    private void recordMetrics(String mapperId, String queryType, long duration) {
        Timer.builder("sql.query.duration")
            .tag("mapper", extractMapperName(mapperId))
            .tag("query_type", queryType)
            .register(meterRegistry)
            .record(duration, TimeUnit.MILLISECONDS);

        requestStats.get().recordQuery(mapperId, duration);
    }

    private void detectNPlus1(String mapperId) {
        int count = requestStats.get().getQueryCount(mapperId);
        if (count > 5) {
            log.warn("N+1 detected: {} executed {} times", mapperId, count);
            Counter.builder("n_plus_1.detected")
                .tag("mapper", extractMapperName(mapperId))
                .register(meterRegistry)
                .increment();
        }
    }

    public static void clearRequestStats() {
        requestStats.remove();
    }
}

public class RequestSqlStats {
    private final Map<String, QueryStats> queryStatsMap = new ConcurrentHashMap<>();

    public void recordQuery(String mapperId, long duration) {
        queryStatsMap.computeIfAbsent(mapperId, k -> new QueryStats()).record(duration);
    }

    public int getQueryCount(String mapperId) {
        QueryStats stats = queryStatsMap.get(mapperId);
        return stats != null ? stats.getCount() : 0;
    }
}
```

### 8.4 Performance Test Configuration

```java
@SpringBootTest
@ActiveProfiles("performance-test")
public class PerformanceProfilingTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private MeterRegistry meterRegistry;

    @Test
    void profilePA01001List() {
        PA01001SearchRequest request = PA01001SearchRequest.builder()
            .siteCd("S01")
            .startDate(LocalDate.of(2026, 1, 1))
            .build();

        // Warm-up
        for (int i = 0; i < 3; i++) {
            restTemplate.postForEntity("/api/pa/pa01001/list", request, ApiResponse.class);
        }

        // Profile
        List<Long> durations = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            long start = System.currentTimeMillis();
            restTemplate.postForEntity("/api/pa/pa01001/list", request, ApiResponse.class);
            durations.add(System.currentTimeMillis() - start);
        }

        // Collect metrics
        Timer sqlTimer = meterRegistry.find("sql.query.duration")
            .tag("mapper", "PA01001Mapper").timer();

        Counter nPlus1Counter = meterRegistry.find("n_plus_1.detected")
            .tag("mapper", "PA01001Mapper").counter();

        // Generate report
        PerformanceResult result = PerformanceResult.builder()
            .endpoint("/api/pa/pa01001/list")
            .avgResponseTime(durations.stream().mapToLong(Long::longValue).average().orElse(0))
            .sqlQueryCount(sqlTimer != null ? (long) sqlTimer.count() : 0)
            .nPlus1Detected(nPlus1Counter != null && nPlus1Counter.count() > 0)
            .build();
    }
}
```

### 8.5 Runtime Report Schema

```yaml
# performance-runtime.yaml
metadata:
  generated_by: "s5-04-runtime-profiler"
  generated_at: "${TIMESTAMP}"
  test_profile: "performance-test"

runtime_results:
  PA:
    PA01001:
      list:
        endpoint: "/api/pa/pa01001/list"
        samples: 10
        response_time:
          avg_ms: 45.5
          max_ms: 78
          p95_ms: 72
        sql_metrics:
          query_count: 2
          avg_duration_ms: 12.3
        n_plus_1:
          detected: false

      getListWithDetails:
        response_time:
          avg_ms: 450.5  # High - N+1
        sql_metrics:
          query_count: 101  # 1 + N
        n_plus_1:
          detected: true
          query_pattern: "PA01001DetailMapper.selectByParentId"
          occurrences: 100
          recommendation: "Use batch query with IN clause"

comparison_with_static:
  matches:
    - issue: "N1-001"
      static_prediction: "N+1 in getListWithDetails"
      runtime_confirmation: true

  false_positives:
    - issue: "N1-003"
      static_prediction: "Possible N+1 in processBatch"
      runtime_result: "Not detected - batch size limited"

  calibration_recommendations:
    - "Add pattern for dynamic foreach SQL"
    - "Lower loop detection threshold from 5 to 3"
```

### 8.6 APM Integration

```yaml
apm_integration:
  elastic_apm:
    enabled: true
    config:
      service_name: "hallain-migration"
      server_url: "http://apm-server:8200"
    agents:
      java:
        instrument: ["spring-web", "jdbc", "mybatis"]
    dashboards:
      - "Query execution time distribution"
      - "N+1 detection alerts"
      - "Slow queries (> 1s)"

  prometheus:
    enabled: true
    endpoint: "/actuator/prometheus"
    custom_metrics:
      - name: "migration_sql_query_duration_seconds"
        type: "histogram"
        buckets: [0.01, 0.05, 0.1, 0.5, 1, 5]
      - name: "migration_n_plus_1_total"
        type: "counter"

  grafana_dashboard:
    uid: "migration-perf"
    panels:
      - "SQL Query Count per Endpoint"
      - "N+1 Detection Rate"
      - "Response Time Percentiles"
```

---

## Version History

### v1.2.0 (2026-01-08)
- Step 7: Schema Validation 추가
- s5-04-performance-baseline.schema.yaml 스키마 참조
- 10개 검증 규칙 적용 (V001-V010)

### v1.1.0 (2026-01-07)
- **Runtime Profiling Integration 추가** (Section 8)
  - Hybrid analysis architecture (Static + Runtime)
  - P6Spy, Micrometer configuration
  - SQL interceptor implementation
  - Performance test configuration
  - Runtime report schema
  - APM integration (Elastic APM, Prometheus/Grafana)

### v1.0.0 (2026-01-07)
- Initial version
- N+1 query pattern detection
- Query complexity analysis
- Transaction scope analysis
- Non-blocking gate (warning only)
- Technical debt integration
