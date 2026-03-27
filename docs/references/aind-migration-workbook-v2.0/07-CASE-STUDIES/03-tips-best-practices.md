# Tips & Best Practices

**Version**: 1.0.0
**Last Updated**: 2026-01-16

---

## Overview

AI 기반 Legacy Migration에서 일관된 품질의 산출물을 얻기 위한 실용적인 팁을 제공합니다.

---

## 1. 일관된 품질 산출물을 위한 팁

### 1.1 Skill 사용 규칙

```yaml
rule_1:
  name: "Skill First, Always"
  description: |
    Phase 작업을 시작하기 전 반드시 해당 Skill을 invoke하세요.
    Skill 없이 작업하면 일관성이 깨집니다.

  bad_example: |
    # 잘못된 방법
    "Controller 분석해줘"  # Skill 없이 임의 요청

  good_example: |
    # 올바른 방법
    /s1-01-discovery-feature-inventory  # Skill invoke 후 작업
```

### 1.2 Context 관리

```yaml
rule_2:
  name: "Context는 유한 자원"
  description: |
    200K 토큰 Context를 효율적으로 사용하세요.
    한 번에 모든 파일을 로드하지 마세요.

  tips:
    - "도메인 단위로 작업 분할 (30-50 Feature per Wave)"
    - "중간 결과는 YAML 파일로 저장"
    - "Layer별 점진적 로딩 (Controller → Service → DAO)"

  context_budget: |
    # Context 예산 분배 예시
    System Prompt:   10K tokens (5%)
    Source Code:     80K tokens (40%)
    Analysis Result: 60K tokens (30%)
    Response Space:  50K tokens (25%)
```

### 1.3 Wave 분할 기준

```yaml
rule_3:
  name: "Safe Wave Size"
  description: |
    Context 초과를 방지하기 위한 Wave 크기 기준

  thresholds:
    controllers_per_wave: "< 100"
    endpoints_per_wave: "< 200"
    features_per_wave: "30-50 (safe range)"

  wave_division_algorithm: |
    1. 도메인별 Feature 수 확인
    2. 50 초과 도메인 → Sub-wave 분할
    3. 의존성 고려하여 순서 결정
```

---

## 2. 흔한 실수 및 회피 방법

### 2.1 Discovery 단계 실수

| 실수 | 결과 | 회피 방법 |
|------|------|----------|
| Controller 일부만 분석 | Stage 2에서 누락 발견 | `find` 명령어로 전체 수 먼저 확인 |
| SP 호출 패턴 누락 | 코드 생성 실패 | `{call` 패턴 grep으로 사전 확인 |
| Dynamic SQL 과소평가 | 변환 오류 급증 | `<if>`, `<choose>` 태그 카운트 |

### 2.2 Validation 단계 실수

| 실수 | 결과 | 회피 방법 |
|------|------|----------|
| Forward만 검증 | 누락 미발견 | Bidirectional Validation 필수 |
| Gap 임시 처리 | 같은 문제 반복 | Root Cause 분석 후 Pattern 수정 |
| Coverage 98%에서 만족 | 20개 Feature 누락 | 99% 이상 달성 필수 |

### 2.3 Generation 단계 실수

| 실수 | 결과 | 회피 방법 |
|------|------|----------|
| Mini-Pilot 건너뜀 | 대량 재작업 | 6개 Feature 반드시 검증 |
| 복잡도별 샘플링 안함 | 특정 복잡도 실패 | HIGH/MEDIUM/LOW 각 2개씩 |
| 빌드 확인 없이 진행 | Stage 5 시작 불가 | 매 도메인 빌드 확인 |

---

## 3. Prompt 작성 가이드

### 3.1 명확한 요청 공식

```
[Context] + [Task] + [Output Format] + [Quality Criteria]
```

**예시:**

```markdown
# Bad Prompt
"PA 도메인 분석해줘"

# Good Prompt
[Context] PA 도메인의 15개 Controller를 분석합니다.
[Task] 각 Controller의 엔드포인트, 서비스 호출, MyBatis 매핑을 추출하세요.
[Output] YAML 형식으로, feature-inventory.yaml 스키마를 따르세요.
[Criteria] SP 호출 100% 식별, Dynamic SQL 복잡도 평가 포함
```

### 3.2 정량적 기준 명시

```yaml
# Bad: 모호한 기준
"품질 좋게 해주세요"

# Good: 정량적 기준
criteria:
  sql_equivalence: ">= 35/40"
  structural_match: ">= 85%"
  coverage: "100%"
```

### 3.3 예시 제공

```yaml
# 분석 결과 예시 제공
example_output: |
  feature:
    id: "PA001-selectList"
    domain: "pa"
    endpoint:
      url: "/pa/selectList.mi"
      method: "POST"
    service:
      name: "PATaskService"
      method: "selectList"
    data_access:
      mapper: "PAMapper.xml"
      query_id: "selectList"
      stored_procedure: "PKG_PA.SELECT_LIST"
```

---

## 4. 검토 시 주의점

### 4.1 AI 결과 맹신 금지

```yaml
verification_principle:
  rule: "Trust but Verify"
  description: |
    AI 결과를 신뢰하되, 핵심 항목은 반드시 검증하세요.

  must_verify:
    - "Controller/Endpoint 수 일치 여부"
    - "SP 호출 목록 완전성"
    - "SQL 동등성"

  verification_method: |
    # 수동 검증 명령어
    # 1. Controller 수 비교
    LEGACY=$(find hallain/ -name "*Controller.java" | wc -l)
    INVENTORY=$(grep -c "controller:" inventory.yaml)
    echo "Legacy: $LEGACY, Inventory: $INVENTORY"
```

### 4.2 Summary vs Actual 검증

```yaml
validation_rule:
  name: "summary.count == actual_data_count"
  description: |
    Summary에 기록된 수치와 실제 데이터 수가 일치해야 합니다.

  check_script: |
    # Summary에서 읽은 값
    SUMMARY_COUNT=$(grep "total_features:" summary.yaml | awk '{print $2}')

    # 실제 데이터 카운트
    ACTUAL_COUNT=$(grep -c "feature_id:" features.yaml)

    if [ "$SUMMARY_COUNT" != "$ACTUAL_COUNT" ]; then
      echo "MISMATCH: Summary=$SUMMARY_COUNT, Actual=$ACTUAL_COUNT"
      exit 1
    fi
```

---

## 5. 체크리스트 활용 vs 창의적 접근 균형

### 5.1 Rigid vs Flexible Skills

```yaml
skill_types:
  rigid:
    examples: ["TDD", "Debugging", "Validation"]
    approach: "체크리스트 100% 준수"
    flexibility: "0%"
    reason: "품질 보장이 최우선"

  flexible:
    examples: ["Architecture Design", "Refactoring"]
    approach: "원칙 기반, 상황 적응"
    flexibility: "30-50%"
    reason: "창의적 해결이 필요한 영역"
```

### 5.2 체크리스트가 사고를 제한할 때

```yaml
when_checklist_limits:
  symptoms:
    - "체크리스트 항목만 보고 전체 맥락을 놓침"
    - "예외 상황을 체크리스트에 끼워맞추려 함"
    - "새로운 패턴을 발견했지만 체크리스트에 없어서 무시"

  solutions:
    - "체크리스트는 최소 기준, 추가 발견 환영"
    - "Lessons Learned에 새 패턴 기록"
    - "Skill 개선 제안"

  balance_principle: |
    체크리스트 = 반드시 확인할 것 (Floor)
    창의적 접근 = 더 나은 방법 탐색 (Ceiling)
    두 가지를 동시에 추구하세요.
```

### 5.3 창의적 접근이 필요한 순간

```yaml
creative_moments:
  - trigger: "기존 패턴으로 설명되지 않는 코드"
    approach: "새 패턴으로 분류, 문서화"

  - trigger: "체크리스트 100% 통과했지만 결과가 이상함"
    approach: "체크리스트 자체 검토, 항목 추가 제안"

  - trigger: "더 효율적인 방법이 떠오름"
    approach: "실험 후 검증되면 Best Practice에 추가"
```

---

## 6. 효율적인 작업 패턴

### 6.1 배치 처리 패턴

```yaml
batch_pattern:
  name: "Domain-First Batch"
  description: |
    도메인 단위로 전체 Pipeline을 완료한 후 다음 도메인으로

  flow: |
    cm 도메인:
      Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5
    pa 도메인:
      Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5
    ...

  benefit: "완료된 도메인은 독립적으로 배포 가능"
```

### 6.2 체크포인트 패턴

```yaml
checkpoint_pattern:
  name: "Feature-Level Checkpoint"
  description: |
    Feature 단위로 상태 저장, 중단 시 안전 재개

  implementation: |
    .choisor/tasks/{domain}/{feature}/
    ├── status.yaml        # pending | in_progress | completed | failed
    ├── last_checkpoint    # 마지막 성공 Phase
    └── error_log.yaml     # 실패 시 오류 정보

  resume_command: |
    python -m choisor resume --from-checkpoint
```

### 6.3 병렬 실행 패턴

```yaml
parallel_pattern:
  name: "Independent Domain Parallel"
  description: |
    의존성 없는 도메인은 병렬 처리

  identification: |
    # 의존성 그래프에서 독립 도메인 식별
    independent_domains:
      - [pe, bs, qm]  # 서로 의존 없음 → 병렬 가능
    dependent_domains:
      - cm → pa, mm   # cm 먼저 완료 필요

  execution: |
    # Parallel execution
    Session 1: pe 도메인 처리
    Session 2: bs 도메인 처리
    Session 3: qm 도메인 처리
```

---

## 7. 문제 해결 패턴

### 7.1 Stage 1 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| Feature 수 불일치 | Controller 일부 누락 | `find` 명령어로 전체 확인 |
| SP 미식별 | XML 패턴 다름 | `{call`, `CALL` 모두 검색 |
| 복잡도 오분류 | 기준 모호 | Dynamic SQL 태그 수로 재분류 |

### 7.2 Stage 4 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| 빌드 실패 | 의존성 누락 | Stage 3 Interface 검토 |
| MyBatis 오류 | Dynamic SQL 변환 실패 | 해당 XML 수동 검토 |
| 테스트 실패 | Spec 불일치 | Stage 1 Spec 재검토 |

### 7.3 Stage 5 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| Structural Score 낮음 | Naming Convention 위반 | Stage 3 ADR 재적용 |
| Functional Score 낮음 | SQL 불일치 | SQL 동등성 수동 검증 |
| Quality Gate 실패 | 복합 원인 | 각 Phase 리포트 개별 분석 |

---

## 8. 실무 적용 고려사항

### 8.1 테스트 공수 예측

```yaml
test_effort_estimation:
  formula: |
    테스트 공수 = Feature 수 × 복잡도 계수 × 검증 반복 횟수

  complexity_factors:
    LOW: 0.5   # 단순 CRUD
    MEDIUM: 1.0  # Dynamic SQL, 조건 분기
    HIGH: 2.0   # SP 호출, 복잡한 비즈니스 로직

  example: |
    912 Features
    - LOW: 400 × 0.5 = 200 단위
    - MEDIUM: 400 × 1.0 = 400 단위
    - HIGH: 112 × 2.0 = 224 단위
    총 테스트 공수: 824 단위
```

### 8.2 수정 공수 최소화 전략

```yaml
rework_minimization:
  strategy_1:
    name: "Phase Gate 엄격 적용"
    effect: "후반 재작업 70% 감소"

  strategy_2:
    name: "Mini-Pilot 필수화"
    effect: "대량 생성 실패 방지"

  strategy_3:
    name: "Pattern-Based Remediation"
    effect: "유사 문제 일괄 처리"

  strategy_4:
    name: "First Pass Success 85% 목표"
    effect: "재작업 비용 55% 절감"
```

---

**Next:** [02-lessons-learned.md](02-lessons-learned.md) - 프로젝트 교훈
