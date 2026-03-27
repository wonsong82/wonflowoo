# AIND Migration Workbook (Choisor) — Reference Analysis

How the AIND migration workbook approaches AI-driven enterprise legacy migration, and what's relevant to our universal framework.

## What It Is

A comprehensive methodology for AI-powered legacy system migration. Built from real experience migrating hallain_tft — a 10+ year old manufacturing/ERP system (8,377 Java files, 5,864 API endpoints, 912 features, 11 domains). The workbook defines a Stage-Phase-Task-Skill hierarchy with quality gates at every level.

**Choisor** is the orchestrator (Python daemon) that manages multi-session Claude Code execution, task queuing, phase gate validation, and progress tracking.

## Core Philosophy

- **Specification-First**: Never convert code directly. Extract complete specs from legacy, then generate new code from those specs. `Legacy Code → Specification → Generated Code → Validation`
- **Bidirectional Validation**: Forward extraction alone missed 4.7% of endpoints (264 of 5,864). Backward validation (comparing against ground truth) catches what forward extraction misses.
- **AI Leads, Human Validates**: AI handles analysis, pattern recognition, code generation, batch processing. Humans handle Phase Gate approval, architecture decisions, business logic verification, final quality sign-off.
- **Quality Over Speed**: Priority order: 100% business logic preservation > traceability > consistency > speed. Rework costs 2x more than getting it right the first time.
- **Phase Gates Are Non-Negotiable**: Loosening Stage 1 gates (95% coverage) caused 35% total rework and 2+ week delays. Strict gates (100% coverage) kept rework under 5%.

## Five-Stage Lifecycle

```
Stage 1: DISCOVERY — "What exists?"
  Phase 1: Feature Inventory (scan all controllers, extract endpoints)
  Phase 2: Deep Analysis (trace all layers, document business logic)
  Phase 3: Spec Generation (structured YAML specs from analysis)

Stage 2: VALIDATION — "Is the spec complete?"
  Phase 1: Source Inventory (ground truth from actual codebase)
  Phase 2: Structural Comparison (spec vs ground truth)
  Phase 3: Gap Analysis (find what's missing)
  Phase 4: Spec Completion (fill the gaps)

Stage 3: PREPARATION — "How to build it?"
  Phase 1-3: Dependency Analysis, System Integration, Tech Debt
  Phase 4-6: Architecture Design, Code Gen Spec, Implementation Planning

Stage 4: GENERATION — "Build it!"
  Phase 1: System Setup
  Phase 2: Mini-Pilot (6 features: 2 high, 2 medium, 2 low complexity)
  Phase 3: Domain Execution (batch generation)
  Phase 4: Integration

Stage 5: ASSURANCE — "Does it work?"
  Phase 1: Structural Standardization
  Phase 2: Functional Validation (4-layer scoring)
  Phase 3: Quality Standardization
  Phase 4: Integration Validation
  Phase 5: Quality Gate (final pass/fail)
```

Each stage is gated. Each phase is gated. Tasks within a phase run parallel. Phases within a stage run sequential.

## Stage-Phase-Task-Skill Hierarchy

```
PROJECT
  └── STAGE (purpose-level: Discovery, Validation, Generation...)
      └── PHASE (work unit: Inventory, Analysis, Spec Gen...)
          └── TASK (execution unit: FEAT-PA-001, FEAT-PA-002... — parallelizable)
              └── SKILL (AI instruction: SKILL.md with output schema)
```

**Key property**: Tasks (features) within a phase can run in parallel across multiple Claude Code sessions. Phases must run sequentially within a stage. Stages must pass gates to proceed.

## Choisor Orchestrator Architecture

```
Control Plane:
  Daemon — background process managing everything
  Task Queue — priority-based (P0 foundation → P1 hub → P2 core → P3 supporting)
  Phase Gate Controller — validates outputs before allowing progression

Session Pool:
  Multiple Claude Code sessions running in parallel
  Session allocation: round-robin, least-loaded, affinity (same domain = same session), priority

Data Plane:
  Task Definitions — YAML, feature-level granularity
  Output Storage — stage/phase/domain/feature directory structure
  State Store — JSON, checkpoint/resume capable
```

Configuration lives in `.choisor/config.yaml`. Task states: PENDING → ASSIGNED → IN_PROGRESS → VALIDATING → COMPLETED/FAILED/RETRYING.

## Skill System

Skills are structured AI instruction files with:
- Naming: `s{Stage}-{Phase}-{category}-{name}` (e.g., `s1-02-discovery-deep-analysis`)
- Each skill has a `SKILL.md` (instructions) + `output.schema.yaml` (expected output structure)
- Schema validation at Phase Gate — outputs must conform
- Common types in `.claude/skills/common/types.schema.yaml`

Skills live in `.claude/skills/` and are invoked as slash commands in Claude Code.

## Quality Assurance System

### 4-Layer Validation
| Layer | What | Example |
|---|---|---|
| 1. Syntactic | YAML syntax, file structure, schema compliance | Is the output valid YAML? |
| 2. Structural | Naming, URL patterns, package structure, dependencies | Does it follow conventions? |
| 3. Functional | SQL equivalence, business logic, data flow | Does it do the same thing? |
| 4. Behavioral | Parallel testing: same input → same output | Does it behave identically? |

### Functional Validation Scoring
| Dimension | Weight | What it checks |
|---|---|---|
| SQL Equivalence | 40% | Columns, conditions, joins, ordering, dynamic SQL |
| API Equivalence | 25% | Same external calling interface |
| Business Logic | 20% | Same business rules applied |
| Data Model | 15% | Same data structure mapping |

**Pass threshold**: 70+ points with 0 critical issues.

### Phase Gate Enforcement
Every phase completion triggers: file count check → structure validation → schema validation → size check → auto-commit → state update. Any failure = REJECT, triggers remediation.

## Parallel Execution Patterns

Three levels of parallelism:
1. **Session-level**: Multiple Claude Code sessions, each handling different domains
2. **Task-level**: SubAgents within a single session
3. **Domain-level**: Independent domains processed simultaneously

Synchronization patterns:
- **Barrier**: All tasks in Phase N must complete before Phase N+1 starts
- **Fork-Join**: Main task splits into parallel subtasks, results combined
- **Pipeline**: Features flow through phases in assembly-line fashion

Dependency graph: P0 (common) → P1 (hub domain) → P2 (core domains, parallelizable) → P3 (supporting domains, parallelizable)

## Key Lessons Learned (Battle-Tested)

### Critical
1. **Stage 1 quality determines everything**: 100% coverage → 5% rework. 95% coverage → 35% rework, 50% schedule delay.
2. **Phase Gates are non-negotiable**: Loosening them saves 1-2 days short-term, costs 2+ weeks long-term.
3. **Mini-Pilot before batch**: 2 hours of pilot testing prevents 3 days of wasted batch generation.
4. **Orchestration is mandatory**: Manual tracking fails beyond 10 features. 912 features requires automation.

### High
5. **Rework costs 2x**: First-pass success rate of 85%+ should be the target. Invest in skill quality.
6. **Bidirectional validation**: Forward-only extraction missed 4.7% of endpoints.
7. **LLM context is finite**: Layer-by-layer progressive loading. Persist intermediate results. 300-line file limit.
8. **Checkpoint/resume is essential**: No batch job completes uninterrupted.

### Anti-Patterns
- Big Bang (process everything at once)
- Skip Phase Gate (schedule pressure)
- Copy-paste remediation (no root cause analysis)
- Manual state tracking (spreadsheets)
- All-Opus strategy (expensive model for everything)

## What's Relevant to Our Framework

### Directly applicable:
- **Stage-Phase-Task-Skill hierarchy** — universal work decomposition pattern (purpose → work unit → execution unit → AI instruction)
- **Phase Gate concept** — quality checkpoints that block progression, not just suggestions
- **Specification-First approach** — extract WHAT+WHY before generating HOW (maps directly to our spec system)
- **Bidirectional validation** — verify completeness from both directions
- **Dependency graph with priority layers** — P0→P1→P2→P3 ordering for any project with interdependencies
- **Checkpoint/resume** — essential for any non-trivial workflow
- **Mini-pilot pattern** — test on representative samples before scaling
- **Skill system with output schemas** — structured AI instructions with validatable outputs
- **Quantified lessons** — actual data on what works and what fails at enterprise scale

### Needs adaptation for universality:
- **Migration-specific stages** — our framework needs a more general stage model (Discovery → Architecture → Planning → Delegation is already closer)
- **Java/Spring/MyBatis assumptions** — validation scoring is domain-specific
- **Claude Code coupling** — Choisor assumes Claude Code sessions as execution units
- **Fixed 5-stage model** — we need stages that adapt to project type (greenfield has no "legacy analysis")
- **Single-repo assumption** — the directory structure assumes one monorepo

### Key concepts to extract:
- **Task granularity at feature level** — the right unit of parallelism (not file, not module, but business feature)
- **Schema-validated outputs** — skills produce outputs that can be mechanically verified
- **Priority-based domain ordering** — foundation first, then hub, then core (parallel), then supporting (parallel)
- **AI leads, human validates** — clear role separation at Phase Gates, not at every step
- **Cost of rework data** — 1% coverage miss at Stage 1 = ~7% rework multiplier downstream

---

*Analyzed from: `references/aind-migration-workbook-v2.0/` — overview, stage-phase model, orchestrator setup, parallel execution, quality assurance, lessons learned, case studies.*
