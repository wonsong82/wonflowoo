# Choisor 2.0 - 태스크 오케스트레이터 백서

**버전**: 2.0.0
**최종 수정**: 2026년 1월
**작성자**: Choisor 개발팀

---

## 목차

1. [개요](#1-개요)
2. [핵심 개념](#2-핵심-개념)
   - 2.1 [Choisor란?](#21-choisor란)
   - 2.2 [주요 용어](#22-주요-용어)
   - 2.3 [아키텍처 개요](#23-아키텍처-개요)
3. [5단계 마이그레이션 워크플로우](#3-5단계-마이그레이션-워크플로우)
   - 3.1 [단계 개요](#31-단계-개요)
   - 3.2 [Phase 유형](#32-phase-유형-systemdomainfeature)
   - 3.3 [Phase Gate 제어](#33-phase-gate-제어)
4. [시작하기](#4-시작하기)
   - 4.1 [사전 요구사항](#41-사전-요구사항)
   - 4.2 [프로젝트 초기화](#42-프로젝트-초기화)
   - 4.3 [디렉토리 구조](#43-디렉토리-구조)
5. [설정](#5-설정)
   - 5.1 [config.yaml (런타임 설정)](#51-configyaml-런타임-설정)
   - 5.2 [project.yaml (프로젝트 속성)](#52-projectyaml-프로젝트-속성)
   - 5.3 [workflow.yaml (워크플로우 정의)](#53-workflowyaml-워크플로우-정의)
6. [명령어 레퍼런스](#6-명령어-레퍼런스)
   - 6.1 [초기화 명령어](#61-초기화-명령어)
   - 6.2 [상태 및 모니터링 명령어](#62-상태-및-모니터링-명령어)
   - 6.3 [태스크 관리 명령어](#63-태스크-관리-명령어)
   - 6.4 [세션 제어 명령어](#64-세션-제어-명령어)
7. [태스크 생명주기](#7-태스크-생명주기)
   - 7.1 [태스크 생성](#71-태스크-생성)
   - 7.2 [태스크 상태](#72-태스크-상태)
   - 7.3 [우선순위 알고리즘](#73-우선순위-알고리즘)
8. [멀티 세션 오케스트레이션](#8-멀티-세션-오케스트레이션)
   - 8.1 [데몬 아키텍처](#81-데몬-아키텍처)
   - 8.2 [세션 풀 관리](#82-세션-풀-관리)
   - 8.3 [병렬 실행](#83-병렬-실행)
9. [플러그인 아키텍처](#9-플러그인-아키텍처)
   - 9.1 [플러그인 유형](#91-플러그인-유형)
   - 9.2 [커스텀 플러그인 생성](#92-커스텀-플러그인-생성)
   - 9.3 [기본 플러그인](#93-기본-플러그인)
10. [검증 시스템](#10-검증-시스템)
    - 10.1 [Stage 검증기](#101-stage-검증기)
    - 10.2 [계약 검증](#102-계약-검증)
    - 10.3 [품질 게이트](#103-품질-게이트)
11. [모범 사례](#11-모범-사례)
    - 11.1 [워크플로우 최적화](#111-워크플로우-최적화)
    - 11.2 [오류 처리](#112-오류-처리)
    - 11.3 [문제 해결](#113-문제-해결)

- [부록](#부록)
  - [A. 설정 레퍼런스](#a-설정-레퍼런스)
  - [B. 명령어 빠른 참조](#b-명령어-빠른-참조)
  - [C. 용어집](#c-용어집)

---

## 1. 개요

**Choisor 2.0**은 복잡한 다단계 마이그레이션 워크플로우를 관리하기 위해 설계된 스킬 중심 태스크 오케스트레이터입니다. Spring MVC에서 Spring Boot로의 마이그레이션 프로젝트를 위해 개발되었으며, 엔터프라이즈 규모의 AI 지원 코드 변환을 오케스트레이션하기 위한 종합적인 프레임워크를 제공합니다.

### 주요 기능

| 기능 | 설명 |
|------|------|
| **동적 스킬 발견** | `.claude/skills/s{stage}-{phase}-*/SKILL.md` 패턴에서 스킬 자동 발견 |
| **Phase Gate 제어** | 모든 Feature가 Phase N을 완료해야 Phase N+1로 진행 가능 |
| **병렬 실행** | 동시 태스크 실행 기본 지원 (예: s4-03 + s4-04) |
| **멀티 세션 오케스트레이션** | 최대 10개의 병렬 Claude Code 세션 관리 |
| **계약 검증** | 심각도 기반 보고를 통한 단계 간 데이터 계약 검증 |
| **플러그인 아키텍처** | 커스텀 생성기 및 검증기를 위한 확장 가능한 시스템 |

### 대상 사용 사례

- **레거시 코드 마이그레이션**: Spring MVC → Spring Boot, iBatis → MyBatis
- **대규모 리팩토링**: 1000개 이상의 파일을 가진 엔터프라이즈 애플리케이션
- **AI 지원 개발**: 인간 감독하의 자동화된 코드 생성
- **워크플로우 자동화**: 다단계, 의존성 인식 태스크 실행

### 설계 원칙

1. **QUERY-FIRST**: SQL 보존이 최우선 - 100% 쿼리 호환성
2. **Phase Gate 규율**: 질서 있는 진행으로 연쇄 오류 방지
3. **스킬 정렬**: 발견 가능한 스킬과 1:1 매핑된 태스크
4. **코드보다 설정**: 코드 수정 없이 YAML을 통한 워크플로우 변경

---

## 2. 핵심 개념

### 2.1 Choisor란?

Choisor(초이서)는 Claude Code 세션과 복잡한 마이그레이션 워크플로우 사이에 위치하는 오케스트레이션 레이어입니다. 다음과 같은 중요한 문제들을 해결합니다:

**문제점**: 대규모 마이그레이션 프로젝트는 수백 개의 Feature를 포함하며, 각각 여러 변환 Phase를 거쳐야 합니다. 수동 조정은 오류가 발생하기 쉽고 확장성이 없습니다.

**해결책**: Choisor가 제공하는 기능:

- 파일시스템 구조에서 자동 태스크 발견
- 지능적인 태스크 우선순위 지정 및 할당
- 워크플로우 무결성을 위한 Phase Gate 강제
- 처리량을 위한 멀티 세션 병렬화
- 품질 보증을 위한 검증 체크포인트

```
┌─────────────────────────────────────────────────────────────┐
│                     Choisor 오케스트레이터                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Phase     │  │    태스크    │  │    세션     │         │
│  │   Gate      │  │    큐       │  │    풀       │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │               │                │                  │
│         └───────────────┼────────────────┘                  │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   스케줄러                            │   │
│  │    - 5초 간격 폴링                                    │   │
│  │    - 우선순위 기반 태스크 선택                          │   │
│  │    - 세션 할당                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│         ┌───────────────┼───────────────┐                  │
│         ▼               ▼               ▼                  │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐            │
│  │  세션 1   │   │  세션 2   │   │  세션 N   │            │
│  │  (Opus)   │   │  (Opus)   │   │  (Opus)   │            │
│  └───────────┘   └───────────┘   └───────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 주요 용어

| 용어 | 정의 |
|------|------|
| **Stage** | 주요 워크플로우 단계 (1-5): Discovery, Validation, Preparation, Generation, Assurance |
| **Phase** | Stage 내의 하위 단계 (1-5), 특정 스킬과 정렬됨 |
| **Skill** | `.claude/skills/s{N}-{NN}-*/SKILL.md`의 Claude Code 스킬 정의 |
| **Task** | Stage, Phase, Skill, Feature를 결합한 원자적 작업 단위 |
| **Feature** | 마이그레이션 대상 비즈니스 기능 (예: FEAT-PA-001) |
| **Domain** | Feature를 그룹화하는 기능 도메인 (예: PA, CM, MM) |
| **Phase Gate** | 모든 Feature가 Phase N을 완료해야 N+1로 진행할 수 있는 체크포인트 |
| **Session** | Choisor가 관리하는 Claude Code 실행 컨텍스트 |
| **Priority Tier** | 도메인 중요도 분류 (P0-Foundation ~ P3-Supporting) |

### 2.3 아키텍처 개요

Choisor는 계층화된 아키텍처를 사용합니다:

```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 인터페이스 레이어                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  /choisor   │  │    상태     │  │   모니터링   │         │
│  │   명령어    │  │    표시     │  │    도구     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                      코어 엔진 레이어                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    Phase    │  │   우선순위   │  │    스킬     │         │
│  │    Gate     │  │    엔진     │  │  레지스트리  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                       데몬 레이어                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   스케줄러   │  │    세션     │  │    병렬     │         │
│  │             │  │     풀      │  │  코디네이터  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                      플러그인 레이어                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   태스크    │  │  인스트럭션  │  │    검증기    │         │
│  │   생성기    │  │    생성기    │  │   플러그인   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                       저장소 레이어                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ tasks.json  │  │  sessions/  │  │ config.yaml │         │
│  │             │  │sessions.json│  │project.yaml │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

**핵심 컴포넌트**:

1. **Phase Gate**: 모든 Feature에 걸쳐 순차적 Phase 진행 강제
2. **Priority Engine**: 가중치 점수를 사용하여 태스크 실행 순서 계산
3. **Skill Registry**: 사용 가능한 스킬을 동적으로 발견하고 카탈로그화
4. **Scheduler**: 사용 가능한 태스크를 폴링하고 세션에 할당
5. **Session Pool**: Claude Code 세션 생명주기 관리
6. **Parallel Coordinator**: 동시 스킬 실행 조정

---

## 3. 5단계 마이그레이션 워크플로우

### 3.1 단계 개요

Choisor는 레거시 코드 마이그레이션을 위한 구조화된 5단계 워크플로우를 구현합니다:

| Stage | 이름 | Phases | 목적 |
|-------|------|--------|------|
| **1** | Discovery | 4 | Feature 인벤토리, 심층 분석, 스펙 생성 |
| **2** | Validation | 4 | Ground truth 비교, 갭 분석 |
| **3** | Preparation | 5 | 아키텍처 설계, 의존성 해결 |
| **4** | Generation | 5 | 코드 생성, 테스트 생성 |
| **5** | Assurance | 5 | 품질 검증, 성능 기준선 |

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Stage 1 │───▶│ Stage 2 │───▶│ Stage 3 │───▶│ Stage 4 │───▶│ Stage 5 │
│Discovery│    │Validation│   │Preparation│  │Generation│   │Assurance│
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
  Feature       Ground         아키텍처        코드 &         품질
  인벤토리       Truth          설계           테스트         게이트
```

### 상세 Stage 분석

#### Stage 1: Discovery (s1-01 ~ s1-04)

| Phase | Skill | 유형 | 출력 |
|-------|-------|------|------|
| 1 | s1-01-discovery-feature-inventory | domain | feature-inventory.yaml |
| 2 | s1-02-discovery-miplatform-protocol | domain | miplatform-protocol.yaml |
| 3 | s1-03-discovery-deep-analysis | feature | summary.yaml, main.yaml |
| 4 | s1-04-discovery-spec-generation | feature | main.yaml, api-specs/*.yaml |

#### Stage 2: Validation (s2-01 ~ s2-04)

| Phase | Skill | 유형 | 출력 |
|-------|-------|------|------|
| 1 | s2-01-validation-source-inventory | domain | source-inventory.yaml |
| 2 | s2-02-validation-structural-comparison | domain | comparison-report.yaml |
| 3 | s2-03-validation-gap-analysis | feature | gap-analysis.yaml |
| 4 | s2-04-validation-spec-completion | feature | completion-report.yaml |

#### Stage 3: Preparation (s3-01 ~ s3-05)

| Phase | Skill | 유형 | 출력 |
|-------|-------|------|------|
| 1 | s3-01-preparation-dependency-graph | system | dependency-graph.yaml |
| 2 | s3-02-preparation-interface-extraction | system | interface-specs.yaml |
| 3 | s3-03-preparation-technical-debt | system | tech-debt-report.yaml |
| 4 | s3-04-preparation-architecture-design | system | architecture.yaml |
| 5 | s3-05-preparation-generation-spec | system | generation-spec.yaml |

#### Stage 4: Generation (s4-01 ~ s4-05)

| Phase | Skill | 유형 | 출력 |
|-------|-------|------|------|
| 1 | s4-01-generation-project-scaffold | system | 프로젝트 구조 |
| 2 | s4-02-generation-mini-pilot | system | 파일럿 검증 |
| 3 | s4-03-generation-domain-batch | feature | Java/MyBatis 코드 |
| 4 | s4-04-generation-test-generation | feature | 단위/통합 테스트 |
| 5 | s4-05-generation-integration-build | system | 빌드 검증 |

#### Stage 5: Assurance (s5-01 ~ s5-05)

| Phase | Skill | 유형 | 출력 |
|-------|-------|------|------|
| 1 | s5-01-assurance-structural-check | feature | 구조 보고서 |
| 2 | s5-02-assurance-functional-validation | feature | 기능 보고서 |
| 3 | s5-03-assurance-api-contract-test | feature | API 테스트 결과 |
| 4 | s5-04-assurance-performance-baseline | system | 성능 메트릭 |
| 5 | s5-05-assurance-quality-gate | system | 품질 결정 |

### 3.2 Phase 유형 (system/domain/feature)

각 Phase는 세 가지 세분화 수준 중 하나에서 작동합니다:

| 유형 | 태스크 수 | 설명 | 예시 |
|------|----------|------|------|
| **system** | 총 1개 | 프로젝트 전체 작업 | 프로젝트 스캐폴드, 품질 게이트 |
| **domain** | 도메인당 1개 | 도메인 수준 집계 | 도메인별 Feature 인벤토리 |
| **feature** | Feature당 1개 | Feature 수준 병렬화 가능 | Feature별 심층 분석 |

```
Phase 유형 시각화:

system  ────────────────────────────────────────────────────▶
         [════════════════════════════════════════════════]
                              1개 태스크

domain  ────────────────────────────────────────────────────▶
         [═══════════]  [═══════════]  [═══════════]
              PA             CM             MM
         (도메인당 1개)

feature ────────────────────────────────────────────────────▶
         [═][═][═][═][═][═][═][═][═][═][═][═][═][═][═][═]
          F1 F2 F3 F4 F5 F6 F7 F8 F9 ...
         (Feature당 1개 - 병렬화 가능)
```

**설정 예시 (project.yaml)**:

```yaml
phase_types:
  stage1:
    phase1: "domain"    # Feature 인벤토리
    phase2: "domain"    # 프로토콜 분석
    phase3: "feature"   # 심층 분석
    phase4: "feature"   # 스펙 생성
  stage4:
    phase1: "system"    # 프로젝트 스캐폴드
    phase2: "system"    # 미니 파일럿
    phase3: "feature"   # 도메인 배치
    phase4: "feature"   # 테스트 생성
    phase5: "system"    # 통합 빌드
```

### 3.3 Phase Gate 제어

Phase Gate는 순차적 진행을 강제하여 워크플로우 무결성을 보장합니다:

**규칙**: 모든 Feature가 Phase N을 완료해야 어떤 Feature도 Phase N+1로 진행할 수 있습니다.

```
Phase Gate 시각화:

Phase 1 ─────────────────────────────────────────────────────
         [FEAT-PA-001 ✓] [FEAT-PA-002 ✓] [FEAT-CM-001 ✓]
         ════════════════ GATE 통과 ═══════════════════
                              │
                              ▼
Phase 2 ─────────────────────────────────────────────────────
         [FEAT-PA-001 ✓] [FEAT-PA-002 ⟳] [FEAT-CM-001 ✓]
         ════════════════ GATE 차단 ══════════════════
                    (PA-002 아직 진행 중)
```

**Phase Gate 설정**:

```yaml
# config.yaml
phase_gate:
  enabled: true           # Phase Gate 강제 활성화
  strict_mode: true       # 위반 시 즉시 실패
  auto_to_max: true       # 최대 허용 Phase로 자동 진행
  max_allowed_phase: null # null = 동적 계산
```

**Phase Gate 알고리즘**:

```python
def get_max_allowed_phase(tasks):
    """완료 상태에 따라 최대 허용 Phase 결정"""
    for phase in reversed([1, 2, 3, 4, 5]):
        if is_phase_complete(phase, tasks):
            return min(phase + 1, 5)
    return 1  # Phase 1부터 시작

def is_phase_complete(phase, tasks):
    """모든 Feature가 이 Phase를 완료했는지 확인"""
    feature_tasks = [t for t in tasks if t.type == "feature"]
    for feature_id in get_unique_features(feature_tasks):
        if not has_completed_phase(feature_id, phase, feature_tasks):
            return False
    return True
```

---

## 4. 시작하기

### 4.1 사전 요구사항

Choisor를 사용하기 전에 다음을 확인하세요:

| 요구사항 | 버전 | 비고 |
|---------|------|------|
| Python | 3.9+ | 데몬에 필요 |
| Claude Code | 최신 | CLI가 초기화되어 있어야 함 |
| PyYAML | 모든 버전 | 설정 파싱용 |
| Pydantic | 2.0+ | 스키마 검증용 |

**Claude Code 초기화 확인**:

```bash
# Claude Code가 초기화되었는지 확인
ls -la .claude/

# 예상 출력에 포함되어야 할 항목:
# - settings.json
# - skills/ 디렉토리
```

### 4.2 프로젝트 초기화

`/choisor init` 명령을 사용하여 Choisor를 초기화합니다:

```bash
# 대화형 초기화
/choisor init

# 특정 템플릿 사용
/choisor init --template spring-migration

# 프로젝트별 프리셋 사용
/choisor init --template hallain-tft

# 기존 프로젝트 재초기화
/choisor init --force

# 사용 가능한 템플릿 목록
/choisor init --list-templates
```

**사용 가능한 템플릿**:

| 템플릿 | 설명 |
|--------|------|
| `spring-migration` | 일반 Spring MVC → Spring Boot 마이그레이션 |
| `hallain-tft` | 사전 정의된 도메인이 있는 Hallain TFT 프로젝트 |
| `custom` | 커스텀 프로젝트를 위한 최소 설정 |

**초기화 옵션**:

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--template` | 특정 템플릿 사용 | `--template spring-migration` |
| `--force` | 기존 재초기화 | `--force` |
| `--name` | 프로젝트 이름 설정 | `--name my-project` |
| `--source-base` | 레거시 소스 디렉토리 | `--source-base legacy` |
| `--target-base` | 생성 코드 디렉토리 | `--target-base generated` |
| `--java-package` | Java 패키지 경로 | `--java-package com/example` |

### 4.3 디렉토리 구조

초기화 후 Choisor는 다음 구조를 생성합니다:

```
<project-root>/
├── .choisor/                      # Choisor 설정 및 상태
│   ├── config.yaml                # 런타임 설정
│   ├── project.yaml               # 프로젝트 속성
│   ├── workflow.yaml              # 워크플로우 정의 (선택)
│   ├── tasks/
│   │   └── tasks.json             # 태스크 목록 및 상태
│   ├── sessions/
│   │   └── sessions.json          # 세션 풀 상태
│   ├── instructions/              # 활성 인스트럭션 파일
│   ├── logs/                      # 세션 및 태스크 로그
│   │   └── instructions/          # 아카이브된 인스트럭션
│   └── plugins/                   # 프로젝트별 플러그인
│       ├── generators/
│       └── validators/
│
├── .claude/                       # Claude Code 설정
│   └── skills/
│       ├── choisor/               # Choisor 스킬
│       ├── s1-01-discovery-*/     # Stage 1 Phase 1 스킬
│       ├── s1-02-discovery-*/     # Stage 1 Phase 2 스킬
│       └── ...                    # 기타 Stage 스킬
│
└── work/
    └── specs/                     # Stage 출력
        ├── stage1-outputs/
        │   ├── phase1/{priority}/{domain}/
        │   ├── phase2/
        │   ├── phase3/{priority}/{domain}/{feature}/
        │   └── phase4/
        ├── stage2-outputs/
        ├── stage3-outputs/
        ├── stage4-outputs/
        └── stage5-outputs/
```

---

## 5. 설정

Choisor는 3개 파일 설정 시스템을 사용합니다:

| 파일 | 목적 | 범위 |
|------|------|------|
| `config.yaml` | 런타임/운영 설정 | 동적, 자주 수정 |
| `project.yaml` | 프로젝트 속성 | 정적, 프로젝트별 |
| `workflow.yaml` | 워크플로우 정의 | 선택, 커스텀 워크플로우용 |

### 5.1 config.yaml (런타임 설정)

`config.yaml` 파일은 실행 중에 수정할 수 있는 런타임 설정을 포함합니다:

```yaml
# .choisor/config.yaml

# 할당 제어
assignment:
  enabled: true         # true: 정상 할당, false: 새 할당 중지
  delay: null           # 할당 지연 시간(분) (null = 지연 없음)
  stale_timeout: 10     # 세션이 stale로 간주되기까지의 시간(분)

# 자동 커밋
auto_commit:
  enabled: true
  commit_on_completion: true

# 제공자
provider: "anthropic"
default_model: "claude-opus-4-5-20251101"

# Claude Code 세션 설정
claude_code:
  max_sessions: 1
  max_output_tokens: 65536
  default_model: "claude-opus-4-5-20251101"

# 현재 워크플로우 위치 (런타임 상태)
current:
  stage: "stage1"
  phase: "phase1"

# Phase Gate 설정 (런타임 제어)
phase_gate:
  max_allowed_phase: "phase4"   # 최대 허용 Phase
  auto_to_max: true             # 최대 허용으로 자동 진행

# 병렬 실행 설정
parallel:
  enabled: true
  pairs:
    - ["s4-03", "s4-04"]        # 코드 생성 + 테스트 생성
  max_parallel_sessions: 10

# 경로 설정
paths:
  skills_root: ".claude/skills"
  contracts_path: ".claude/skills/common/inter-stage-contracts.yaml"

# 작업 범위 필터링 (런타임 필터)
work_scope:
  enabled_domains: null         # ["pa", "mm"] 또는 null (전체)
  enabled_stages: null          # [1, 2, 3] 또는 null (전체)

# 우선순위 알고리즘
priority:
  algorithm: "weighted_score"   # "weighted_score" | "fifo"
  weights:
    dependency_ready: 0.5
    priority_score: 0.3
    estimated_duration: 0.2
```

**주요 설정 설명**:

| 설정 | 목적 | 일반적인 조정 |
|------|------|--------------|
| `assignment.enabled` | 태스크 할당 제어 | `false`로 설정하여 일시 중지 |
| `assignment.delay` | 할당 속도 제한 | 5분 지연을 위해 `5` 설정 |
| `parallel.max_parallel_sessions` | 동시 세션 수 | 리소스 제한 시 감소 |
| `work_scope.enabled_domains` | 특정 도메인에 집중 | `["PA", "CM"]` |

### 5.2 project.yaml (프로젝트 속성)

`project.yaml` 파일은 프로젝트별 속성을 포함합니다:

```yaml
# .choisor/project.yaml

name: "my-migration-project"
description: "Spring MVC to Spring Boot 마이그레이션 프로젝트"

# Feature 식별 패턴
feature:
  id_prefix: "FEAT-"           # Feature ID 접두사
  gap_suffix: "GAP"            # GAP Feature 접미사
  skip_gap_features: true      # 생성에서 GAP Feature 건너뛰기

# 도메인 설정
domain:
  skip_domains: []             # 건너뛸 도메인
  priority_map:                # 도메인 우선순위 티어 매핑
    P0-Foundation: ["CM"]
    P1-Hub: ["PA"]
    P2-Core: ["MM", "QM"]
    P3-Supporting: ["RP"]

# Stage별 Phase 유형
phase_types:
  stage1:
    phase1: "domain"           # Feature 인벤토리
    phase2: "domain"           # 프로토콜 분석
    phase3: "feature"          # 심층 분석
    phase4: "feature"          # 스펙 생성
  # ... (stages 2-5)

# 경로 템플릿
paths:
  source_base: "hallain"                # 레거시 소스
  target_base: "next-hallain"           # 생성 코드
  java_src_path: "src/main/java"
  mapper_path: "src/main/resources/mapper"
  java_package: "com/hallain"
  specs_root: "work/specs"

# Stage 정의
stages:
  stage1:
    name: "Discovery"
    phases: ["phase1", "phase2", "phase3", "phase4"]
    skills:
      phase1: "s1-01-discovery-feature-inventory"
      phase2: "s1-02-discovery-miplatform-protocol"
      phase3: "s1-03-discovery-deep-analysis"
      phase4: "s1-04-discovery-spec-generation"
  # ... (기타 stages)

# 태스크 소스 위치
task_sources:
  feature_inventory_base: "work/specs/stage1-outputs/phase1"
  feature_inventory_pattern: "work/specs/stage1-outputs/phase1/{priority}/{domain}/feature-inventory.yaml"
  stage1_specs: "work/specs/stage1-outputs/phase3"
  stage4_specs: "work/specs/stage1-outputs/phase3"
```

### 5.3 workflow.yaml (워크플로우 정의)

선택적 `workflow.yaml`은 커스텀 워크플로우 정의를 가능하게 합니다:

```yaml
# .choisor/workflow.yaml

workflow:
  name: "hallain_tft"
  description: "Spring MVC to Spring Boot 마이그레이션"

  # 스킬 발견 패턴
  skill_pattern: "s{stage}-{phase:02d}-*"
  skill_dir: ".claude/skills"

  stages:
    - id: "discovery"
      number: 1
      name: "Discovery"
      description: "Feature 발견 및 분석"
      output_dir: "stage1-outputs"
      phases:
        - id: "feature-inventory"
          number: 1
          type: "domain"
          skill: "s1-01-discovery-feature-inventory"
          outputs:
            - "feature-inventory.yaml"
        - id: "deep-analysis"
          number: 3
          type: "feature"
          skill: "s1-03-discovery-deep-analysis"
          outputs:
            - "summary.yaml"
            - "main.yaml"

    - id: "generation"
      number: 4
      name: "Generation"
      parallel_pairs:
        - ["domain-batch", "test-generation"]
      phases:
        - id: "domain-batch"
          number: 3
          type: "feature"
          skill: "s4-03-generation-domain-batch"
          generator: "generators.code_generation"   # 커스텀 생성기
        - id: "test-generation"
          number: 4
          type: "feature"
          skill: "s4-04-generation-test-generation"

  # 태스크 소스 설정
  task_sources:
    feature_inventory:
      path: "work/specs/stage1-outputs/phase1/{priority}/{domain}/feature-inventory.yaml"
      pattern: "work/specs/stage1-outputs/phase1/**/feature-inventory.yaml"
```

---

## 6. 명령어 레퍼런스

### 6.1 초기화 명령어

| 명령어 | 설명 |
|--------|------|
| `/choisor init` | 프로젝트용 Choisor 초기화 |
| `/choisor init --template <name>` | 특정 템플릿 사용 |
| `/choisor init --force` | 기존 프로젝트 재초기화 |
| `/choisor init --list-templates` | 사용 가능한 템플릿 목록 |

**예시**:

```bash
# 표준 초기화
/choisor init --template spring-migration

# 커스텀 경로와 함께
/choisor init --template spring-migration \
  --name my-project \
  --source-base legacy \
  --target-base generated \
  --java-package com/example

# 강제 재초기화
/choisor init --force
```

### 6.2 상태 및 모니터링 명령어

| 명령어 | 설명 |
|--------|------|
| `/choisor status` | 현재 프로젝트 상태 표시 |
| `/choisor scan [--stage N]` | 태스크 스캔 및 tasks.json 업데이트 |
| `/choisor sync` | 파일시스템과 태스크 상태 동기화 |
| `/choisor query [options]` | 필터로 태스크 조회 |

**상태 명령어 출력**:

```
╔══════════════════════════════════════════════════════════════╗
║                    Choisor 상태 보고서                        ║
╠══════════════════════════════════════════════════════════════╣
║ 프로젝트: hallain-tft                                        ║
║ 현재 Phase: 1.3 (Discovery - 심층 분석)                      ║
║ Phase Gate: Phase 3 허용                                     ║
╠══════════════════════════════════════════════════════════════╣
║ 태스크 요약:                                                 ║
║   전체: 156  대기중: 89  진행중: 3  완료: 64                 ║
╠══════════════════════════════════════════════════════════════╣
║ Phase 진행률:                                                ║
║   Phase 1: ████████████████████████ 100% (24/24)            ║
║   Phase 2: ████████████████████████ 100% (24/24)            ║
║   Phase 3: ████████████░░░░░░░░░░░░  52% (16/31)            ║
║   Phase 4: ░░░░░░░░░░░░░░░░░░░░░░░░   0% (0/31)             ║
╠══════════════════════════════════════════════════════════════╣
║ 활성 세션: 3/10                                              ║
║   세션 f4fe7c8a: FEAT-PA-003 (s1-03)                        ║
║   세션 2b3c4d5e: FEAT-CM-001 (s1-03)                        ║
║   세션 9a8b7c6d: FEAT-MM-002 (s1-03)                        ║
╚══════════════════════════════════════════════════════════════╝
```

**Query 명령어 옵션**:

```bash
# 상태별 필터
/choisor query --status pending

# 도메인별 필터
/choisor query --domain PA

# Stage 및 Phase별 필터
/choisor query --stage 4 --phase 3

# 제한이 있는 목록 형식
/choisor query --list --limit 20

# JSON 출력
/choisor query --format json
```

### 6.3 태스크 관리 명령어

| 명령어 | 설명 |
|--------|------|
| `/choisor manual-assign <feature-id>` | 특정 Feature 수동 할당 |
| `/choisor clean-restart <feature-ids>` | 재작업을 위해 Feature 리셋 |

**수동 할당**:

```bash
# 특정 Feature를 다음 가용 세션에 할당
/choisor manual-assign FEAT-PA-001

# 여러 Feature 할당
/choisor manual-assign FEAT-PA-001 FEAT-PA-002
```

**클린 재시작**:

```bash
# 단일 Feature 리셋
/choisor clean-restart FEAT-PA-001

# 여러 Feature 리셋
/choisor clean-restart FEAT-PA-001,FEAT-PA-002,FEAT-CM-001

# 이 작업은 다음을 수행합니다:
# 1. 태스크 상태를 "pending"으로 리셋
# 2. assigned_session 클리어
# 3. 기존 출력 파일 삭제
# 4. 인스트럭션 파일 아카이브
```

### 6.4 세션 제어 명령어

| 명령어 | 설명 |
|--------|------|
| `/choisor stop` | 첫 번째 실행 중인 세션 중지 |
| `/choisor stop --feature <id>` | Feature ID로 중지 |
| `/choisor stop --session <id>` | 세션 ID로 중지 |
| `/choisor stop --task <id>` | 태스크 ID로 중지 |
| `/choisor stop --all` | 모든 실행 중인 세션 중지 |

**예시**:

```bash
# 첫 번째 실행 중인 세션 중지
/choisor stop

# 특정 Feature 작업 중인 세션 중지
/choisor stop --feature FEAT-CM-001

# 세션 ID로 중지 (접두사 OK)
/choisor stop --session f4fe7c8a

# 태스크 ID로 중지
/choisor stop --task s1-03-FEAT-CM-001

# 비상 전체 중지
/choisor stop --all
```

---

## 7. 태스크 생명주기

### 7.1 태스크 생성

태스크는 파일시스템 구조와 설정에 기반하여 생성됩니다:

```
태스크 생성 흐름:

1. 스펙 파일에서 파일시스템 스캔
   └─▶ work/specs/stage1-outputs/phase3/{priority}/{domain}/{feature}/

2. 프로젝트 설정으로 필터링
   └─▶ GAP Feature 건너뛰기 (설정된 경우)
   └─▶ enabled_domains로 필터링
   └─▶ enabled_stages로 필터링

3. Task 객체 생성
   └─▶ 경로에서 feature_id 추출
   └─▶ 경로에서 domain 결정
   └─▶ stage/phase에서 skill_id 설정
   └─▶ 도메인 티어에서 우선순위 계산

4. tasks.json에 저장
   └─▶ .choisor/tasks/tasks.json
```

**Task 객체 구조**:

```python
@dataclass
class Task:
    id: str                        # 예: "s1-03-FEAT-PA-001"
    stage: int                     # 1-5
    phase: int                     # 1-5
    skill_id: str                  # 예: "s1-03"
    feature_id: str                # 예: "FEAT-PA-001"
    domain: str                    # 예: "PA"
    status: TaskStatus             # pending, assigned, in_progress 등
    title: str                     # 사람이 읽을 수 있는 제목
    priority: int                  # 1-10 (높을수록 중요)
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]       # 추가 컨텍스트
    assigned_session: Optional[str]
    dependencies: List[str]        # 의존 태스크 ID
    estimated_duration: Optional[int]  # 분
```

### 7.2 태스크 상태

태스크는 다음 상태를 거쳐 진행됩니다:

```
태스크 상태 머신:

  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │                      ┌──────────┐                       │
  │                      │ PENDING  │◄───────────────┐      │
  │                      └────┬─────┘                │      │
  │                           │                      │      │
  │                    할당   │                리셋  │      │
  │                           ▼                      │      │
  │                      ┌──────────┐                │      │
  │                      │ ASSIGNED │────────────────┘      │
  │                      └────┬─────┘     (타임아웃)        │
  │                           │                             │
  │                    시작   │                             │
  │                           ▼                             │
  │                    ┌────────────┐                       │
  │                    │IN_PROGRESS │                       │
  │                    └─────┬──────┘                       │
  │                          │                              │
  │          ┌───────────────┼───────────────┐              │
  │          │               │               │              │
  │          ▼               ▼               ▼              │
  │     ┌─────────┐     ┌────────┐     ┌────────┐          │
  │     │COMPLETED│     │ FAILED │     │  SKIP  │          │
  │     └─────────┘     └────────┘     └────────┘          │
  │          │               │               │              │
  │          └───────────────┴───────────────┘              │
  │                          │                              │
  │                     종료 상태                            │
  └─────────────────────────────────────────────────────────┘
```

| 상태 | 설명 | 전환 |
|------|------|------|
| **PENDING** | 할당 대기 중인 태스크 | → ASSIGNED |
| **ASSIGNED** | 세션에 할당된 태스크 | → IN_PROGRESS, → PENDING (타임아웃) |
| **IN_PROGRESS** | 실행 중인 태스크 | → COMPLETED, → FAILED, → SKIP |
| **COMPLETED** | 성공적으로 완료된 태스크 | 종료 |
| **FAILED** | 오류로 실패한 태스크 | 종료 (리셋 가능) |
| **SKIP** | 건너뛴 태스크 (예: 빈 폴더) | 종료 |

### 7.3 우선순위 알고리즘

Choisor는 가중치 점수 알고리즘을 사용하여 태스크 우선순위를 지정합니다:

```
점수 = (dependency_ready × 0.4) + (priority_score × 0.4) + (duration_score × 0.2)
```

**구성요소 분석**:

| 구성요소 | 가중치 | 계산 |
|---------|--------|------|
| `dependency_ready` | 0.4 | 모든 의존성 완료 시 1.0, 아니면 0.0 |
| `priority_score` | 0.4 | 태스크 우선순위 (1-10) 0.0-1.0으로 정규화 |
| `duration_score` | 0.2 | `1.0 - min(estimated_duration/120, 1.0)` |

**우선순위 설정**:

```yaml
# config.yaml
priority:
  algorithm: "weighted_score"  # 또는 "fifo"
  weights:
    dependency_ready: 0.5
    priority_score: 0.3
    estimated_duration: 0.2
```

**도메인 우선순위 매핑**:

태스크는 도메인 티어에서 우선순위를 상속받습니다:

| 티어 | 우선순위 점수 | 도메인 (예시) |
|------|--------------|---------------|
| P0-Foundation | 10 | CM (공통) |
| P1-Hub | 8 | PA (생산) |
| P2-Core | 6 | MM, QM |
| P3-Supporting | 4 | RP |

---

## 8. 멀티 세션 오케스트레이션

### 8.1 데몬 아키텍처

Choisor 데몬은 스케줄링 루프를 관리합니다:

```
데몬 아키텍처:

┌─────────────────────────────────────────────────────────────┐
│                      Choisor 데몬                            │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                     스케줄러                           │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              스케줄 틱 (5초)                     │  │  │
│  │  │                                                  │  │  │
│  │  │  1. 설정 리로드 (변경 시)                        │  │  │
│  │  │  2. stale 세션 확인                             │  │  │
│  │  │  3. 실행 중인 세션 완료 확인                     │  │  │
│  │  │  4. 완료된 세션 처리                            │  │  │
│  │  │  5. 초과 세션 정리                              │  │  │
│  │  │  6. 할당 지연 확인                              │  │  │
│  │  │  7. 가용 세션 가져오기                          │  │  │
│  │  │  8. 필요시 새 세션 생성                         │  │  │
│  │  │  9. 세션에 태스크 할당                          │  │  │
│  │  │  10. 병렬 기회 확인                             │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                     세션 풀                            │  │
│  │                                                        │  │
│  │    세션 상태:                                          │  │
│  │    IDLE → ASSIGNED → RUNNING → COMPLETED              │  │
│  │      ↑                           │                     │  │
│  │      └───────── 해제 ────────────┘                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**데몬 시작**:

```bash
# 별도 터미널에서
python -m choisor.daemon.main
```

**데몬 설정**:

```yaml
# config.yaml
daemon:
  refresh_interval: 10  # 초 (5-300)

assignment:
  enabled: true
  delay: null           # 분
  stale_timeout: 10     # 분
```

### 8.2 세션 풀 관리

세션 풀은 Claude Code 세션 생명주기를 관리합니다:

```python
class SessionState(Enum):
    IDLE = "idle"           # 태스크 대기 중
    ASSIGNED = "assigned"   # 태스크 할당됨, 시작 중
    RUNNING = "running"     # 활발히 실행 중
    COMPLETED = "completed" # 태스크 완료, 해제 대기
    FAILED = "failed"       # 오류 발생
    TERMINATED = "terminated"  # 수동 중지됨
```

**세션 생명주기**:

```
세션 생명주기:

1. 생성 (create_session)
   └─▶ 세션이 IDLE 상태로 진입
   └─▶ UUID 할당
   └─▶ sessions.json에 저장

2. 할당 (assign_task)
   └─▶ 상태: IDLE → ASSIGNED
   └─▶ 태스크 ID 기록
   └─▶ 인스트럭션 파일 작성
   └─▶ Claude 프로세스 시작
   └─▶ 상태: ASSIGNED → RUNNING

3. 실행 (Claude가 관리)
   └─▶ 프로세스가 인스트럭션 실행
   └─▶ 파일시스템에 출력 작성
   └─▶ 프로세스 완료

4. 완료 (check_session_status)
   └─▶ 상태: RUNNING → COMPLETED
   └─▶ 스케줄러에 알림

5. 해제 (release_session)
   └─▶ 완료된 태스크를 히스토리에 추가
   └─▶ 상태: COMPLETED → IDLE
   └─▶ 다음 태스크 준비 완료
```

**세션 풀 통계**:

```python
def get_stats() -> Dict[str, int]:
    return {
        "idle": 2,
        "assigned": 1,
        "running": 5,
        "completed": 0,
        "failed": 0,
        "terminated": 0,
        "total": 8,
    }
```

### 8.3 병렬 실행

Choisor는 특정 스킬 쌍에 대해 병렬 실행을 지원합니다:

```
병렬 실행 (s4-03 + s4-04):

Feature: FEAT-PA-001
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  세션 A                       세션 B                       │
│  ┌──────────────────────┐    ┌──────────────────────┐     │
│  │ s4-03: 도메인 배치   │    │ s4-04: 테스트 생성   │     │
│  │ (코드 생성)          │    │ (테스트 생성)        │     │
│  └──────────┬───────────┘    └──────────┬───────────┘     │
│             │                           │                  │
│             └───────────┬───────────────┘                  │
│                         │                                  │
│                         ▼                                  │
│             ┌───────────────────────┐                     │
│             │   모두 완료           │                     │
│             │  FEAT-PA-001 완료     │                     │
│             └───────────────────────┘                     │
└────────────────────────────────────────────────────────────┘
```

**설정**:

```yaml
# config.yaml
parallel:
  enabled: true
  pairs:
    - ["s4-03", "s4-04"]   # 코드 생성 + 테스트 생성
  max_parallel_sessions: 10
```

**병렬 코디네이터 로직**:

```python
class ParallelCoordinator:
    def can_run_parallel_by_skill_id(self, skill_id: str) -> bool:
        """스킬이 다른 스킬과 병렬로 실행될 수 있는지 확인"""
        for pair in self.parallel_pairs:
            if skill_id in pair:
                return True
        return False

    def get_parallel_skill_id(self, skill_id: str) -> Optional[str]:
        """주어진 스킬에 대한 병렬 스킬 가져오기"""
        for pair in self.parallel_pairs:
            if skill_id == pair[0]:
                return pair[1]
            if skill_id == pair[1]:
                return pair[0]
        return None
```

---

## 9. 플러그인 아키텍처

### 9.1 플러그인 유형

Choisor는 세 가지 유형의 플러그인을 지원합니다:

| 플러그인 유형 | 목적 | 인터페이스 |
|--------------|------|-----------|
| **TaskGeneratorPlugin** | 커스텀 태스크 생성 | `generate(project_root, config, workflow, registry, project_config) → List[Task]` |
| **InstructionGeneratorPlugin** | 커스텀 인스트럭션 생성 | `generate(task, config, workflow, project_config) → str` |
| **ValidatorPlugin** | 커스텀 출력 검증 | `validate(task, output_path, workflow) → ValidationResult` |

### 9.2 커스텀 플러그인 생성

**디렉토리 구조**:

```
.choisor/plugins/
├── __init__.py
├── generators/
│   ├── __init__.py
│   └── custom_generator.py
└── validators/
    ├── __init__.py
    └── custom_validator.py
```

**태스크 생성기 플러그인 예시**:

```python
# .choisor/plugins/generators/code_generation.py

from choisor.plugins.base import TaskGeneratorPlugin
from choisor.core import Task

class CodeGenerationTaskGenerator(TaskGeneratorPlugin):
    """Stage 4 코드 생성을 위한 커스텀 태스크 생성기"""

    @property
    def stage_id(self) -> str:
        return "generation"

    def generate(
        self,
        project_root,
        config,
        workflow,
        registry,
        project_config,
    ) -> list[Task]:
        tasks = []

        # 코드 생성 태스크를 위한 커스텀 로직
        specs_path = project_root / "work/specs/stage1-outputs/phase3"

        for feature_dir in self._scan_features(specs_path):
            # GAP Feature 건너뛰기
            if project_config.feature.skip_gap_features:
                if project_config.feature.gap_suffix in feature_dir.name:
                    continue

            complexity = self._calculate_complexity(feature_dir)

            task = Task(
                id=f"{feature_dir.name}-codegen",
                stage=workflow.get_stage("generation").number,
                phase=3,
                skill_id="s4-03",
                feature_id=feature_dir.name,
                # ... 나머지 태스크 생성
            )
            tasks.append(task)

        return tasks
```

**검증기 플러그인 예시**:

```python
# .choisor/plugins/validators/code_validator.py

from choisor.plugins.base import ValidatorPlugin
from choisor.generators.validators.base import ValidationResult

class CodeValidator(ValidatorPlugin):
    """생성된 코드를 위한 커스텀 검증기"""

    @property
    def stage_id(self) -> str:
        return "generation"

    def validate(self, task, output_path, workflow) -> ValidationResult:
        result = ValidationResult(passed=True)

        # Java 파일 존재 확인
        java_files = list(output_path.glob("**/*.java"))
        if not java_files:
            result.add_error("Java 파일이 생성되지 않음")

        # 매퍼 파일 존재 확인
        mapper_files = list(output_path.glob("**/*.xml"))
        if not mapper_files:
            result.add_warning("매퍼 XML 파일을 찾을 수 없음")

        # 컴파일 오류 확인 (기본 구문 검사)
        for java_file in java_files:
            if not self._check_syntax(java_file):
                result.add_error(f"{java_file.name}에서 구문 오류")

        return result
```

### 9.3 기본 플러그인

Choisor는 workflow.yaml과 함께 작동하는 기본 플러그인을 제공합니다:

**DefaultTaskGeneratorPlugin**:

```python
class DefaultTaskGeneratorPlugin(TaskGeneratorPlugin):
    """workflow.yaml에서 작동하는 기본 태스크 생성기"""

    def generate(self, ...) -> list[Task]:
        stage = self._workflow.get_stage(self._stage_id)
        tasks = []

        for phase in stage.phases:
            phase_type = phase.type  # "system", "domain", 또는 "feature"

            if phase_type == "system":
                # 총 1개 태스크
                tasks.append(self._create_system_task(phase))
            elif phase_type == "domain":
                # 도메인당 1개 태스크
                for domain in self._get_domains():
                    tasks.append(self._create_domain_task(phase, domain))
            else:  # feature
                # Feature당 1개 태스크
                for feature in self._get_features():
                    tasks.append(self._create_feature_task(phase, feature))

        return tasks
```

**플러그인 로딩**:

```python
class PluginLoader:
    """프로젝트 디렉토리에서 플러그인 로드"""

    def load(self) -> PluginRegistry:
        registry = PluginRegistry()

        if not self.plugins_dir.exists():
            return registry

        # Python 경로에 플러그인 디렉토리 추가
        sys.path.insert(0, str(self.plugins_dir))

        # 생성기 플러그인 로드
        for plugin_file in (self.plugins_dir / "generators").glob("*.py"):
            self._load_generator_plugin(plugin_file, registry)

        # 검증기 플러그인 로드
        for plugin_file in (self.plugins_dir / "validators").glob("*.py"):
            self._load_validator_plugin(plugin_file, registry)

        return registry
```

---

## 10. 검증 시스템

### 10.1 Stage 검증기

Stage 검증기는 출력 무결성을 확인합니다:

```python
class StageValidator(ABC):
    """Stage 출력 검증기를 위한 추상 기본 클래스"""

    @abstractmethod
    def get_stage(self) -> int:
        """이 검증기가 처리하는 Stage 번호 반환"""
        pass

    @abstractmethod
    def validate(
        self,
        task: Task,
        output_path: Path,
        config: ChoisorConfig
    ) -> ValidationResult:
        """Stage 출력 검증"""
        pass
```

**ValidationResult 구조**:

```python
@dataclass
class ValidationResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.passed = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    @classmethod
    def success(cls, details=None) -> "ValidationResult":
        return cls(passed=True, details=details or {})

    @classmethod
    def failure(cls, errors: list[str], details=None) -> "ValidationResult":
        return cls(passed=False, errors=errors, details=details or {})
```

### 10.2 계약 검증

계약 검증은 단계 간 데이터 무결성을 보장합니다:

**계약 위반 심각도**:

| 심각도 | 설명 | 조치 |
|--------|------|------|
| **CRITICAL** | 차단 위반 | 즉시 중단, 재생성 필요 |
| **MAJOR** | 중요한 문제 | 경고, 수동 검토 필요 |
| **MINOR** | 사소한 불일치 | 로그 후 계속 |

**검증 규칙**:

| 규칙 | 설명 |
|------|------|
| `output_exists` | 출력 파일/디렉토리가 존재해야 함 |
| `yaml_syntax` | 유효한 YAML 형식 |
| `not_empty` | 파일에 내용이 있어야 함 |
| `metadata_required` | 필수 메타데이터 필드 존재 |
| `timestamp_format` | 타임스탬프 ISO8601 형식 |
| `summary_count_match` | 요약 카운트가 실제 데이터와 일치 |
| `url_lowercase` | URL은 소문자여야 함 |
| `url_trailing_slash` | 후행 슬래시 없음 |
| `url_extension` | 확장자 없음 (.mi, .do, .action) |

**ContractValidator 사용법**:

```python
validator = ContractValidator(contracts_path)
validator.load_contracts()

# Stage 출력 검증
violations = validator.validate_stage_output(
    stage=1,
    phase=4,
    output_path=Path("work/specs/stage1-outputs/phase4/FEAT-PA-001")
)

# 차단 위반 확인
if validator.has_blocking_violations(violations):
    raise ValidationError("심각한 위반 발견")

# 요약 가져오기
summary = validator.get_violations_summary(violations)
# {"CRITICAL": 0, "MAJOR": 2, "MINOR": 5}
```

**URL 정규화**:

```python
def normalize_url(url: str) -> str:
    """계약 규칙에 따라 URL 정규화"""
    if not url:
        return url

    # 1단계: 소문자화
    normalized = url.lower()

    # 2단계: 후행 슬래시 제거
    normalized = normalized.rstrip("/")

    # 3단계: 확장자 제거
    for ext in [".mi", ".do", ".action"]:
        if normalized.endswith(ext):
            normalized = normalized[:-len(ext)]
            break

    return normalized
```

### 10.3 품질 게이트

품질 게이트는 워크플로우 진행 기준을 강제합니다:

```
품질 게이트 기준:

┌─────────────────────────────────────────────────────────────┐
│                    Stage 완료 게이트                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  커버리지 요구사항:                                          │
│  ├─ Feature 커버리지  ≥ 99%                                 │
│  ├─ Endpoint 커버리지 ≥ 95%                                 │
│  └─ SQL 커버리지      = 100%                                │
│                                                             │
│  위반 임계값:                                                │
│  ├─ CRITICAL          = 0                                   │
│  ├─ MAJOR             ≤ 5 (정당화 필요)                     │
│  └─ MINOR             ≤ 20                                  │
│                                                             │
│  Phase Gate 상태:                                           │
│  └─ 모든 Feature가 현재 Phase를 완료해야 함                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  결과: 통과 / 실패 / 조건부                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. 모범 사례

### 11.1 워크플로우 최적화

**도메인 우선순위 지정**:

```yaml
# project.yaml - 도메인 처리 순서 최적화
domain:
  priority_map:
    P0-Foundation: ["CM"]       # 먼저 처리 - 공유 컴포넌트
    P1-Hub: ["PA"]              # 고가치 기능
    P2-Core: ["MM", "QM"]       # 핵심 비즈니스 로직
    P3-Supporting: ["RP"]       # 낮은 우선순위
```

**병렬 세션 튜닝**:

| 시나리오 | 권장 세션 수 | 근거 |
|----------|-------------|------|
| 로컬 개발 머신 | 1-3 | 리소스 제약 |
| CI/CD 파이프라인 | 3-5 | 균형 잡힌 처리량 |
| 전용 서버 | 5-10 | 최대 병렬성 |

**Phase Gate 전략**:

```yaml
# config.yaml - Phase Gate 튜닝
phase_gate:
  enabled: true
  strict_mode: true        # 위반 시 즉시 실패
  auto_to_max: true        # 수동 진행을 기다리지 않음
  max_allowed_phase: null  # 시스템이 계산하도록 함
```

### 11.2 오류 처리

**Stale 세션 복구**:

Choisor는 자동으로 stale 세션을 복구합니다:

```
Stale 세션 감지:

1. 세션 비활성 > stale_timeout (기본: 10분)
2. 스케줄러가 stale 상태 감지
3. 태스크를 PENDING으로 리셋
4. 세션을 IDLE로 해제
5. 태스크 재할당 가능
```

**설정**:

```yaml
assignment:
  stale_timeout: 10  # stale 감지까지의 시간(분)
```

**태스크 실패 처리**:

```bash
# 실패한 태스크 수동 리셋
/choisor clean-restart FEAT-PA-001

# 실패 이유 확인
/choisor query --status failed --list
```

### 11.3 문제 해결

**일반적인 문제**:

| 문제 | 증상 | 해결책 |
|------|------|--------|
| 태스크가 할당되지 않음 | 상태에 pending으로 표시되지만 진행 없음 | `assignment.enabled: true` 확인 |
| Phase Gate 차단 | 상태에 "게이트 차단" | 현재 Phase의 대기 중인 태스크 완료 |
| 세션 타임아웃 | 세션이 stale 상태가 됨 | `stale_timeout` 증가 |
| 태스크 없음 | 스캔이 0개 태스크 반환 | 스펙 파일 구조 확인 |
| 병렬 작동 안 함 | 한 번에 하나의 태스크만 | `parallel.enabled: true` 확인 |

**진단 명령어**:

```bash
# 현재 상태 확인
/choisor status

# 태스크 스캔 확인
/choisor scan --stage 1

# 특정 도메인 조회
/choisor query --domain PA --list

# 세션 상태 확인
# .choisor/sessions/sessions.json 확인
```

**로그 분석**:

```bash
# 데몬 로그 위치
.choisor/logs/

# 아카이브된 인스트럭션
.choisor/logs/instructions/

# tasks.json의 태스크 히스토리
.choisor/tasks/tasks.json
```

---

## 부록

### A. 설정 레퍼런스

#### config.yaml (전체 레퍼런스)

```yaml
# 할당 제어
assignment:
  enabled: bool          # 태스크 할당 활성화/비활성화 (기본: true)
  delay: int | null      # 할당 지연 시간(분) (기본: null)
  stale_timeout: int     # stale 세션 타임아웃(분) (기본: 10)

# 자동 커밋
auto_commit:
  enabled: bool          # 자동 커밋 활성화 (기본: true)
  commit_on_completion: bool  # 각 Phase 후 커밋 (기본: true)

# 제공자
provider: str            # LLM 제공자 (기본: "anthropic")
default_model: str       # 모델 ID (기본: "claude-opus-4-5-20251101")

# Claude Code
claude_code:
  max_sessions: int      # 최대 동시 세션 (기본: 1)
  max_output_tokens: int # 출력 토큰 제한 (기본: 65536)
  default_model: str     # 세션의 기본 모델

# 현재 위치
current:
  stage: str             # 현재 Stage (예: "stage1")
  phase: str             # 현재 Phase (예: "phase1")

# Phase Gate
phase_gate:
  max_allowed_phase: str | null  # 최대 Phase (null = 자동)
  auto_to_max: bool      # 자동 진행 (기본: true)
  enabled: bool          # Phase Gate 활성화 (기본: true)
  strict_mode: bool      # 위반 시 실패 (기본: true)

# 병렬 실행
parallel:
  enabled: bool          # 병렬 활성화 (기본: true)
  pairs: list[list[str]] # 스킬 쌍 (기본: [["s4-03", "s4-04"]])
  max_parallel_sessions: int  # 최대 병렬 (기본: 10)

# 경로
paths:
  skills_root: str       # 스킬 디렉토리 (기본: ".claude/skills")
  contracts_path: str    # 계약 파일 경로

# 작업 범위
work_scope:
  enabled_domains: list[str] | null  # 도메인 필터 (null = 전체)
  enabled_stages: list[int] | null   # Stage 필터 (null = 전체)

# 우선순위
priority:
  algorithm: str         # "weighted_score" | "fifo"
  weights:
    dependency_ready: float   # 의존성 가중치 (기본: 0.5)
    priority_score: float     # 우선순위 가중치 (기본: 0.3)
    estimated_duration: float # 기간 가중치 (기본: 0.2)
```

#### project.yaml (전체 레퍼런스)

```yaml
# 프로젝트 식별
name: str                # 프로젝트 이름 (필수)
description: str         # 프로젝트 설명

# Feature 패턴
feature:
  id_prefix: str         # Feature ID 접두사 (기본: "FEAT-")
  gap_suffix: str        # GAP Feature 접미사 (기본: "GAP")
  skip_gap_features: bool  # GAP Feature 건너뛰기 (기본: true)

# 도메인 설정
domain:
  skip_domains: list[str]  # 건너뛸 도메인
  priority_map:
    P0-Foundation: list[str]
    P1-Hub: list[str]
    P2-Core: list[str]
    P3-Supporting: list[str]

# Phase 유형
phase_types:
  stage1:
    phase1: str  # "system" | "domain" | "feature"
    phase2: str
    phase3: str
    phase4: str
  # ... (stages 2-5)

# 경로
paths:
  source_base: str       # 레거시 소스 디렉토리 (필수)
  target_base: str       # 생성 코드 디렉토리 (필수)
  java_src_path: str     # Java 소스 경로 (기본: "src/main/java")
  mapper_path: str       # 매퍼 경로 (기본: "src/main/resources/mapper")
  java_package: str      # Java 패키지 (필수)
  specs_root: str        # 스펙 루트 (기본: "work/specs")

# Stage 정의
stages:
  stage1:
    name: str
    phases: list[str]
    skills:
      phase1: str
      phase2: str
      # ...

# 태스크 소스
task_sources:
  feature_inventory_base: str
  feature_inventory_pattern: str
  stage1_specs: str
  stage4_specs: str
```

### B. 명령어 빠른 참조

| 명령어 | 설명 |
|--------|------|
| `/choisor init` | 프로젝트 초기화 |
| `/choisor init --template <name>` | 템플릿 사용 |
| `/choisor init --force` | 재초기화 |
| `/choisor init --list-templates` | 템플릿 목록 |
| `/choisor status` | 상태 표시 |
| `/choisor scan [--stage N]` | 태스크 스캔 |
| `/choisor sync` | 태스크 상태 동기화 |
| `/choisor query [options]` | 태스크 조회 |
| `/choisor manual-assign <id>` | Feature 할당 |
| `/choisor clean-restart <ids>` | Feature 리셋 |
| `/choisor stop` | 첫 번째 세션 중지 |
| `/choisor stop --feature <id>` | Feature로 중지 |
| `/choisor stop --session <id>` | 세션으로 중지 |
| `/choisor stop --all` | 모든 세션 중지 |

**Query 옵션**:

| 옵션 | 설명 |
|------|------|
| `--status <status>` | 상태별 필터 |
| `--domain <code>` | 도메인별 필터 |
| `--stage <number>` | Stage별 필터 |
| `--phase <number>` | Phase별 필터 |
| `--list` | 태스크 목록 표시 |
| `--limit <n>` | 결과 제한 |
| `--format json` | JSON 출력 |

### C. 용어집

| 용어 | 정의 |
|------|------|
| **Choisor** | 다단계 마이그레이션 워크플로우를 위한 태스크 오케스트레이터 |
| **Stage** | 주요 워크플로우 단계 (1-5) |
| **Phase** | Stage 내의 하위 단계 (1-5) |
| **Skill** | Claude Code 스킬 정의 (.claude/skills/s{N}-{NN}-*/) |
| **Task** | 원자적 작업 단위 (stage + phase + feature) |
| **Feature** | 마이그레이션 대상 비즈니스 기능 |
| **Domain** | Feature를 그룹화하는 기능 도메인 |
| **Phase Gate** | 순차적 Phase 완료를 보장하는 체크포인트 |
| **Session** | Claude Code 실행 컨텍스트 |
| **Session Pool** | 여러 동시 세션 관리자 |
| **Scheduler** | 세션에 태스크를 할당하는 컴포넌트 |
| **Priority Tier** | 도메인 중요도 분류 (P0-P3) |
| **Contract** | 단계 간 데이터 형식 사양 |
| **Validator** | 출력 무결성을 확인하는 컴포넌트 |
| **Plugin** | 커스텀 로직을 위한 확장 가능한 컴포넌트 |
| **QUERY-FIRST** | SQL 보존을 우선시하는 설계 원칙 |
| **GAP Feature** | 갭 분석용으로 표시된 Feature (생성에서 건너뜀) |
| **Stale Session** | 타임아웃 임계값을 초과하여 비활성화된 세션 |

---

## 문서 이력

| 버전 | 날짜 | 변경 사항 |
|------|------|----------|
| 2.0.0 | 2026-01 | 최초 릴리스 |

---

*이 문서는 Choisor 2.0 프로젝트의 일부입니다. 최신 업데이트는 프로젝트 저장소를 참조하세요.*
