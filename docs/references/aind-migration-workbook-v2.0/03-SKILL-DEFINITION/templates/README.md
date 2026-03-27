# Skill Templates

이 디렉토리에는 AI-Driven Migration 프로젝트에서 사용되는 Skill 템플릿이 포함되어 있습니다.

## Available Templates

| Template | Purpose | Use When |
|----------|---------|----------|
| `SKILL-TEMPLATE.md` | 범용 Skill 템플릿 | 모든 유형의 Skill 작성 시 |
| `analysis-skill-template.md` | Analysis Skill 템플릿 | S1, S2, S3 분석 작업 |
| `generation-skill-template.md` | Generation Skill 템플릿 | S1, S3, S4 생성 작업 |
| `validation-skill-template.md` | Validation Skill 템플릿 | S2, S5 검증 작업 |
| `transformation-skill-template.md` | Transformation Skill 템플릿 | 형식 변환 작업 |
| `orchestration-skill-template.md` | Orchestration Skill 템플릿 | Cross-cutting 제어 작업 |

## Skill Path Structure (Important!)

> **Claude Code 공식 문서 기준**: Skills는 **flat 구조**로 배치해야 합니다.
> 디렉토리명과 `name` 필드가 **반드시 일치**해야 합니다.

### Skill 저장 위치 (우선순위)

| Priority | Location | Path | Scope |
|----------|----------|------|-------|
| 1 | Enterprise | managed settings | 전체 조직 |
| 2 | Personal | `~/.claude/skills/` | 개인, 전체 프로젝트 |
| 3 | Project | `.claude/skills/` | 저장소 공유 |
| 4 | Plugin | Plugin 번들 | Plugin 설치자 |

### 올바른 디렉토리 구조

```
.claude/skills/
├── discovery-feature-inventory/      # 디렉토리명 = name 필드
│   └── SKILL.md
├── discovery-miplatform-protocol/
│   └── SKILL.md
├── preparation-api-design/
│   └── SKILL.md
└── execution-code-generation/
    └── SKILL.md
```

### 잘못된 구조 (피해야 함)

```
# ❌ 중첩 구조 - 디렉토리명과 name 불일치
.claude/skills/
└── discovery/                        # 중간 stage 디렉토리 금지
    └── feature-inventory/            # name: discovery-feature-inventory와 불일치
        └── SKILL.md
```

### 네이밍 규칙

| 항목 | 규칙 | 예시 |
|------|------|------|
| 디렉토리명 | 소문자, 숫자, 하이픈만 | `discovery-feature-inventory` |
| 파일명 | 반드시 `SKILL.md` (대소문자 구분) | `SKILL.md` |
| name 필드 | 소문자, 숫자, 하이픈 (최대 64자) | `discovery-feature-inventory` |
| **일치 필수** | 디렉토리명 = name 필드 | ✓ |

## Usage

1. 적절한 템플릿 파일 복사
2. `{placeholder}` 값을 실제 값으로 대체
3. 불필요한 섹션 제거 또는 필요한 섹션 추가
4. 품질 체크리스트 검증

## Template Selection Guide

```
Is this an analysis task?
├─ Yes → analysis-skill-template.md
└─ No
   └─ Is this a generation task?
      ├─ Yes → generation-skill-template.md
      └─ No
         └─ Is this a validation task?
            ├─ Yes → validation-skill-template.md
            └─ No
               └─ Is this a transformation task?
                  ├─ Yes → transformation-skill-template.md
                  └─ No → orchestration-skill-template.md
```

## Quick Start

```bash
# 1. Skill 디렉토리 생성 (디렉토리명 = skill name)
mkdir -p .claude/skills/{stage}-{skill-name}

# 2. 템플릿 복사
cp templates/SKILL-TEMPLATE.md .claude/skills/{stage}-{skill-name}/SKILL.md

# 예시:
mkdir -p .claude/skills/discovery-feature-inventory
cp templates/SKILL-TEMPLATE.md .claude/skills/discovery-feature-inventory/SKILL.md

# 3. 편집
# name 필드가 디렉토리명과 일치하는지 확인!
# name: discovery-feature-inventory

# 4. 검증
# Quality checks 체크리스트 확인

# 5. Claude Code 재시작
# Skills 변경 후 반드시 재시작 필요
```

## Multi-File Skill Structure (대규모 Skill)

복잡한 Skill의 경우 보조 파일을 사용하되, `SKILL.md`는 500줄 이내로 유지:

```
discovery-deep-analysis/
├── SKILL.md              # 개요 및 네비게이션 (필수)
├── reference.md          # 상세 API 문서 - 필요 시 로드
├── examples.md           # 사용 예시 - 필요 시 로드
└── scripts/
    ├── helper.py         # 유틸리티 스크립트 - 실행만, 로드 안함
    └── validate.py       # 검증 스크립트 - 실행만, 로드 안함
```
