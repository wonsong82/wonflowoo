# Quick Start Guide

**Version**: 1.0.0
**Last Updated**: 2026-01-16

---

## Overview

이 가이드는 AI 기반 Legacy Migration을 처음 시작하는 사용자를 위한 5분 요약입니다.

---

## 1. Claude Code 기본 사용법

### 1.1 설치 및 실행

```bash
# Claude Code 설치 (npm)
npm install -g @anthropic-ai/claude-code

# 프로젝트 디렉토리에서 실행
cd your-project
claude
```

### 1.2 기본 명령어

| 명령어 | 설명 |
|--------|------|
| `/help` | 도움말 표시 |
| `/clear` | 대화 초기화 |
| `/<skill-name>` | 스킬 실행 (예: `/s1-01-discovery-feature-inventory`) |

### 1.3 CLAUDE.md

프로젝트 루트에 `CLAUDE.md` 파일을 생성하면 Claude Code가 프로젝트 컨텍스트를 이해합니다.

```markdown
# 프로젝트 이름

## Tech Stack
- Framework: Spring MVC → Spring Boot 3.2
- ORM: iBatis → MyBatis

## Key Principles
- QUERY-FIRST: SQL 100% 보존
```

---

## 2. Skills 개념 및 실행 방법

### 2.1 Skill이란?

Skill은 특정 작업을 수행하기 위한 **표준화된 지시서**입니다.

```
.claude/skills/
├── s1-01-discovery-feature-inventory/   ← Stage 1, Phase 1
│   ├── SKILL.md                         ← 실행 지시서
│   └── output.schema.yaml               ← 출력 스키마
├── s1-02-discovery-miplatform-protocol/ ← Stage 1, Phase 2
└── ...
```

### 2.2 Skill 실행

```bash
# Claude Code에서 스킬 실행
/s1-01-discovery-feature-inventory
```

### 2.3 Skill 네이밍 규칙

```
s{Stage}-{Phase}-{category}-{name}
│   │      │         │
│   │      │         └── 구체적 이름
│   │      └── 카테고리 (discovery, validation, generation, assurance)
│   └── Phase 번호 (01, 02, ...)
└── Stage 번호 (1-5)
```

---

## 3. Choisor (Orchestrator)

### 3.1 역할

Choisor는 대규모 마이그레이션 작업을 자동으로 관리하는 **오케스트레이터**입니다.

```
┌─────────────────────────────────────────────────────────┐
│                      Choisor                            │
├─────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐           │
│  │ Task      │  │ Progress  │  │ Phase     │           │
│  │ Assignment│  │ Tracking  │  │ Gate      │           │
│  └───────────┘  └───────────┘  └───────────┘           │
├─────────────────────────────────────────────────────────┤
│  Config: .choisor/config.yaml                           │
│  Status: .choisor/tasks/                                │
└─────────────────────────────────────────────────────────┘
```

### 3.2 기본 설정 (`.choisor/config.yaml`)

```yaml
# 현재 진행 상태
current:
  stage: "stage1"
  phase: "phase1"

# Phase Gate 설정
phase_gate:
  max_allowed_phase: "phase1"

# 작업 범위
work_scope:
  enabled_domains: [cm, pa]  # 처리할 도메인
```

### 3.3 주요 명령어

```bash
# 상태 조회
python -m choisor status

# 다음 작업 할당
python -m choisor assign-next

# 작업 완료 처리
python -m choisor process-completion <task-id>
```

---

## 4. 첫 번째 Feature 분석 실습

### Step 1: 프로젝트 설정 확인

```bash
# 디렉토리 구조 확인
ls -la
# CLAUDE.md 존재 확인
cat CLAUDE.md
```

### Step 2: Feature Inventory Skill 실행

```bash
# Claude Code 실행
claude

# Skill 실행
> /s1-01-discovery-feature-inventory
```

### Step 3: 산출물 확인

```bash
# 생성된 Feature Inventory 확인
cat work/specs/stage1-outputs/phase1/feature-inventory.yaml
```

**예상 출력:**

```yaml
features:
  - id: "PA001-selectList"
    domain: "pa"
    controller: "PAController.java"
    endpoint: "/pa/selectList.mi"
    complexity: "MEDIUM"
```

### Step 4: 결과 검증

```yaml
# 검증 체크리스트
verification:
  - [ ] 모든 Controller 파일 식별됨
  - [ ] 엔드포인트 URL 패턴 정확함
  - [ ] 복잡도 분류 적절함
```

---

## 5. 다음 단계

### 5.1 전체 워크플로우 이해

```
Assessment → Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5
(평가)       (분석)    (검증)    (준비)    (생성)    (품질)
```

자세한 내용: [00-OVERVIEW.md](00-OVERVIEW.md)

### 5.2 Pipeline 흐름 파악

각 Stage/Phase의 Input/Output을 이해합니다.

자세한 내용: [02-WORKFLOW-DESIGN/00-pipeline-overview.md](02-WORKFLOW-DESIGN/00-pipeline-overview.md)

### 5.3 품질 기준 확인

Phase Gate 통과 기준을 숙지합니다.

자세한 내용: [06-QUALITY-ASSURANCE/02-phase-gate-criteria.md](06-QUALITY-ASSURANCE/02-phase-gate-criteria.md)

---

## Troubleshooting

### 문제: Skill 실행 시 오류

```
Error: Skill not found
```

**해결:** `.claude/skills/` 디렉토리에 Skill 파일이 존재하는지 확인

```bash
ls .claude/skills/
```

### 문제: Context 초과 오류

```
Error: Context limit exceeded
```

**해결:** 대상 파일 수를 줄이거나 Wave 분할 적용

```yaml
# config.yaml에서 도메인 제한
work_scope:
  enabled_domains: [cm]  # 작은 도메인부터 시작
```

### 문제: Phase Gate 실패

**해결:** Phase Gate 기준 확인 후 미달 항목 보완

```bash
# Gate 기준 확인
cat workbook/06-QUALITY-ASSURANCE/02-phase-gate-criteria.md
```

---

## Quick Reference

| 항목 | 위치 |
|------|------|
| 전체 개요 | `workbook/00-OVERVIEW.md` |
| Skill 카탈로그 | `.claude/skills/` |
| Choisor 설정 | `.choisor/config.yaml` |
| 산출물 저장 | `work/specs/` |
| Phase Gate 기준 | `workbook/06-QUALITY-ASSURANCE/02-phase-gate-criteria.md` |

---

**Next:** [00-OVERVIEW.md](00-OVERVIEW.md) - 프레임워크 철학 및 전체 구조 이해
