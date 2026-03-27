# AIND Migration Workbook 개발자 교육 커리큘럼

**Version**: 1.0.0
**Last Updated**: 2025-12-18
**교육 기간**: 2주 (10 워킹데이)
**대상**: 중급 이상 개발자 (AI 활용 경험 다양)
**형태**: 집합 오프라인 교육 (전일제, 이론 + 실습)

---

## 교육 목표

### 최종 역량 목표
교육 수료 후 수강생은 다음을 수행할 수 있다:
- AIND Migration 방법론 전체를 이해하고 설명할 수 있다
- 레거시 시스템 마이그레이션 프로젝트를 직접 설계하고 리드할 수 있다
- AI 스킬을 작성하고 커스터마이징하여 실무에 적용할 수 있다

### 학습 목표 (KSA)

| 구분 | 목표 |
|------|------|
| **Knowledge** | 5-Stage 방법론 철학, Stage-Phase 모델, 스킬 구조, 품질 게이트 개념 |
| **Skill** | 레거시 분석, 워크플로우 설계, 스킬 작성, Claude Code 활용, 오케스트레이터 운영 |
| **Attitude** | 명세 우선 사고, AI+Human 협업 마인드, 품질 우선(Quality Over Speed) |

---

## 전체 구조

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AIND Migration 교육 커리큘럼                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Week 1: 핵심 방법론]                                                   │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐                    │
│  │  Day 1  │  Day 2  │  Day 3  │  Day 4  │  Day 5  │                    │
│  │ Overview│Assessment│Assessment│Workflow │Workflow │                    │
│  │ +Setup  │   (1)   │   (2)   │ Design  │ Design  │                    │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘                    │
│                                                                         │
│  [Week 2: 실무 적용]                                                     │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐                    │
│  │  Day 6  │  Day 7  │  Day 8  │  Day 9  │  Day 10 │                    │
│  │  Skill  │  Skill  │Tool+Exec│QA+Case  │Mini Proj│                    │
│  │   (1)   │   (2)   │ Pattern │ Study   │+발표    │                    │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Day 1: 방법론 전체 소개 + 환경 설정

**워크북 섹션**: 00-OVERVIEW, 환경 설정
**학습 목표**: 방법론 철학 이해, 실습 환경 구축

### 오전 (09:00-12:00)

#### 09:00-10:30 | 레거시 마이그레이션의 도전과제
- **강의** (60분)
  - 왜 레거시 마이그레이션이 어려운가?
  - 전통적 마이그레이션 방식의 한계
  - AI 활용 마이그레이션의 가능성과 현실
- **토론** (30분)
  - 참가자별 레거시 마이그레이션 경험 공유
  - 겪었던 문제점 및 Pain Point 정리

#### 10:45-12:00 | AIND Migration 방법론 철학
- **강의** (60분)
  - 핵심 가치: "신규 서비스는 레거시 시스템의 모든 동작을 보장"
  - 4대 원칙:
    1. Specification-First (명세 우선)
    2. Bidirectional Validation (양방향 검증)
    3. AI + Human Collaboration (AI-Human 협업)
    4. Quality Over Speed (품질 우선)
  - 5-Stage Migration Lifecycle 개요
- **Q&A** (15분)

### 오후 (13:00-18:00)

#### 13:00-14:30 | 5-Stage 모델 상세 이해
- **강의** (60분)
  - Stage 1: Discovery (발견/이해)
  - Stage 2: Validation (검증)
  - Stage 3: Preparation (준비)
  - Stage 4: Generation (생성)
  - Stage 5: Assurance (보증)
  - Phase Gate 개념 소개
- **워크샵** (30분)
  - 각 Stage의 핵심 질문과 산출물 정리
  - 실제 프로젝트에 적용 시나리오 토론

#### 14:45-16:30 | 실습 환경 설정
- **실습** (105분)
  - Claude Code 설치 및 API 설정
  - 실습용 레거시 코드베이스 클론
  - 프로젝트 구조 탐색
  - 기본 명령어 실행 테스트
  - CLAUDE.md 파일 이해

#### 16:45-18:00 | 워크북 구조 및 Day 1 정리
- **강의** (45분)
  - 워크북 7개 섹션 구조 설명
  - 각 섹션의 역할과 관계
  - 교육 과정 전체 로드맵
- **실습** (30분)
  - 워크북 문서 탐색 및 북마크
  - Day 2 준비사항 안내

### Day 1 산출물
- [ ] Claude Code 설치 및 동작 확인
- [ ] 실습용 레거시 코드베이스 접근 확인
- [ ] 방법론 핵심 개념 정리 노트

---

## Day 2: Assessment (1) - 레거시 분석 기초

**워크북 섹션**: 01-ASSESSMENT (01-legacy-analysis-checklist.md)
**학습 목표**: 레거시 분석 체크리스트 이해 및 적용

### 오전 (09:00-12:00)

#### 09:00-10:30 | Assessment 개요 및 Codebase Profiling
- **강의** (45분)
  - Assessment의 목적과 중요성
  - 14개 Assessment Task 개요
  - Codebase Profiling 방법론
    - Basic Statistics (파일 수, LOC, 패키지 수)
    - Architecture Pattern Identification
    - Framework & Library Inventory
- **데모** (45분)
  - cloc, find 명령어를 활용한 코드베이스 통계
  - 실습 레거시 시스템 프로파일링 시연

#### 10:45-12:00 | 실습: Codebase Profiling
- **실습** (75분)
  - ASSESS-001: 기본 통계 수집
  - ASSESS-002: 아키텍처 패턴 식별
  - ASSESS-003: 프레임워크/라이브러리 인벤토리
  - 결과물 작성 및 공유

### 오후 (13:00-18:00)

#### 13:00-14:30 | Domain Decomposition
- **강의** (45분)
  - 도메인 경계 식별 방법
  - 도메인 간 의존성 분석
  - Priority Classification (P0-P3)
- **실습** (45분)
  - ASSESS-004: 도메인 경계 식별
  - ASSESS-005: 의존성 매트릭스 작성
  - ASSESS-006: 우선순위 분류

#### 14:45-16:30 | Component Analysis
- **강의** (30분)
  - Controller/Endpoint 분석
  - Service Layer 분석
  - Persistence Layer 분석
  - Data Model 분석
- **실습** (75분)
  - ASSESS-007: 엔드포인트 추출
  - ASSESS-008: 서비스 레이어 구조 분석
  - ASSESS-009: MyBatis Mapper 분석
  - ASSESS-010: VO/DTO 클래스 분석

#### 16:45-18:00 | Day 2 실습 결과 리뷰
- **발표** (45분)
  - 팀별 분석 결과 발표
  - 피드백 및 토론
- **정리** (30분)
  - Day 2 핵심 내용 정리
  - Day 3 예고 (Technical Debt, Complexity)

### Day 2 산출물
- [ ] Codebase Profile 문서 (통계, 아키텍처, 프레임워크)
- [ ] 도메인 분해 및 의존성 매트릭스
- [ ] Component 분석 결과 (Endpoint, Service, Mapper, VO)

---

## Day 3: Assessment (2) - 복잡도 추정 및 실현 가능성 평가

**워크북 섹션**: 01-ASSESSMENT (02-complexity-estimation.md, 03-feasibility-matrix.md)
**학습 목표**: 복잡도 추정, Go/No-Go 결정 능력 확보

### 오전 (09:00-12:00)

#### 09:00-10:30 | Technical Debt & External Dependencies
- **강의** (30분)
  - Dead Code 탐지 방법
  - Code Quality Issues 식별
  - Database Dependencies 분석
  - External System Integration 파악
- **실습** (60분)
  - ASSESS-011: Dead Code 탐지
  - ASSESS-012: 정적 분석 도구 활용
  - ASSESS-013: DB 의존성 분석
  - ASSESS-014: 외부 시스템 연동 목록화

#### 10:45-12:00 | Complexity Estimation
- **강의** (45분)
  - 3-Tier 복잡도 모델 (HIGH/MEDIUM/LOW)
  - 복잡도 요소별 가중치
    - Stored Procedure 비율
    - Dynamic SQL 복잡도
    - External Integration 수
    - Custom Framework 의존도
  - 복잡도 점수 계산 방법
- **워크샵** (30분)
  - 실습 레거시 시스템 복잡도 추정
  - 점수 산출 및 논의

### 오후 (13:00-18:00)

#### 13:00-14:30 | Feasibility Matrix
- **강의** (45분)
  - Go/No-Go 결정 프레임워크
  - 실현 가능성 평가 기준
    - 기술적 실현 가능성
    - 리소스 가용성
    - 리스크 수준
  - Decision Tree 활용법
- **워크샵** (45분)
  - 실습 시스템 Feasibility Matrix 작성
  - Go/No-Go 결정 시뮬레이션

#### 14:45-16:30 | Assessment Report 작성
- **강의** (30분)
  - Assessment Summary Report 구조
  - 템플릿 활용법
  - 보고서 작성 베스트 프랙티스
- **실습** (75분)
  - legacy-assessment-report.yaml 작성
  - 전체 Assessment 결과 통합
  - 마이그레이션 전략 권고안 작성

#### 16:45-18:00 | Assessment 종합 발표
- **발표** (60분)
  - 팀별 Assessment Report 발표
  - Go/No-Go 결정 및 근거 설명
  - 교차 피드백
- **정리** (15분)
  - Assessment 단계 핵심 체크리스트
  - Week 1 전반 복습

### Day 3 산출물
- [ ] Technical Debt 분석 결과
- [ ] Complexity Score 및 산출 근거
- [ ] Feasibility Matrix 및 Go/No-Go 결정
- [ ] Assessment Summary Report (YAML)

---

## Day 4: Workflow Design (1) - Stage-Phase 모델 이해

**워크북 섹션**: 02-WORKFLOW-DESIGN (01-stage-phase-model.md)
**학습 목표**: Stage-Phase 계층 구조 설계 능력 확보

### 오전 (09:00-12:00)

#### 09:00-10:30 | Stage-Phase 계층 구조
- **강의** (60분)
  - 4-Level 계층: Project → Stage → Phase → Task → Skill
  - 각 Level의 정의와 특성
  - Stage-Phase Sequencing Rules
    - Rule 1: Sequential within Stage
    - Rule 2: Stage Gate between Stages
    - Rule 3: Parallel Tasks within Phase
    - Rule 4: Phase Gate before Advance
- **워크샵** (30분)
  - 계층 구조 다이어그램 그리기
  - 실제 프로젝트 매핑 연습

#### 10:45-12:00 | 5-Stage 모델 심화
- **강의** (45분)
  - Stage별 상세 분석
    - Stage 1: Discovery (3 Phases)
    - Stage 2: Validation (4 Phases)
    - Stage 3: Preparation (6 Phases)
    - Stage 4: Generation (4 Phases)
    - Stage 5: Assurance (5 Phases)
  - 각 Stage의 Question, Outputs, Success Criteria
- **실습** (30분)
  - 워크북 stage-phase-model.md 분석
  - Stage별 Phase 목록 정리

### 오후 (13:00-18:00)

#### 13:00-14:30 | Phase Design Patterns
- **강의** (45분)
  - 5가지 Phase 유형
    - Inventory Phase (Discovery/Collection)
    - Analysis Phase (Deep Dive)
    - Generation Phase (Creation)
    - Validation Phase (Verification)
    - Integration Phase (Consolidation)
  - 유형별 특성 및 적용 시점
- **워크샵** (45분)
  - 실습 프로젝트의 Phase 유형 분류
  - Phase 순서 최적화 토론

#### 14:45-16:30 | Task Lifecycle & Phase Gate
- **강의** (45분)
  - Task Granularity (Feature 단위)
  - Task Lifecycle States
    - PENDING → ASSIGNED → IN_PROGRESS → VALIDATING → COMPLETED
    - 예외: FAILED, REJECTED, RETRYING, TIMEOUT
  - Phase Gate 개념 및 구성요소
  - Gate Enforcement Flow
- **실습** (60분)
  - Task 정의 연습 (Feature ID 부여)
  - Phase Gate Rules 작성 연습
  - Gate 통과/실패 시나리오 시뮬레이션

#### 16:45-18:00 | Output Structure 설계
- **강의** (30분)
  - 디렉토리 구조 표준
  - Priority-Based Grouping (P0-P3)
  - 파일 네이밍 규칙
- **실습** (45분)
  - 실습 프로젝트 Output 디렉토리 구조 설계
  - config.yaml 초안 작성

### Day 4 산출물
- [ ] Stage-Phase 계층 다이어그램
- [ ] Phase 유형 분류표
- [ ] Task 정의서 (샘플 Feature 3-5개)
- [ ] Phase Gate Rules 초안
- [ ] Output 디렉토리 구조 설계서

---

## Day 5: Workflow Design (2) - 커스터마이제이션 & Decision Tree

**워크북 섹션**: 02-WORKFLOW-DESIGN (02-customization-guide.md, 03-decision-trees.md)
**학습 목표**: 프로젝트별 워크플로우 커스터마이징 능력

### 오전 (09:00-12:00)

#### 09:00-10:30 | Workflow Customization
- **강의** (45분)
  - 커스터마이제이션 포인트
    - Stage 추가/병합/스킵
    - Phase 추가/순서 변경
    - Gate Rule 수정
    - Task 병렬/순차 조정
  - 프로젝트 특성별 커스터마이제이션 전략
    - 소규모 vs 대규모
    - Rehosting vs Refactoring vs Rewriting
- **사례 연구** (45분)
  - hallain_tft 프로젝트 커스터마이제이션 사례
  - 의사결정 근거 분석

#### 10:45-12:00 | Decision Trees
- **강의** (45분)
  - Decision Tree의 역할
  - 주요 결정 포인트
    - Stage 진입 결정
    - Phase 스킵 결정
    - 병렬/순차 실행 결정
    - Remediation 전략 결정
  - Decision Tree 작성 방법
- **실습** (30분)
  - 워크북 decision-trees.md 분석
  - 핵심 Decision Tree 이해

### 오후 (13:00-18:00)

#### 13:00-14:30 | 실습: 워크플로우 설계
- **실습** (90분)
  - 실습 레거시 시스템용 워크플로우 설계
  - Stage 선택 및 커스터마이제이션
  - Phase 구성 및 Gate 정의
  - Task 병렬화 전략 수립

#### 14:45-16:30 | config.yaml 작성
- **강의** (30분)
  - config.yaml 구조 상세
  - 설정 옵션별 의미
  - 실제 config 예시 분석
- **실습** (75분)
  - 프로젝트용 config.yaml 완성
  - Stage/Phase 설정
  - Phase Gate 설정
  - Execution 설정

#### 16:45-18:00 | Workflow Design 발표 및 리뷰
- **발표** (60분)
  - 팀별 워크플로우 설계 발표
  - config.yaml 리뷰
  - 피드백 및 개선점 토론
- **정리** (15분)
  - Week 1 종합 정리
  - Week 2 예고

### Day 5 산출물
- [ ] 커스터마이징된 Stage-Phase 구조
- [ ] Decision Tree (프로젝트 맞춤)
- [ ] config.yaml (완성본)
- [ ] 워크플로우 설계 문서

---

## Day 6: Skill Definition (1) - 스킬 구조 이해

**워크북 섹션**: 03-SKILL-DEFINITION (01-skill-structure.md)
**학습 목표**: SKILL.md 구조 이해 및 분석 능력

### 오전 (09:00-12:00)

#### 09:00-10:30 | Skill 개요 및 구조
- **강의** (60분)
  - Skill의 정의와 역할
  - Skill 특성: Deterministic, Self-contained, Composable
  - Skill 디렉토리 구조
  - Naming Convention (stage{N}-phase{N}-{name})
  - SKILL.md 7개 필수 섹션
    1. Overview
    2. Prerequisites
    3. Methodology
    4. Outputs
    5. Quality Checks
    6. Error Handling
    7. Examples
- **실습** (30분)
  - 워크북 제공 Skill 예시 분석
  - 섹션별 역할 파악

#### 10:45-12:00 | Skill 섹션 상세: Overview & Prerequisites
- **강의** (45분)
  - Overview 작성 가이드
    - Purpose (목적)
    - Scope (범위: In/Out of scope)
    - Core Principles (핵심 원칙)
    - Relationship (선행/후행 Skill)
  - Prerequisites 작성 가이드
    - Phase Dependencies
    - Input Requirements
    - Environment
- **워크샵** (30분)
  - 샘플 Skill의 Overview/Prerequisites 분석
  - 개선점 토론

### 오후 (13:00-18:00)

#### 13:00-14:30 | Skill 섹션 상세: Methodology & Outputs
- **강의** (45분)
  - Methodology 작성 가이드
    - Execution Model (sequential/parallel/hybrid)
    - Steps (단계별 상세)
    - Decision Points
  - Outputs 작성 가이드
    - Directory 구조
    - Files 명세
    - File Header
- **워크샵** (45분)
  - Methodology 작성 연습
  - Outputs 스펙 작성 연습

#### 14:45-16:30 | Skill 섹션 상세: Quality Checks & Error Handling
- **강의** (45분)
  - Quality Checks 작성 가이드
    - Automated Checks
    - Manual Reviews
    - Metrics
  - Error Handling 작성 가이드
    - Known Issues
    - Escalation
    - Recovery
- **실습** (60분)
  - 기존 Skill의 Quality Checks 분석
  - Error Handling 시나리오 작성

#### 16:45-18:00 | Skill Types 및 Dependencies
- **강의** (45분)
  - 4가지 Skill 유형
    - Analysis Skills (분석)
    - Generation Skills (생성)
    - Validation Skills (검증)
    - Transformation Skills (변환)
  - Skill Dependencies 관리
  - Skill Execution Context (변수)
- **정리** (30분)
  - Day 6 핵심 내용 정리
  - Day 7 실습 준비

### Day 6 산출물
- [ ] Skill 구조 분석 노트
- [ ] 샘플 Skill Overview/Prerequisites 작성
- [ ] Methodology/Outputs 스펙 초안
- [ ] Quality Checks/Error Handling 초안

---

## Day 7: Skill Definition (2) - 스킬 개발 실습

**워크북 섹션**: 03-SKILL-DEFINITION (02-skill-catalog.md, 03-skill-development.md)
**학습 목표**: 실제 SKILL.md 작성 및 테스트

### 오전 (09:00-12:00)

#### 09:00-10:30 | Skill Catalog 분석
- **강의** (30분)
  - 전체 Skill Catalog 구조 (25개 이상)
  - Stage별 주요 Skill 소개
- **실습** (60분)
  - Skill Catalog 탐색
  - 관심 Skill 3개 선택 및 심층 분석
  - Skill 간 의존 관계 매핑

#### 10:45-12:00 | Skill Development Guide
- **강의** (45분)
  - 새 Skill 개발 프로세스
  - Best Practices
    - Clarity (명확성)
    - Completeness (완전성)
    - Maintainability (유지보수성)
  - Anti-patterns
    - Vague Instructions
    - Missing Validation
    - Implicit Knowledge
- **워크샵** (30분)
  - Anti-pattern 사례 분석
  - 개선 방안 토론

### 오후 (13:00-18:00)

#### 13:00-15:00 | 실습: Skill 작성 (Part 1)
- **실습** (120분)
  - 팀별 Skill 작성 프로젝트
  - 선택 가능 Skill:
    - Analysis Skill (레거시 특정 패턴 분석)
    - Validation Skill (특정 품질 검증)
    - Transformation Skill (데이터 변환)
  - SKILL.md 전체 7개 섹션 작성

#### 15:15-16:45 | 실습: Skill 작성 (Part 2)
- **실습 계속** (90분)
  - Skill 파일 완성
  - Templates 폴더 작성
  - Examples 작성
  - Validation Rules 정의

#### 17:00-18:00 | Skill 리뷰 및 테스트
- **발표** (45분)
  - 팀별 작성 Skill 발표
  - 코드 리뷰 스타일 피드백
- **실습** (15분)
  - 작성한 Skill로 실제 Task 실행 테스트
  - 결과 검토 및 수정

### Day 7 산출물
- [ ] 팀별 작성 SKILL.md (완성본)
- [ ] Templates 폴더 및 파일
- [ ] Examples 및 샘플 출력
- [ ] Skill 실행 테스트 결과

---

## Day 8: Tool Ecosystem + Execution Patterns

**워크북 섹션**: 04-TOOL-ECOSYSTEM, 05-EXECUTION-PATTERNS
**학습 목표**: Claude Code 고급 활용, 오케스트레이터 운영

### 오전 (09:00-12:00)

#### 09:00-10:30 | Claude Code 고급 설정
- **강의** (45분)
  - CLAUDE.md 구성 상세
  - 모델 선택 전략 (Opus vs Sonnet vs Haiku)
  - 컨텍스트 관리
  - Skill 연동 설정
- **실습** (45분)
  - 프로젝트용 CLAUDE.md 작성
  - 모델별 특성 테스트
  - 최적 설정 도출

#### 10:45-12:00 | Orchestrator 설정
- **강의** (45분)
  - Choisor Daemon 개요
  - Session Pool 관리
  - Phase Gate Controller
  - 설정 파일 구조
- **실습** (30분)
  - Orchestrator 설치 및 초기 설정
  - Session 생성 테스트

### 오후 (13:00-18:00)

#### 13:00-14:30 | Batch Processing
- **강의** (45분)
  - 배치 처리 전략
  - 체크포인팅 메커니즘
  - 진행 상황 추적
  - 중단/재시작 처리
- **실습** (45분)
  - 배치 작업 설정
  - 체크포인트 테스트
  - 재시작 시나리오 실습

#### 14:45-16:30 | Parallel Execution & Error Recovery
- **강의** (45분)
  - 병렬 실행 패턴
  - 동기화 포인트
  - 리소스 관리
  - 오류 감지 및 재시도
  - 복구 절차
- **실습** (60분)
  - 병렬 Task 실행 테스트
  - 의도적 오류 유발 및 복구 실습
  - 로그 분석

#### 16:45-18:00 | Monitoring Dashboard
- **강의** (30분)
  - 메트릭 수집 체계
  - 대시보드 구성
  - 알람 설정
- **실습** (45분)
  - 모니터링 대시보드 설정
  - 주요 메트릭 확인
  - History Viewer 활용

### Day 8 산출물
- [ ] 프로젝트용 CLAUDE.md
- [ ] Orchestrator 설정 완료
- [ ] 배치/병렬 실행 테스트 결과
- [ ] 모니터링 대시보드 설정

---

## Day 9: Quality Assurance + Case Studies

**워크북 섹션**: 06-QUALITY-ASSURANCE, 07-CASE-STUDIES
**학습 목표**: 검증 프레임워크 적용, 실제 사례 학습

### 오전 (09:00-12:00)

#### 09:00-10:30 | Validation Framework
- **강의** (60분)
  - 4-Layer 검증 프레임워크
    - SQL Equivalence (40%)
    - API Equivalence (25%)
    - Business Logic (20%)
    - Data Model (15%)
  - 스코어링 시스템
  - 통과 기준 (70점 + Critical 0건)
- **실습** (30분)
  - 검증 프레임워크 설정
  - 샘플 Feature 검증 실행

#### 10:45-12:00 | Phase Gate Criteria & Remediation
- **강의** (45분)
  - Stage별 Phase Gate 기준 상세
  - Remediation 절차
    - 자동 Remediation
    - 수동 Remediation
    - Escalation 경로
  - Remediation Loop 관리
- **워크샵** (30분)
  - Phase Gate 실패 시나리오 분석
  - Remediation 전략 수립 연습

### 오후 (13:00-18:00)

#### 13:00-14:30 | Case Study: hallain_tft
- **강의** (60분)
  - hallain_tft 프로젝트 개요
    - 8,377 Java 파일
    - 5,864 API 엔드포인트
    - 912 Features
    - 11 도메인
  - 적용 과정 및 도전과제
  - 해결 방안 및 결과
- **토론** (30분)
  - 성공 요인 분석
  - 우리 프로젝트에 적용 가능한 점

#### 14:45-16:30 | Lessons Learned & Anti-patterns
- **강의** (45분)
  - 주요 교훈 (Lessons Learned)
    - 무엇이 잘 되었나?
    - 무엇이 어려웠나?
    - 다음에는 어떻게 할 것인가?
  - Anti-patterns 카탈로그
    - 피해야 할 패턴
    - 발생 원인
    - 예방 방법
- **워크샵** (60분)
  - Anti-pattern 식별 연습
  - 예방 전략 수립

#### 16:45-18:00 | Day 10 Mini Project 준비
- **브리핑** (30분)
  - Mini Project 과제 설명
  - 팀 구성 및 역할 분담
  - 평가 기준 안내
- **팀 작업** (45분)
  - 프로젝트 계획 수립
  - 역할 분담
  - 필요 자료 준비

### Day 9 산출물
- [ ] 검증 프레임워크 설정 및 테스트 결과
- [ ] Phase Gate Criteria 체크리스트
- [ ] Case Study 분석 노트
- [ ] Mini Project 계획서

---

## Day 10: Mini Migration Project + 발표 + 수료

**워크북 섹션**: 전체 종합
**학습 목표**: 방법론 전체 적용, 프로젝트 리드 경험

### 오전 (09:00-12:00)

#### 09:00-12:00 | Mini Migration Project 실행
- **실습** (180분)
  - 팀별 Mini Project 수행
  - 적용 범위:
    - Assessment: 레거시 분석 (축소)
    - Workflow Design: Stage-Phase 설계
    - Skill: 1개 이상 Skill 적용
    - Execution: 최소 1개 Feature의 Stage 1 완료
  - 강사 순회 지도 및 Q&A

### 오후 (13:00-18:00)

#### 13:00-15:00 | Mini Project 완성 및 발표 준비
- **실습 계속** (60분)
  - 프로젝트 완성
  - 산출물 정리
- **발표 준비** (60분)
  - 발표 자료 작성
  - 데모 준비

#### 15:15-17:00 | 팀별 발표 및 평가
- **발표** (90분)
  - 팀별 15-20분 발표
  - 내용:
    - Assessment 결과 요약
    - 설계한 Workflow
    - 작성/적용한 Skill
    - Stage 1 실행 결과
    - 배운 점 및 개선점
  - Q&A 및 피드백

#### 17:15-18:00 | 교육 종합 정리 및 수료
- **강의** (30분)
  - 2주간 학습 내용 종합 정리
  - 실무 적용 가이드
  - 추가 학습 자료 안내
  - Q&A
- **수료** (15분)
  - 수료증 수여
  - 폐회

### Day 10 산출물
- [ ] Mini Project 결과물
  - Assessment Report (축소)
  - Workflow Design (config.yaml)
  - Skill 적용 결과
  - Stage 1 산출물 (1개 Feature)
- [ ] 발표 자료
- [ ] 수료증

---

## 평가 기준

### 출석 및 참여 (20%)
- 10일 전일 출석
- 토론 및 워크샵 참여도
- 질문 및 피드백 활동

### 일일 산출물 (40%)
- Day별 요구 산출물 제출
- 산출물 품질 및 완성도

### Mini Project (40%)
- Assessment 품질 (10%)
- Workflow 설계 적절성 (10%)
- Skill 작성 품질 (10%)
- 발표 및 커뮤니케이션 (10%)

---

## 사전 준비사항

### 수강생 준비
- [ ] 노트북 (개발 환경 구축 가능)
- [ ] Claude API 접근권 (제공 또는 개인 계정)
- [ ] Git 기본 지식
- [ ] Java/Spring 기본 이해 (실습 레거시가 Java 기반인 경우)

### 교육 환경 준비
- [ ] 실습용 레거시 코드베이스 준비
- [ ] Claude Code 라이선스/API 키 확보
- [ ] 실습 서버 환경 (필요시)
- [ ] 교육장 네트워크 환경 확인

---

## 교육 자료

### 필수 자료
- AIND Migration Workbook (전체)
- 실습용 레거시 코드베이스
- 일일 실습 가이드 (별도 제공)

### 참고 자료
- Claude Code 공식 문서
- hallain_tft Case Study 상세 보고서
- Skill Catalog 참조 문서

---

**Document Version**: 1.0.0
**Created**: 2025-12-18
**Author**: Choi | Build Center