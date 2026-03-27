# Token Optimization Strategy

**Version**: 1.0.0
**Last Updated**: 2026-01-18

---

## 1. Overview

### 1.1 핵심 원칙

> **"토큰 비용 절약보다 Spec 완전성이 우선이다"**
>
> Spec의 누락은 절대 허용할 수 없는 프로젝트이므로
> 스크립트에 의존하는 것은 매우 위험하다.
> 그럼에도 불구하고, 스크립트 활용의 효과성이 명확한 작업에는
> 제한적으로 허용할 수 있다.

### 1.2 자동화율 현실 평가

```yaml
automation_reality:
  initial_estimate: "62%"
  realistic_estimate: "46%"
  gap: "-16%p"

  token_savings:
    initial: "56% (~1,091K)"
    realistic: "36% (~693K)"
    gap: "-398K tokens"
```

---

## 2. Risk Analysis (위험 분석)

### 2.1 스크립트 자동화의 근본적 한계

```yaml
fundamental_limitations:
  complex_sql:
    issue: "중첩된 Dynamic SQL"
    example: "<isNotNull> 안에 <iterate> 포함"
    reason: "regex 파싱 한계, 구조 추적 불가"

  context_understanding:
    issue: "컨텍스트 기반 타입 추론"
    example: "VO 상속, 제네릭 해석"
    reason: "관계 분석 능력 부재"

  business_logic:
    issue: "비즈니스 로직 의미 검증"
    example: "날짜 범위 30일 제한 규칙"
    reason: "도메인 지식 필요"

  edge_cases:
    issue: "예외 상황 판단"
    example: "Dead code vs 실제 사용 코드"
    reason: "런타임 동작 추론 필요"
```

### 2.2 Auto-Fix 신뢰도 문제

```yaml
auto_fix_actual_success_rate:
  missing_import:
    claimed: "90%"
    actual: "60-70%"
    failure_reason: "동일 클래스명 다른 패키지"

  type_mismatch:
    claimed: "70%"
    actual: "20-30%"
    failure_reason: "의미적 타입 불일치"

  method_not_found:
    claimed: "50%"
    actual: "10-20%"
    failure_reason: "시그니처 추론 한계"
```

### 2.3 Spec 누락 위험 유형

```yaml
spec_omission_risks:
  critical:
    - "비표준 패턴 미인식"
    - "동적 생성 코드 누락"
    - "SP 호출 체인 추적 실패"

  major:
    - "Fuzzy 매칭 오판단"
    - "타입 변환 오류"
    - "Annotation 조합 문제"

  minor:
    - "명명 규칙 불일치"
    - "스타일 가이드 위반"
```

---

## 3. Safe Automation Zones (안전한 자동화 영역)

### 3.1 100% 자동화 가능 (Spec 영향 없음)

```yaml
fully_automatable:
  file_operations:
    tasks:
      - "파일 스캔/목록화"
      - "디렉토리 구조 분석"
      - "glob/find 패턴 검색"
    automation_rate: "100%"

  build_test:
    tasks:
      - "Gradle/Maven 빌드 실행"
      - "테스트 실행 및 결과 수집"
      - "Coverage 리포트 생성"
    automation_rate: "100%"

  validation:
    tasks:
      - "JSON/YAML Schema Validation"
      - "파일 존재 여부 확인"
      - "산출물 구조 검증"
    automation_rate: "100%"

  reporting:
    tasks:
      - "결과 집계/통계"
      - "리포트 템플릿 렌더링"
      - "로그 수집"
    automation_rate: "100%"
```

### 3.2 부분 자동화 가능 (AI 검증 필수)

```yaml
partially_automatable:
  simple_pattern:
    description: "단순 패턴 치환 (중첩 없는 경우)"
    example: "#var# → #{var}"
    automation_rate: "70%"
    requirement: "AI 검증 단계 필수"

  coverage_calc:
    description: "Coverage 수치 계산"
    automation_rate: "90%"
    requirement: "Fuzzy 매칭 판단은 AI"

  basic_classification:
    description: "기본 Severity 분류"
    automation_rate: "60%"
    requirement: "Critical 승격/강등은 AI"
```

---

## 4. Application Strategy (적용 전략)

### 4.1 2-Phase Hybrid Approach

```
┌─────────────────────────────────────────────────────────────┐
│           Phase 1: Pre-processing (Script)                  │
│                                                             │
│  안전한 자동화 영역:                                         │
│  • 파일 목록화, 구조 스캔                                    │
│  • 빌드/테스트 실행 및 결과 수집                             │
│  • Schema Validation                                        │
│                                                             │
│  예상 기여: 전체 작업의 25-30%                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│           Phase 2: AI Processing (Core)                     │
│                                                             │
│  AI 필수 영역:                                              │
│  • Spec 생성 및 수정                                        │
│  • 비즈니스 로직 분석/검증                                   │
│  • 코드 생성                                                │
│  • 오류 분석 및 해결                                        │
│  • 설계 판단 및 의사결정                                    │
│                                                             │
│  예상 기여: 전체 작업의 70-75%                               │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Stage별 권장 전략

```yaml
stage_recommendations:
  stage_1_discovery:
    safe_automation:
      - "Controller/Service 파일 목록화"
      - "XML Mapper 파일 스캔"
    ai_required:
      - "5-Layer 역추적 분석"
      - "비즈니스 룰 추출"
    automation_rate: "42%"

  stage_2_validation:
    safe_automation:
      - "Ground Truth 파일 스캔"
      - "집합 비교 (Forward/Backward)"
    ai_required:
      - "Root Cause 분석"
      - "Fuzzy Matching 판단"
    automation_rate: "55%"

  stage_3_preparation:
    safe_automation:
      - "의존성 그래프 구축"
      - "Technical Debt 패턴 탐지"
    ai_required:
      - "아키텍처 설계 판단"
      - "Interface/DTO 설계"
    automation_rate: "40%"

  stage_4_generation:
    safe_automation:
      - "빌드 실행"
      - "테스트 실행"
    ai_required:
      - "코드 생성"
      - "Edge Case 처리"
    automation_rate: "49%"

  stage_5_assurance:
    safe_automation:
      - "Checkstyle/PMD 실행"
      - "점수 계산"
    ai_required:
      - "비즈니스 로직 검증"
      - "Human Approval"
    automation_rate: "44%"
```

---

## 5. Implementation Guidelines (구현 가이드)

### 5.1 스크립트 도입 기준

```yaml
adoption_criteria:
  mandatory:
    spec_impact: "없음 (100% 확실)"
    reversible: "원본 보존 필수"
    verifiable: "AI 검토 단계 포함"

  decision_matrix:
    spec_생성_수정: "NEVER - AI Only"
    파일_스캔: "ALWAYS - Script"
    빌드_실행: "ALWAYS - Script"
    코드_분석: "NEVER - AI Only"
    결과_집계: "ALWAYS - Script"
    판단_의사결정: "NEVER - Human/AI"
```

### 5.2 금지 사항 (절대 위반 불가)

```yaml
prohibited_actions:
  code_generation:
    rule: "스크립트 단독 코드 생성 금지"
    reason: "Edge Case, 비즈니스 로직 누락 위험"

  spec_modification:
    rule: "검증 없는 Spec 수정 금지"
    reason: "누락 발생 시 운영 장애 직결"

  approval_automation:
    rule: "Human Approval 자동화 금지"
    reason: "S3-04, S5-05 Gate는 사람 필수"
```

---

## 6. Best Practices

### 6.1 DO: 스크립트로 처리할 것

```yaml
safe_for_scripts:
  - "파일 스캔/목록화"
  - "단순 패턴 치환 (중첩 없는 경우)"
  - "빌드/테스트 실행"
  - "결과 수집 및 리포팅"
  - "Schema Validation"
```

### 6.2 DON'T: 스크립트로 시도하지 말 것

```yaml
ai_only_tasks:
  - "복잡한 코드 생성"
  - "비즈니스 로직 해석"
  - "컨텍스트 기반 판단"
  - "의미있는 테스트 케이스 설계"
  - "오류 원인 분석"
```

---

## 7. Conclusion

### 핵심 교훈

```yaml
key_lessons:
  lesson_1:
    title: "스크립트는 전처리 도구"
    detail: "파일 스캔, 빌드 실행 등 명확한 작업에만 효과적"

  lesson_2:
    title: "자동화율 과대평가 경계"
    detail: "초기 62% → 현실 46%, 항상 보수적 평가 필요"

  lesson_3:
    title: "투자 대비 효과 고려"
    detail: "스크립트 개발 비용 vs AI 토큰 비용 비교 필수"

  final_recommendation:
    message: "AI 토큰 비용 < Spec 누락 위험"
    strategy: "보수적 접근, 확실한 영역에만 제한 적용"
```

---

**Next**: [05-monitoring-strategies.md](05-monitoring-strategies.md) (if exists)
