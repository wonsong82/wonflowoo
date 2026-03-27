# Directory Structure Guide

**Version**: 1.0.0
**Last Updated**: 2026-01-16

---

## Overview

AI 기반 Legacy Migration 프로젝트의 주요 디렉토리 구조를 설명합니다.

---

## 1. 전체 구조

```
project-root/
│
├── hallain/                 ← Legacy 소스 코드
│
├── next-hallain/            ← 생성된 Spring Boot 프로젝트
│
├── .choisor/                ← 오케스트레이터 설정 및 상태
│
├── .claude/                 ← Claude Code 설정
│   └── skills/              ← AI Skill 정의
│
├── work/                    ← 작업 산출물
│   └── specs/               ← Stage별 산출물
│
├── workbook/                ← 방법론 문서
│
└── CLAUDE.md                ← 프로젝트 컨텍스트
```

---

## 2. `.choisor/` - 오케스트레이터

```
.choisor/
├── config.yaml              ← 핵심 설정 파일
├── tasks/                   ← 작업 상태 관리
│   └── {domain}/
│       └── {feature}/
│           ├── status.yaml  ← pending | in_progress | completed | failed
│           └── error.yaml   ← 실패 시 오류 정보
└── logs/                    ← 실행 로그
```

### 2.1 `config.yaml` 주요 설정

```yaml
# 현재 진행 상태
current:
  stage: "stage4"            # 현재 Stage
  phase: "phase3"            # 현재 Phase

# Phase Gate 제어
phase_gate:
  max_allowed_phase: "phase3"  # 진행 가능한 최대 Phase
  auto_to_max: false           # 자동 진행 여부

# 작업 범위
work_scope:
  enabled_domains: [cm, pa, mm]  # 처리할 도메인 (null = 전체)

# 경로 설정
paths:
  source: "hallain/"             # Legacy 소스
  specs: "work/specs/"           # 산출물 저장

# Stage 정의
stages:
  stage1:
    name: "Discovery"
    skills:
      phase1: "s1-01-discovery-feature-inventory"
      phase2: "s1-02-discovery-miplatform-protocol"
      ...
```

---

## 3. `.claude/skills/` - AI Skill 정의

```
.claude/skills/
│
├── common/                  ← 공통 스키마 및 계약
│   ├── types.schema.yaml    ← 공통 타입 정의
│   └── inter-stage-contracts.yaml  ← Stage 간 데이터 계약
│
├── choisor/                 ← Choisor 오케스트레이터 코드
│   ├── main.py
│   ├── commands/            ← CLI 명령어
│   ├── daemon/              ← 백그라운드 서비스
│   └── lib/                 ← 유틸리티
│
├── s1-01-discovery-feature-inventory/
│   ├── SKILL.md             ← 실행 지시서
│   └── output.schema.yaml   ← 출력 검증 스키마
│
├── s1-02-discovery-miplatform-protocol/
│   ├── SKILL.md
│   └── output.schema.yaml
│
├── ...
│
└── s5-05-assurance-quality-gate/
    ├── SKILL.md
    └── output.schema.yaml
```

### 3.1 SKILL.md 구조

```markdown
# Skill Name

## 목적
이 Skill의 목적 설명

## 입력
- 입력 파일 경로
- 필수 선행 조건

## 출력
- 출력 파일 경로
- 출력 스키마 참조

## 실행 절차
1. Step 1
2. Step 2
3. ...

## 검증 체크리스트
- [ ] 검증 항목 1
- [ ] 검증 항목 2

## 품질 기준
- 기준 1: 값
- 기준 2: 값
```

### 3.2 output.schema.yaml 구조

```yaml
$schema: "https://json-schema.org/draft/2020-12/schema"
type: object
required:
  - feature
  - data_access
properties:
  feature:
    type: object
    properties:
      id:
        type: string
      domain:
        type: string
  data_access:
    type: object
    properties:
      queries:
        type: array
```

---

## 4. `work/specs/` - 산출물 저장

```
work/specs/
│
├── stage1-outputs/
│   ├── phase1/
│   │   ├── feature-inventory.yaml      ← 전체 Feature 목록
│   │   └── summary.yaml                ← 요약 통계
│   │
│   ├── phase2/
│   │   └── protocol-analysis.yaml      ← MiPlatform 프로토콜 분석
│   │
│   ├── phase3/
│   │   └── {domain}/
│   │       └── {feature}/
│   │           └── *-analysis.yaml     ← 5-layer 심층 분석
│   │
│   └── phase4/
│       └── {domain}/
│           └── {feature}/
│               ├── main.yaml           ← 완성된 Feature 스펙
│               └── api-spec.yaml       ← OpenAPI 스펙
│
├── stage2-outputs/
│   ├── phase1/
│   │   └── source-inventory.yaml       ← Ground Truth
│   │
│   ├── phase2/
│   │   └── comparison-report.yaml      ← 비교 결과
│   │
│   ├── phase3/
│   │   └── gap-analysis.yaml           ← Gap 분석
│   │
│   └── phase4/
│       └── completion-log.yaml         ← 보완 로그
│
├── stage3-outputs/
│   ├── phase1/
│   │   └── dependency-graph.yaml       ← 의존성 그래프
│   │
│   ├── phase2/
│   │   └── interfaces.yaml             ← 인터페이스 정의
│   │
│   ├── phase3/
│   │   └── technical-debt.yaml         ← 기술 부채
│   │
│   ├── phase4/
│   │   ├── architecture-design.yaml    ← 아키텍처 설계
│   │   └── adr/                        ← Architecture Decision Records
│   │
│   └── phase5/
│       └── generation-spec.yaml        ← 생성 명세
│
├── stage4-outputs/
│   ├── phase2/
│   │   └── mini-pilot-report.yaml      ← Mini-Pilot 결과
│   │
│   └── phase5/
│       └── integration-report.yaml     ← 통합 빌드 결과
│
└── stage5-outputs/
    ├── phase1/
    │   └── structural-report.yaml      ← 구조적 검증
    │
    ├── phase2/
    │   └── functional-report.yaml      ← 기능적 검증
    │
    ├── phase3/
    │   └── api-contract-report.yaml    ← API 계약 검증
    │
    ├── phase4/
    │   └── performance-report.yaml     ← 성능 검증
    │
    └── phase5/
        └── quality-gate-report.yaml    ← 최종 품질 Gate
```

---

## 5. `next-hallain/` - 생성된 프로젝트

```
next-hallain/
│
├── build.gradle             ← Gradle 빌드 설정
├── settings.gradle
│
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/halla/
│   │   │       ├── common/          ← 공통 모듈
│   │   │       │   ├── config/      ← Spring 설정
│   │   │       │   ├── exception/   ← 예외 처리
│   │   │       │   └── util/        ← 유틸리티
│   │   │       │
│   │   │       └── {domain}/        ← 도메인별 코드
│   │   │           ├── controller/  ← REST Controller
│   │   │           ├── service/     ← Service Layer
│   │   │           ├── vo/          ← Value Objects
│   │   │           └── mapper/      ← MyBatis Mapper Interface
│   │   │
│   │   └── resources/
│   │       ├── application.yml      ← Spring Boot 설정
│   │       └── mapper/
│   │           └── {domain}/        ← MyBatis XML
│   │               └── *.xml
│   │
│   └── test/
│       ├── java/
│       │   └── com/halla/
│       │       └── {domain}/
│       │           └── *Test.java   ← 단위/통합 테스트
│       │
│       └── resources/
│           └── db/
│               └── test-data/       ← 테스트 데이터
│
└── docs/                    ← 생성된 API 문서
    └── openapi/
```

---

## 6. `workbook/` - 방법론 문서

```
workbook/
│
├── README.md                ← 목차 및 Quick Start
├── QUICK-START.md           ← 5분 시작 가이드
├── 00-OVERVIEW.md           ← 프레임워크 개요
│
├── 01-ASSESSMENT/           ← 평가 단계
│   ├── 01-legacy-analysis-checklist.md
│   ├── 02-complexity-estimation.md
│   └── 03-feasibility-matrix.md
│
├── 02-WORKFLOW-DESIGN/      ← 워크플로우 설계
│   ├── 00-pipeline-overview.md      ← In/Out 흐름
│   ├── 01-stage-phase-model.md
│   ├── 02-customization-guide.md
│   └── 03-decision-trees.md
│
├── 03-SKILL-DEFINITION/     ← Skill 정의
│   ├── 01-skill-framework.md
│   ├── 02-skill-taxonomy.md
│   └── templates/
│
├── 04-TOOL-ECOSYSTEM/       ← 도구 설정
│   ├── 01-claude-code-configuration.md
│   ├── 02-orchestrator-setup.md
│   └── 03-monitoring-dashboard.md
│
├── 05-EXECUTION-PATTERNS/   ← 실행 패턴
│   ├── 01-batch-processing.md
│   ├── 02-parallel-execution.md
│   └── 03-error-recovery.md
│
├── 06-QUALITY-ASSURANCE/    ← 품질 보증
│   ├── 01-validation-framework.md
│   ├── 02-phase-gate-criteria.md
│   ├── 03-remediation-procedures.md
│   └── 04-human-checklist.md        ← Human 검증 체크리스트
│
├── 07-CASE-STUDIES/         ← 사례 연구
│   ├── 01-hallain-tft-case.md
│   ├── 02-lessons-learned.md
│   └── 03-tips-best-practices.md    ← 실용적 팁
│
└── APPENDIX/                ← 부록
    ├── 01-glossary.md
    ├── 02-templates.md
    ├── 03-troubleshooting.md
    └── 04-directory-structure.md    ← 이 문서
```

---

## 7. 파일 용도 Quick Reference

| 파일 | 용도 | 주요 사용 시점 |
|------|------|--------------|
| `.choisor/config.yaml` | 현재 상태 및 설정 | 프로젝트 시작, 상태 확인 |
| `SKILL.md` | Skill 실행 지시 | Phase 작업 시작 전 |
| `output.schema.yaml` | 산출물 검증 | 결과 검증 |
| `feature-inventory.yaml` | Feature 목록 | Stage 1 완료 후 참조 |
| `main.yaml` | Feature 스펙 | Stage 4 코드 생성 입력 |
| `quality-gate-report.yaml` | 최종 품질 | Stage 5 Gate 결정 |

---

## 8. 경로 탐색 팁

### 특정 Feature 스펙 찾기

```bash
# PA 도메인의 selectList Feature 스펙
cat work/specs/stage1-outputs/phase4/pa/PA001-selectList/main.yaml
```

### 특정 도메인 Controller 찾기

```bash
# 생성된 PA Controller
ls next-hallain/src/main/java/com/halla/pa/controller/
```

### Skill 확인하기

```bash
# Stage 1 Phase 1 Skill
cat .claude/skills/s1-01-discovery-feature-inventory/SKILL.md
```

### Phase Gate 기준 확인

```bash
# Phase Gate 기준
cat workbook/06-QUALITY-ASSURANCE/02-phase-gate-criteria.md
```

---

**Next:** [01-glossary.md](01-glossary.md) - 용어집
