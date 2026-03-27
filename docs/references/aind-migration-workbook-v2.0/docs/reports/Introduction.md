# Project Odyssey Introduction

## 목표
복잡한 Agent 코드 없이, **텍스트(프롬프트)만으로** Agentic Workflow를 구현하고 레거시 시스템의 현대화 전환을 자동화한다.

## 근본 원칙 (Fundamental Principles)

GIGO (Garbage In, Garbage Out)

## 세 가지 Engineering

| Engineering | 핵심 질문 | 이 프로젝트에서의 적용 |
|-------------|----------|---------------------|
| **Prompt Engineering** | 무엇을 어떻게 지시할 것인가? | Skill 문서, CLAUDE.md |
| **Process Engineering** | 어떤 순서로 어떤 일을 시킬 것인가? | Stage-Phase 계층 구조 |
| **Context Engineering** | 어떤 정보를 어떻게 제공할 것인가? | Modular Spec, Layered Loading |


### Prompt Engineering
- LLM은 궁극적으로 텍스트만 입력받는다
- 다양한 기법(RAG, Agent, Tool Use)도 결국 프롬프트를 구성하는 방법론
- **잘 작성된 프롬프트 > 복잡한 에이전트 코드**

[프롬프트 짜던 노인](crafting_prompts.md)

### Process Engineering
> **"It's the Process, Stupid!"**

- 관건은 **"어떤 순서로 어떤 일을 시킬 것인가"**
- Stage-Phase 계층 구조가 핵심
- 의존성 순서(P0→P1→P2→P3)가 Critical

### Context Engineering
- Context Compact는 좋은 신호가 아니다. 원래라면 Overflow Error
- Process를 통해 Task를 분해하면 Context를 통제할 수 있다
- LLM은 Memory가 없다 → 물리적으로 만들어 보관한다
- **Context는 작은 단위의 주제별로 분리하여 YAML 포맷으로 저장**

```
원리의 일반화 가능성:
├── Process Engineering → 어떤 대형 프로젝트에도 적용 가능
├── Context Engineering → LLM 작업 일반에 적용 가능
└── Skills는 한 수단일 뿐 → 다른 도구로도 동일 원리 적용 가능
```

## 영향을 준 기법

| Category | Tool/Technique | 영향도 | 적용 여부 |
|----------|---------------|--------|----------|
| **IDE/Extension** | Cursor Rule | Medium | 참조 |
| | Cline / Roo / Kilo | High | 참조 |
| | Continue | Low | 참조 |
| **Memory/Context** | **Memory-Bank** | **High** | **직접 적용** |
| | **Sequential Thinking** | **High** | **직접 적용** |
| **Workflow** | **Workflows (Cline)** | **High** | **직접 적용** |
| | Persona | Medium | 참조 |
| **Specification** | **poml** | **High** | **영감 수용** |
| | spec-kit | Medium | 참조 |
| **Agent Framework** | agent-os | Low | 참조 |
| | pocket-flow | Low | 참조 |
| | agent.md | Medium | 참조 |
| **Visual Workflow** | **comfyui** | **Medium** | 개념 차용 |
| **Claude Native** | **claude.md** | **Critical** | **핵심 적용** |
| | **claude-code + skills** | **Critical** | **핵심 적용** |
| **Protocol** | MCP | Medium | 적용 |
| LoRA Tuning | checkpoint | Low | 참조 |

## 핵심 차용 개념

1. **Memory-Bank**: 컨텍스트의 물리적 저장 → Stage별 Outputs 구조
2. **Sequential Thinking**: 단계적 사고 → Stage-Phase 계층
3. **Workflows**: 재사용 가능한 작업 흐름 → Skills
4. **poml**: 프롬프트 모듈화 → Modular Spec 구조

## 개념도
![](./attatchments/concept.png)

## Key Concepts
### Context Breakdown 예시
```text
specs/feat-002-order-management/
├── main.yaml                          # Feature metadata + overview
├── api-specs/                         # API endpoint specifications
│   ├── create-order.yaml
│   ├── get-order.yaml
│   ├── update-order-status.yaml
│   ├── cancel-order.yaml
│   └── ... (1 file per endpoint)
├── business-logic/                    # Business rules by category
│   ├── order-validation-rules.yaml
│   ├── payment-rules.yaml
│   ├── inventory-rules.yaml
│   └── notification-rules.yaml
├── data-model/                        # Entity specifications
│   ├── order-entity.yaml
│   ├── order-item-entity.yaml
│   ├── payment-entity.yaml
│   └── ... (1 file per entity)
├── dependencies/                      # Internal/External dependencies
│   ├── internal-dependencies.yaml
│   └── external-dependencies.yaml
├── error-scenarios/                   # Error handling
│   └── error-scenarios.yaml
└── README.md                          # Feature documentation
```

### Context 예시

```yaml
# API 엔드포인트 상세
endpoints:
  - name: "SetReqExceptionFromSave"
    http_method: "POST"
    route: "/Exception/SetReqExceptionFromSave"
    purpose: "예외 요청 제출 및 승인 라인 초기화"
    parameters:
      - name: "RequestFlag"
        type: "string"
        required: true
        description: "Y=제출, N=임시저장"
    stored_procedures:
      - "ISMEXCP_REQUEST_INS"
      - "ISMBIMP_APPR_CONTAINER_INS"
    workflow: "5-step approval process"

# 비즈니스 로직 (워크플로우)
workflow_steps:
  - step: 1
    name: "Request Submission"
    trigger: "User clicks submit (RequestFlag=Y)"
    actions:
      - "Save to DB (ISMEXCP_REQUEST_INS)"
      - "Initialize approval line"
      - "Send email notifications"
    post_conditions:
      - "Request state = PENDING"
      - "Approvers notified"

  - step: 2
    name: "Approval Review"
    trigger: "Approver opens MyWork item"
    actions:
      - "Load request details"
      - "Review and decide (APPROVE/REJECT)"

  # ... (3-5 단계 생략)

# 데이터 모델
entities:
  - name: "ExceptionRequest"
    properties:
      - REQ_NO (PK)
      - WORK_TYPE (FK to Code)
      - PM_EMP_NO (FK to Employee)
      - REQ_TITLE
      - REQ_STATE (PENDING/APPROVED/REJECTED)
```

## 작업예시

### 수동관리 (Manual Management)
![](./attatchments/claude-code-skills-multi-sessions.png)


### Orchestrator 활용 자동화 (Orchestrator Utilized Automation)
![](./attachments/choisor.png)


### Git Auto Commit

![](./attatchments/git-auto-commit.png)


![](./attatchments/git-commit-message.png)


## Case Study
### 한라건설 PoC

#### Project Summary
-  Duration: 46 days (Nov 7 - Dec 22, 2025)

| Legacy System | Modern System |
| :--- | :--- |
| Spring MVC 3.x | Spring Boot 3.x |
| iBatis 2.0 | MyBatis 3.0 |
| Java 7/8 | Java 17+ |
| MiPlatform | REST API |
| Legacy Build | Gradle 8.x |

#### Key Achievements

| Category | Target | Achieved | Rate |
|----------|--------|----------|------|
| **Features Processed** | 912 | 912 | 100% |
| **Domains Validated** | 11 | 11 | 100% |
| **API Endpoints** | 5,848 | 5,878 | 100.5% |
| **Java Files Generated** | 10,000+ | 11,894 | 119% |
| **MyBatis XML Files** | 1,000+ | 1,220 | 122% |
| **Build Status** | SUCCESS | SUCCESS | PASS |

#### Stage Completion Overview

| Stage | Description | Duration | Status | Score |
|-------|-------------|----------|--------|-------|
| **Stage 1** | Specification Extraction | 13 days | COMPLETE | 100% |
| **Stage 2** | Backward Validation | 6 days | COMPLETE | 88.6% coverage |
| **Stage 3** | Foundation & Planning | 4 days | COMPLETE | 100% |
| **Stage 4** | Code Generation | 16 days | COMPLETE | 902 features |
| **Stage 5** | Validation & QA | 7 days | **APPROVED** | **94/100** |