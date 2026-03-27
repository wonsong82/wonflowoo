# Troubleshooting Guide

**Version**: 1.0.0
**Last Updated**: 2025-12-15

---

## 1. Common Issues by Stage

### 1.1 Stage 1: Discovery Issues

#### Issue: Incomplete Endpoint Extraction

```yaml
issue:
  symptom: "추출된 endpoints 수가 예상보다 적음"
  expected: ">= 5,600"
  actual: "< 5,000"

diagnosis:
  - check: "Controller 파일 패턴 확인"
    command: "find . -name '*Controller.java' | wc -l"

  - check: "@RequestMapping 패턴 확인"
    pattern: "@RequestMapping.*\\.mi"

  - check: "Non-standard controller 확인"
    examples:
      - "*Handler.java"
      - "*Action.java"

resolution:
  - "Controller 패턴 확장"
  - "누락된 패턴 추가 스캔"
  - "Stage 2 Phase 1에서 Ground Truth와 비교"
```

#### Issue: Layer Trace Incomplete

```yaml
issue:
  symptom: "4-layer 추적 실패 (TS/ES 연결 불가)"
  frequency: "10%+ features"

diagnosis:
  - check: "Interface-Implementation 매핑 확인"
  - check: "패키지 구조 불일치"
  - check: "외부 의존성 (benitware.framework)"

resolution:
  - action: "수동 매핑 테이블 구축"
    for: "비표준 패턴"

  - action: "외부 JAR 분석"
    for: "benitware.framework 의존성"

  - action: "Partial trace 허용 + 문서화"
    for: "해결 불가 케이스"
```

#### Issue: Context Limit Exceeded

```yaml
issue:
  symptom: "대형 Feature 분석 중 컨텍스트 초과"
  error: "Context budget exceeded"

diagnosis:
  - check: "Feature 크기 확인"
    threshold: "> 30 files"

  - check: "단일 파일 크기"
    threshold: "> 1000 lines"

resolution:
  - action: "Layered Loading 적용"
    strategy: "Layer별 순차 분석"

  - action: "중간 결과 저장"
    format: "YAML persist"

  - action: "Feature 분할 검토"
    condition: "너무 큰 Feature"
```

---

### 1.2 Stage 2: Validation Issues

#### Issue: High Missing Rate

```yaml
issue:
  symptom: "Stage 1 스펙 대비 Source Inventory 누락률 높음"
  threshold: "> 5%"

diagnosis:
  - check: "추출 도구 정확성"
  - check: "URL 정규화 불일치"
  - check: "동적 URL 패턴"

resolution:
  critical: "누락률 > 10%"
  action: "Stage 1 재실행"

  moderate: "누락률 5-10%"
  action: "Gap Analysis + Spec Completion"

  acceptable: "누락률 < 5%"
  action: "Batch remediation"
```

#### Issue: Spec Standardization Failures

```yaml
issue:
  symptom: "YAML 구조 불일치로 비교 실패"
  examples:
    - "endpoint_id vs endpoint"
    - "중첩 구조 불일치"

diagnosis:
  - check: "Stage 1 생성 스킬 버전"
  - check: "표준 구조 정의 확인"

resolution:
  - action: "Spec Standardization 스킬 실행"
    target: "불일치 파일"

  - action: "자동 변환 스크립트"
    for: "대량 불일치"

  - action: "표준 구조 강제"
    timing: "Stage 1 Phase 3"
```

---

### 1.3 Stage 4: Generation Issues

#### Issue: Build Failure

```yaml
issue:
  symptom: "생성된 코드 컴파일 실패"
  frequency: "Feature 단위"

diagnosis:
  - check: "Import 문 누락/오류"
    pattern: "Cannot find symbol"

  - check: "타입 불일치"
    pattern: "incompatible types"

  - check: "메서드 시그니처 불일치"
    pattern: "method does not exist"

resolution:
  import_error:
    - "Package structure 확인"
    - "공통 모듈 의존성 확인"

  type_error:
    - "VO 필드 타입 검토"
    - "Legacy 타입 매핑 확인"

  method_error:
    - "Interface-Implementation 동기화"
    - "Spec 재검토"
```

#### Issue: Test Failures

```yaml
issue:
  symptom: "단위 테스트 실패"
  type: "assertion_failure | exception"

diagnosis:
  assertion_failure:
    - check: "기대값 vs 실제값 비교"
    - check: "테스트 데이터 정확성"

  exception:
    - check: "NullPointerException 위치"
    - check: "Configuration 누락"

resolution:
  - action: "테스트 데이터 수정"
    for: "데이터 불일치"

  - action: "Null 체크 추가"
    for: "NPE"

  - action: "Mock 설정 확인"
    for: "의존성 오류"
```

---

### 1.4 Stage 5: Validation Issues

#### Issue: Low SQL Equivalence Score

```yaml
issue:
  symptom: "SQL Equivalence < 30 (40점 만점)"
  impact: "FAIL 판정"

diagnosis:
  - check: "SELECT 컬럼 불일치"
    severity: "high"

  - check: "WHERE 조건 누락"
    severity: "critical"

  - check: "JOIN 구조 차이"
    severity: "high"

  - check: "Dynamic SQL 누락"
    severity: "critical"

resolution:
  column_mismatch:
    - "Legacy SQL에서 컬럼 목록 추출"
    - "생성된 Mapper 수정"

  where_missing:
    - "동적 조건 태그 추가"
    - "<if>, <choose> 확인"

  join_difference:
    - "JOIN 순서 및 조건 맞춤"

  dynamic_sql:
    - "MyBatis XML 직접 비교"
    - "모든 <if> 조건 포함"
```

#### Issue: Critical Issues Found

```yaml
issue:
  symptom: "Critical 이슈 발견으로 FAIL"
  examples:
    - "필수 비즈니스 로직 누락"
    - "데이터 타입 불일치"
    - "주요 SQL 불일치"

diagnosis:
  - check: "이슈 상세 내용 확인"
  - check: "영향 범위 파악"
  - check: "Root cause 분석"

resolution:
  immediate:
    - "Critical 이슈 우선 수정"
    - "재검증 실행"

  pattern_based:
    - "유사 Feature 확인"
    - "Batch remediation"

  escalation:
    - "3회 실패 시 escalate"
    - "Domain expert 검토"
```

---

## 2. Orchestrator Issues

### 2.1 Choisor Issues

#### Issue: Session State Corruption

```yaml
issue:
  symptom: "세션 상태 불일치 또는 손상"
  error: "Invalid session state"

diagnosis:
  - check: "sessions.json 파일 무결성"
  - check: "동시 세션 충돌"
  - check: "비정상 종료 여부"

resolution:
  - action: "세션 상태 초기화"
    command: "choisor reset --session {id}"

  - action: "마지막 체크포인트에서 복구"
    command: "choisor resume --from-checkpoint"

  - action: "세션 재생성"
    command: "choisor new-session --feature {id}"
```

#### Issue: Phase Transition Failure

```yaml
issue:
  symptom: "Phase 완료 후 다음 Phase로 전환 안됨"
  mode: "auto-to-max"

diagnosis:
  - check: "Phase Gate 결과"
  - check: "필수 출력 파일 존재"
  - check: "오류 로그"

resolution:
  gate_failure:
    - "Gate 조건 확인"
    - "필요 시 remediation"

  missing_output:
    - "출력 파일 수동 생성"
    - "Phase 재실행"

  system_error:
    - "로그 확인 후 재시도"
    - "수동 Phase 진행"
```

### 2.2 Parallel Execution Issues

#### Issue: Resource Contention

```yaml
issue:
  symptom: "병렬 실행 시 성능 저하 또는 오류"
  cause: "리소스 경합"

diagnosis:
  - check: "동시 세션 수"
    threshold: "> 4"

  - check: "메모리 사용량"
  - check: "API rate limits"

resolution:
  - action: "동시 세션 수 제한"
    recommendation: "max 4"

  - action: "Rate limiting 적용"
    delay: "1-2 seconds between requests"

  - action: "리소스 모니터링"
    metrics: ["memory", "cpu", "api_calls"]
```

#### Issue: Dependency Violation

```yaml
issue:
  symptom: "의존성 순서 위반으로 실패"
  error: "Dependency not satisfied"

diagnosis:
  - check: "Priority Group 순서"
    order: "P0 → P1 → P2 → P3"

  - check: "Cross-domain 의존성"
  - check: "실행 순서 로그"

resolution:
  - action: "의존성 그래프 확인"
    source: "stage3-outputs/phase1/dependency-graph/"

  - action: "실행 순서 조정"
    constraint: "의존성 선행 완료"

  - action: "순차 실행으로 전환"
    for: "복잡한 의존성"
```

---

## 3. Quality Issues

### 3.1 Score Below Threshold

```yaml
issue:
  symptom: "Validation score < 70"
  decision: "FAIL"

diagnosis:
  - check: "차원별 점수 분석"
    dimensions:
      - "endpoint_equivalence (25)"
      - "sql_equivalence (40)"
      - "business_logic (20)"
      - "data_model (15)"

  - check: "Critical 이슈 존재"
  - check: "가장 낮은 차원"

resolution:
  low_sql_score:
    - "SQL 직접 비교"
    - "동적 SQL 확인"
    - "Mapper 수정"

  low_endpoint_score:
    - "URL 패턴 확인"
    - "HTTP 메서드 확인"
    - "파라미터 매핑"

  low_logic_score:
    - "비즈니스 로직 추적"
    - "검증 규칙 확인"
    - "계산 로직 검증"
```

### 3.2 Remediation Loops

```yaml
issue:
  symptom: "수정 → 검증 → 실패 반복"
  count: "> 3 attempts"

diagnosis:
  - check: "Root cause 정확성"
  - check: "수정 범위 충분성"
  - check: "Side effect 발생"

resolution:
  - action: "Root cause 재분석"
    method: "Legacy 코드 직접 검토"

  - action: "Domain expert 검토 요청"
    trigger: "3회 실패"

  - action: "전체 Feature 재생성 검토"
    trigger: "5회 실패"
```

---

## 4. Environment Issues

### 4.1 API Rate Limiting

```yaml
issue:
  symptom: "API 호출 제한 오류"
  error: "429 Too Many Requests"

diagnosis:
  - check: "분당 호출 수"
  - check: "동시 세션 수"
  - check: "토큰 사용량"

resolution:
  - action: "Rate limit 대기"
    delay: "exponential backoff"

  - action: "동시성 감소"
    max_concurrent: 2

  - action: "배치 크기 조정"
    recommendation: "smaller batches"
```

### 4.2 Memory Issues

```yaml
issue:
  symptom: "OutOfMemoryError 또는 시스템 느려짐"

diagnosis:
  - check: "대형 파일 로드"
  - check: "누적 세션 데이터"
  - check: "로그 파일 크기"

resolution:
  - action: "세션 정리"
    command: "choisor cleanup --completed"

  - action: "로그 로테이션"
    retention: "7 days"

  - action: "청크 단위 처리"
    for: "대형 Feature"
```

---

## 5. Emergency Procedures

### 5.1 Complete Reset

```yaml
emergency_reset:
  trigger: "복구 불가능한 상태"

  steps:
    - step: 1
      action: "현재 상태 백업"
      command: "cp -r stage{N}-outputs/ backup/"

    - step: 2
      action: "세션 전체 초기화"
      command: "choisor reset --all"

    - step: 3
      action: "마지막 알려진 좋은 상태로 복원"
      command: "cp -r backup/checkpoint-{N}/ stage{N}-outputs/"

    - step: 4
      action: "검증 후 재시작"

  caution: "데이터 손실 가능, 최후 수단으로만 사용"
```

### 5.2 Rollback Procedure

```yaml
rollback_procedure:
  trigger: "Stage 완료 후 심각한 문제 발견"

  steps:
    - step: 1
      action: "현재 Stage 출력 보존"
      path: "stage{N}-outputs-{timestamp}/"

    - step: 2
      action: "이전 Phase로 롤백"
      method: "checkpoint restore"

    - step: 3
      action: "문제 원인 분석"
      document: "rollback-analysis.md"

    - step: 4
      action: "수정된 Skill로 재실행"
```

---

## 6. Diagnostic Commands

### 6.1 System Health Check

```bash
# 프로젝트 구조 확인
tree -L 2 stage{N}-outputs/

# Feature 상태 확인
cat .choisor/sessions/sessions.json | jq '.features[] | select(.status != "completed")'

# 최근 오류 확인
grep -r "ERROR\|FAIL" stage{N}-outputs/ | tail -20

# 진행률 확인
find stage{N}-outputs/ -name "*.yaml" | wc -l
```

### 6.2 Validation Quick Check

```bash
# YAML 문법 검증
find stage{N}-outputs/ -name "*.yaml" -exec yamllint {} \;

# 필수 파일 존재 확인
for feat in FEAT-PA-*; do
  [ -f "$feat/main.yaml" ] || echo "Missing: $feat/main.yaml"
done

# 점수 분포 확인
grep -r "overall:" stage5-outputs/phase2/ | \
  awk -F'score:' '{print $2}' | sort -n | uniq -c
```

---

## 7. Support Resources

### 7.1 Log Locations

```yaml
log_locations:
  choisor: ".choisor/logs/"
  session: ".choisor/sessions/"
  validation: "stage{N}-outputs/logs/"
  error: "stage{N}-outputs/errors/"
```

### 7.2 Documentation References

```yaml
documentation:
  methodology: "docs/workbook/"
  skills: ".claude/skills/"
  project: "CLAUDE.md"
  status: "PROJECT_STATUS.md"
```

### 7.3 Escalation Path

```yaml
escalation_path:
  level_1:
    scope: "Feature-level issues"
    action: "Self-remediation using this guide"

  level_2:
    scope: "Domain-level patterns"
    action: "Batch remediation, Skill improvement"

  level_3:
    scope: "System-level issues"
    action: "Architecture review, Process change"
```

---

**End of Troubleshooting Guide**
