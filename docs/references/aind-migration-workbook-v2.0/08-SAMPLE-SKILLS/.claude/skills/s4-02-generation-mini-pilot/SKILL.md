---
name: s4-02-generation-mini-pilot
description: Use when validating code generation patterns before batch execution, generating pilot features for template verification, or testing generation templates with representative features (project)
---

# Mini-Pilot

> **Skill ID**: S4-02
> **Skill Type**: Generation (Sequential with Feedback Loop)
> **Stage**: 4 - Generation
> **Phase**: 4.2 - Mini-Pilot
> **Human Review**: REQUIRED (Tech Lead approval before batch generation)

## 1. Overview

### 1.1 Purpose

> **QUERY-FIRST 원칙**: Query 이관이 어떤 Task보다 우선한다.

**2-Phase 분리 파일럿**으로 코드 생성 패턴을 검증합니다:
- **PHASE 1**: Query 이관 (Mapper XML 변환) 파일럿 → Fidelity 검증
- **PHASE 2**: Java 코드 생성 파일럿 (Query 검증 PASS 후)

**PHASE 1 - Query 이관 파일럿:**
- 2-3개 도메인의 대표 sqlmap 파일 선정
- iBatis → MyBatis 변환 규칙 검증
- Legacy SQL 100% 보존 확인
- Query Fidelity Gate 통과

**PHASE 2 - Java 생성 파일럿:**
- Query 검증 PASS된 Feature만 대상
- Controller, Service, Repository (Mapper Interface)
- DTO (Request, Response), Entity

**검증 목적:**
- iBatis → MyBatis 변환 규칙 검증
- **Query 100% 보존 확인 (최우선)**
- Generation template 정확성 확인
- 컴파일 및 구조적 정합성 확인
- Human Review를 통한 품질 검증

### 1.2 Scope

**In Scope:**
- **PHASE 1**: 저복잡도 sqlmap 파일 5-10개 선정 (2-3개 도메인)
- **PHASE 2**: Query 검증 PASS 후 2-3개 Feature Java 코드 생성
- Query Fidelity 검증
- 피드백 기반 변환 규칙 조정
- Manual review 요청

**Out of Scope:**
- 대량 배치 생성 (→ S4-03)
- 테스트 코드 생성 (→ S4-04)
- 전체 도메인 커버리지

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Query-First** | Query 이관이 Java 생성보다 선행 | 비즈니스 로직 보존 최우선 |
| **Selective** | 저복잡도 대표 sqlmap/Feature 선정 | 빠른 검증, 리스크 최소화 |
| **Sequential** | 순차적 생성 (병렬 아님) | 피드백 루프 반영 |
| **Iterative** | 문제 발견 시 변환 규칙 조정 | 품질 향상 |
| **Validated** | Human Review 필수 | 대량 생성 전 품질 보증 |

### 1.4 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s4-01-generation-project-scaffold` | Scaffold 프로젝트 필요 |
| `s3-05-preparation-generation-spec` | 생성 템플릿 및 규칙 |
| `s2-04-validation-spec-completion` | 완성된 Feature Spec |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s4-03-generation-domain-batch` | 검증된 패턴으로 대량 생성 |
| `s4-04-generation-test-generation` | 생성 코드에 대한 테스트 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S4-01"
    skill_name: "s4-01-generation-project-scaffold"
    status: "completed"
    artifacts:
      - "next-hallain/build.gradle.kts"
      - "next-hallain/src/main/java/com/hallain/"

  - skill_id: "S3-05"
    skill_name: "s3-05-preparation-generation-spec"
    status: "completed"
    artifacts:
      - "generation-templates/"
      - "generation-rules.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| scaffolded_project | directory | `next-hallain/` | Java/Gradle | Yes |
| feature_specs | directory | `work/specs/stage2-outputs/phase4/` | YAML | Yes |
| generation_templates | directory | `work/specs/stage3-outputs/phase5/generation-templates/` | YAML | Yes |
| generation_rules | file | `work/specs/stage3-outputs/phase5/generation-rules.yaml` | YAML | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Write | - | Java/XML 파일 생성 |
| Read | - | Spec/Template 읽기 |
| Bash | - | Gradle 컴파일 검증 |

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: sequential
  unit: feature
  parallelization:
    enabled: false  # 피드백 루프를 위해 순차 실행
  batch_size: 3     # 2-3개 파일럿
  lifecycle:
    timeout_minutes: 180
    retry_on_failure: 2

feedback_loop:
  enabled: true
  on_issues:
    - "Update generation templates"
    - "Refine generation rules"
    - "Document edge cases"
```

### 3.2 Generation Pipeline (2-Phase)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 1: Query 이관 파일럿                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐│
│  │   Select     │────▶│   Convert    │────▶│   Fidelity   │────▶│   Human    ││
│  │   sqlmap     │     │   iBatis →   │     │   Check      │     │   Review   ││
│  │   Files      │     │   MyBatis    │     │   (100%)     │     │   PASS     ││
│  └──────────────┘     └──────────────┘     └──────────────┘     └────────────┘│
│                                                  │                             │
│                                                  │ Mismatch Found              │
│                                                  ▼                             │
│                                           ┌──────────────┐                     │
│                                           │   Update     │                     │
│                                           │   Rules      │                     │
│                                           └──────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         │ Query Fidelity Gate PASS
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 2: Java 생성 파일럿                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐│
│  │   Select     │────▶│   Generate   │────▶│   Validate   │────▶│   Human    ││
│  │   Features   │     │   Java Code  │     │   Compile    │     │   Review   ││
│  │   (Verified) │     │   (5-Layer)  │     │              │     │   PASS     ││
│  └──────────────┘     └──────────────┘     └──────────────┘     └────────────┘│
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Process Steps

---

## PHASE 1: Query 이관 파일럿

---

#### Step 1: sqlmap File Selection

**Description:** 파일럿 대상 sqlmap 파일 선정

**Selection Criteria:**
```yaml
sqlmap_selection:
  criteria:
    - complexity: "low-medium"       # 저~중복잡도
    - statement_count: "3-10"        # 적정 규모
    - sql_patterns:
        - "Basic SELECT"
        - "Simple JOIN"
        - "DECODE/CASE expression"
        - "Dynamic SQL (<isNotNull>, <isNotEmpty>)"
  domains:
    priority_1: "MM"    # 케이스 발생 도메인 - 필수 포함
    priority_2: "QM"    # 저복잡도
    priority_3: "BS"    # 저복잡도
  recommended_count: "5-10 files (2-3 domains)"
```

**Sub-steps:**
1. Priority 도메인의 sqlmap 파일 목록 확인
2. 복잡도 분석 (Statement 수, SQL 패턴)
3. 5-10개 파일 선정 (MM 필수 포함)
4. 선정 파일 목록 문서화

**Recommended Selection:**
```yaml
pilot_sqlmaps:
  mm_domain:
    - file: "sqlmap-mM0101001M.xml"
      reason: "Simple CRUD pattern"
    - file: "sqlmap-mM0101002M.xml"
      reason: "Basic JOIN pattern"
  qm_domain:
    - file: "sqlmap-qM0100101.xml"
      reason: "Low complexity CRUD"
  bs_domain:
    - file: "sqlmap-bS0100101.xml"
      reason: "Common pattern reference"
```

**Validation:** 5-10개 sqlmap 파일 선정 완료

---

#### Step 2: iBatis → MyBatis Conversion

**Description:** 선정된 sqlmap 파일을 MyBatis Mapper XML로 변환

> **CRITICAL**: SQL 원문 100% 보존. 문법만 변환.

**Conversion Rules (허용됨):**
```yaml
allowed_transformations:
  parameter_binding:
    - from: "#var#"
      to: "#{var}"
    - from: "$var$"
      to: "${var}"

  dynamic_sql:
    - from: "<isNotNull property=\"{prop}\">"
      to: "<if test=\"{prop} != null\">"
    - from: "<isNotEmpty property=\"{prop}\">"
      to: "<if test=\"{prop} != null and {prop} != ''\">"
    - from: "<isEqual property=\"{prop}\" compareValue=\"{val}\">"
      to: "<if test=\"{prop} == '{val}'\">"
    - from: "<iterate property=\"{prop}\">"
      to: "<foreach collection=\"{prop}\" item=\"item\">"

  attributes:
    - from: "parameterClass"
      to: "parameterType"
    - from: "resultClass"
      to: "resultType"

  namespace:
    - from: "<sqlMap namespace=\"...\">"
      to: "<mapper namespace=\"com.hallain.{domain}.repository.{Screen}Mapper\">"
```

**Prohibited Changes (절대 금지):**
```yaml
prohibited_changes:
  - "SQL 로직 재해석/재생성"
  - "컬럼명/테이블명 추측 또는 축약"
  - "조건값 변경 (예: 'INPRCH' → '1')"
  - "JOIN 조건 수정 또는 생략"
  - "WHERE 절 IN 값 변경"
  - "GROUP BY/ORDER BY 구조 변경"
  - "ROLLUP 구조 간소화"
  - "DECODE/CASE 로직 간소화"
  - "서브쿼리 구조 변경"
```

**Output Location:**
```
next-hallain/src/main/resources/mapper/{domain}/
└── {Screen}Mapper.xml
```

**Validation:** Mapper XML 파일 생성 완료

---

#### Step 3: Query Fidelity Verification

**Description:** 변환된 Mapper XML이 Legacy sqlmap과 100% 일치하는지 검증

> **BLOCKING**: 100% 일치하지 않으면 PHASE 2 진행 불가

**Verification Procedure:**
```yaml
verification_steps:
  1_open_legacy:
    action: "Legacy sqlmap XML 파일 열기"
    path: "hallain/src/main/resources/com/halla/{domain}/sqlmap/sqlmap-{featureId}.xml"

  2_open_generated:
    action: "Generated Mapper XML 열기"
    path: "next-hallain/src/main/resources/mapper/{domain}/{Screen}Mapper.xml"

  3_compare_statements:
    action: "Statement별 Line-by-Line 비교"
    per_statement:
      - "SELECT statements"
      - "INSERT statements"
      - "UPDATE statements"
      - "DELETE statements"
```

**SQL Fidelity Checklist:**
```yaml
sql_fidelity_checklist:
  items:
    - id: "TBL-001"
      check: "테이블명 100% 일치"
      example: "FROM EMM_PRCH_APRV_DTL EE, EMM_PRCH_APRV FF"
      on_mismatch: "BLOCK"

    - id: "COL-001"
      check: "컬럼명 100% 일치"
      example: "EE.MAT_ORD_NO, FF.ORD_PRG_STAT_CD"
      on_mismatch: "BLOCK"

    - id: "JOIN-001"
      check: "JOIN 조건 100% 일치"
      example: "EE.MAT_ORD_NO = FF.MAT_ORD_NO"
      prohibited: "A.ORD_NO = B.ORD_NO 와 같은 축약/추측 금지"
      on_mismatch: "BLOCK"

    - id: "WHERE-001"
      check: "WHERE 절 조건값 100% 일치"
      example: "ORD_PRG_STAT_CD IN (10,20,30)"
      prohibited: "IN ('20', '30', '40', '50') 와 같은 값 변경 금지"
      on_mismatch: "BLOCK"

    - id: "WHERE-002"
      check: "리터럴 값 100% 일치"
      example: "INOUT_FLAG_CD = 'INPRCH'"
      prohibited: "INOUT_FLAG_CD = '1' 와 같은 값 변경 금지"
      on_mismatch: "BLOCK"

    - id: "GRPORD-001"
      check: "GROUP BY/ORDER BY 100% 일치"
      example: "GROUP BY ROLLUP((MAT_CD3, GOODS_NM3), (MAT_CD2, GOODS_NM2))"
      prohibited: "단순 ROLLUP(MAT_CD) 와 같은 구조 변경 금지"
      on_mismatch: "BLOCK"

    - id: "SUB-001"
      check: "서브쿼리 구조 100% 일치"
      example: "UNION ALL 구조, 서브쿼리 개수"
      on_mismatch: "BLOCK"

    - id: "LOGIC-001"
      check: "DECODE/CASE 로직 100% 일치"
      example: "DECODE(ORD_CANC_FLAG_CD, 'N', 1, 'C', -1)"
      prohibited: "NVL(...) != 'Y' 와 같은 로직 간소화 금지"
      on_mismatch: "BLOCK"
```

**On Mismatch:**
```yaml
on_mismatch:
  action: "BLOCK - 즉시 중단"
  resolution:
    1: "Legacy sqlmap에서 해당 SQL 복사"
    2: "iBatis → MyBatis 문법만 변환"
    3: "Generated Mapper XML 덮어쓰기"
    4: "Fidelity Check 재실행"
  escalation: "2회 실패 시 Human Review 요청"
```

**Validation:** Legacy와 100% 일치 확인 (전체 파일)

---

#### Step 4: Phase 1 Human Review

**Description:** Query 이관 결과에 대한 Human Review

**Review Checklist:**
```yaml
phase1_human_review:
  type: "mandatory"
  reviewer: "Tech Lead"
  checklist:
    - "Mapper XML이 Legacy sqlmap과 100% 일치"
    - "iBatis → MyBatis 문법만 변환됨"
    - "SQL 로직 변경 없음"
    - "변환 규칙 검증 완료"
    - "PHASE 2 (Java 생성) 진행 가능"

  approval_required: true
  on_reject:
    - "Mismatch 항목 문서화"
    - "변환 규칙 수정"
    - "재변환 후 재검증"
```

**Validation:** Phase 1 Human Review PASS

---

## PHASE 2: Java 생성 파일럿 (Query Fidelity Gate PASS 후)

---

#### Step 5: Feature Selection (Query Verified)

**Description:** Query 검증 완료된 파일럿 대상 Feature 선정

> **PRECONDITION**: Phase 1 Human Review PASS 필수

**Selection Criteria:**
```yaml
feature_selection:
  preconditions:
    - "Phase 1: Query 이관 파일럿 완료"
    - "Phase 1: Human Review PASS"

  # v1.1.0: Priority Order 추가 - Stage 2 검증 완료 Feature 우선
  priority_order:
    1_validated_features:
      description: "Stage 2 검증 완료 Feature 우선 선정"
      check_path: "work/specs/stage2-outputs/phase4/{feature}/validation-result.yaml"
      required_status: "valid"
      rationale: "이미 분석/검증된 Feature로 품질 보장"

    2_low_complexity:
      description: "저복잡도 Feature"
      criteria:
        - complexity_score: "< 40"
        - endpoints_count: "3-5"

    3_domain_distribution:
      description: "2-3개 도메인 분산"
      rationale: "다양한 패턴 검증"

  criteria:
    - complexity_score: "< 40"       # 저복잡도
    - endpoints_count: "3-5"         # 적정 규모
    - external_dependencies: "none"  # 외부 의존성 없음
    - query_verified: true           # Query 검증 완료 필수
    - representative_patterns:
        - "CRUD operations"
        - "List/Detail/Save pattern"
  recommended_count: "2-3 features"
```

**Feature Selection Process (v1.1.0):**
1. Stage 2 `validation-result.yaml` 파일 존재 여부 확인
2. `status: valid` Feature 필터링
3. 해당 Feature 중 복잡도 기준 충족하는 것 선정
4. 검증 완료 Feature 없으면 기존 기준으로 선정

**Recommended Selection:**
```yaml
pilot_features:
  - feature_id: "FEAT-QM-001"
    domain: "QM"
    query_verified: true
    reason: "Simple CRUD, Query verified"
  - feature_id: "FEAT-BS-001"
    domain: "BS"
    query_verified: true
    reason: "List/Detail pattern, Query verified"
```

**Validation:** 2-3개 Feature 선정 완료 (Query 검증됨)

---

#### Step 6: Java Code Generation (5-Layer)

**Description:** 선정된 Feature의 5-Layer Java 코드 생성

> **NOTE**: Mapper XML은 이미 PHASE 1에서 생성됨. Java 코드만 생성.

**Sub-steps (per feature):**
1. Entity 클래스 생성
2. DTO 클래스 생성 (Request, Response)
3. Mapper Interface 생성
4. Service 클래스 생성
5. Controller 클래스 생성

**Generation Order:**
```yaml
generation_order:
  1: "Entity"         # 기반 데이터 모델
  2: "DTO"            # Request/Response
  3: "Mapper"         # Repository interface (Mapper XML은 이미 존재)
  4: "Service"        # 비즈니스 로직
  5: "Controller"     # API 엔드포인트
```

**Output Files (per feature):**
```
next-hallain/src/main/java/com/hallain/{domain}/
├── controller/
│   └── {Screen}Controller.java
├── service/
│   └── {Screen}Service.java
├── repository/
│   └── {Screen}Mapper.java      # Interface only (XML은 Phase 1 산출물)
├── dto/
│   ├── {Screen}SearchRequest.java
│   ├── {Screen}DetailRequest.java
│   ├── {Screen}SaveRequest.java
│   └── {Screen}Response.java
└── entity/
    └── {Screen}Entity.java

# Mapper XML은 Phase 1에서 이미 생성됨
# next-hallain/src/main/resources/mapper/{domain}/{Screen}Mapper.xml
```

**Validation:** 5-Layer Java 파일 생성 완료

---

#### Step 7: Validate Compilation

**Description:** 생성 코드 컴파일 검증

**Sub-steps:**
1. `./gradlew compileJava` 실행
2. 컴파일 오류 확인
3. 오류 발생 시 원인 분석

**Validation Commands:**
```bash
cd backend
./gradlew compileJava --info
```

**On Compile Error:**
```yaml
compile_error_handling:
  - type: "import_missing"
    resolution: "Add import statement"
  - type: "type_mismatch"
    resolution: "Fix type in template"
  - type: "syntax_error"
    resolution: "Fix template syntax"
  - action: "Update template, regenerate"
```

**Validation:** 컴파일 성공

---

#### Step 8: Pattern Validation

**Description:** 생성 코드가 generation-rules.yaml 패턴을 준수하는지 검증

**Check Items:**
```yaml
pattern_validation:
  naming_conventions:
    - check: "Controller class naming"
      pattern: "{Screen}Controller"
      example: "PA01001Controller"
    - check: "Service class naming"
      pattern: "{Screen}Service"
    - check: "Method naming"
      pattern: "get{Entity}List, save{Entity}"

  annotation_rules:
    - check: "Controller annotations"
      required: ["@RestController", "@RequestMapping", "@RequiredArgsConstructor"]
    - check: "Service annotations"
      required: ["@Service", "@Transactional(readOnly=true)"]
    - check: "Mapper annotations"
      required: ["@Mapper"]
```

**Validation:** 패턴 준수 확인

---

#### Step 9: Phase 2 Human Review & Feedback Loop

**Description:** Java 코드 생성 결과에 대한 Human Review 및 피드백

**Feedback Actions:**
```yaml
feedback_loop:
  on_compile_error:
    - "Analyze error cause"
    - "Update generation template"
    - "Regenerate affected files"
    - "Re-validate"

  on_pattern_mismatch:
    - "Document deviation"
    - "Update generation-rules.yaml"
    - "Regenerate"

  max_iterations: 3
  escalate_after: 3
```

**Review Checklist:**
```yaml
phase2_human_review:
  type: "mandatory"
  reviewer: "Tech Lead"
  checklist:
    - "Code follows reference patterns"
    - "Naming conventions correct"
    - "Controller endpoints are correct"
    - "Service transaction handling is proper"
    - "Mapper Interface와 Mapper XML 매칭"
    - "Ready for batch generation"

  approval_required: true
  on_reject:
    - "Document feedback"
    - "Update templates"
    - "Regenerate pilot"
    - "Re-submit for review"
```

**Validation:** Phase 2 Human Review PASS

---

### 3.4 Decision Points

**PHASE 1 Decision Points:**
| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | Query Fidelity 100% | Phase 1 Human Review | BLOCK & 재변환 |
| DP-2 | Phase 1 Review PASS | PHASE 2 진행 | 피드백 반영 후 재검토 |
| DP-3 | 2회 이상 Fidelity 실패 | Human Escalation | 재시도 |

**PHASE 2 Decision Points:**
| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-4 | 컴파일 성공 | 다음 Feature 진행 | 피드백 루프 |
| DP-5 | 패턴 불일치 | 템플릿 수정 | 계속 진행 |
| DP-6 | Phase 2 Review PASS | Gate 통과 | 수정 후 재검토 |
| DP-7 | 3회 이상 실패 | Escalate | 재시도 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "next-hallain/src/main/java/com/hallain/"
    resources: "next-hallain/src/main/resources/"

  per_feature:
    java_files:
      - "{domain}/controller/{Screen}Controller.java"
      - "{domain}/service/{Screen}Service.java"
      - "{domain}/repository/{Screen}Mapper.java"
      - "{domain}/dto/{Screen}SearchRequest.java"
      - "{domain}/dto/{Screen}DetailRequest.java"
      - "{domain}/dto/{Screen}SaveRequest.java"
      - "{domain}/dto/{Screen}Response.java"
      - "{domain}/entity/{Screen}Entity.java"
    resource_files:
      - "mapper/{domain}/{Screen}Mapper.xml"
```

### 4.2 Output Files Summary

| Layer | File Pattern | Count per Feature |
|-------|--------------|-------------------|
| Controller | {Screen}Controller.java | 1 |
| Service | {Screen}Service.java | 1 |
| Repository | {Screen}Mapper.java | 1 |
| DTO | {Screen}*Request.java, {Screen}Response.java | 4 |
| Entity | {Screen}Entity.java | 1 |
| Mapper XML | {Screen}Mapper.xml | 1 |
| **Total** | | **9 files** |

### 4.3 Tracking Output

```yaml
# pilot-progress.yaml
metadata:
  generated_by: "s4-02-generation-mini-pilot"
  generated_at: "2026-01-07T14:00:00Z"

summary:
  total_features: 3
  completed: 3
  compile_success: true
  human_review: "APPROVED"

features:
  - feature_id: "FEAT-QM-001"
    status: "completed"
    files_generated: 9
    compile_result: "success"
    feedback_iterations: 1

  - feature_id: "FEAT-BS-001"
    status: "completed"
    files_generated: 9
    compile_result: "success"
    feedback_iterations: 0

  - feature_id: "FEAT-CM-001"
    status: "completed"
    files_generated: 9
    compile_result: "success"
    feedback_iterations: 0

template_updates:
  - template: "controller-template.yaml"
    change: "Added @Tag annotation"
    reason: "Swagger documentation"

ready_for_batch: true
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| pilot_features_compile | structural | `./gradlew compileJava` 성공 | Feedback loop | Yes |
| follows_templates | content | generation-rules.yaml 패턴 준수 | ERROR | Yes |
| minimum_features | metric | >= 2 full feature sets | ERROR | Yes |
| files_per_feature | structural | 9 files per feature | WARNING | No |

### 5.2 Manual Reviews

| Review | Reviewer | Criteria | Required |
|--------|----------|----------|----------|
| Code quality review | Tech Lead | 패턴 준수, 가독성 | Yes |
| MyBatis XML review | Tech Lead | SQL 정확성 | Yes |
| API structure review | Tech Lead | Endpoint 설계 | Yes |

### 5.3 Gate Criteria (2-Phase)

```yaml
gate_criteria:
  # PHASE 1 Gate
  phase1_gate:
    id: "G4.2-P1"
    name: "Query Fidelity Gate"
    threshold: 100  # 100% 필수 (99% 불가)
    human_review_required: true
    blocking: true  # PHASE 2 진행 불가

    metrics:
      - metric: "query_fidelity"
        weight: 0.6
        target: "100%"
        check: "Legacy sqlmap과 Generated Mapper XML 100% 일치"
        blocking: true
      - metric: "syntax_conversion_only"
        weight: 0.2
        target: "true"
        check: "iBatis → MyBatis 문법만 변환됨"
        blocking: true
      - metric: "phase1_human_review"
        weight: 0.2
        target: "approved"
        type: "human_review"
        reviewer: "Tech Lead"
        blocking: true
        purpose: "Query 이관 정확성 검증"

    on_pass:
      message: "Query Fidelity Gate PASS - PHASE 2 진행 가능"
      proceed_to: "PHASE 2"
    on_fail:
      action: "BLOCK - PHASE 2 진행 불가"
      resolution: "Legacy sqlmap 직접 복사 후 문법만 변환"

  # PHASE 2 Gate
  phase2_gate:
    id: "G4.2-P2"
    name: "Mini-Pilot Gate"
    threshold: 70
    human_review_required: true

    preconditions:
      - "PHASE 1 Gate PASS 필수"

    metrics:
      - metric: "pilot_features_compile"
        weight: 0.3
        target: "true"
        command: "cd backend && ./gradlew compileJava"
        blocking: true
      - metric: "follows_templates"
        weight: 0.3
        target: "true"
        check: "Code matches generation-rules.yaml patterns"
        blocking: true
      - metric: "minimum_features"
        weight: 0.2
        target: ">= 2"
        blocking: true
      - metric: "phase2_human_review"
        weight: 0.2
        target: "approved"
        type: "human_review"
        reviewer: "Tech Lead"
        blocking: true
        purpose: "Validate patterns before large-scale batch generation"

    on_pass:
      auto_commit: true
      message: "feat(S4-P4.2): Mini-pilot validated"
      ready_for_batch: true  # Signals S4-03 can proceed
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Compile error | javac 실패 | 템플릿 오류 | 템플릿 수정 | Yes |
| Import missing | 클래스 못찾음 | Import 누락 | Import 추가 | Yes |
| MyBatis parse error | XML 파싱 실패 | 변환 규칙 누락 | 규칙 추가 | Yes |
| Pattern mismatch | 코드 리뷰 실패 | 템플릿 불일치 | 템플릿 수정 | Yes |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| 3회 이상 실패 | critical | 수동 분석 요청 | Tech Lead |
| Human review 거부 | major | 피드백 반영 후 재시도 | Developer |
| 템플릿 대규모 수정 필요 | major | S3-05 재실행 검토 | Architect |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 컴파일 실패 | 템플릿 수정 → 재생성 | Feature |
| 전체 파일럿 실패 | 템플릿 전면 검토 | Phase |
| Human review 실패 | 피드백 반영 후 재생성 | Feature |

---

## 7. Examples

### 7.1 Sample Input

**Feature Spec (FEAT-QM-001):**
```yaml
feature:
  feature_id: "FEAT-QM-001"
  screen_id: "QM01001"
  domain: "qm"
  name: "품질검사 조회"
  complexity: "low"
  endpoints:
    - path: "/list"
      method: "POST"
      operation: "selectList"
    - path: "/detail"
      method: "POST"
      operation: "selectOne"
    - path: "/save"
      method: "POST"
      operation: "save"
  table: "TB_QM_INSPECTION"
```

### 7.2 Sample Output

**Generated Controller:**
```java
package com.hallain.qm.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import com.hallain.common.response.ApiResponse;
import com.hallain.qm.service.QM01001Service;
import com.hallain.qm.dto.*;

@RestController
@RequestMapping("/api/qm/qm01001")
@Tag(name = "QM01001 - 품질검사 조회")
@RequiredArgsConstructor
public class QM01001Controller {

    private final QM01001Service qm01001Service;

    @PostMapping("/list")
    @Operation(summary = "품질검사 목록 조회")
    public ApiResponse<List<QM01001Response>> getInspectionList(
            @Valid @RequestBody QM01001SearchRequest request) {
        return ApiResponse.success(qm01001Service.getInspectionList(request));
    }

    @PostMapping("/detail")
    @Operation(summary = "품질검사 상세 조회")
    public ApiResponse<QM01001Response> getInspection(
            @Valid @RequestBody QM01001DetailRequest request) {
        return ApiResponse.success(qm01001Service.getInspection(request));
    }

    @PostMapping("/save")
    @Operation(summary = "품질검사 저장")
    public ApiResponse<Void> saveInspection(
            @Valid @RequestBody List<QM01001SaveRequest> requests) {
        qm01001Service.saveInspection(requests);
        return ApiResponse.success();
    }
}
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| SP 호출 존재 | CALLABLE 패턴 | MyBatis CALLABLE 변환 |
| 복잡한 동적 SQL | Multiple isNotNull | Multiple <if test> |
| 대형 DTO | 20+ 필드 | Split into sub-DTOs |
| 순환 참조 | A → B → A | Interface 분리 |

---

## Version History

### v1.1.0 (2026-01-15)
- Step 5: Feature Selection에 `priority_order` 추가
- Stage 2 검증 완료 Feature 우선 선정 로직
- Feature Selection Process 명시화

### v1.0.0 (2026-01-07)
- Initial version
- 3개 파일럿 Feature 지원
- 피드백 루프 메커니즘
- Human review 통합
