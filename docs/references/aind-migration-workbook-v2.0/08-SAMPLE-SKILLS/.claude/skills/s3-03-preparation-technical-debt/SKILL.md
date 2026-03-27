---
name: s3-03-preparation-technical-debt
description: Use when documenting technical debt patterns in legacy code, categorizing debt as preserve/remediate/defer, or preparing remediation recommendations before code generation (project)
---

# Technical Debt Analysis

> **Skill ID**: S3-03
> **Skill Type**: Analysis (기술 부채 패턴 문서화)
> **Stage**: 3 - Preparation
> **Phase**: 3.3a - Technical Debt Analysis

## 1. Overview

### 1.1 Purpose

Legacy 코드베이스의 **기술 부채(Technical Debt) 패턴**을 식별하고 문서화하여, 마이그레이션 시 **보존(Preserve)**, **개선(Remediate)**, **보류(Defer)** 전략을 결정합니다. 이 분석은 코드 생성 품질과 마이그레이션 범위 결정에 활용됩니다.

**분석 대상:**
- Code smell 패턴 (God class, Long method, etc.)
- Deprecated API 사용
- 하드코딩된 값 (credentials 제외, Wave 0에서 처리됨)
- 비표준 패턴 (프레임워크 미사용 직접 구현)
- 에러 처리 패턴 (empty catch, swallowed exceptions)

**추출 정보:**
- 도메인별 기술 부채 인벤토리
- 부채 유형별 분류 및 빈도
- 처리 전략 권장사항

### 1.2 Analysis Scope

| Aspect | In Scope | Out of Scope |
|--------|----------|--------------|
| Code Patterns | Code smells, anti-patterns | 비즈니스 로직 오류 |
| Security | Non-credential hardcoding | Credentials (Wave 0) |
| Architecture | Pattern violations | 기능 요구사항 |
| Blocking | Non-blocking (informational) | Gate failure 유발 안함 |

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Informational** | Gate를 blocking 하지 않음 | 부채는 점진적 해결 대상 |
| **Categorization** | 명확한 3분류 적용 | 처리 전략 결정 용이 |
| **Prioritization** | 영향도 기반 우선순위 | 제한된 리소스 최적 배분 |
| **Migration Focus** | 마이그레이션 관점 분석 | 운영 부채와 구분 |

### 1.4 Debt Categories

```yaml
debt_categories:
  preserve:
    description: "현행 유지 (변환만 수행)"
    criteria:
      - "비즈니스 로직에 영향 없음"
      - "마이그레이션 범위 외"
      - "수정 비용 > 유지 비용"
    examples:
      - "비효율적 but 동작하는 알고리즘"
      - "Legacy 코딩 스타일"

  remediate:
    description: "마이그레이션 시 개선"
    criteria:
      - "Spring Boot에서 더 나은 대안 존재"
      - "보안/성능에 직접 영향"
      - "개선 비용이 합리적"
    examples:
      - "Log4j 1.x 사용"
      - "직접 JDBC vs MyBatis"
      - "Empty catch blocks"

  defer:
    description: "마이그레이션 후 별도 개선"
    criteria:
      - "개선 필요하나 범위 외"
      - "기능 변경 수반"
      - "충분한 테스트 필요"
    examples:
      - "God class 분리"
      - "비즈니스 로직 리팩토링"
```

### 1.5 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S3-03은 기술 부채를 분석하며, **SQL 패턴 관련 부채(N+1, complex query)가 중요 항목으로 분류**

### 1.6 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s2-04-validation-spec-completion` | 완료된 Spec 및 소스 매핑 정보 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s3-04-preparation-architecture-design` | 부채 패턴 반영한 아키텍처 결정 |
| `s4-03-generation-domain-batch` | 개선 대상 자동 적용 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S2-04"
    skill_name: "s2-04-validation-spec-completion"
    dependency_type: "input"
    artifact: "completed specs with source mapping"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| completed_specs | directory | `work/specs/stage2-outputs/phase4/` | YAML | Yes |
| legacy_source | directory | `${LEGACY_CODEBASE}/src/main/java/` | Java | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Grep | - | 패턴 검색 |
| Read | - | 소스 파일 분석 |
| Glob | - | 파일 탐색 |

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: parallel
  unit: domain
  parallelization:
    max_parallel: 5
    timeout_minutes: 120
    retry_on_failure: 2
```

### 3.2 Analysis Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Scan        │────▶│ Classify     │────▶│ Categorize   │────▶│ Recommend    │
│  Patterns    │     │ Debt Type    │     │ Strategy     │     │ Actions      │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 3.3 Debt Detection Patterns

```yaml
debt_patterns:
  code_smells:
    god_class:
      pattern: "class with > 2000 LOC or > 50 methods"
      detection: "LOC count, method count"
      severity: "major"
      category: "defer"

    long_method:
      pattern: "method with > 100 LOC"
      detection: "method LOC count"
      severity: "minor"
      category: "defer"

    duplicate_code:
      pattern: "similar code blocks > 20 lines"
      detection: "code similarity analysis"
      severity: "minor"
      category: "defer"

  deprecated_apis:
    log4j_1x:
      pattern: "import org.apache.log4j"
      detection: "import statement"
      severity: "critical"
      category: "remediate"
      remediation: "SLF4J + Logback"

    java_util_date:
      pattern: "new Date(), Calendar.getInstance()"
      detection: "instantiation pattern"
      severity: "minor"
      category: "preserve"

  error_handling:
    empty_catch:
      pattern: "catch (Exception e) { }"
      detection: "empty catch block"
      severity: "major"
      category: "remediate"
      remediation: "적절한 로깅 또는 재throw"

    swallowed_exception:
      pattern: "catch with only logging, no action"
      detection: "catch block analysis"
      severity: "minor"
      category: "preserve"

  hardcoding:
    magic_numbers:
      pattern: "numeric literals in business logic"
      detection: "literal detection"
      severity: "minor"
      category: "preserve"

    string_literals:
      pattern: "repeated string literals"
      detection: "string literal count"
      severity: "minor"
      category: "preserve"

  architecture:
    direct_jdbc:
      pattern: "Connection, Statement, PreparedStatement 직접 사용"
      detection: "JDBC class usage"
      severity: "major"
      category: "remediate"
      remediation: "MyBatis 사용"

    service_in_controller:
      pattern: "DAO 직접 호출 in Controller"
      detection: "dependency analysis"
      severity: "major"
      category: "remediate"
      remediation: "Service 계층 추가"

    static_utility_abuse:
      pattern: "과도한 static method 사용"
      detection: "static method count"
      severity: "minor"
      category: "defer"
```

### 3.4 Process Steps

#### Step 1: Pattern Scanning

**Description:** 도메인별 기술 부채 패턴 스캔

**Sub-steps:**
1. 도메인 내 모든 Java 파일 탐색
2. 각 패턴별 정규식/분석 적용
3. 매칭 결과 수집
4. 위치 정보 기록 (파일, 라인)

**Scan Patterns:**
```yaml
scan_patterns:
  - name: "empty_catch"
    regex: "catch\\s*\\([^)]+\\)\\s*\\{\\s*\\}"
    file_types: ["*.java"]

  - name: "log4j_import"
    regex: "import\\s+org\\.apache\\.log4j"
    file_types: ["*.java"]

  - name: "direct_jdbc"
    regex: "(DriverManager\\.getConnection|new\\s+PreparedStatement)"
    file_types: ["*.java"]

  - name: "god_class"
    type: "metric"
    condition: "LOC > 2000 OR method_count > 50"
```

**Validation:** 모든 파일 스캔 완료

**Outputs:**
- Raw detection 결과

---

#### Step 2: Debt Classification

**Description:** 탐지된 패턴을 부채 유형별 분류

**Sub-steps:**
1. 패턴 → 부채 유형 매핑
2. 심각도(severity) 할당
3. 발생 빈도 집계
4. 영향 범위 분석

**Classification Example:**
```yaml
classification:
  - pattern: "empty_catch"
    debt_type: "error_handling"
    severity: "major"
    occurrences: 45
    affected_files: 23

  - pattern: "log4j_import"
    debt_type: "deprecated_api"
    severity: "critical"
    occurrences: 156
    affected_files: 78
```

**Validation:** 모든 탐지 항목 분류 완료

---

#### Step 3: Strategy Categorization

**Description:** 처리 전략 결정 (Preserve/Remediate/Defer)

**Sub-steps:**
1. 심각도 기반 초기 분류
2. 마이그레이션 영향도 평가
3. 수정 비용 추정
4. 최종 카테고리 결정

**Decision Matrix:**
| Severity | Migration Impact | Cost | Category |
|----------|------------------|------|----------|
| Critical | High | Any | Remediate |
| Major | High | Low | Remediate |
| Major | Low | High | Defer |
| Minor | Any | Any | Preserve |

**Validation:** 모든 항목에 카테고리 할당

---

#### Step 4: Recommendation Generation

**Description:** 개선 권장사항 생성

**Sub-steps:**
1. Remediate 항목에 구체적 개선 방안 제시
2. Defer 항목에 향후 개선 로드맵 제안
3. 우선순위 정렬
4. 리포트 생성

**Validation:** remediation-recommendations.yaml 생성

---

### 3.5 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | Critical 부채 존재 | remediate 우선 처리 | 일반 진행 |
| DP-2 | Wave 0 대상 | 이미 처리됨 표시 | 신규 분석 |
| DP-3 | 50+ occurrences | 자동화 개선 권장 | 수동 개선 가능 |
| DP-4 | Security 관련 | Human review 권장 | 자동 분류 |

---

### 3.6 Large File Handling

> **⚠️ Read Tool Limit**: Claude Code Read tool has 256KB file size limit. Files exceeding this limit must be split.

#### File Size Decision

| Condition | Action |
|-----------|--------|
| Expected output < 200KB | Single `technical-debt-inventory.yaml` file |
| Expected output >= 200KB | Domain-based split storage |

#### Size Estimation Formula

```yaml
estimated_size:
  formula: |
    (total_debt_items × 0.3KB) +
    (total_locations × 0.2KB) +
    (critical_items × 0.5KB) +
    (major_items × 0.4KB)
  threshold: 200KB
```

#### Split Storage Structure (When Large)

```
technical-debt-inventory/
├── _manifest.yaml           # metadata + summary + chunk list
├── critical-items.yaml      # critical_items 섹션
├── major-items.yaml         # major_items 섹션
├── inventory-pa.yaml        # PA 도메인 inventory
├── inventory-mm.yaml        # MM 도메인 inventory
├── inventory-sc.yaml        # SC 도메인 inventory
├── inventory-sm.yaml        # SM 도메인 inventory
├── inventory-pe.yaml        # PE 도메인 inventory
├── inventory-ea.yaml        # EA 도메인 inventory
├── inventory-sa.yaml        # SA 도메인 inventory
├── inventory-eb.yaml        # EB 도메인 inventory
├── inventory-qm.yaml        # QM 도메인 inventory
├── inventory-bs.yaml        # BS 도메인 inventory
├── inventory-cm.yaml        # CM 도메인 inventory
└── inventory-benitware.yaml # benitware 도메인 inventory
```

#### Manifest Schema

```yaml
# technical-debt-inventory/_manifest.yaml
metadata:
  generated_by: "s3-03-preparation-technical-debt"
  generated_at: "2026-01-07T14:00:00Z"
  format: "chunked"
  total_domains: 12

summary:
  total_debt_items: 1234
  by_severity: { critical: 156, major: 423, minor: 655 }
  by_category: { preserve: 712, remediate: 289, defer: 233 }

chunks:
  - name: "critical-items"
    file: "critical-items.yaml"
    item_count: 156
  - name: "major-items"
    file: "major-items.yaml"
    item_count: 423
  - name: "inventory-pa"
    file: "inventory-pa.yaml"
    domain: "PA"
    item_count: 456
  - name: "inventory-mm"
    file: "inventory-mm.yaml"
    domain: "MM"
    item_count: 178
  # ... other domains
```

#### Processing Logic

```yaml
output_processing:
  step_1: "모든 도메인 분석 완료 후 총 크기 추정"
  step_2:
    if_small: "단일 technical-debt-inventory.yaml 생성"
    if_large:
      - "technical-debt-inventory/ 디렉토리 생성"
      - "critical-items.yaml 생성 (critical 항목만)"
      - "major-items.yaml 생성 (major 항목만)"
      - "도메인별 inventory-{domain}.yaml 생성"
      - "_manifest.yaml 생성 (인덱스 + metadata + summary)"
  step_3: "후속 skill에서 manifest 기반 청크 읽기"
```

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "work/specs/stage3-outputs/phase3a/"

  structure:
    - "technical-debt-inventory.yaml"
    - "debt-by-domain.yaml"
    - "remediation-recommendations.yaml"
```

### 4.2 Output Files

| File | Type | Purpose | Required |
|------|------|---------|----------|
| technical-debt-inventory.yaml | YAML | 전체 부채 인벤토리 | Yes |
| debt-by-domain.yaml | YAML | 도메인별 부채 요약 | Yes |
| remediation-recommendations.yaml | YAML | 개선 권장사항 | No |

### 4.3 File Header

```yaml
# Generated by: s3-03-preparation-technical-debt
# Stage: 3 - Preparation
# Phase: 3.3a - Technical Debt Analysis
# Generated: ${TIMESTAMP}
# Model: ${MODEL_NAME}
```

### 4.4 Output Schemas

#### technical-debt-inventory.yaml

```yaml
# technical-debt-inventory.yaml
metadata:
  generated_by: "s3-03-preparation-technical-debt"
  generated_at: "2026-01-07T14:00:00Z"
  total_domains: 12
  analysis_scope: "Java source files"

summary:
  total_debt_items: 1234
  by_severity:
    critical: 156
    major: 423
    minor: 655
  by_category:
    preserve: 712
    remediate: 289
    defer: 233
  by_type:
    code_smells: 456
    deprecated_apis: 312
    error_handling: 234
    hardcoding: 145
    architecture: 87

critical_items:
  - id: "DEBT-001"
    type: "deprecated_api"
    pattern: "log4j_1x"
    severity: "critical"
    category: "remediate"
    occurrences: 156
    affected_domains: ["PA", "MM", "SC", "SM", "PE", "EA", "SA", "EB"]
    description: "Log4j 1.x 사용 - 보안 취약점"
    remediation: "SLF4J + Logback으로 교체"
    note: "Wave 0에서 부분 처리됨"

major_items:
  - id: "DEBT-002"
    type: "error_handling"
    pattern: "empty_catch"
    severity: "major"
    category: "remediate"
    occurrences: 45
    affected_domains: ["PA", "MM", "SM"]
    description: "빈 catch 블록 - 예외 무시"
    remediation: "로깅 추가 또는 적절한 예외 처리"

  - id: "DEBT-003"
    type: "architecture"
    pattern: "direct_jdbc"
    severity: "major"
    category: "remediate"
    occurrences: 23
    affected_domains: ["PA", "CM"]
    description: "JDBC 직접 사용 - iBatis 미사용"
    remediation: "MyBatis Mapper로 변환"

  - id: "DEBT-004"
    type: "code_smells"
    pattern: "god_class"
    severity: "major"
    category: "defer"
    occurrences: 12
    affected_domains: ["PA", "MM", "SC"]
    description: "God Class (2000+ LOC)"
    remediation: "클래스 분리 (마이그레이션 후)"
    affected_classes:
      - class: "PA01001Service"
        loc: 3500
        methods: 78
      - class: "MM02001Service"
        loc: 2800
        methods: 62

inventory:
  - id: "DEBT-001"
    type: "deprecated_api"
    pattern: "log4j_1x"
    severity: "critical"
    category: "remediate"
    locations:
      - file: "src/main/java/com/hallain/pa/service/PA01001Service.java"
        line: 15
        code: "import org.apache.log4j.Logger;"
      - file: "src/main/java/com/hallain/mm/service/MMService.java"
        line: 12
        code: "import org.apache.log4j.Logger;"
    # ... more locations
```

#### debt-by-domain.yaml

```yaml
# debt-by-domain.yaml
metadata:
  generated_by: "s3-03-preparation-technical-debt"
  generated_at: "2026-01-07T14:00:00Z"

domains:
  - domain: "PA"
    priority: "P2"
    files_analyzed: 2895
    debt_summary:
      total: 456
      critical: 45
      major: 123
      minor: 288
      preserve: 312
      remediate: 89
      defer: 55
    top_issues:
      - { pattern: "log4j_1x", count: 45 }
      - { pattern: "empty_catch", count: 23 }
      - { pattern: "god_class", count: 5 }
    health_score: 65  # 100 - (critical*3 + major*1) / files * 10

  - domain: "MM"
    priority: "P2"
    files_analyzed: 878
    debt_summary:
      total: 178
      critical: 23
      major: 56
      minor: 99
      preserve: 112
      remediate: 45
      defer: 21
    top_issues:
      - { pattern: "log4j_1x", count: 23 }
      - { pattern: "direct_jdbc", count: 12 }
      - { pattern: "god_class", count: 3 }
    health_score: 72

  - domain: "CM"
    priority: "P0"
    files_analyzed: 249
    debt_summary:
      total: 34
      critical: 5
      major: 12
      minor: 17
      preserve: 20
      remediate: 10
      defer: 4
    top_issues:
      - { pattern: "log4j_1x", count: 5 }
      - { pattern: "static_utility_abuse", count: 8 }
    health_score: 85

domain_comparison:
  highest_debt: "PA"
  lowest_debt: "QM"
  average_health_score: 71
  domains_needing_attention:
    - domain: "PA"
      reason: "Most critical issues, largest codebase"
    - domain: "MM"
      reason: "Direct JDBC usage needs migration"
```

#### remediation-recommendations.yaml

```yaml
# remediation-recommendations.yaml
metadata:
  generated_by: "s3-03-preparation-technical-debt"
  generated_at: "2026-01-07T14:00:00Z"

recommendations:
  immediate:
    - id: "REC-001"
      debt_id: "DEBT-001"
      title: "Log4j 1.x → SLF4J + Logback 마이그레이션"
      priority: 1
      effort: "medium"
      impact: "critical"
      wave_dependency: "Wave 0 (이미 계획됨)"
      approach:
        - "SLF4J 의존성 추가"
        - "Logger 선언 변경: Logger → org.slf4j.Logger"
        - "로깅 메서드 호환 (대부분 동일)"
        - "log4j.properties → logback.xml 변환"
      automation_possible: true
      automated_by: "코드 생성 시 자동 적용"

    - id: "REC-002"
      debt_id: "DEBT-002"
      title: "Empty Catch Block 개선"
      priority: 2
      effort: "low"
      impact: "major"
      approach:
        - "예외 로깅 추가: log.error(\"Error\", e)"
        - "비즈니스 로직 검토 후 적절한 처리"
        - "필요시 RuntimeException으로 래핑"
      automation_possible: true
      automated_by: "코드 생성 템플릿에 기본 로깅 포함"

  during_migration:
    - id: "REC-003"
      debt_id: "DEBT-003"
      title: "Direct JDBC → MyBatis 변환"
      priority: 1
      effort: "medium"
      impact: "major"
      approach:
        - "JDBC 코드 블록 식별"
        - "동등한 MyBatis Mapper 생성"
        - "Service에서 Mapper 주입으로 변경"
      automation_possible: false
      manual_review_required: true

  post_migration:
    - id: "REC-004"
      debt_id: "DEBT-004"
      title: "God Class 분리"
      priority: 3
      effort: "high"
      impact: "major"
      approach:
        - "단일 책임 원칙 기반 분리"
        - "기능별 Service 클래스 분리"
        - "충분한 테스트 커버리지 확보 후 수행"
      automation_possible: false
      prerequisite: "80%+ 테스트 커버리지"

effort_summary:
  total_remediate_items: 289
  automated: 200
  manual_low: 45
  manual_medium: 30
  manual_high: 14
  estimated_total_hours: 120
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| all_domains_analyzed | structural | 12개 도메인 분석 | WARNING | No |
| debt_categorized | content | 모든 항목 분류됨 | WARNING | No |
| yaml_syntax | structural | YAML 파싱 오류 없음 | ERROR | Yes |

### 5.2 Gate Criteria

```yaml
gate_criteria:
  id: "G3.3a"
  name: "Technical Debt Gate"
  threshold: 70
  blocking: false  # Informational phase
  metrics:
    - metric: "all_domains_analyzed"
      weight: 0.5
      target: "12"
    - metric: "debt_categorized"
      weight: 0.5
      target: "100%"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Large file timeout | 분석 지연 | 10MB+ 파일 | Chunk 분석 | Yes |
| Pattern false positive | 과다 탐지 | 정규식 한계 | 수동 필터링 | No |
| Binary file | 파싱 오류 | .class 등 | Skip | No |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Critical > 500 | minor | INFO 로그 | - |
| Security 패턴 | major | Human review 권장 | Tech Lead |

---

## 7. Examples

### 7.1 Sample Pattern Detection

**Input (Java Source):**
```java
public class PA01001Service {
    private static final Logger log = Logger.getLogger(PA01001Service.class);

    public void processData() {
        try {
            // business logic
        } catch (Exception e) {
            // empty catch
        }
    }

    public List<DataVO> getData() {
        Connection conn = DriverManager.getConnection(url, user, pass);
        // direct JDBC usage
    }
}
```

**Detected Patterns:**
```yaml
detections:
  - pattern: "log4j_1x"
    line: 2
    code: "Logger.getLogger"

  - pattern: "empty_catch"
    line: 8
    code: "catch (Exception e) { }"

  - pattern: "direct_jdbc"
    line: 13
    code: "DriverManager.getConnection"
```

### 7.2 Sample Output

위의 4.4 Output Schema 섹션 참조

---

## Version History

### v1.0.0 (2026-01-07)
- Initial version
- 기술 부채 패턴 탐지 (code smells, deprecated APIs, error handling)
- Preserve/Remediate/Defer 분류
- 도메인별 Health Score 계산
