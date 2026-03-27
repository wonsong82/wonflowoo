# AI-Powered Legacy Migration Workbook

**Version**: 1.0.0
**Last Updated**: 2025-12-15

---

## Overview

이 워크북은 AI 기반 레거시 시스템 마이그레이션을 위한 포괄적인 방법론 가이드입니다. 대규모 엔터프라이즈 시스템의 현대화 프로젝트에서 AI 에이전트를 효과적으로 활용하기 위한 체계적인 프레임워크를 제공합니다.

### Key Principles

- **AI-Powered**: LLM 기반 분석, 생성, 검증 자동화
- **Quality-First**: 100% 비즈니스 로직 보존 우선
- **Systematic**: Stage-Phase-Task 계층적 워크플로우
- **Scalable**: 수백~수천 개 Feature 처리 가능

---

## Quick Start (5분 시작)

처음 시작하시나요? **[QUICK-START.md](QUICK-START.md)** 부터 읽어보세요.

- Claude Code 기본 사용법
- Skills 개념 및 실행 방법
- Choisor 역할 및 기본 구조
- 첫 번째 Feature 분석 실습

---

## Table of Contents

### [00-OVERVIEW](00-OVERVIEW.md)
프레임워크 철학, 5-Stage 라이프사이클, 핵심 원칙

---

### 01-ASSESSMENT (평가)
프로젝트 시작 전 레거시 시스템 분석 및 실현 가능성 평가

| File | Description |
|------|-------------|
| [01-legacy-analysis-checklist.md](01-ASSESSMENT/01-legacy-analysis-checklist.md) | 레거시 분석 체크리스트 (14개 Assessment Task) |
| [02-complexity-estimation.md](01-ASSESSMENT/02-complexity-estimation.md) | 복잡도 추정 (HIGH/MEDIUM/LOW 3-tier) |
| [03-feasibility-matrix.md](01-ASSESSMENT/03-feasibility-matrix.md) | 실현 가능성 매트릭스 (Go/No-Go 결정) |

---

### 02-WORKFLOW-DESIGN (워크플로우 설계)
Stage-Phase 모델 및 커스터마이제이션

| File | Description |
|------|-------------|
| [00-pipeline-overview.md](02-WORKFLOW-DESIGN/00-pipeline-overview.md) | **Pipeline Flow 시각화** - Stage/Phase 간 In/Out 흐름 |
| [01-stage-phase-model.md](02-WORKFLOW-DESIGN/01-stage-phase-model.md) | Stage-Phase 계층 구조 및 Phase Gate |
| [02-customization-guide.md](02-WORKFLOW-DESIGN/02-customization-guide.md) | 프로젝트별 워크플로우 커스터마이제이션 |
| [03-decision-trees.md](02-WORKFLOW-DESIGN/03-decision-trees.md) | 주요 결정 포인트별 Decision Tree |

---

### 03-SKILL-DEFINITION (스킬 정의)
SKILL.md 구조 및 개발 가이드

| File | Description |
|------|-------------|
| [01-skill-structure.md](03-SKILL-DEFINITION/01-skill-structure.md) | SKILL.md 표준 구조 및 유형 |
| [02-skill-catalog.md](03-SKILL-DEFINITION/02-skill-catalog.md) | 전체 스킬 카탈로그 (5개 Stage × 다중 Phase) |
| [03-skill-development.md](03-SKILL-DEFINITION/03-skill-development.md) | 새 스킬 개발 가이드 |

---

### 04-TOOL-ECOSYSTEM (도구 생태계)
Claude Code, Orchestrator, 모니터링 설정

| File | Description |
|------|-------------|
| [01-claude-code-configuration.md](04-TOOL-ECOSYSTEM/01-claude-code-configuration.md) | CLAUDE.md 구성 및 모델 선택 전략 |
| [02-orchestrator-setup.md](04-TOOL-ECOSYSTEM/02-orchestrator-setup.md) | Choisor 및 고급 오케스트레이터 설정 |
| [03-monitoring-dashboard.md](04-TOOL-ECOSYSTEM/03-monitoring-dashboard.md) | 메트릭 수집 및 대시보드 구성 |

---

### 05-EXECUTION-PATTERNS (실행 패턴)
배치 처리, 병렬 실행, 오류 복구

| File | Description |
|------|-------------|
| [01-batch-processing.md](05-EXECUTION-PATTERNS/01-batch-processing.md) | 배치 처리 전략 및 체크포인팅 |
| [02-parallel-execution.md](05-EXECUTION-PATTERNS/02-parallel-execution.md) | 병렬 실행 및 동기화 패턴 |
| [03-error-recovery.md](05-EXECUTION-PATTERNS/03-error-recovery.md) | 오류 감지, 재시도, 복구 절차 |

---

### 06-QUALITY-ASSURANCE (품질 보증)
검증 프레임워크, Phase Gate, Remediation

| File | Description |
|------|-------------|
| [01-validation-framework.md](06-QUALITY-ASSURANCE/01-validation-framework.md) | 4-Layer 검증 프레임워크 및 스코어링 |
| [02-phase-gate-criteria.md](06-QUALITY-ASSURANCE/02-phase-gate-criteria.md) | Stage별 Phase Gate 기준 |
| [03-remediation-procedures.md](06-QUALITY-ASSURANCE/03-remediation-procedures.md) | 검증 실패 시 Remediation 절차 |
| [04-human-checklist.md](06-QUALITY-ASSURANCE/04-human-checklist.md) | **Human Critical Checklist** - 재작업 방지 핵심 체크리스트 |

---

### 07-CASE-STUDIES (사례 연구)
실제 프로젝트 적용 사례 및 교훈

| File | Description |
|------|-------------|
| [01-hallain-tft-case.md](07-CASE-STUDIES/01-hallain-tft-case.md) | hallain_tft 마이그레이션 사례 |
| [02-lessons-learned.md](07-CASE-STUDIES/02-lessons-learned.md) | 프로젝트 교훈 및 Anti-patterns |
| [03-tips-best-practices.md](07-CASE-STUDIES/03-tips-best-practices.md) | **Tips & Best Practices** - 실용적 팁 모음 |

---

### APPENDIX (부록)
용어집, 템플릿, 트러블슈팅

| File | Description |
|------|-------------|
| [01-glossary.md](APPENDIX/01-glossary.md) | 용어 정의 (A-W) |
| [02-templates.md](APPENDIX/02-templates.md) | Spec, Report, Skill 템플릿 |
| [03-troubleshooting.md](APPENDIX/03-troubleshooting.md) | 문제 해결 가이드 |
| [04-directory-structure.md](APPENDIX/04-directory-structure.md) | **폴더 구조 해설** - 주요 디렉토리 설명 |

---

## Quick Start

### 1. Assessment (1-2주)
```
01-ASSESSMENT/ 체크리스트로 레거시 분석
→ 복잡도 추정 및 실현 가능성 평가
→ Go/No-Go 결정
```

### 2. Setup (1주)
```
CLAUDE.md 구성 (04-TOOL-ECOSYSTEM/01)
→ Skill 카탈로그 검토 (03-SKILL-DEFINITION/02)
→ Orchestrator 설정 (04-TOOL-ECOSYSTEM/02)
```

### 3. Execution (N주)
```
Stage 1: Discovery (Feature 추출 → 분석 → 스펙 생성)
→ Stage 2: Validation (Ground Truth 비교)
→ Stage 3: Preparation (아키텍처 설계)
→ Stage 4: Generation (코드 생성)
→ Stage 5: Assurance (검증 및 표준화)
```

### 4. Quality Control
```
Phase Gate 적용 (06-QUALITY-ASSURANCE/02)
→ 실패 시 Remediation (06-QUALITY-ASSURANCE/03)
→ Final Quality Gate 통과
```

---

## Workbook Statistics

| Category | Count |
|----------|-------|
| Sections | 8 |
| Documents | 25 |
| Templates | 10+ |
| Skills Referenced | 25 |
| Decision Trees | 5+ |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-01-16 | Quick Start Guide, Pipeline Overview, Human Checklist, Tips & Best Practices, Directory Structure 추가 |
| 1.0.0 | 2025-12-15 | Initial release |

---

## Contributing

이 워크북은 지속적으로 개선됩니다. 새로운 패턴, 교훈, 도구가 발견되면 해당 섹션을 업데이트하세요.

---

**Created by**: Choi | Build Center
**Based on**: hallain_tft Migration Project Experience
