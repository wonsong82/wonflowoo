# Lessons Learned

**Version**: 1.0.0
**Last Updated**: 2025-12-15

---

## 1. Overview

AI 기반 Legacy Migration 프로젝트에서 축적된 핵심 교훈을 정리합니다.

### 1.1 Categories

```yaml
lesson_categories:
  process: "워크플로우 및 프로세스 관련"
  technical: "기술적 접근 방식 관련"
  quality: "품질 보증 관련"
  tooling: "도구 및 자동화 관련"
  people: "협업 및 커뮤니케이션 관련"
```

---

## 2. Process Lessons

### 2.1 Phase Gate는 협상 불가

```yaml
lesson_PL_001:
  title: "Phase Gate는 협상 불가"
  category: "process"
  severity: "critical"

  context: |
    초기에 일정 압박으로 Phase Gate를 유연하게 적용하려 함

  problem: |
    Stage 1 Phase Gate를 느슨하게 통과시킴
    → Stage 2에서 대량의 스펙 재작업 발생
    → 전체 일정 2주 지연

  lesson: |
    Phase Gate 기준은 절대적으로 지켜야 함
    조기 발견된 문제는 저렴하게 수정 가능
    후기 발견된 문제는 기하급수적 비용 증가

  prevention:
    - "Phase Gate 기준을 프로젝트 시작 시 명확히 정의"
    - "Gate 통과 결정권자 명확히 지정"
    - "Override 절차와 문서화 의무화"
```

### 2.2 Bidirectional Validation의 가치

```yaml
lesson_PL_002:
  title: "Forward-only는 위험하다"
  category: "process"
  severity: "high"

  context: |
    Forward extraction만으로 충분하다고 생각

  problem: |
    Stage 1에서 추출한 5,600개 endpoints
    Stage 2 Source Inventory에서 5,864개 발견
    → 264개 (4.7%) 누락

  lesson: |
    Forward extraction은 LLM 해석에 의존
    Backward validation은 Ground Truth 기반
    양방향 검증으로 완전성 보장

  prevention:
    - "Stage 2를 필수 단계로 포함"
    - "Source Inventory를 자동화 도구로 구축"
    - "Coverage 비교를 정량적으로 수행"
```

### 2.3 Mini-Pilot의 중요성

```yaml
lesson_PL_003:
  title: "Mini-Pilot 없이 대량 실행 금지"
  category: "process"
  severity: "critical"

  context: |
    코드 생성 파이프라인이 동작하므로 바로 전체 실행 시도

  problem: |
    100개 Feature 생성 후 공통 패턴 오류 발견
    → 100개 모두 재생성 필요
    → 3일 작업 낭비

  lesson: |
    Mini-Pilot은 반드시 복잡도별 샘플링으로
    High/Medium/Low 각 2개씩 6개 검증
    패턴 문제 조기 발견

  prevention:
    - "Mini-Pilot을 Stage 4 필수 Phase로"
    - "복잡도별 균형 샘플링"
    - "Retrospective 후 대량 실행"
```

---

## 3. Technical Lessons

### 3.1 Dynamic SQL은 특별 처리 필요

```yaml
lesson_TL_001:
  title: "Dynamic SQL 캡처는 어렵다"
  category: "technical"
  severity: "high"

  context: |
    MyBatis XML에서 <if>, <choose>, <foreach> 태그 사용 빈도 높음

  problem: |
    정적 SQL만 캡처하면 실제 실행 쿼리와 불일치
    70%+ 쿼리가 동적 조건 포함
    → Functional Validation 대량 실패

  lesson: |
    Dynamic SQL 분석을 위한 별도 처리 필요
    모든 조건 분기 명시적 문서화
    가능한 SQL 조합 열거

  prevention:
    - "MyBatis XML 파서에 동적 태그 처리 추가"
    - "분석 스킬에 Dynamic SQL 체크리스트 포함"
    - "검증 시 조건별 SQL 비교"

  code_example: |
    <!-- Legacy -->
    <select id="selectList">
      SELECT * FROM ORDERS
      WHERE 1=1
      <if test="startDate != null">
        AND ORDER_DATE >= #{startDate}
      </if>
      <if test="endDate != null">
        AND ORDER_DATE <= #{endDate}
      </if>
    </select>

    <!-- 캡처해야 할 내용 -->
    dynamic_conditions:
      - condition: "startDate != null"
        sql: "AND ORDER_DATE >= #{startDate}"
      - condition: "endDate != null"
        sql: "AND ORDER_DATE <= #{endDate}"
```

### 3.2 Context 관리 전략

```yaml
lesson_TL_002:
  title: "LLM Context는 유한 자원"
  category: "technical"
  severity: "high"

  context: |
    대형 Feature 분석 시 모든 파일을 한번에 로드

  problem: |
    200K 토큰 컨텍스트 초과
    → 분석 중단 또는 품질 저하
    → 재시작 시 이전 맥락 손실

  lesson: |
    레이어별 점진적 로딩 필수
    중간 결과 파일로 저장
    Feature당 최대 파일 수 제한

  prevention:
    - "Layered Loading Strategy 적용"
    - "중간 결과 YAML로 persist"
    - "파일당 300 lines 제한"

  strategy: |
    1. Controller 분석 → summary 저장
    2. TaskService 분석 → business-logic 저장
    3. EntityService 분석 → dependencies 저장
    4. MyBatis 분석 → data-access 저장
    5. VO 분석 → entities 저장
    6. 최종 통합 → main.yaml 생성
```

### 3.3 Naming Convention 조기 확정

```yaml
lesson_TL_003:
  title: "Naming Convention은 Day 1에 확정"
  category: "technical"
  severity: "medium"

  context: |
    코드 생성 중간에 naming convention 변경

  problem: |
    PA domain 200개 Feature 생성 완료 후
    Controller naming 규칙 변경 결정
    → 전체 PA 코드 rename 필요

  lesson: |
    Naming convention은 코드 생성 전 확정
    Architecture Design (Stage 3 Phase 4)에서 결정
    ADR로 문서화

  prevention:
    - "Stage 3 Phase 4 완료 전 코드 생성 금지"
    - "Naming convention ADR 필수 작성"
    - "Sample 코드로 convention 검증"
```

---

## 4. Quality Lessons

### 4.1 SQL 동등성이 핵심

```yaml
lesson_QL_001:
  title: "SQL이 틀리면 전부 틀린 것"
  category: "quality"
  severity: "critical"

  context: |
    Controller, Service 코드는 완벽한데 SQL만 다름

  problem: |
    SELECT 컬럼 순서 다름 → UI 표시 오류
    WHERE 조건 누락 → 잘못된 데이터 반환
    ORDER BY 누락 → 정렬 불일치

  lesson: |
    Functional Validation에서 SQL 가중치 40%
    SQL 동등성 검증이 가장 중요
    컬럼, 조건, 조인, 정렬 모두 검증

  prevention:
    - "SQL Equivalence Score 35점 이상 필수"
    - "SQL 비교 도구 자동화"
    - "Dynamic SQL 조건별 검증"

  scoring: |
    sql_equivalence:
      weight: 40%
      breakdown:
        select_columns: 10
        where_conditions: 10
        join_structure: 10
        order_by: 5
        dynamic_sql: 5
```

### 4.2 Remediation 프로세스 필수

```yaml
lesson_QL_002:
  title: "실패는 예상하고 대비하라"
  category: "quality"
  severity: "high"

  context: |
    Validation 실패 시 ad-hoc으로 수정

  problem: |
    일관성 없는 수정 → 새로운 문제 발생
    수정 이력 없음 → 같은 문제 반복
    Root cause 미분석 → 유사 Feature 동일 실패

  lesson: |
    Remediation은 표준 프로세스로
    Root cause 분석 필수
    Pattern 기반 batch remediation

  prevention:
    - "Remediation Report 템플릿 표준화"
    - "Lessons Learned 즉시 기록"
    - "유사 Feature 일괄 적용"
```

### 4.3 First Pass Success가 효율성 결정

```yaml
lesson_QL_003:
  title: "재작업이 가장 비싸다"
  category: "quality"
  severity: "high"

  context: |
    빠른 생성 후 수정 전략 vs 신중한 첫 생성

  problem: |
    First pass success 70% → 30% 재작업
    재작업 비용 = 신규 작업의 1.5배
    전체 효율 저하

  lesson: |
    First pass success 85% 이상 목표
    Skill 품질 개선에 투자
    검증 체크리스트 사전 적용

  metrics: |
    first_pass_success:
      target: ">= 85%"
      impact:
        at_70%: "30% 재작업, 효율 손실 45%"
        at_85%: "15% 재작업, 효율 손실 22%"
        at_95%: "5% 재작업, 효율 손실 7%"
```

---

## 5. Tooling Lessons

### 5.1 Orchestration은 필수

```yaml
lesson_OL_001:
  title: "수동 관리로는 100개도 힘들다"
  category: "tooling"
  severity: "critical"

  context: |
    초기에 수동으로 Feature 하나씩 처리

  problem: |
    어디까지 했는지 파악 어려움
    상태 추적 스프레드시트 관리 부담
    실수로 중복 작업 또는 누락

  lesson: |
    912개 Feature는 반드시 자동화 필요
    Orchestrator (Choisor) 도입
    상태 관리, 순서 제어, 진행 추적

  prevention:
    - "10개 이상 Feature는 Orchestrator 필수"
    - "상태 persist 자동화"
    - "Dashboard 구축"
```

### 5.2 Checkpoint/Resume 필수

```yaml
lesson_OL_002:
  title: "중단 없이 끝까지 가는 작업은 없다"
  category: "tooling"
  severity: "high"

  context: |
    500개 Feature 생성 중 시스템 중단

  problem: |
    어디까지 완료했는지 불명확
    처음부터 다시 시작 → 시간 낭비
    부분 완료 Feature 상태 혼란

  lesson: |
    모든 작업에 checkpoint 포함
    Feature 단위 상태 저장
    안전한 resume 지원

  implementation: |
    checkpoint_strategy:
      granularity: "feature"
      persist_on:
        - "phase_complete"
        - "validation_complete"
        - "error_occurred"
      resume_from:
        - "last_successful_checkpoint"
```

### 5.3 실시간 모니터링 가치

```yaml
lesson_OL_003:
  title: "보이지 않으면 관리할 수 없다"
  category: "tooling"
  severity: "medium"

  context: |
    배치 작업 실행 후 완료까지 대기

  problem: |
    3시간 후 대량 실패 발견
    실시간 알림 없음 → 늦은 대응
    패턴 파악 지연

  lesson: |
    실시간 dashboard 구축
    임계값 기반 alerting
    Trend 분석으로 조기 감지

  monitoring: |
    real_time_metrics:
      - "processing_rate"
      - "success_rate"
      - "error_rate"
      - "queue_depth"

    alerts:
      - trigger: "error_rate > 20%"
        action: "pause_and_investigate"
      - trigger: "success_rate < 80%"
        action: "review_skill_quality"
```

---

## 6. Collaboration Lessons

### 6.1 Human-AI 역할 분담

```yaml
lesson_CL_001:
  title: "AI는 리드, Human은 검증"
  category: "people"
  severity: "high"

  context: |
    Human이 모든 결정을 내리고 AI는 실행만

  problem: |
    Human 병목 발생
    AI 능력 활용 부족
    느린 진행 속도

  lesson: |
    AI가 분석/생성 리드
    Human은 Phase Gate 검증에 집중
    Critical decision만 Human 개입

  role_distribution: |
    ai_leads:
      - "코드 분석"
      - "스펙 생성"
      - "코드 생성"
      - "초기 검증"

    human_validates:
      - "Phase Gate 승인"
      - "아키텍처 결정"
      - "비즈니스 규칙 확인"
      - "최종 품질 승인"
```

### 6.2 명확한 기준 커뮤니케이션

```yaml
lesson_CL_002:
  title: "애매한 지시는 애매한 결과"
  category: "people"
  severity: "medium"

  context: |
    "품질 좋게 해주세요" 같은 모호한 지시

  problem: |
    AI와 Human의 품질 기준 불일치
    재작업 발생
    기대 불충족

  lesson: |
    정량적 기준 명시 필수
    Score 임계값 명확히
    예시와 함께 설명

  communication_pattern: |
    # Bad
    "SQL을 잘 비교해주세요"

    # Good
    "SQL Equivalence Score 35점 이상 달성해주세요.
     비교 항목:
     - SELECT 컬럼 일치 (10점)
     - WHERE 조건 일치 (10점)
     - JOIN 구조 일치 (10점)
     - ORDER BY 일치 (5점)"
```

---

## 7. Anti-Patterns

### 7.1 절대 하지 말 것

```yaml
anti_patterns:
  AP_001:
    name: "Big Bang Approach"
    description: "전체를 한번에 처리하려는 시도"
    consequence: "제어 불가능, 품질 저하"
    alternative: "Phase별, Domain별 점진적 처리"

  AP_002:
    name: "Skip Phase Gate"
    description: "일정 압박으로 검증 건너뛰기"
    consequence: "후반 대량 재작업"
    alternative: "Phase Gate 엄격 적용"

  AP_003:
    name: "Copy-Paste Remediation"
    description: "Root cause 분석 없이 빠른 수정"
    consequence: "같은 문제 반복"
    alternative: "Pattern 분석 후 일괄 수정"

  AP_004:
    name: "Manual State Tracking"
    description: "스프레드시트로 진행 관리"
    consequence: "동기화 오류, 누락"
    alternative: "Orchestrator 사용"

  AP_005:
    name: "All-Opus Strategy"
    description: "모든 작업에 최고급 모델 사용"
    consequence: "비용 낭비"
    alternative: "Complexity 기반 모델 선택"
```

---

## 8. Success Patterns

### 8.1 권장 패턴

```yaml
success_patterns:
  SP_001:
    name: "Skill-First Approach"
    description: "SKILL.md 읽고 따르기"
    benefit: "일관된 품질, 재현 가능"

  SP_002:
    name: "Bidirectional Validation"
    description: "Forward + Backward 검증"
    benefit: "완전성 보장"

  SP_003:
    name: "Complexity-Based Model Selection"
    description: "복잡도에 따른 AI 모델 선택"
    benefit: "비용 효율성"

  SP_004:
    name: "Domain Batch Processing"
    description: "도메인 단위 일괄 처리"
    benefit: "관리 용이성"

  SP_005:
    name: "Checkpoint-Resume Pattern"
    description: "작업 단위 상태 저장"
    benefit: "안정성, 복구 가능"

  SP_006:
    name: "Pattern-Based Remediation"
    description: "유사 문제 일괄 수정"
    benefit: "효율성, 일관성"
```

---

## 9. 실제 프로젝트 적용 시 고려사항

### 9.1 초기 단계가 전체를 결정한다

```yaml
lesson_RL_001:
  title: "Stage 1 품질이 프로젝트 성패를 결정"
  category: "real_world"
  severity: "critical"

  evidence: |
    hallain_tft 프로젝트 데이터:
    - Stage 1 Coverage 95% → Stage 5 재작업률 23%
    - Stage 1 Coverage 99% → Stage 5 재작업률 5%

  impact_chain: |
    Stage 1 Controller 누락 (5%)
    → Stage 2 Gap 발견 (재분석 1일)
    → Stage 1 Phase 3-4 재작업 (3일)
    → Stage 4 재생성 (2일)
    → Stage 5 재검증 (1일)
    = 총 7일 지연 (원래 1일 검증으로 방지 가능)

  prevention: |
    Stage 1 Phase 1에서 반드시 수행:
    1. Legacy 소스에서 Controller 수 직접 카운트
    2. Inventory 수와 비교
    3. 100% 일치 확인 후 Phase 2 진행
```

### 9.2 테스트 공수 현실적 예측

```yaml
lesson_RL_002:
  title: "테스트 공수는 생성 공수의 1.5배"
  category: "real_world"
  severity: "high"

  actual_data: |
    hallain_tft 912 Features:
    - 코드 생성: 5일 (자동화)
    - 테스트 생성: 3일 (자동화)
    - 테스트 수정: 4일 (수동)
    - 통합 테스트: 3일
    = 테스트 총 10일 / 생성 5일 = 2배

  estimation_formula: |
    테스트 공수 = 생성 공수 × 1.5 ~ 2.0
    (복잡도에 따라 변동)

  breakdown:
    auto_generation: "30%"
    manual_fix: "40%"
    integration_test: "30%"
```

### 9.3 수정 공수 최소화 실전 전략

```yaml
lesson_RL_003:
  title: "수정은 생성보다 2배 비싸다"
  category: "real_world"
  severity: "high"

  evidence: |
    First pass success 70% 시나리오:
    - 700 Features 성공 → 700 × 1 = 700 단위
    - 212 Features 재작업 → 212 × 2 = 424 단위
    - 총 1124 단위 (1.6배 비용)

    First pass success 90% 시나리오:
    - 821 Features 성공 → 821 × 1 = 821 단위
    - 91 Features 재작업 → 91 × 2 = 182 단위
    - 총 1003 단위 (1.1배 비용)

  strategy: |
    First pass success 85% 이상 목표:
    1. Mini-Pilot 6개 반드시 검증
    2. Skill 품질 개선에 투자
    3. 검증 체크리스트 사전 적용
```

---

## 10. 초기 단계 품질이 전체를 결정한다 (사례)

### 10.1 Case A: Stage 1 충실 → 순조로운 진행

```yaml
case_a:
  scenario: "Stage 1 Phase Gate 엄격 적용"

  stage1_metrics:
    controller_coverage: "100%"
    sp_identification: "100%"
    dynamic_sql_classification: "완료"

  result:
    stage2_gaps: "12개 (1.3%)"
    stage4_build_success: "첫 시도 성공"
    stage5_quality_score: "93.97"
    total_rework: "5%"

  timeline: |
    계획: 4주
    실제: 4주 + 2일
    지연 원인: SP 1개 누락 → Mini-Pilot에서 발견
```

### 10.2 Case B: Stage 1 부실 → 대량 재작업

```yaml
case_b:
  scenario: "Stage 1 Phase Gate 느슨하게 적용"

  stage1_metrics:
    controller_coverage: "95%"  # 5% 누락
    sp_identification: "90%"    # 10% 누락
    dynamic_sql_classification: "미완료"

  result:
    stage2_gaps: "264개 (29%)"
    stage4_build_success: "3번째 시도"
    stage5_quality_score: "78 (Gate 실패)"
    total_rework: "35%"

  timeline: |
    계획: 4주
    실제: 6주 + 3일
    지연 원인:
    - Stage 2에서 Controller 45개 추가 발견 → Stage 1 재작업 1주
    - Stage 4에서 SP 20개 누락 발견 → 재생성 3일
    - Stage 5 Gate 실패 → Remediation 1주
```

### 10.3 비용 비교

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    초기 품질 vs 총 비용 관계                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Stage 1 Coverage │      100%      │       95%      │       90%             │
│  ──────────────────────────────────────────────────────────────────         │
│  Stage 2 Gaps     │      1-2%      │      5-10%     │     15-30%            │
│  Stage 4 Failures │      < 5%      │     10-15%     │     20-30%            │
│  Stage 5 Score    │    90+ (Pass)  │  80-85 (Risk)  │  < 80 (Fail)          │
│  Total Rework     │      5%        │      20%       │      40%              │
│  Schedule Impact  │    On-time     │   +20% delay   │  +50% delay           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. 실무 적용 시 FAQ

### Q1: Phase Gate를 유연하게 적용해도 되나요?

```yaml
answer: |
  절대 안 됩니다.

  Phase Gate 유연 적용 시 결과:
  - 단기: 1-2일 절약된 것처럼 보임
  - 중기: Stage 2-3에서 누락 발견 → 재작업
  - 장기: Stage 5 Gate 실패 → 전체 일정 2주+ 지연

  결론: Phase Gate는 "투자"이지 "비용"이 아닙니다.
```

### Q2: Mini-Pilot 없이 바로 대량 생성해도 되나요?

```yaml
answer: |
  절대 안 됩니다.

  Mini-Pilot 없이 진행 시 결과:
  - 100개 Feature 생성 후 공통 오류 발견
  - 100개 모두 재생성 필요
  - 3일 작업 낭비

  Mini-Pilot 6개 검증 시:
  - 2시간 투자
  - 패턴 오류 조기 발견
  - 수백 시간 절약

  결론: 2시간 투자로 3일을 아낄 수 있습니다.
```

### Q3: AI 결과를 믿어도 되나요?

```yaml
answer: |
  "Trust but Verify" 원칙을 적용하세요.

  신뢰해도 되는 것:
  - 코드 구조 분석
  - 패턴 인식
  - 반복 작업 자동화

  반드시 검증해야 하는 것:
  - Controller/Endpoint 수 (Legacy와 비교)
  - SP 호출 목록 (XML grep 결과와 비교)
  - SQL 동등성 (수동 샘플 검증)

  검증 비용: 전체 작업의 10%
  검증 없을 때 재작업 비용: 전체 작업의 30%+
```

### Q4: 한 도메인을 완료하고 다음으로 가야 하나요?

```yaml
answer: |
  네, 도메인 단위 완료를 권장합니다.

  이유:
  1. 완료된 도메인은 독립적으로 배포/테스트 가능
  2. 문제 발생 시 영향 범위 제한됨
  3. 진척도 측정이 명확함

  예외:
  - 도메인 간 순환 의존성이 있으면 함께 처리
  - 공통 모듈(cm)은 먼저 완료 필수
```

---

## 12. Key Takeaways

```yaml
top_5_lessons:
  1:
    title: "초기 품질이 전체를 결정한다"
    action: "Stage 1 Coverage 100% 달성 후 진행"

  2:
    title: "Phase Gate는 협상 불가"
    action: "Gate 기준 미달 시 무조건 재작업"

  3:
    title: "Mini-Pilot은 필수"
    action: "6개 Feature 검증 후 대량 생성"

  4:
    title: "재작업이 가장 비싸다"
    action: "First pass success 85% 이상 목표"

  5:
    title: "AI 결과도 검증 필요"
    action: "핵심 지표는 수동으로 Cross-check"
```

---

**Next**: [03-tips-best-practices.md](03-tips-best-practices.md) - 실용적인 팁과 모범 사례
