# Workflow Decision Trees

**Version**: 1.1.0
**Last Updated**: 2025-12-15

---

## 1. Overview

이 문서는 Legacy Migration Framework 운영 중 발생하는 주요 의사결정 상황에 대한 Decision Tree를 제공합니다.

### 1.1 Decision Tree 구조

```
[Decision Point]
    │
    ├── Condition A? ─── Yes ──→ [Action A]
    │
    └── No
         │
         ├── Condition B? ─── Yes ──→ [Action B]
         │
         └── No ──→ [Default Action]
```

---

## 2. Phase Gate Decisions

### 2.1 Phase Gate Pass/Fail Decision

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE GATE VALIDATION                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ All mandatory outputs │
                  │      generated?       │
                  └───────────────────────┘
                        │             │
                       Yes            No
                        │             │
                        ▼             ▼
          ┌─────────────────┐       ┌─────────────────┐
          │ Quality metrics │       │   FAIL: Missing │
          │   met? (>=90%)  │       │     Outputs     │
          └─────────────────┘       └─────────────────┘
                │       │                       │
               Yes      No                      │
                │       │                       ▼
                ▼       ▼                   ┌───────────────────┐
          ┌─────────┐  ┌──────────────────┐ │ Re-execute Phase  │
          │  PASS   │  │ Remediation Rate │ └───────────────────┘
          └─────────┘  │     < 10%?       │
                       └──────────────────┘
                            │        │
                           Yes       No
                            │        │
                            ▼        ▼
                  ┌──────────────┐ ┌───────────────────┐
                  │ CONDITIONAL  │ │ FAIL: Quality     │
                  │    PASS      │ │ Issues Excessive  │
                  └──────────────┘ └───────────────────┘
                         │                  │
                         ▼                  ▼
               ┌──────────────────┐ ┌───────────────────┐
               │ Proceed with     │ │ Root Cause        │
               │ remediation      │ │ Analysis Required │
               │ in next phase    │ └───────────────────┘
               └──────────────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Phase Gate Validation]) --> A{All mandatory outputs<br/>generated?}

    A -->|Yes| B{Quality metrics<br/>met? >= 90%}
    A -->|No| FAIL1[❌ FAIL: Missing Outputs]

    B -->|Yes| PASS[✅ PASS]
    B -->|No| C{Remediation Rate<br/>< 10%?}

    C -->|Yes| COND[⚠️ CONDITIONAL PASS]
    C -->|No| FAIL2[❌ FAIL: Quality Issues Excessive]

    FAIL1 --> REEXEC[Re-execute Phase]
    COND --> PROCEED[Proceed with remediation<br/>in next phase]
    FAIL2 --> RCA[Root Cause Analysis Required]

    style PASS fill:#28a745,color:#fff
    style COND fill:#ffc107,color:#000
    style FAIL1 fill:#dc3545,color:#fff
    style FAIL2 fill:#dc3545,color:#fff
```

### 2.2 Phase Gate 조건부 통과 처리

```yaml
conditional_pass_handling:
  decision_tree:
    step_1:
      question: "Remediation 가능한 항목인가?"
      yes: "다음 Phase에서 병행 처리"
      no: "step_2"

    step_2:
      question: "Business-critical 항목인가?"
      yes: "즉시 수정 후 재검증"
      no: "step_3"

    step_3:
      question: "마감 일정 여유가 있는가?"
      yes: "현재 Phase에서 수정"
      no: "Risk로 등록 후 진행"
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Conditional Pass<br/>Handling]) --> A{Remediation<br/>가능한 항목?}

    A -->|Yes| R1[다음 Phase에서<br/>병행 처리]
    A -->|No| B{Business-critical<br/>항목?}

    B -->|Yes| R2[즉시 수정 후<br/>재검증]
    B -->|No| C{마감 일정<br/>여유 있음?}

    C -->|Yes| R3[현재 Phase에서<br/>수정]
    C -->|No| R4[Risk로 등록 후<br/>진행]

    style R1 fill:#17a2b8,color:#fff
    style R2 fill:#dc3545,color:#fff
    style R3 fill:#28a745,color:#fff
    style R4 fill:#ffc107,color:#000
```

---

## 3. Complexity Assessment Decisions

### 3.1 Feature Complexity Classification

```
┌─────────────────────────────────────────────────────────────────────┐
│               FEATURE COMPLEXITY CLASSIFICATION                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │  Stored Procedure     │
                  │     or Trigger?       │
                  └───────────────────────┘
                        │           │
                       Yes          No
                        │           │
                        ▼           │
                  ┌─────────┐       │
                  │  HIGH   │       │
                  │ (Force) │       │
                  └─────────┘       │
                                    ▼
                  ┌───────────────────────┐
                  │   Cross-domain        │
                  │   dependencies?       │
                  └───────────────────────┘
                        │           │
                       Yes          No
                        │           │
                        ▼           │
                  ┌─────────┐       │
                  │  HIGH   │       │
                  │ (Force) │       │
                  └─────────┘       │
                                    ▼
                  ┌───────────────────────┐
                  │  Calculate Score      │
                  │  (5 dimensions)       │
                  └───────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │         Score >= 70?          │
              └───────────────────────────────┘
                    │                 │
                   Yes                No
                    │                 │
                    ▼                 ▼
              ┌─────────┐    ┌──────────────────┐
              │  HIGH   │    │  Score >= 40?    │
              └─────────┘    └──────────────────┘
                                   │        │
                                  Yes       No
                                   │        │
                                   ▼        ▼
                             ┌─────────┐ ┌─────────┐
                             │ MEDIUM  │ │   LOW   │
                             └─────────┘ └─────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Feature Complexity<br/>Classification]) --> A{Stored Procedure<br/>or Trigger?}

    A -->|Yes| HIGH1[🔴 HIGH<br/>Force]
    A -->|No| B{Cross-domain<br/>dependencies?}

    B -->|Yes| HIGH2[🔴 HIGH<br/>Force]
    B -->|No| C[Calculate Score<br/>5 dimensions]

    C --> D{Score >= 70?}

    D -->|Yes| HIGH3[🔴 HIGH]
    D -->|No| E{Score >= 40?}

    E -->|Yes| MEDIUM[🟡 MEDIUM]
    E -->|No| LOW[🟢 LOW]

    style HIGH1 fill:#dc3545,color:#fff
    style HIGH2 fill:#dc3545,color:#fff
    style HIGH3 fill:#dc3545,color:#fff
    style MEDIUM fill:#ffc107,color:#000
    style LOW fill:#28a745,color:#fff
```

### 3.2 AI Model Selection

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI MODEL SELECTION                               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Complexity Tier?      │
                  └───────────────────────┘
                    │       │       │
                   HIGH   MEDIUM   LOW
                    │       │       │
                    ▼       ▼       ▼
              ┌───────┐ ┌───────┐ ┌───────┐
              │ Opus  │ │Sonnet │ │ Haiku │
              └───────┘ └───────┘ └───────┘
                    │       │       │
                    ▼       ▼       ▼
         ┌─────────────────────────────────────┐
         │        Cost Constraint?             │
         └─────────────────────────────────────┘
                    │               │
                   Yes              No
                    │               │
                    ▼               ▼
         ┌─────────────────┐  ┌─────────────────┐
         │ Downgrade:      │  │ Use selected    │
         │ Opus→Sonnet     │  │ model as-is     │
         │ Sonnet→Haiku    │  └─────────────────┘
         └─────────────────┘
                    │
                    ▼
         ┌─────────────────────────────────────┐
         │     Quality Fallback Enabled?       │
         └─────────────────────────────────────┘
                    │               │
                   Yes              No
                    │               │
                    ▼               ▼
         ┌─────────────────┐  ┌─────────────────┐
         │ Monitor quality │  │ Accept quality  │
         │ Auto-upgrade if │  │ trade-off       │
         │ validation fails│  └─────────────────┘
         └─────────────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([AI Model Selection]) --> A{Complexity Tier?}

    A -->|HIGH| OPUS[🟣 Opus]
    A -->|MEDIUM| SONNET[🔵 Sonnet]
    A -->|LOW| HAIKU[🟢 Haiku]

    OPUS --> B{Cost Constraint?}
    SONNET --> B
    HAIKU --> B

    B -->|Yes| DOWN[Downgrade:<br/>Opus→Sonnet<br/>Sonnet→Haiku]
    B -->|No| USE[Use selected<br/>model as-is]

    DOWN --> C{Quality Fallback<br/>Enabled?}

    C -->|Yes| MONITOR[Monitor quality<br/>Auto-upgrade if<br/>validation fails]
    C -->|No| ACCEPT[Accept quality<br/>trade-off]

    style OPUS fill:#6f42c1,color:#fff
    style SONNET fill:#007bff,color:#fff
    style HAIKU fill:#28a745,color:#fff
```

---

## 4. Validation Decisions

### 4.1 Spec Validation Decision

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SPEC VALIDATION DECISION                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │  Validation Score?    │
                  └───────────────────────┘
                    │       │       │
                 >=95     85-94   <85
                    │       │       │
                    ▼       ▼       ▼
              ┌───────┐ ┌───────────┐ ┌──────────┐
              │ PASS  │ │ WARNING   │ │  FAIL    │
              └───────┘ └───────────┘ └──────────┘
                    │       │               │
                    ▼       ▼               ▼
         ┌──────────┐  ┌────────────┐  ┌────────────────┐
         │ Proceed  │  │ Review     │  │ Root Cause     │
         │ to next  │  │ low-score  │  │ Analysis       │
         │ phase    │  │ items      │  └────────────────┘
         └──────────┘  └────────────┘         │
                             │                ▼
                             ▼        ┌────────────────────┐
                    ┌────────────────┐│ Re-analysis from   │
                    │ Manual review  ││ Phase 2 required?  │
                    │ sufficient?    │└────────────────────┘
                    └────────────────┘                │       │
                          │      │                   Yes      No
                         Yes     No                   │       │
                          │      │                    ▼       ▼
                          ▼      ▼              ┌─────────┐ ┌─────────────┐
                    ┌──────────┐ ┌────────────┐ │ Re-run  │ │ Targeted    │
                    │ Document │ │ Escalate   │ │ Phase 2 │ │ Remediation │
                    │ & proceed│ │ to lead    │ └─────────┘ └─────────────┘
                    └──────────┘ └────────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Spec Validation]) --> A{Validation Score?}

    A -->|">= 95"| PASS[✅ PASS]
    A -->|"85-94"| WARN[⚠️ WARNING]
    A -->|"< 85"| FAIL[❌ FAIL]

    PASS --> PROCEED[Proceed to<br/>next phase]

    WARN --> REVIEW[Review low-score<br/>items]
    REVIEW --> B{Manual review<br/>sufficient?}
    B -->|Yes| DOC[Document<br/>& proceed]
    B -->|No| ESC[Escalate<br/>to lead]

    FAIL --> RCA[Root Cause<br/>Analysis]
    RCA --> C{Re-analysis from<br/>Phase 2 required?}
    C -->|Yes| RERUN[Re-run<br/>Phase 2]
    C -->|No| REMED[Targeted<br/>Remediation]

    style PASS fill:#28a745,color:#fff
    style WARN fill:#ffc107,color:#000
    style FAIL fill:#dc3545,color:#fff
```

### 4.2 Functional Validation Decision

```
┌─────────────────────────────────────────────────────────────────────┐
│               FUNCTIONAL VALIDATION DECISION                        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │  Total Score >= 70?   │
                  │  AND Critical = 0?    │
                  └───────────────────────┘
                        │           │
                       Yes          No
                        │           │
                        ▼           ▼
                  ┌─────────┐ ┌───────────────────┐
                  │  PASS   │ │ Critical Issues?  │
                  └─────────┘ └───────────────────┘
                        │           │       │
                        │          Yes      No
                        │           │       │
                        ▼           ▼       ▼
         ┌──────────────┐  ┌─────────────┐ ┌─────────────────┐
         │ Proceed to   │  │ Immediate   │ │ Score >= 50?    │
         │ Phase 3      │  │ Fix Required│ └─────────────────┘
         └──────────────┘  └─────────────┘       │       │
                                  │             Yes      No
                                  ▼              │       │
                           ┌────────────┐        ▼       ▼
                           │ Identify   │  ┌─────────┐ ┌────────────┐
                           │ critical   │  │ Minor   │ │ Major      │
                           │ gaps       │  │ Remed.  │ │ Rework     │
                           └────────────┘  └─────────┘ └────────────┘
                                  │              │           │
                                  ▼              ▼           ▼
                           ┌────────────┐  ┌─────────┐ ┌────────────┐
                           │ Generate   │  │ Apply   │ │ Return to  │
                           │ remediation│  │ quick   │ │ Stage 4    │
                           │ spec       │  │ fixes   │ │ Phase 3    │
                           └────────────┘  └─────────┘ └────────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Functional Validation]) --> A{Score >= 70<br/>AND Critical = 0?}

    A -->|Yes| PASS[✅ PASS]
    A -->|No| B{Critical Issues<br/>exist?}

    PASS --> NEXT[Proceed to<br/>Phase 3]

    B -->|Yes| CRIT[Immediate Fix<br/>Required]
    B -->|No| C{Score >= 50?}

    CRIT --> GAPS[Identify critical<br/>gaps]
    GAPS --> SPEC[Generate<br/>remediation spec]

    C -->|Yes| MINOR[Minor<br/>Remediation]
    C -->|No| MAJOR[Major<br/>Rework]

    MINOR --> QUICK[Apply quick<br/>fixes]
    MAJOR --> RETURN[Return to<br/>Stage 4 Phase 3]

    style PASS fill:#28a745,color:#fff
    style CRIT fill:#dc3545,color:#fff
    style MINOR fill:#ffc107,color:#000
    style MAJOR fill:#dc3545,color:#fff
```

---

## 5. Error Handling Decisions

### 5.1 Task Failure Decision

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TASK FAILURE HANDLING                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │   Failure Type?       │
                  └───────────────────────┘
            │           │           │           │
        Timeout    API Error   Validation   Unknown
            │           │         Error         │
            ▼           ▼           │           ▼
    ┌───────────┐ ┌───────────┐     │    ┌───────────┐
    │ Retry     │ │ Check API │     │    │ Log &     │
    │ count < 3?│ │ status    │     │    │ Escalate  │
    └───────────┘ └───────────┘     │    └───────────┘
       │     │          │           │
      Yes    No         ▼           ▼
       │     │    ┌───────────┐ ┌───────────────┐
       ▼     ▼    │ Rate      │ │ Data issue?   │
  ┌──────┐ ┌────────┐│ limited?  │ └───────────────┘
  │Retry │ │Escalate││           │      │       │
  │ with │ │        │└───────────┘     Yes      No
  │backoff│└────────┘    │    │         │       │
  └──────┘        │     Yes   No        ▼       ▼
                  ▼      │    │   ┌─────────┐ ┌────────┐
           ┌──────────┐  ▼    ▼   │ Fix     │ │ Logic  │
           │ Wait &   │┌────────┐ │ input   │ │ review │
           │ retry    ││Escalate│ │ data    │ │required│
           └──────────┘└────────┘ └─────────┘ └────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Task Failure]) --> A{Failure Type?}

    A -->|Timeout| B{Retry count<br/>< 3?}
    A -->|API Error| C[Check API<br/>status]
    A -->|Validation Error| D{Data issue?}
    A -->|Unknown| ESC1[Log &<br/>Escalate]

    B -->|Yes| RETRY[Retry with<br/>backoff]
    B -->|No| ESC2[Escalate]

    C --> E{Rate limited?}
    E -->|Yes| WAIT[Wait &<br/>retry]
    E -->|No| ESC3[Escalate]

    D -->|Yes| FIX[Fix input<br/>data]
    D -->|No| LOGIC[Logic review<br/>required]

    style RETRY fill:#17a2b8,color:#fff
    style WAIT fill:#ffc107,color:#000
    style FIX fill:#28a745,color:#fff
    style ESC1 fill:#dc3545,color:#fff
    style ESC2 fill:#dc3545,color:#fff
    style ESC3 fill:#dc3545,color:#fff
```

### 5.2 Session Recovery Decision

```
┌─────────────────────────────────────────────────────────────────────┐
│                   SESSION RECOVERY DECISION                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Session terminated    │
                  │ unexpectedly?         │
                  └───────────────────────┘
                        │           │
                       Yes          No
                        │           │
                        ▼           ▼
          ┌─────────────────┐   ┌─────────────────┐
          │ Last checkpoint │   │ Normal          │
          │ available?      │   │ completion      │
          └─────────────────┘   └─────────────────┘
                │       │
               Yes      No
                │       │
                ▼       ▼
    ┌───────────────┐ ┌───────────────────┐
    │ Checkpoint    │ │ Progress lost?    │
    │ < 1 hour old? │ └───────────────────┘
    └───────────────┘       │         │
          │      │         Yes        No
         Yes     No         │         │
          │      │          ▼         ▼
          ▼      ▼    ┌───────────┐ ┌───────────────┐
    ┌─────────┐ ┌──────────┐│ Re-start │ │ Clean start   │
    │ Resume  │ │ Evaluate ││ task from│ │ (no recovery) │
    │ from    │ │ re-start ││ beginning│ └───────────────┘
    │checkpoint│ │ cost     │└───────────┘
    └─────────┘ └──────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Session Recovery]) --> A{Session terminated<br/>unexpectedly?}

    A -->|No| NORMAL[Normal<br/>completion ✓]
    A -->|Yes| B{Last checkpoint<br/>available?}

    B -->|Yes| C{Checkpoint<br/>< 1 hour old?}
    B -->|No| D{Progress lost?}

    C -->|Yes| RESUME[Resume from<br/>checkpoint]
    C -->|No| EVAL[Evaluate<br/>re-start cost]

    D -->|Yes| RESTART[Re-start task<br/>from beginning]
    D -->|No| CLEAN[Clean start<br/>no recovery needed]

    style RESUME fill:#28a745,color:#fff
    style NORMAL fill:#28a745,color:#fff
    style RESTART fill:#ffc107,color:#000
    style CLEAN fill:#17a2b8,color:#fff
```

---

## 6. Migration Strategy Decisions

### 6.1 Migration Approach Selection

```
┌─────────────────────────────────────────────────────────────────────┐
│              MIGRATION APPROACH SELECTION                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Business Logic        │
                  │ Complexity?           │
                  └───────────────────────┘
                    │       │       │
                  Simple  Medium  Complex
                    │       │       │
                    ▼       │       ▼
          ┌─────────────┐   │  ┌─────────────────┐
          │ Code        │   │  │ Spec-First      │
          │ Translation │   │  │ Approach        │
          │ possible?   │   │  │ (Mandatory)     │
          └─────────────┘   │  └─────────────────┘
              │      │      │
             Yes     No     │
              │      │      │
              ▼      ▼      ▼
       ┌──────────┐ ┌────────────────┐
       │REHOSTING │ │ Test Coverage  │
       │          │ │ Available?     │
       └──────────┘ └────────────────┘
                          │       │
                         Yes      No
                          │       │
                          ▼       ▼
                   ┌──────────┐ ┌───────────────┐
                   │REFACTORING│ │RE-PLATFORMING│
                   └──────────┘ └───────────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Migration Approach<br/>Selection]) --> A{Business Logic<br/>Complexity?}

    A -->|Simple| B{Code Translation<br/>possible?}
    A -->|Medium| C{Test Coverage<br/>Available?}
    A -->|Complex| SPEC[Spec-First<br/>Approach<br/>Mandatory]

    B -->|Yes| REHOST[🔵 REHOSTING]
    B -->|No| C

    C -->|Yes| REFACTOR[🟢 REFACTORING]
    C -->|No| REPLATFORM[🟡 RE-PLATFORMING]

    style REHOST fill:#007bff,color:#fff
    style REFACTOR fill:#28a745,color:#fff
    style REPLATFORM fill:#ffc107,color:#000
    style SPEC fill:#6f42c1,color:#fff
```

### 6.2 Rollback Decision

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ROLLBACK DECISION                                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Stage 5 Quality Gate  │
                  │ Status?               │
                  └───────────────────────┘
                    │       │       │
               APPROVED CONDITIONAL REJECTED
                    │       │       │
                    ▼       ▼       ▼
           ┌──────────┐ ┌─────────────┐ ┌────────────────┐
           │ Proceed  │ │ Critical    │ │ Severity of    │
           │ to deploy│ │ issues      │ │ rejection?     │
           └──────────┘ │ count?      │ └────────────────┘
                        └─────────────┘    │       │
                           │    │       Blocker  Critical
                          <5   >=5        │       │
                           │    │         ▼       ▼
                           ▼    ▼    ┌─────────┐ ┌──────────┐
                     ┌─────────┐ ┌─────────┐│ Full    │ │ Partial  │
                     │ Accept  │ │ Review  ││ Rollback│ │ Rollback │
                     │ with    │ │ needed  ││ to      │ │ affected │
                     │ timeline│ │         ││ Stage 4 │ │ features │
                     └─────────┘ └─────────┘└─────────┘ └──────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Rollback Decision]) --> A{Stage 5 Quality Gate<br/>Status?}

    A -->|APPROVED| DEPLOY[✅ Proceed to<br/>deploy]
    A -->|CONDITIONAL| B{Critical issues<br/>count?}
    A -->|REJECTED| C{Severity of<br/>rejection?}

    B -->|"< 5"| ACCEPT[Accept with<br/>timeline]
    B -->|">= 5"| REVIEW[Review<br/>needed]

    C -->|Blocker| FULL[🔴 Full Rollback<br/>to Stage 4]
    C -->|Critical Only| PARTIAL[🟡 Partial Rollback<br/>affected features]

    style DEPLOY fill:#28a745,color:#fff
    style ACCEPT fill:#17a2b8,color:#fff
    style FULL fill:#dc3545,color:#fff
    style PARTIAL fill:#ffc107,color:#000
```

---

## 7. Resource Allocation Decisions

### 7.1 Session Scaling Decision

```
┌─────────────────────────────────────────────────────────────────────┐
│                   SESSION SCALING DECISION                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Pending Task Count?   │
                  └───────────────────────┘
                    │       │       │
                   >100   20-100   <20
                    │       │       │
                    ▼       ▼       ▼
          ┌─────────────┐ ┌───────┐ ┌───────────────┐
          │ Current     │ │Optimal│ │ Scale down    │
          │ utilization │ │ range │ │ consideration │
          │ check       │ └───────┘ └───────────────┘
          └─────────────┘       │           │
              │      │          │           ▼
            <70%   >=70%        │    ┌─────────────────┐
              │      │          │    │ Idle sessions?  │
              ▼      ▼          │    └─────────────────┘
      ┌───────────┐ ┌────────────┐        │       │
      │ Diagnose  │ │ Scale up   │       Yes      No
      │ bottleneck│ │ sessions   │        │       │
      └───────────┘ └────────────┘        ▼       ▼
                          │        ┌─────────┐ ┌─────────┐
                          ▼        │Terminate│ │ Maintain│
                   ┌─────────────┐ │ idle    │ │ current │
                   │ Max sessions│ │ sessions│ └─────────┘
                   │ reached?    │ └─────────┘
                   └─────────────┘
                        │     │
                       Yes    No
                        │     │
                        ▼     ▼
                ┌──────────┐ ┌────────────┐
                │ Queue    │ │ Add new    │
                │ tasks    │ │ session    │
                └──────────┘ └────────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Session Scaling]) --> A{Pending Task<br/>Count?}

    A -->|"> 100"| B{Current<br/>utilization?}
    A -->|"20-100"| OPT[✅ Optimal<br/>range]
    A -->|"< 20"| C{Idle<br/>sessions?}

    B -->|"< 70%"| DIAG[Diagnose<br/>bottleneck]
    B -->|">= 70%"| SCALE[Scale up<br/>sessions]

    SCALE --> D{Max sessions<br/>reached?}
    D -->|Yes| QUEUE[Queue<br/>tasks]
    D -->|No| ADD[Add new<br/>session]

    C -->|Yes| TERM[Terminate<br/>idle sessions]
    C -->|No| MAINTAIN[Maintain<br/>current]

    style OPT fill:#28a745,color:#fff
    style SCALE fill:#17a2b8,color:#fff
    style TERM fill:#ffc107,color:#000
    style ADD fill:#28a745,color:#fff
```

---

## 8. Priority Decisions

### 8.1 Task Priority Assignment

```
┌─────────────────────────────────────────────────────────────────────┐
│                   TASK PRIORITY ASSIGNMENT                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Domain Type?          │
                  └───────────────────────┘
                    │       │       │       │
               Foundation  Hub    Core  Supporting
                    │       │       │       │
                    ▼       ▼       ▼       ▼
               ┌─────┐  ┌─────┐ ┌─────┐ ┌─────┐
               │ P0  │  │ P1  │ │ P2  │ │ P3  │
               └─────┘  └─────┘ └─────┘ └─────┘
                    │       │       │       │
                    ▼       ▼       ▼       ▼
          ┌─────────────────────────────────────────┐
          │       Cross-domain dependency?          │
          └─────────────────────────────────────────┘
                    │               │
                   Yes              No
                    │               │
                    ▼               ▼
          ┌─────────────────┐ ┌─────────────────┐
          │ Promote priority│ │ Keep assigned   │
          │ (P2→P1, P3→P2) │ │ priority        │
          └─────────────────┘ └─────────────────┘
                    │               │
                    ▼               ▼
          ┌─────────────────────────────────────────┐
          │           Dependency resolved?          │
          └─────────────────────────────────────────┘
                    │               │
                   Yes              No
                    │               │
                    ▼               ▼
          ┌─────────────────┐ ┌─────────────────┐
          │ Execute task    │ │ Wait for        │
          │                 │ │ dependencies    │
          └─────────────────┘ └─────────────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Task Priority<br/>Assignment]) --> A{Domain Type?}

    A -->|Foundation| P0[🔴 P0<br/>Highest]
    A -->|Hub| P1[🟠 P1<br/>High]
    A -->|Core| P2[🟡 P2<br/>Medium]
    A -->|Supporting| P3[🟢 P3<br/>Low]

    P0 --> B{Cross-domain<br/>dependency?}
    P1 --> B
    P2 --> B
    P3 --> B

    B -->|Yes| PROMOTE[Promote priority<br/>P2→P1, P3→P2]
    B -->|No| KEEP[Keep assigned<br/>priority]

    PROMOTE --> C{Dependency<br/>resolved?}
    KEEP --> C

    C -->|Yes| EXEC[▶️ Execute task]
    C -->|No| WAIT[⏳ Wait for<br/>dependencies]

    style P0 fill:#dc3545,color:#fff
    style P1 fill:#fd7e14,color:#fff
    style P2 fill:#ffc107,color:#000
    style P3 fill:#28a745,color:#fff
    style EXEC fill:#007bff,color:#fff
```

---

## 9. Quality Gate Decisions

### 9.1 Final Quality Gate

```
┌─────────────────────────────────────────────────────────────────────┐
│                   FINAL QUALITY GATE DECISION                       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Blocker Issues = 0?   │
                  └───────────────────────┘
                        │           │
                       Yes          No
                        │           │
                        ▼           ▼
          ┌─────────────────┐   ┌─────────────────┐
          │ Critical < 5?   │   │    REJECTED     │
          └─────────────────┘   │  (Fix blockers) │
                │       │       └─────────────────┘
               Yes      No
                │       │
                ▼       ▼
    ┌───────────────┐ ┌─────────────────────┐
    │ Score >= 85%? │ │ Critical < 15?      │
    └───────────────┘ └─────────────────────┘
          │      │           │        │
         Yes     No         Yes       No
          │      │           │        │
          ▼      ▼           ▼        ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ APPROVED │ │Score>=70%│ │CONDITIONAL│ │ REJECTED │
    └──────────┘ └──────────┘ │ APPROVED │ └──────────┘
                     │    │   └──────────┘
                    Yes   No
                     │    │
                     ▼    ▼
              ┌──────────┐ ┌──────────┐
              │CONDITIONAL│ │ REJECTED │
              │ APPROVED │ └──────────┘
              └──────────┘
```

**Mermaid 버전:**

```mermaid
flowchart TD
    START([Final Quality Gate]) --> A{Blocker Issues<br/>= 0?}

    A -->|No| REJ1[❌ REJECTED<br/>Fix blockers first]
    A -->|Yes| B{Critical < 5?}

    B -->|Yes| C{Score >= 85%?}
    B -->|No| D{Critical < 15?}

    C -->|Yes| APP[✅ APPROVED]
    C -->|No| E{Score >= 70%?}

    D -->|Yes| COND1[⚠️ CONDITIONAL<br/>APPROVED]
    D -->|No| REJ2[❌ REJECTED]

    E -->|Yes| COND2[⚠️ CONDITIONAL<br/>APPROVED]
    E -->|No| REJ3[❌ REJECTED]

    style APP fill:#28a745,color:#fff
    style COND1 fill:#ffc107,color:#000
    style COND2 fill:#ffc107,color:#000
    style REJ1 fill:#dc3545,color:#fff
    style REJ2 fill:#dc3545,color:#fff
    style REJ3 fill:#dc3545,color:#fff
```

---

## 10. Decision Documentation

### 10.1 Decision Record Template

```yaml
decision_record:
  id: "DEC-{YYYY-MM-DD}-{NNN}"
  decision_tree: "{tree_name}"
  decision_point: "{node_id}"

  context:
    stage: "{stage}"
    phase: "{phase}"
    task: "{task_id}"

  inputs:
    - key: "{input_name}"
      value: "{input_value}"

  path_taken:
    - node: "{node_1}"
      condition: "{condition}"
      result: "{yes|no}"
    - node: "{node_2}"
      condition: "{condition}"
      result: "{yes|no}"

  outcome:
    action: "{selected_action}"
    rationale: "{why this path}"

  timestamp: "YYYY-MM-DD HH:MM:SS"
  recorded_by: "{system|human}"
```

---

## 11. Mermaid Diagram Rendering

### 11.1 Mermaid 다이어그램 보기

위의 Mermaid 다이어그램을 렌더링하려면:

1. **GitHub/GitLab**: Markdown 파일에서 자동 렌더링
2. **VS Code**: Mermaid Preview 확장 설치
3. **Online Editor**: [mermaid.live](https://mermaid.live) 에서 코드 붙여넣기
4. **Obsidian**: 기본 지원

### 11.2 스타일 가이드

```yaml
mermaid_style_guide:
  colors:
    success: "#28a745"  # Green
    warning: "#ffc107"  # Yellow
    error: "#dc3545"    # Red
    info: "#17a2b8"     # Cyan
    primary: "#007bff"  # Blue

  shapes:
    start_end: "([text])"      # Stadium
    decision: "{text}"         # Diamond
    process: "[text]"          # Rectangle

  arrows:
    normal: "-->"
    labeled: "-->|label|"
```

---

**Next**: [03-SKILL-DEFINITION](../03-SKILL-DEFINITION/01-skill-structure.md)
