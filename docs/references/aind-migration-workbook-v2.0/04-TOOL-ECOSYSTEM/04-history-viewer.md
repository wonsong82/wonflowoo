# History Viewer

**Version**: 1.0.0
**Last Updated**: 2025-12-16

---

## 1. Overview

History Viewer는 Claude Code 세션 히스토리를 탐색하고 관리하는 데스크톱 애플리케이션입니다. 마이그레이션 프로젝트에서 수백~수천 개의 Claude Code 세션이 생성되므로, 체계적인 히스토리 관리가 필수적입니다.

### 1.1 History Viewer의 역할

```
┌──────────────────────────────────────────────────────────────┐
│                    HISTORY VIEWER ARCHITECTURE               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────────────────────────────────────────────┐   │
│   │                  Claude Code Sessions                │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │   │
│   │  │Session 1│  │Session 2│  │Session 3│  │Session N│  │   │
│   │  │(Feature)│  │(Feature)│  │(Feature)│  │(Feature)│  │   │
│   │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  │   │
│   └───────┼────────────┼────────────┼────────────┼───────┘   │
│           │            │            │            │           │
│           └────────────┴────────────┴────────────┘           │
│                              │                               │
│                              ▼                               │
│   ┌──────────────────────────────────────────────────────┐   │
│   │                    History Viewer                    │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │   │
│   │  │  Tree View  │  │  Search     │  │  Analytics  │   │   │
│   │  │  (Projects) │  │  (Full-text)│  │  (Tokens)   │   │   │
│   │  └─────────────┘  └─────────────┘  └─────────────┘   │   │
│   └──────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. 사용 목적

### 2.1 마이그레이션 프로젝트에서의 활용

```yaml
primary_use_cases:
  decision_tracking:
    purpose: "과거 결정사항 추적"
    scenario: "특정 Feature의 Phase 진행 중 이전 결정사항 확인"
    benefit: "일관성 유지 및 중복 작업 방지"

  pattern_analysis:
    purpose: "반복 패턴 식별"
    scenario: "유사한 Feature 처리 방식 비교"
    benefit: "워크플로우 개선 및 표준화"

  progress_monitoring:
    purpose: "Feature별 진행 상황 추적"
    scenario: "Stage/Phase별 완료율 확인"
    benefit: "프로젝트 일정 관리 및 리스크 조기 발견"

  cost_management:
    purpose: "토큰 사용량 모니터링"
    scenario: "프로젝트/세션별 비용 분석"
    benefit: "예산 관리 및 최적화"
```

### 2.2 워크플로우 통합

```
Stage 1: Discovery
  └─> History Viewer: 과거 Feature 추출 패턴 확인
      └─> 일관성 검증 및 개선점 도출

Stage 2: Validation  
  └─> History Viewer: 유사 Feature 검증 결과 참조
      └─> 검증 실패 패턴 분석

Stage 3-5: Generation/Assurance
  └─> History Viewer: 코드 생성 패턴 비교
      └─> 품질 기준 일관성 확인
```

---

## 3. 주요 기능

### 3.1 계층적 탐색

```yaml
tree_structure:
  level_1: "Project"
    description: "프로젝트 단위 그룹핑"
    example: "hallain_tft_migration"
  
  level_2: "Session"
    description: "개별 Claude Code 세션"
    example: "feature_001_discovery"
  
  metadata:
    - "timestamp"
    - "token_usage"
    - "session_duration"
```

### 3.2 전체 텍스트 검색

```yaml
search_capabilities:
  full_text_search:
    scope: "모든 세션 메시지"
    use_case: "특정 키워드/에러 메시지 검색"
    example: "Phase Gate 실패 원인 추적"

  project_filter:
    scope: "프로젝트별 필터링"
    use_case: "특정 프로젝트 세션만 검색"
    
  date_range:
    scope: "기간별 필터링"
    use_case: "최근 N일간 세션 검색"
```

### 3.3 코드 구문 강조

```yaml
code_display:
  syntax_highlighting:
    purpose: "코드 블록 가독성 향상"
    languages: "다양한 프로그래밍 언어 지원"
    benefit: "세션 내 코드 변경사항 명확히 파악"
```

### 3.4 토큰 사용량 분석

```yaml
analytics:
  project_level:
    metric: "프로젝트별 총 토큰 사용량"
    visualization: "차트/그래프"
    use_case: "프로젝트 비용 예측"
  
  session_level:
    metric: "세션별 토큰 사용량"
    visualization: "리스트/테이블"
    use_case: "비효율적 세션 식별"
  
  trend_analysis:
    metric: "시간대별 사용량 추이"
    visualization: "시계열 그래프"
    use_case: "사용 패턴 분석"
```

---

## 4. 설치 및 설정

### 4.1 설치

```bash
# GitHub 저장소 클론
git clone https://github.com/jhlee0409/claude-code-history-viewer.git
cd claude-code-history-viewer

# 의존성 설치 및 실행
npm install
npm start
```

### 4.2 히스토리 파일 위치

```yaml
history_location:
  default_path: "~/.claude/history.jsonl"
  format: "JSONL (JSON Lines)"
  structure:
    - "display: 사용자 메시지"
    - "project: 프로젝트명"
    - "timestamp: Unix timestamp (ms)"
    - "pastedContents: 코드/내용"
```

### 4.3 프로젝트별 설정

```yaml
project_configuration:
  project_naming:
    convention: "프로젝트명 일관성 유지"
    example: "{project_name}_{feature_id}_{stage}"
    benefit: "트리 구조에서 그룹핑 용이"

  session_naming:
    convention: "세션명에 Feature/Phase 정보 포함"
    example: "feature_001_discovery_phase_1"
    benefit: "검색 및 필터링 효율성 향상"
```

---

## 5. 실제 활용 사례

### 5.1 결정사항 추적

```
시나리오: Feature 001의 Phase 2에서 특정 아키텍처 결정이 있었는지 확인

1. History Viewer 실행
2. 프로젝트 트리에서 대상 워크스페이스 선택
3. 검색창에 "Feature 001 Phase 2 architecture" 입력
4. 관련 세션 목록 확인
5. 해당 세션 열어서 결정사항 확인
```

### 5.2 패턴 분석

```
시나리오: Stage 1 Discovery Phase에서 반복되는 문제 패턴 식별

1. 검색: "discovery phase error"
2. 결과 세션들을 시간순으로 정렬
3. 공통 에러 메시지/패턴 식별
4. 워크플로우 개선점 도출
```

### 5.3 비용 최적화

```
시나리오: 토큰 사용량이 비정상적으로 높은 세션 찾기

1. Analytics 탭에서 프로젝트별 토큰 사용량 확인
2. 세션별 사용량 정렬 (내림차순)
3. 상위 10개 세션 분석
4. 비효율적 패턴 식별 및 개선
```

---

## 6. 워크북 통합

### 6.1 Phase Gate 검증 시 활용

```yaml
phase_gate_validation:
  before_phase:
    action: "유사 Feature의 동일 Phase 결과 확인"
    tool: "History Viewer 검색"
    benefit: "예상 문제 사전 파악"
  
  after_phase:
    action: "Phase 완료 세션 기록 확인"
    tool: "History Viewer Analytics"
    benefit: "Phase별 평균 토큰 사용량 파악"
```

### 6.2 Remediation 시 활용

```yaml
remediation_support:
  error_analysis:
    action: "과거 유사 에러 처리 방식 확인"
    tool: "History Viewer 검색"
    benefit: "검증된 해결 방법 적용"
  
  pattern_matching:
    action: "동일 에러 패턴 세션 그룹화"
    tool: "History Viewer 필터링"
    benefit: "근본 원인 분석"
```

---

## 7. Best Practices

### 7.1 세션 명명 규칙

```yaml
naming_convention:
  format: "{project}_{feature_id}_{stage}_{phase}"
  example: "hallain_tft_feature_001_stage1_phase1"
  benefit: "트리 구조에서 자동 그룹핑"
```

### 7.2 정기적 리뷰

```yaml
review_schedule:
  daily: "당일 세션 토큰 사용량 확인"
  weekly: "주간 패턴 분석 및 개선점 도출"
  monthly: "월간 비용 분석 및 예산 조정"
```

### 7.3 검색 전략

```yaml
search_strategies:
  specific_queries:
    tip: "Feature ID, Phase 번호 등 구체적 키워드 사용"
    example: "feature_001 phase_2 validation"
  
  error_tracking:
    tip: "에러 메시지 전체 또는 핵심 부분 검색"
    example: "Phase Gate failed"
  
  decision_tracking:
    tip: "결정 키워드와 함께 검색"
    example: "architecture decision feature_001"
```

---

## 8. 제한사항 및 고려사항

### 8.1 제한사항

```yaml
limitations:
  file_size:
    issue: "대규모 프로젝트에서 history.jsonl 파일 크기 증가"
    mitigation: "정기적 아카이빙 또는 분할 관리"
  
  search_performance:
    issue: "수천 개 세션에서 검색 속도 저하"
    mitigation: "프로젝트/기간 필터 활용"
```

### 8.2 보안 고려사항

```yaml
security:
  sensitive_data:
    warning: "히스토리에 민감한 정보 포함 가능"
    recommendation: "프로덕션 환경에서 주의"
  
  access_control:
    warning: "로컬 파일 접근 필요"
    recommendation: "개인 기기에서만 사용"
```

---

**Repository**: https://github.com/jhlee0409/claude-code-history-viewer

**Next**: [05-EXECUTION-PATTERNS](../05-EXECUTION-PATTERNS/01-batch-processing.md)