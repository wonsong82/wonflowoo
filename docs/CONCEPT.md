# WonfloWoo (One Flow) — Concept

A universal AI-aided development workflow framework. One flow, any project shape.

A living document capturing the design decisions and rationale behind this framework. Updated as we discover, decide, and refine.

## Table of Contents

- [Part 1: Overview](#part-1-overview)
  - [TL;DR](#tldr)
  - [Core Model: Main Tech Lead / Spawned Tech Leads / Developers](#core-model-main-tech-lead--spawned-tech-leads--developers)
  - [Orchestrator Lifecycle](#orchestrator-lifecycle)
    - [Ceremony Scaling](#ceremony-scaling)
  - [High-Level Flows by Case](#high-level-flows-by-case)
    - [Case 1: Start Fresh (Greenfield)](#case-1-start-fresh-greenfield)
    - [Case 2: Add Features to Existing Project](#case-2-add-features-to-existing-project)
    - [Case 3: Bootstrap from Existing Codebase](#case-3-bootstrap-from-existing-codebase)
    - [Case 4: Bug Fix / Incident Response](#case-4-bug-fix--incident-response)
    - [Case 5: Refactoring / Tech Debt](#case-5-refactoring--tech-debt)
    - [Case 6: Migration](#case-6-migration)

- [Part 2: Lifecycle Phases](#part-2-lifecycle-phases)
  - [Phase 1: Discovery](#phase-1-discovery)
  - [Phase 2: Architecture](#phase-2-architecture)
  - [Phase 3: Planning](#phase-3-planning)
  - [Combined Flow (Cases 1-2: Greenfield / Add Feature)](#combined-flow-cases-1-2-greenfield--add-feature)
  - [Phase 4: Delegation + Developer Planning](#phase-4-delegation--developer-planning)
    - [Task Instruction Files](#task-instruction-files)
    - [Task File Structure](#task-file-structure)
    - [Two-Level Planning](#two-level-planning-orchestrator-vs-developer)
    - [Developer Planning](#developer-planning)
    - [Developer Alignment Loop](#developer-alignment-loop)
    - [Progress Monitoring](#progress-monitoring)
    - [Failure Handling](#failure-handling)
  - [Phase 5: Implementation](#phase-5-implementation)

- [Part 3: Bootstrap](#part-3-bootstrap)
  - [Bootstrap Process (Case 3)](#bootstrap-process-case-3)

- [Part 4: Core Systems](#part-4-core-systems)
  - [The Spec System](#the-spec-system)
    - [Two-Tier Spec Architecture](#two-tier-spec-architecture)
    - [System Spec Structure](#system-spec-structure)
    - [4-Layer Spec Model](#4-layer-spec-model)
    - [L1: Interfaces](#l1-interfaces-generic-io)
    - [L2: Logic](#l2-logic)
    - [L3: Data](#l3-data)
    - [L4: Dependencies](#l4-dependencies)
    - [Frontend Specs](#frontend-specs)
    - [Spec File Organization](#spec-file-organization)
    - [Spec Size Management](#spec-size-management)
    - [Spec Lifecycle](#spec-lifecycle)
    - [Spec Generation](#spec-generation)
    - [Spec Validation](#spec-validation-inspired-by-choisor)
    - [Consistency Enforcement](#consistency-enforcement)
    - [Cross-Module Flows](#cross-module-flows)
  - [Architecture Document Structure](#architecture-document-structure)
    - [Architecture Doc Schemas (Examples)](#architecture-doc-schemas-examples)
    - [Directory Structure](#directory-structure)
    - [File Naming Convention](#file-naming-convention)
  - [Orchestrator Draft — Living Working Memory](#orchestrator-draft--living-working-memory)
  - [Research Capabilities](#research-capabilities)

- [Part 5: Supporting Systems](#part-5-supporting-systems)
  - [Category → Model Routing](#category--model-routing)
  - [Draft File Template](#draft-file-template)
  - [Documentation Layers](#documentation-layers)
  - [Execution Principles](#execution-principles)
  - [Testing Strategy](#testing-strategy)
  - [Wisdom Accumulation](#wisdom-accumulation)
  - [Human Roles](#human-roles)
  - [Tooling Requirements](#tooling-requirements)
  - [Framework Adoption](#framework-adoption)
  - [Multi-Repo Specs](#multi-repo-specs)
  - [Versioning](#versioning)

- [Part 6: Reference](#part-6-reference)
  - [Phase Deliverables Summary](#phase-deliverables-summary)
  - [Design Principles](#design-principles)
  - [Resolved Decisions](#resolved-decisions)
  - [Open Questions](#open-questions)

---

# Part 1: Overview

## TL;DR

A **main tech lead** (persistent AI agent) coordinates the project — talking to the human, capturing decisions into a draft, and spawning **tech lead agents** for non-trivial work. Spawned tech leads have the same contextual understanding (loaded from the same files) but with fresh context — no conversation history baggage. **Developers** implement and report back. The entire mental model is externalized through a **two-tier spec system**: system spec (holistic view, always loaded) + individual feature specs (4-layer detail, loaded on demand). Architecture docs (YAML + Markdown) capture intent; specs capture reality.

**6 cases**: Greenfield, add feature, bootstrap from existing codebase, bug fix, refactoring, migration. Each follows the lifecycle at different entry points and depths.

**5-phase lifecycle**: Discovery (WHAT — capture requirements, Cases 1-2 only) → Architecture (HOW — design approach, consult specialist) → Planning (orchestration — task waves, gap analysis by specialist) → Delegation (self-contained task files as technical user stories + per-wave three-step dispatch: plan → review → implement) → Implementation (developers execute, generate specs from code). Ceremony scales from trivial (skip everything) to enterprise (full ceremony + specialists at every phase).

**Specs are the core**: 4-layer model per spec (Interfaces — any I/O type; Logic — detailed step-by-step flows; Data — any storage or stateless; Dependencies — internal + external). System spec (`_system.yml`) gives the orchestrator the whole picture without blowing the context window. Individual specs loaded on demand. AI-assisted generation, bidirectional validation, schema-enforced consistency.

**Key mechanisms**: Draft as orchestrator's living memory (persists across all phases, never deleted). Independent 5-digit ID sequences per artifact type (requirements, drafts, plans, tasks). Task files include architecture context inline so developers can work independently. Developer plans persisted alongside task files. All diagrams in Mermaid. Bootstrap uses fan-out/fan-in for large codebases.

---

## Core Model: Main Tech Lead / Spawned Tech Leads / Developers

The framework mirrors how real engineering organizations work, with a key optimization for AI context management.

### Three Agent Roles

| Role | Lifecycle | Context | Talks to |
|---|---|---|---|
| **Main Tech Lead** | Persistent across the project | All arch docs + `_system.yml` + draft + specs (lazy loaded) + human conversation | Human directly |
| **Spawned Tech Lead** | Created per task, destroyed after | All arch docs + `_system.yml` + draft + specs (lazy loaded) — same as main, minus conversation | Main Tech Lead |
| **Developer** | Created per task, destroyed after | Task file + referenced arch docs + specs + actual code | Spawned Tech Lead (for alignment), Main Tech Lead (indirectly) |

### Dispatch Roles (Runtime Taxonomy)

The three roles above are the **conceptual collaboration model**. At runtime, orchestration dispatches concrete roles with different context depths:

| Context Level | Dispatch roles | Typical purpose |
|---|---|---|
| **Tech-lead (macro view)** | `architect`, `architecture-consultant`, `gap-analyst`, `plan-reviewer`, `spec-updater` | Architecture design/review, gap detection, plan alignment, spec maintenance |
| **Developer (task view)** | `sr-dev`, `jr-dev`, `quick-dev`, `frontend-dev` | Task-level planning and implementation |
| **Utility (query-scoped)** | `librarian`, `explorer` | External research and internal codebase search |

On OmO, the reasoning-heavy tech-lead roles (`architect`, `gap-analyst`, `spec-updater`) dispatch via `task(subagent_type="sisyphus")` (Opus-routed reasoning worker). Platform-specific dispatch syntax/mapping details remain in the slim core manuals (`AGENTS.md`, `CLAUDE.md`).

### Main Tech Lead (Persistent)

The main tech lead is the **human-facing orchestrator**. It maintains the conversation thread with the human and coordinates all work across the project lifecycle.

- **Talks to the human** — the only agent the human interacts with directly
- **Captures everything meaningful into the draft** — so spawned tech leads have the same understanding without needing the conversation history
- **Spawns tech leads for non-trivial work** — reviews, gap analysis, architecture design, planning, delegation. Keeps its own context clean.
- **Coordinates the lifecycle** — decides what phase we're in, what work is needed next, receives results from spawned tech leads

**Loads:**
- All architecture docs (tech-stack, conventions, dependencies, system-design)
- System spec (`_system.yml`) — always loaded
- Individual specs — lazy loaded as needed
- Draft — living memory for the current work item
- Human conversation — the only context spawned tech leads don't have

### Spawned Tech Lead (Per-Task)

Spawned tech leads have the **same contextual understanding** as the main tech lead. They load the same files. The ONLY difference: they don't carry the accumulated human conversation history — but anything meaningful from that conversation is already in the draft.

**Why spawn instead of doing it yourself?** Context hygiene. A complex project's conversation thread can consume significant context budget. A spawned tech lead starts fresh — 100% of its context budget goes to the actual work, not conversation history from three phases ago.

**Spawned for:**
- Architecture design (propose + consult specialist)
- Gap analysis during planning
- Developer plan review (alignment loop)
- Acceptance criteria validation
- Any non-trivial technical work

**Loads:**
- All architecture docs — same as main
- System spec (`_system.yml`) — same as main
- Individual specs — lazy loaded as needed, same as main
- Draft — same as main. This is the bridge — everything the main tech lead learned from the human is captured here.

**Reports results to main tech lead → gets destroyed.** Main tech lead updates the draft with results.

### Developers

- Receive self-contained task instruction files from the tech lead
- Specialized by execution role (`sr-dev`, `jr-dev`, `quick-dev`, `frontend-dev`) — determines model routing
- **Create their own detailed implementation plans** in a fresh session — loading task file + arch docs + relevant specs + actual code
- **Must align their plan with the tech lead before implementing** (see Phase 4: Delegation + Developer Planning)
- After implementation, **report a change manifest** (files changed + interfaces/data touched); a dedicated `spec-updater` updates specs

### Why This Works

The draft + specs + arch docs **externalize the entire mental model**. Any agent that loads these files becomes an equally capable tech lead. The main tech lead doesn't need to do all the work — it coordinates and captures, spawned tech leads do the heavy lifting with fresh context.

```
Human: "Add RBAC to the system"
  │
  ▼
Main Tech Lead
  ├── Loads _system.yml + arch docs + creates draft
  ├── Captures requirements from human conversation → draft updated
  │
  ├── Spawns Tech Lead → "Run Discovery for RBAC"
  │     ├── Loads: draft + arch docs + _system.yml + relevant specs
  │     ├── Researches, captures requirements details
  │     ├── Writes requirements doc, updates draft
  │     └── Reports back → destroyed
  │
  ├── Main reads updated draft → relays to human for confirmation
  │
  ├── Spawns Tech Lead → "Design architecture for RBAC"
  │     ├── Loads: draft + requirements + arch docs + specs
  │     ├── Proposes architecture, consults specialist
  │     ├── Writes arch doc updates, updates draft
  │     └── Reports back → destroyed
  │
  ├── Main reads updated draft → relays to human for alignment
  │
  └── ... (continues for Planning, Delegation, Implementation)
```

### Platform Constraint: Flat Spawning

On both OmO and Claude Code, **sub-agents cannot spawn other sub-agents**. Only the main tech lead can dispatch agents. This means the 3-tier concept (main → tech lead → developer) is preserved through **files**, not through nested spawning:

1. Main spawns developer → developer writes `.plan.md` → reports back
2. Main spawns tech lead → tech lead reviews `.plan.md` → APPROVE/REJECT
3. Main spawns developer again → implements → reports change manifest
4. Main spawns `spec-updater` → updates affected specs + `_system.yml` → reports back

All spawning goes through main. Tech leads and developers never talk to each other directly — they coordinate via persisted files (task files, .plan.md).

---

## Context Loading Protocol

The slim core manuals (`AGENTS.md`, `CLAUDE.md`) keep only global rules and dispatch mapping. Detailed phase behavior is loaded lazily from workflow docs.

On OmO specifically, `AGENTS.md` now includes **Role Routing** plus sub-agent sections because the same file is auto-loaded by both the main orchestrator and spawned sub-agents. Routing text ensures sub-agents know they are not the orchestrator and should load role guides.

Baseline load order for orchestrators:
1. `.wonflowoo/workspace/config.yml`
2. `.wonflowoo/workspace/architecture/` (core architecture docs)
3. `.wonflowoo/workspace/specs/_system.yml` (always)
4. active `.wonflowoo/workspace/drafts/`
5. active `.wonflowoo/workspace/plans/`
6. relevant individual specs (lazy)

When entering a phase, load: `.wonflowoo/framework/workflow/{phase}.md`

Sub-agents load role-specific guides from `.wonflowoo/framework/agent-guides/`:
- Tech-lead roles: `.wonflowoo/framework/agent-guides/tech-leads.md`
- Developer roles: `.wonflowoo/framework/agent-guides/developers.md`
- Spec-updater: `.wonflowoo/framework/agent-guides/spec-updater.md`

This lazy loading pattern keeps the slim core manuals compact while preserving full detail for each role and phase.

---

## Orchestrator Lifecycle

The main tech lead owns the full translation from business intent to implementation. For each phase, it spawns a tech lead agent to do the actual technical work, keeping its own context clean for human coordination:

```
Business Ask (vague, business-oriented)
    │
    ▼
1. DISCOVERY — Clarify requirements with business stakeholders.
    │           Pin down scope, intent, acceptance criteria.
    │           Output: Requirements document
    ▼
2. ARCHITECTURE — Design technical approach.
    │               Tech stack, system design, data model, conventions.
    │               Align with existing conventions / other tech leads.
    │               Output: Architecture docs (YAML + Markdown)
    ▼
3. PLANNING — Break architecture into concrete tasks.
    │           Sequence work into dependency-ordered waves.
    │           High-level task plan (what, not how).
    │           Output: Orchestrator plan (task groups, ordering, delegation targets)
    ▼
4. DELEGATION — Write self-contained task instruction files and dispatch to developers.
    │             Each task file is a technical user story: context, brief, arch detail, guardrails, acceptance criteria.
    │             Developer loads task file → creates detailed plan → alignment loop → implementation.
    ▼
5. IMPLEMENTATION — Developers execute and report change manifests from actual code.
                     `spec-updater` updates specs after each task so specs remain ground truth, never aspirational.
```

Each phase produces artifacts that feed the next — and those same artifacts become the context subagents receive.

### Ceremony Scaling

Not every task needs the full lifecycle. The framework scales ceremony to match complexity:

| Complexity | Criteria | Flow |
|---|---|---|
| **Trivial** | Single file, obvious fix, bug fix | Skip everything → direct implementation → update spec if behavior changed |
| **Simple** | 1-2 files, clear scope | Lightweight discovery → lightweight architecture (orchestrator decides alone, no specialist) → plan → implement |
| **Medium** | Feature-level, 3-10 files | Full discovery → architecture with specialist → planning with gap analysis → delegation → implement |
| **Large** | System-level, 10+ files | Full ceremony: all phases at full depth, specialist consultation at architecture + planning, high-accuracy review optional |
| **Enterprise** | Cross-system, multi-team | Full ceremony + mandatory specialist consultation at every phase + high-accuracy review + multi-stakeholder alignment |

The orchestrator classifies complexity at the start and adjusts depth accordingly. A typo fix doesn't need a 30-minute interview. A new system does. Same phases, different depth.

Note: Discovery only applies to Cases 1-2 (greenfield, add feature). Bug fixes skip directly to implementation (trivial/simple) or get lightweight planning (complex). Refactoring and migration enter at Architecture. See High-Level Flows by Case for case-specific entry points.

**Phase gate behavior:** Controlled by `auto_proceed` in `.wonflowoo/workspace/config.yml`. When `false` (default), the agent STOPS at every phase gate and waits for human confirmation. When `true`, the agent logs the summary to the draft and proceeds automatically. Use `auto_proceed: true` for experienced users or automated pipelines.

---

## High-Level Flows by Case

Six cases cover the main ways the framework gets used. Each follows the same lifecycle phases but enters at different points and emphasizes different things.

### Case 1: Start Fresh (Greenfield)

No codebase, no specs, no architecture docs. Building from zero.

```
User: "Build me an inventory management system"
  │
  ▼
DISCOVERY
  ├── Research external landscape (librarian) — similar systems, tech options, best practices
  ├── Interview user — scope, features, constraints, personas
  ├── Clearance check
  ▼
ARCHITECTURE
  ├── Propose tech stack, data model, conventions, folder structure
  ├── Write architecture docs (YAML + MD) — these are the first .wonflowoo/workspace/ files created
  ├── Align with user
  ▼
PLANNING
  ├── Gap analysis
  ├── Break into dependency-ordered waves
  ├── Wave 1 always includes: scaffolding, shared types, base infra, convention-setting reference implementation
  ▼
DELEGATION
  ├── Write task instruction files to .wonflowoo/workspace/tasks/
  ├── Developers load task files → create plans → alignment loop
  ▼
IMPLEMENTATION
  ├── Developers build, generate specs from actual code
  ├── Specs become the ground truth for all subsequent work
  └── Each completed wave unblocks the next
```

**What's unique**: No internal codebase to research. Discovery relies entirely on external research (librarian). Architecture docs are created from scratch — the orchestrator is building its mental model and externalizing it for the first time.

---

### Case 2: Add Features to Existing Project

Specs and architecture docs already exist. The system is understood.

```
User: "Add role-based access control to the API"
  │
  ▼
DISCOVERY
  ├── Load system spec (_system.yml) + architecture docs → identify which specs are relevant to the request
  ├── Load relevant specs only (not all — two-tier system avoids context overload)
  ├── Research external (librarian) — only if unfamiliar tech involved (e.g., RBAC best practices)
  ├── Interview user with informed questions — "I see from specs that you have JWT auth with a users table. Should RBAC extend the existing auth middleware or be a separate module?"
  ├── Clearance check → Requirements doc confirmed
  ▼
ARCHITECTURE
  ├── Design how new feature fits WITHIN existing architecture
  ├── Update architecture docs with planned additions (new tables, new endpoints, new conventions if any)
  ├── Align with user
  ▼
PLANNING
  ├── Gap analysis (check new feature against existing specs for conflicts)
  ├── Break into waves — likely fewer waves than greenfield, feature is scoped
  ├── Plan doc confirmed
  ▼
DELEGATION
  ├── Task instruction files reference existing specs + arch docs
  ├── Developers load task file + existing context
  ▼
IMPLEMENTATION
  ├── Developers build within existing codebase
  ├── UPDATE specs to reflect new reality (new endpoints, new tables, updated module responsibilities)
  └── Specs always reflect what exists now, not what existed before
```

**What's unique**: Orchestrator enters with a full mental model from specs — no codebase search needed. If the orchestrator needs to search actual code, the specs are incomplete. Discovery is about capturing NEW requirements, not about understanding the system. Architecture is additive. Specs get updated, not created from scratch.

---

### Case 3: Bootstrap from Existing Codebase

Codebase exists but has no specs or architecture docs. The framework is being adopted on a running project. This is a separate process — not part of the standard lifecycle. See "Bootstrap Process" section for full detail.

```
User: "Here's our codebase, set up the AI workflow"
  │
  ▼
BOOTSTRAP (one-time setup, multi-step pipeline)
  ├── Quick scan — identify significant source files
  ├── Fan-out — per-file analysis (one investigator per file, all parallel)
  ├── Summarize — extract compact metadata per file
  ├── AI grouping — cluster files into feature groups (naming + imports + shared data)
  ├── Feature spec generation — combine per-file analyses into feature-grouped specs (parallel)
  ├── System spec — build _system.yml incrementally (one feature at a time)
  ├── Validation — check completeness, consistency, flag gaps
  │   └── Architecture docs generated (tech-stack, conventions, dependencies, system-design)
  ├── Human review — "Here's what I found. Does this match?"
  └── Corrections applied → .wonflowoo/ directory is now populated (framework + workspace)
  │
  ▼
(Now operates like Case 2 — existing project with specs + arch docs)
```

**What's unique**: No Discovery phase — the codebase IS the input. Multi-step pipeline: per-file analysis (objective) → AI feature grouping (opinionated, from signals) → feature spec generation → incremental system spec. No step ever loads the entire codebase into one context. Scales from small projects (one agent) to massive codebases (2,000+ files). After bootstrap, all subsequent work follows Case 2.

---

### Case 4: Bug Fix / Incident Response

Something's broken. Starts with a symptom, not a feature request. Skips Discovery and Planning.

```
User: "Users are getting 500 errors on the checkout page"
  │
  ▼
DIAGNOSE
  ├── Load system spec (_system.yml) → understand which specs are relevant
  ├── Load relevant specs (checkout, payment, order-processing)
  ├── Understand the symptom — what's the error, when, what changed recently
  ├── Identify root cause (or narrow candidates)
  ▼
CLASSIFY COMPLEXITY
  ├── Trivial (typo, missing null check) → fix directly, no task file needed
  ├── Simple (single spec area, clear fix) → create task file (00003-bugfix.checkout-null-check.yml), fix, update spec if behavior changed
  ├── Complex (cross-cutting, unclear cause) → create draft, may need architecture consultation, task file + plan
  ▼
FIX
  ├── Fix minimally — address root cause, do NOT refactor while fixing
  ├── Verify fix resolves the symptom
  ├── Update specs ONLY if the fix changed observable behavior (new error handling, changed API response, etc.)
  ├── Update system spec if dependency or interface changes occurred
  └── If fix reveals deeper architectural issues → note for separate refactoring task (Case 5)
```

**What's unique**: Reactive, not planned. No Discovery, no Planning. Entry point is a symptom — orchestrator uses specs (not codebase search) to understand the affected area. Minimal change principle — fix the bug, don't improve the neighborhood. Complex bug fixes use `bugfix` as the task-file origin (`{task-id}-bugfix.{task-name}.yml`).

---

### Case 5: Refactoring / Tech Debt

No new business features. Restructuring, cleaning up, or improving existing code. Skips Discovery (no new requirements), enters at Assessment → Architecture.

```
User: "The auth module is a mess, split it into separate concerns"
  │
  ▼
Draft created (.wonflowoo/workspace/drafts/00003-auth-refactor.md)
  │
  ▼
ASSESSMENT
  ├── Load system spec → understand blast radius across the whole system
  ├── Load affected specs (auth, and everything that depends on auth)
  ├── Load arch docs (conventions, system design)
  ├── Identify the specific problems (too many responsibilities, tangled dependencies, unclear boundaries)
  ▼
ARCHITECTURE (with specialist consultation)
  ├── Propose new structure — what it should look like after refactoring
  ├── Define migration path — how to get from current to target without breaking things
  ├── Identify invariants — what must NOT change (public API? behavior? data model?)
  ├── Align with user
  └── → Architecture docs updated
  ▼
PLANNING (with gap analysis specialist)
  ├── Break into safe, incremental steps — each step leaves the system working
  ├── Each step has verification: tests still pass, behavior unchanged
  └── → Plan doc confirmed (.wonflowoo/workspace/plans/00003-auth-refactor.md)
  ▼
DELEGATION → DEVELOPER PLANNING → IMPLEMENTATION
  ├── Task files: 00007-auth-refactor.extract-token-service.yml
  ├── Developers refactor incrementally
  ├── Specs REGENERATED — boundaries may have moved entirely (old specs replaced, new specs created)
  ├── System spec updated to reflect new structure
  └── Verify: same behavior, cleaner structure
```

**What's unique**: No Discovery — no new requirements. The orchestrator uses specs (not codebase search) to understand the current state and blast radius. Architecture focuses on target vs current state. Every step leaves the system working. Specs are regenerated, not just updated — if you split one spec into three, the old spec is replaced by three new ones. System spec reflects the new structure.

---

### Case 6: Migration

Moving from technology A to technology B. Different from refactoring — the goal is functional equivalence in a new stack. Skips Discovery, enters at Extraction → Architecture.

```
User: "Migrate the REST API from Express to Fastify" / "Migrate the database from MySQL to PostgreSQL"
  │
  ▼
Draft created (.wonflowoo/workspace/drafts/00004-express-to-fastify.md)
  │
  ▼
EXTRACTION
  ├── Load system spec → full picture of what exists
  ├── Load system spec → identify affected specs from dependency graph
  ├── Load relevant individual specs for affected areas
  ├── Build complete inventory of what must be migrated (from specs — no codebase search needed)
  │   ├── Every endpoint, handler, middleware (API migration)
  │   ├── Every table, column, constraint (DB migration)
  │   ├── Every integration point, external dependency
  │   └── Every behavioral contract (what callers expect)
  ├── Librarian: research target technology — how it handles the same concerns differently
  ├── Identify translation patterns — Express middleware → Fastify hooks, MySQL syntax → PostgreSQL syntax
  ▼
ARCHITECTURE (with specialist consultation)
  ├── Design target state in new technology
  ├── Map source patterns to target patterns (translation table)
  ├── Identify gaps — things with no direct target equivalent
  ├── Decide on gap resolution — alternative pattern, custom implementation, or feature dropped
  ├── Align with user
  └── → Architecture docs updated (new tech stack, new conventions)
  ▼
PLANNING (with gap analysis specialist)
  ├── Wave 0: Mini-pilot — pick 2-3 representative items (simple, medium, complex)
  ├── Run full migration cycle on pilot → validate approach, catch systemic issues
  ├── Fix systemic issues before batch execution
  ├── Break remaining work into parallel waves
  └── → Plan doc confirmed (.wonflowoo/workspace/plans/00004-express-to-fastify.md)
  ▼
DELEGATION → DEVELOPER PLANNING → IMPLEMENTATION
  ├── Task files: 00008-express-to-fastify.migrate-auth-hooks.yml
  ├── Developers migrate in batches, following validated patterns from pilot
  ├── Bidirectional validation — verify target matches source behavior
  ├── Specs REGENERATED for new technology — same business logic, new technical representation
  ├── System spec updated to reflect new architecture
  └── Verify: functional equivalence confirmed
```

**What's unique**: Functional equivalence is the goal. Extraction uses specs (not codebase search) to build the migration inventory — this is where spec quality pays off most. Mini-pilot validates approach before batch execution. Bidirectional validation catches what forward-only misses (Choisor data: 4.7%). Both specs AND architecture docs are substantially rewritten — the technology changed, the business logic didn't.

---

# Part 2: Lifecycle Phases

## Phase 1: Discovery

The goal is to **capture and confirm WHAT we're building** — turning a vague business ask into concrete, confirmed requirements. Discovery applies to **Cases 1 (Greenfield) and 2 (Add Feature)** — the only cases where new requirements need to be captured. Other cases (bootstrap, bug fix, refactoring, migration) have their own entry points and skip Discovery.

If the request spans multiple cases ("Add RBAC and refactor auth"), the orchestrator splits it into separate work items, each with its own draft and lifecycle.

**Step 1 — Classify complexity.** Assess the scope. This determines how deep Discovery goes (see Ceremony Scaling). Trivial tasks skip Discovery entirely.

**Step 2 — Research before asking.** The orchestrator investigates BEFORE asking the user questions. This produces informed questions, not generic ones.

- **Greenfield**: No codebase to research. Research similar systems, tech landscape, best practices via external search (librarian). "You want an inventory management system — typical ones include multi-warehouse support, real-time stock tracking, POS integration. Which of these do you need?"
- **Add Feature**: Load system spec (`_system.yml`) + architecture docs to understand the whole system. From the system spec, identify which individual specs are relevant to the new feature, then load only those. The orchestrator does NOT load all specs or search the actual codebase — the two-tier system prevents context overload while providing sufficient understanding. If the system spec isn't enough to identify relevant specs, that's a spec quality issue. Fire external search (librarian) only if the new feature involves unfamiliar technology. Questions become specific: "I see from the system spec that auth depends on user-management and is depended on by rbac. Should RBAC extend the existing auth middleware, or be a separate module?"

**Step 3 — Interview with draft-as-memory.** The orchestrator creates a draft file (`.wonflowoo/workspace/drafts/{id}-{name}.md`) as its working memory and conducts a requirements interview. Throughout the conversation, decisions are persisted to the draft — the orchestrator's external memory. The draft is updated after EVERY meaningful exchange.

Draft captures: confirmed requirements, decisions with rationale, research findings, open questions, scope boundaries (IN/OUT). The draft does NOT contain architecture decisions — those belong in the Architecture phase.

The orchestrator also fills in standard requirements the user may not think to mention — common capabilities for the type of system being built, standard non-functional requirements (error handling, validation, edge cases), integration concerns.

**Step 4 — Clearance check.** After each exchange, the orchestrator checks:

```
DISCOVERY CLEARANCE:
□ Core objective clearly defined?
□ Scope boundaries established (IN / OUT)?
□ User roles / personas identified?
□ Key data entities identified?
□ Integration points with external systems identified?
□ Tech preferences or constraints captured? (greenfield only)
□ Impact on existing system understood? (add feature only)
□ Affected modules / specs identified? (add feature only)
□ No critical ambiguities remaining?
```

ALL YES → move to Architecture. ANY NO → ask the specific unclear question.

**Quality gate:** Requirements are confirmed by the human. No ambiguity on WHAT we're building.

**Output:** Requirements document (`.wonflowoo/workspace/requirements/{id}-{name}.md`) — confirmed scope, features, constraints, acceptance criteria. Includes `Status: pending_approval` at the top. When human confirms, update to `Status: approved`.

---

## Phase 2: Architecture

The goal is to design **HOW we're building it** — technical approach, system structure, data model, conventions. You can't parallelize work or delegate tasks if you haven't decided on the system structure. Architecture applies to Cases 1, 2, 5, and 6. Bug fixes (Case 4) typically skip this phase unless the fix reveals fundamental design issues.

**Step 1 — Determine scope.** What needs to be designed depends on the case:

| Case | Architecture Scope |
|---|---|
| **Greenfield** | Full architecture from scratch — tech stack, system design, data model, folder structure, conventions, API design |
| **Add Feature** | Additive — how the new feature integrates within existing architecture. Which arch docs need updating (new tables, new endpoints, new conventions). May be lightweight if feature fits cleanly. |
| **Refactoring** | Structural — propose target structure, define invariants (what must NOT change), design incremental migration path from current to target. |
| **Migration** | Translation — design target state in new technology, map source patterns to target patterns, identify gaps, decide gap resolution. |

**Step 2 — Research target technology (if needed).** For greenfield, add-feature with new tech, or migration: fire external search (librarian) for best practices, official docs, production patterns. The orchestrator should not design architecture based on stale training data when current docs are available.

**Step 3 — Propose architecture.** The orchestrator drafts the technical approach, typically through an `architect`-role dispatch for Medium+ work. After architecture docs are written, the orchestrator may run an optional **read-only** `architecture-consultant` review (recommended for Medium+ and risk-sensitive work) to catch scaling bottlenecks, security gaps, and weak trade-offs before human gate review.

What gets designed:

- **Greenfield**: Tech stack choices (with rationale), system design (how components connect), data model (entities, relationships, constraints), folder structure, naming conventions, API design patterns, error handling approach, auth strategy.
- **Add Feature**: Where the feature sits in the existing architecture, what data model changes are needed, which existing patterns to follow, what new patterns (if any) are introduced.
- **Refactoring**: Target module structure, dependency changes, migration sequence (what gets moved first), invariants (public API stays the same, behavior unchanged).
- **Migration**: Target technology architecture, pattern translation table (source pattern → target equivalent), gap list with resolutions, rollback strategy.

**Step 4 — Write architecture docs.** Decisions are formalized into the appropriate files:

- `tech-stack.yml` — created (greenfield) or updated (if stack changes)
- `conventions.yml` — created or updated with new patterns
- `dependencies.yml` — external service integrations (Shopify API, QuickBooks, SendGrid, S3). NOT npm/pip packages. Skip if no external services.
- `system-design.md` — narrative explaining how it all fits together and WHY, including data model design and API design decisions for greenfield
- `decisions/{NNN}-{name}.md` — ADR for any non-obvious decision (loaded on demand, not auto-loaded)

Note: detailed data model (tables, columns, relationships) and API surface (endpoints, methods) are NOT captured in architecture docs — they live in specs (L3: Data and L1: Interfaces) and the system spec (data_ownership, data_relationships). Architecture docs capture design CONVENTIONS and RATIONALE, not the detailed schema. For greenfield, the planned data model and API design are described in `system-design.md` during the Architecture phase, then become reality in specs after implementation.

**Step 5 — Align with human.** Present the architecture to the user. This is the **last chance to catch fundamental design misunderstandings** before committing effort to implementation.

For enterprise settings: also align with other tech leads / stakeholders.

Summary includes: key technical decisions made, trade-offs accepted, what the specialist flagged (if consulted), what patterns will be followed, what's explicitly out of scope.

**Step 6 — Clearance check.**

```
ARCHITECTURE CLEARANCE:
□ System structure defined (how components connect)?
□ Data model designed (described in system-design.md for greenfield)?
□ API design established (patterns, auth strategy, error format in conventions.yml)?
□ Conventions decided (naming, folder structure, error handling)?
□ Non-obvious decisions documented as ADRs?
□ Architect produced/validated the design for Medium+ work?
□ Optional `architecture-consultant` review considered for Medium+ risk?
□ Human aligned — no fundamental disagreements?
□ Architecture docs written to .wonflowoo/workspace/architecture/?
```

For add-feature, only the relevant items apply (you don't re-decide the entire tech stack for a new feature).

**Quality gate:** Architecture is confirmed by the human. Medium+ work has specialist-backed design (architect required, consultant optional read-only review). Architecture docs are written and committed.

**Output:** Architecture docs (`.wonflowoo/workspace/architecture/`) — structured YAML + narrative Markdown. See Architecture Document Structure section for file details.

---

## Phase 3: Planning

The goal is to break the architecture into concrete, dependency-ordered tasks that can be delegated. The orchestrator produces a **high-level plan** — WHAT needs to be done and in WHAT ORDER, not HOW to implement each task. The HOW is the developer's job.

Planning applies to **Cases 1, 2, 5, and 6**. Bug fixes (Case 4) skip Planning — the orchestrator diagnoses and either fixes directly or delegates a single task.

**Step 1 — Gap analysis (specialist).** Before generating the plan, a **dedicated gap-analysis specialist** (separate agent, high-reasoning model) reviews everything gathered so far: requirements doc, architecture docs, research findings, draft notes. The specialist identifies what the orchestrator missed:

- Questions that should have been asked during Discovery
- Guardrails needed but not established
- Scope creep areas — features implicitly assumed but not confirmed
- Unvalidated assumptions in the architecture
- Missing acceptance criteria
- Edge cases not addressed

The orchestrator incorporates the specialist's findings before proceeding. If the specialist surfaces critical gaps, the orchestrator goes back to the user before planning.

**Step 2 — Task breakdown with dependency ordering.** Tasks are grouped into parallel execution waves. The wave structure varies by case:

**Greenfield (Case 1)** — Full wave structure, maximum parallelism:
```
Wave 1 (Foundation):
├── Project scaffolding + configuration
├── Shared types / interfaces / schemas
├── Base infrastructure (auth, DB setup, etc.)
└── Convention-setting reference implementations

Wave 2 (Core features — max parallel):
├── Core feature A (depends: Wave 1)
├── Core feature B (depends: Wave 1)
├── Core feature C (depends: Wave 1)
└── ... (independent features run in parallel)

Wave 3+ (Dependent features):
├── Feature depending on A + B
├── Integration layer
└── ...

Wave FINAL (Verification):
├── Plan compliance audit
├── Code quality review
└── Scope fidelity check → human approval
```

**Add Feature (Case 2)** — Typically 1-3 waves. May be just "implement + update specs" for small features:
```
Wave 1: Foundation changes (new tables, new shared types)
Wave 2: Feature implementation (may be a single task)
Wave 3: Integration + verification
```

**Refactoring (Case 5)** — Each step must leave the system working. Safety-focused ordering:
```
Wave 1: Extract shared code / interfaces
Wave 2: Split or restructure modules (one at a time, tests pass between each)
Wave 3: Update all callers / dependents
Wave 4: Clean up (remove old code, update specs)
Invariant: Tests pass after EVERY wave. Behavior unchanged throughout.
```

**Migration (Case 6)** — Mini-pilot first, then batch. Bidirectional validation:
```
Wave 0 (PILOT): Pick 2-3 representative items (simple, medium, complex)
  └── Run full migration cycle → validate approach → fix systemic issues

Wave 1-N (Batch execution): Migrate remaining items in parallel waves
  └── Each item: migrate → validate source behavior matches target

Wave FINAL: Full system validation + bidirectional verification
```

**Step 3 — Detail each task (orchestrator level).** Each task in the plan includes:

- **What to build**: High-level description of the deliverable
- **What NOT to do**: Explicit exclusions, guardrails
- **Architecture doc references**: Which YAML/MD files the developer should load
- **Spec references**: Which existing specs are relevant (for existing projects)
- **ADR references**: Which decision records to load (if relevant)
- **Acceptance criteria**: How the orchestrator will verify completion
- **Dependency info**: Which wave, what it blocks, what blocks it
- **Category**: What kind of task (visual-engineering, backend, etc.) — determines model routing

These task briefs in the plan become **task instruction files** (`.wonflowoo/workspace/tasks/`) during the Delegation phase. The plan is the high-level view; task files are the detailed contracts.

Note: The orchestrator does NOT detail implementation steps. That's the developer's job after loading the relevant docs and code.

**Step 4 — Self-review and gap classification.** The orchestrator reviews its own plan:

- **Critical gaps** (require user decision): Add placeholder in plan, ask specific question with options
- **Minor gaps** (can self-resolve): Fix silently, note in summary
- **Ambiguous gaps** (reasonable default exists): Apply default, disclose in summary so user can override

**Step 5 — Present and confirm.** Summary to the human: key decisions made, scope IN/OUT, guardrails applied, auto-resolved items, defaults applied, decisions still needed (if any). If the gap analysis specialist surfaced anything notable, include that.

**Step 6 — Optional high-accuracy review.** For high-stakes work, an independent reviewer validates the plan itself: Are all file references real? Are acceptance criteria concrete and agent-executable? Are there unvalidated assumptions? Loop until the plan passes review — no maximum retries, fix every issue.

**Step 7 — Clearance check.**

```
PLANNING CLEARANCE:
□ Gap analysis completed by specialist?
□ All tasks have clear deliverables and acceptance criteria?
□ Dependency ordering is correct (no circular deps, no missing prerequisites)?
□ Each task is scoped to feature-level (not too granular, not too coarse)?
□ Category assigned to every task (for model routing)?
□ Plan reviewed and confirmed by human?
□ Critical gaps resolved (or explicitly deferred with user approval)?
□ Plan doc written to .wonflowoo/workspace/plans/?
```

**Quality gate:** Plan confirmed by human. Gap analysis specialist has reviewed. For high-stakes work, also validated by independent reviewer.

**Output:** Plan doc (`.wonflowoo/workspace/plans/{id}-{name}.md`) — dependency-ordered execution waves with high-level task briefs. Includes `Status: pending_approval` and `Task IDs: []` (populated during Delegation). When human confirms, update to `Status: approved`.

---

## Combined Flow (Cases 1-2: Greenfield / Add Feature)

```
User Request
    │
    ▼
Draft created (.wonflowoo/workspace/drafts/{id}-{name}.md) — orchestrator's living memory
    │
    ▼
DISCOVERY (WHAT are we building?)
    ├── Research (librarian for greenfield, specs + arch docs for existing)
    ├── Interview user → capture requirements
    ├── Fill in standard requirements user may miss
    ├── Draft updated throughout
    ├── Clearance check ──── ANY NO → ask specific question ──┐
    │                                                          │
    │   ALL YES ◄──────────────────────────────────────────────┘
    │
    └── → Requirements doc confirmed (.wonflowoo/workspace/requirements/{id}-{name}.md)
    ▼
ARCHITECTURE (HOW are we building it?)
    ├── Research target tech if needed (librarian)
    ├── Propose technical approach
    ├── Architect designs docs (Medium+), optional consultant review (read-only)
    ├── Write architecture docs (YAML + MD)
    ├── Align with human ──── MISALIGNED → iterate ──┐
    │                                                 │
    │   ALIGNED ◄─────────────────────────────────────┘
    │
    └── → Architecture docs confirmed (.wonflowoo/workspace/architecture/)
    ▼
PLANNING (HOW do we orchestrate and hand off?)
    ├── Gap analysis by specialist
    ├── Break into dependency-ordered waves (case-specific structure)
    ├── High-level task briefs (what to build, not how)
    ├── Self-review + gap classification (critical/minor/ambiguous)
    ├── Present summary to human
    ├── Optional: high-accuracy review loop
    ├── Human confirms ──── CHANGES NEEDED → iterate ──┐
    │                                                    │
    │   CONFIRMED ◄──────────────────────────────────────┘
    │
    └── → Plan doc confirmed (.wonflowoo/workspace/plans/{id}-{name}.md)
    ▼
DELEGATION
    ├── Per-wave task-file generation (.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.yml)
    ├── Dispatch planning-only to developers
    ├── Mandatory plan review gate
    ├── Dispatch implementation only after approval
    ▼
DEVELOPER PLANNING (per developer)
    ├── Load task file + arch docs + specs + code
    ├── Create implementation plan
    ├── Align with orchestrator
    ▼
IMPLEMENTATION
    ├── Developers execute
    ├── Specs generated/updated from actual code
    └── Draft marked done
```

Note: Cases 3-6 (bootstrap, bug fix, refactoring, migration) have different entry points — see High-Level Flows by Case above.

---

## Phase 4: Delegation + Developer Planning

The goal is to **dispatch planned tasks to developers and enforce plan alignment before any code is written**.

Delegation uses a strict three-step protocol per task: **Plan → Review → Implement**.
These are separate dispatches. Plan+implement in one dispatch is never allowed.

### Two-Level Planning Model

- **Orchestrator plan (`.wonflowoo/workspace/plans/`)**: WHAT + ORDER (high-level briefs, waves, dependencies)
- **Task instruction files (`.wonflowoo/workspace/tasks/*.yml`)**: self-contained technical user stories for execution
- **Developer plan (`.wonflowoo/workspace/tasks/*.plan.md`)**: HOW for current codebase reality

The orchestrator plan stays high-level. Detailed task files are generated **per wave** with current architecture/spec context loaded at generation time.

### Per-Wave Parallel Dispatch Pattern

For a wave with N tasks:

1. **Task-file generation (N parallel tech-lead dispatches)**
   - Expand plan briefs into full task YAML files.
   - Load current requirements + architecture docs + specs before writing each task file.
2. **Developer planning (N parallel developer dispatches)**
   - One developer per task writes `.plan.md` only.
3. **Plan review gate (N parallel reviews, mandatory)**
   - Every `.plan.md` must be approved before implementation.
4. **Implementation (N parallel developer dispatches)**
   - Execute approved plans only.

After each stage, wait for all N results before advancing.

### Task File Contract

Task files are self-contained technical user stories with this naming:

```text
.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.yml
```

Where origin is:
- plan name for planned work
- `bugfix` for bug fixes
- `adhoc` for ad-hoc work

Developer plan companion file:

```text
.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.plan.md
```

Each task file includes at minimum: `task`, `wave`, `status`, `plan_ref` (planned tasks), `category`, `context`, `brief`, `architecture_refs`, `spec_refs`, `adr_refs`, `must_do`, `must_not_do`, `acceptance_criteria`, `depends_on`, `blocks`.

### Mandatory Plan Review Gate

Before coding, each developer plan is reviewed by orchestrator or (recommended for Medium+) a `plan-reviewer` role.

This review is **holistic alignment**, not syntax-only:
- task file ↔ developer plan ↔ requirements/specs/architecture consistency
- acceptance-criteria coverage
- dependency and sequencing sanity
- conventions/guardrails compliance

`plan-reviewer` outputs APPROVE or REJECT with concrete blocking issues. Rejected plans loop back to developer planning only.

### Progress + Failure Handling

Task statuses remain orchestrator-owned (`pending`, `in_progress`, `completed`, `blocked`).

Wave progression is gated: only when all tasks in the current wave are `completed` does the next wave unblock.

Failure handling:
1. Developer-level issue → re-dispatch with stronger constraints/context
2. Plan-level issue → return to Planning; revise plan and regenerate affected task files
3. 3 consecutive failures → stop and escalate with analysis

---

## Phase 5: Implementation

The goal is to **execute the plan and produce working code + updated specs**. Developers implement their aligned plans, the orchestrator monitors progress across waves, and specs are generated/updated to reflect what was actually built.

### Developer Execution

After alignment, the developer implements their plan:

1. **Write code** following the architecture docs and conventions
2. **Verify** against acceptance criteria from the task file
3. **Write a change manifest** — structured report of: files created, files modified, endpoints added/changed, data touched, deviations from plan
4. **Report back** to the orchestrator with the change manifest

The developer does NOT update specs or task file status — they report completion with a change manifest. Spec updates are handled by a dedicated `spec-updater` agent (see below).

### Orchestrator Monitoring

During implementation, the orchestrator:

- **Tracks wave progress** — which tasks are pending, in-progress, completed, blocked
- **Spawns spec-updater** — after each developer completes, the orchestrator spawns a `spec-updater` agent to update affected specs (see Spec Updates below)
- **Validates completions** — checks acceptance criteria AND spec updates before marking the task `completed`
- **Unblocks next wave** — when all tasks in a wave are complete, the next wave's tasks become available
- **Handles failures** — re-dispatch or escalate (see Failure Handling in Delegation)
- **Updates draft** — records implementation progress in a structured Implementation table (task ID, status, deviations, issues, spec paths)

### Spec Updates (spec-updater Agent)

Specs are organized by **feature** (horizontal grouping). Tasks are **vertical slices** that can cut across multiple features. A single task (e.g., "add notification on task assignment") may affect 3 different feature specs plus `_system.yml`. The developer has task-level context but doesn't know the spec structure.

This is why **developers do NOT update specs directly**. Instead, a dedicated `spec-updater` agent with tech-lead context handles spec updates:

1. Developer completes task → provides change manifest (files created/modified, endpoints, data touched)
2. Orchestrator spawns `spec-updater` with: change manifest + task file + affected source code + existing specs + `_system.yml`
3. `spec-updater` determines which specs this task affects by checking `source_paths` in existing specs
4. Updates affected feature specs (L1-L4 layers) and `_system.yml` (if cross-module changes)
5. Reports back: which specs were updated and what changed

This separation ensures:
- **Developer focus**: implement code, verify acceptance criteria, report what changed
- **Spec-updater focus**: route changes to correct specs, maintain spec structure, update macro view

**Per case:**
- **Greenfield (Case 1):** spec-updater creates new spec files from change manifests
- **Existing projects (Case 2):** spec-updater updates existing specs, creates new ones for new modules
- **Refactoring (Case 5):** spec-updater regenerates affected specs to reflect structural changes
- **Migration (Case 6):** spec-updater regenerates specs for migrated modules

### Verification Wave

For non-trivial work, the final wave includes verification:

- **Plan compliance** — does the implementation match what was planned?
- **Code quality** — does the code follow conventions and architecture docs?
- **Scope fidelity** — did we build what was asked, nothing more, nothing less?
- **Spec accuracy** — do the updated specs accurately reflect what was built?

The orchestrator presents results to the human for final approval.

### Optional High-Accuracy Review (Large/Enterprise)

For Large/Enterprise or high-stakes work, run a read-only `architecture-consultant` review after implementation:

- Inputs: requirements + plan + architecture docs + `_system.yml` + relevant specs
- Goal: detect requirement drift, cross-cutting regressions, architecture/spec divergence
- Output: review findings and remediation recommendations

Critical findings are resolved before final completion.

### Completion

When all waves are done and verified:

1. All task files marked `completed`
2. Specs updated to reflect current codebase state
3. Orchestrator draft marked `done` (preserved as historical record)
4. Plan doc archived
5. Human notified of completion with summary

---

# Part 3: Bootstrap

## Bootstrap Process (Case 3)

Bootstrap is a separate process — not part of the standard Discovery → Architecture → Planning lifecycle. It's a one-time setup when adopting the framework on an existing codebase that has no specs or architecture docs.

The challenge: for large codebases, you can't load everything into one context and understand it. The solution is a multi-step pipeline where **no single step ever needs to hold the entire codebase in context**, and the final output is feature-grouped specs optimized for the orchestrator.

### Key Design Principle

Individual specs are organized by **feature** (semantic grouping), not by directory or file. This is optimal for the orchestrator — loading `auth.yml` gives you the complete auth story without loading unrelated content. But feature grouping is an opinionated decision that requires understanding the codebase first.

The bootstrap pipeline solves this by separating **factual analysis** (per-file, objective) from **organizational decisions** (feature grouping, opinionated):

```
Per-file analysis (objective) → Summarize → AI groups into features → Feature spec generation → System spec → Validation → Human review
```

### Step 0 — Framework Adoption + Pre-Flight (Orchestrator)

Before analysis starts, bootstrap first adopts the framework safely:

1. **Detect colliding files/directories** (`AGENTS.md`, `CLAUDE.md`, subdirectory `AGENTS.md`, `.wonflowoo/workspace/`, `.claude/`)
2. **Migrate collisions** to `.migrated` names (for example `AGENTS.migrated.md`, `.ai.migrated/`) rather than deleting
3. **Install framework structure** for bootstrap (`.wonflowoo/workspace/` plus required framework files)
4. **Create bootstrap workspace**: `.wonflowoo/workspace/.bootstrap/analysis/` and `.wonflowoo/workspace/.bootstrap/summaries/`

Migrated files remain valuable read-only context for generation.

### Step 1 — Quick Scan (Orchestrator)

The orchestrator does a shallow scan to understand the project shape:

- Directory tree + file counts per directory
- Language/framework detection (package.json, go.mod, pyproject.toml, etc.)
- Identify significant source files (skip configs, type definitions, test files, generated code)
- Estimate project scale: total files, total lines, depth

Output: a list of significant source files to analyze.

### Step 2 — Fan-Out (Per-File Analysis)

Each investigator agent is assigned one source file (or a small group of closely related files) and produces a per-file analysis — reading actual code and writing a 4-layer YAML analysis to `.wonflowoo/workspace/.bootstrap/analysis/{batch}.yml`.

```
Orchestrator assigns files
  │
  ├── Investigator 1 → src/routes/auth.routes.ts         → analysis
  ├── Investigator 2 → src/services/auth.service.ts       → analysis
  ├── Investigator 3 → src/middleware/auth.middleware.ts   → analysis
  ├── Investigator 4 → src/services/order.service.ts      → analysis
  ├── Investigator 5 → src/routes/order.routes.ts         → analysis
  └── ... (one per significant file, all parallel)
```

**Each investigator produces a per-file analysis covering:**
- **Interfaces**: what this file exposes or consumes (endpoints, events, exports)
- **Logic**: detailed step-by-step flows with error paths — directly from the code
- **Data**: tables, columns, cache keys touched by this file
- **Dependencies**: what this file imports (internal files + external packages)

**Investigators are:**
- **Capable** — must produce detailed logic flows from actual code. Not the cheapest model, but each has a small, focused scope (one file)
- **Parallel** — all run simultaneously. 500 files = 500 parallel investigators
- **Independent** — each sees only their file. No cross-file knowledge needed

### Step 3 — Summarize (Metadata Extraction)

Extract compact metadata from each per-file analysis — just enough for the grouping agent to work with. Compression agents read from `analysis/` and write summaries to `.wonflowoo/workspace/.bootstrap/summaries/{partition}.yml`.

```
Per-file analysis → Compact summary:
  - file: src/services/auth.service.ts
    imports: [src/repositories/refresh-token.repo.ts, src/repositories/user.repo.ts, bcrypt, jsonwebtoken]
    exports: [AuthService]
    interfaces: [none — internal service]
    data_touched: [users (read), refresh_tokens (read/write), redis rate_limiting (read/write)]
    domain_signals: [auth, login, token, jwt, password]
```

Each summary is ~5-10 lines. Even 2,000 files × 10 lines = 20,000 lines of metadata — fits in a large context window.

### Step 4 — AI Feature Grouping

A grouping agent reads ALL file summaries and clusters them into feature groups using:

- **Naming patterns** — files with `auth` in the name likely belong together
- **Import chains** — files that call each other form a cluster
- **Shared data** — files touching the same tables belong to the same domain
- **Domain signals** — keywords like "login", "token", "order", "payment" indicate feature boundaries

```
Grouping agent reads all summaries
  │
  ▼
Produces feature groups:
  auth: [auth.routes.ts, auth.service.ts, auth.middleware.ts, refresh-token.repo.ts]
  order-processing: [order.routes.ts, order.service.ts, order.repo.ts]
  user-management: [user.routes.ts, user.service.ts, user.repo.ts, user-profile.repo.ts]
  notifications: [notification.service.ts, email.service.ts, push.service.ts]
  ...
```

This is the opinionated step — but it's informed by strong signals from the code, not guesswork. Output is written to `.wonflowoo/workspace/.bootstrap/groups.yml`. No human input needed; human validates the result at the end.

### Step 5 — Feature Spec Generation

For each feature group, a spec generation agent combines relevant per-file analyses into one feature-grouped spec and writes directly to `.wonflowoo/workspace/specs/{feature}.yml`.

```
Feature group "auth" defined: [auth.routes.ts, auth.service.ts, auth.middleware.ts, refresh-token.repo.ts]
  │
  ▼
Spec agent loads per-file analyses for those 4 files
  │
  ▼
Produces: .wonflowoo/workspace/specs/auth.yml
  ├── L1 Interfaces: combined from auth.routes.ts analysis (endpoints) + auth.middleware.ts analysis (middleware)
  ├── L2 Logic: combined from auth.service.ts analysis (flows) + auth.middleware.ts analysis (auth check)
  ├── L3 Data: combined from all analyses (users table, refresh_tokens table, redis)
  ├── L4 Dependencies: combined and cross-referenced
  └── source_paths: [all 4 files listed]
```

Each feature spec generation only needs the per-file analyses for its files — typically 5-15 files per feature. Small context load.

**This runs in parallel** — one agent per feature group, all independent.

### Step 6 — System Spec + Architecture Docs (DELEGATED)

By this point the orchestrator has accumulated high context from Steps 0-5. Step 6 is delegated to a **fresh sub-agent** that starts with clean context and reads generated files from disk.

The delegated agent builds `_system.yml` incrementally and writes architecture docs (`tech-stack.yml`, `conventions.yml`, `dependencies.yml`, `system-design.md`).

```
Feature spec "auth" generated
  → Agent reads current _system.yml + auth spec summary
  → Appends auth to _system.yml (feature group, deps, data ownership)

Feature spec "order-processing" generated
  → Agent reads current _system.yml + order-processing spec summary
  → Appends order-processing, adds cross-references to auth

... repeat for each feature spec ...
```

Each incremental append needs: current `_system.yml` (growing but compressed) + one feature spec summary. Never the entire codebase.

File-based flow is mandatory: sub-agents write outputs to `.wonflowoo/workspace/.bootstrap/` / `.wonflowoo/workspace/specs/`, and the orchestrator consumes file paths rather than large in-memory result payloads.

### Step 7 — Validation Pass (DELEGATED)

Step 7 is also delegated to a fresh validation sub-agent. It reads the completed `_system.yml` + specs and checks:

- All source files accounted for? (no files missing from feature groups)
- Dependency graph consistent? (no dangling references)
- Data relationships complete? (all FK relationships captured)
- Feature groups sensible? (no feature with 50 files, no single-file features for non-trivial code)
- Cross-module flows identified?

Flags gaps or inconsistencies → amends `_system.yml` and affected feature specs.

### Step 8 — Human Review

The orchestrator presents the generated specs and architecture docs to the human: "Here's what I found. Does this match how your team thinks about the system?"

```
Bootstrap clearance:
□ Feature groupings match how the team thinks about the system?
□ Tech stack correctly identified?
□ Data relationships accurate?
□ No major features or files missed?
□ Conventions documented match what the team actually follows?
□ Cross-module flows capture the key business processes?
```

Corrections applied → `.wonflowoo/` directory is now populated (framework + workspace) → project operates as Case 2 (existing project with specs + arch docs) for all future work.

### Context Budget at Each Step

| Step | What's loaded | Max context for 500-file project |
|---|---|---|
| Step 1: Quick Scan | Directory tree | Tiny |
| Step 2: Fan-Out | One source file per agent | Small per agent, unlimited parallelism |
| Step 3: Summarize | One per-file analysis → 10-line summary | Tiny per file |
| Step 4: AI Grouping | All 500 summaries | ~5,000 lines — fits easily |
| Step 5: Feature Specs | 5-15 per-file analyses per feature | Small per agent, parallel |
| Step 6: System Spec + Arch Docs (delegated) | Fresh sub-agent reads specs/groups + writes outputs | Orchestrator stays lean; heavy read work offloaded |
| Step 7: Validation (delegated) | Fresh validator reads completed outputs | Orchestrator receives findings + file paths |
| Step 8: Human Review | System spec + feature list | Human reads one doc |

No step ever loads the entire codebase. Scales to any size.

### Scaling Behavior

| Codebase Size | Strategy |
|---|---|
| **Small** (<50 files) | Skip fan-out. One agent reads everything and generates specs directly. |
| **Medium** (50-500 files) | Full pipeline. 50-500 parallel investigators. |
| **Large** (500-2,000 files) | Full pipeline. May need hierarchical grouping at Step 4 (group by package first, then by feature within each package). |
| **Monorepo** | Each package/workspace runs its own bootstrap pipeline independently. System spec links them via external dependencies. |

---

# Part 4: Core Systems

## The Spec System

Specs are the key bridge that lets the orchestrator "know" the codebase without reading all of it. They represent **what a tech lead would carry in their head** — not a line-by-line mirror of the code.

### Key Distinction: Architecture Docs vs Specs

| | Architecture Docs | Specs |
|---|---|---|
| **When created** | During Architecture phase (before implementation) | After implementation (from actual code) |
| **What they describe** | Intent — what we PLAN to build and WHY | Reality — what ACTUALLY exists in the codebase |
| **Who creates them** | Orchestrator (during planning) | `spec-updater` (post-implementation) / bootstrap generators |
| **Source of truth** | Design intent and decisions | Actual code and database |
| **Content** | Tech stack, conventions, data model design, rationale | Module interfaces, actual behavior, real data model, dependencies |

Architecture docs describe the **intended state**. Specs describe the **actual state**. After implementation, specs are always ground truth.

### Two-Tier Spec Architecture

A senior architect carries the whole system map in their head and zooms into specific areas when needed. The spec system mirrors this with two tiers:

| Tier | File | When loaded | What it captures |
|---|---|---|---|
| **System spec** | `.wonflowoo/workspace/specs/_system.yml` | **Always** — first thing the orchestrator loads | Registry of all specs, dependency graph, data ownership, cross-cutting flows. Compressed summaries. |
| **Specs** | `.wonflowoo/workspace/specs/{name}.yml` | **On demand** — when working on a specific area | Full 4-layer detail (interfaces, logic flows, data, dependencies) |

**Why two tiers:** For large systems with 50+ specs, loading all detailed specs would exceed the context window. The system spec gives the orchestrator the full picture in one file. When it needs to work on a specific area, it loads only the relevant specs.

**The orchestrator's workflow:**
1. Load `_system.yml` → understand the whole system
2. Decide which specs are relevant to the current task
3. Load only those specs → get the detail needed
4. Plan/delegate with full context for the affected area

**System spec is derived** — auto-generated or auto-updated from individual specs. When any spec changes, the system spec reflects those changes. It is not manually maintained.

### System Spec Structure

```yaml
# .wonflowoo/workspace/specs/_system.yml — the architect's holistic view (always loaded)

modules:
  - name: auth
    description: JWT authentication with refresh token rotation
    owner: backend
    interfaces_summary: [rest (2 endpoints), pubsub (1 topic), scheduler (1 job)]
    data_summary: [postgresql (users, refresh_tokens), redis (rate limiting)]

  - name: order-processing
    description: Order lifecycle from cart to delivery
    owner: backend
    interfaces_summary: [rest (12 endpoints), pubsub (5 topics), scheduler (2 jobs)]
    data_summary: [postgresql (orders, order_items, order_status_history)]

  - name: checkout-page
    description: Multi-step checkout flow
    owner: frontend
    interfaces_summary: [route (2 paths), api_consumer (3 calls), events (2 emitted)]
    data_summary: [zustand (cart-store), local_state]

dependency_graph:
  auth:
    depends_on: [user-management]
    depended_by: [rbac, order-processing, api-gateway]
  order-processing:
    depends_on: [auth, payment, inventory, notification]
    depended_by: [checkout-page, admin-dashboard]
  checkout-page:
    depends_on: [cart-store, order-processing, payment, shared-components]
    depended_by: []

data_ownership:
  postgresql:
    users: auth
    refresh_tokens: auth
    user_profiles: user-management
    orders: order-processing
    payments: payment
    products: inventory
  redis:
    rate_limiting: auth
    session_cache: user-management

data_relationships:
  - from: order-processing.orders.user_id → auth.users.id
  - from: payment.payments.order_id → order-processing.orders.id
  - from: auth.refresh_tokens.user_id → auth.users.id
  - from: user-management.user_profiles.user_id → auth.users.id

cross_module_flows:
  place_order:
    - order-processing: validate cart, create order (pending)
    - payment: charge payment method
    - order-processing: confirm order
    - inventory: decrement stock
    - notification: send confirmation
    - On payment failure → order-processing rolls back, notification sends alert

  user_registration:
    - auth: create user record, generate tokens
    - user-management: create default profile
    - notification: send welcome email
```

### 4-Layer Spec Model

Every spec is structured in 4 layers. Each layer is generic enough to represent any application type — HTTP APIs, gRPC services, message queues, scheduled jobs, CLI tools, ML pipelines, or anything else.

Every spec includes `source_paths` at the top level — the actual source files this spec represents. Within each layer, `file:` fields map specific interfaces, services, and flows back to their source files. This maintains the connection between spec and code — developers and the orchestrator always know WHERE in the codebase something lives.

| Layer | What it captures | Key question answered |
|---|---|---|
| **L1: Interfaces** | How this module communicates with the outside world — any I/O type, any direction | "What can I call / what calls this?" |
| **L2: Logic** | What this module does — services, behaviors, business rules, key functions | "What does this module actually do?" |
| **L3: Data** | How this module stores or accesses state — DB, cache, files, or "stateless" | "What data does it touch?" |
| **L4: Dependencies** | What this module depends on and what depends on it — internal and external | "What breaks if I change this?" |

### L1: Interfaces (Generic I/O)

Interfaces are NOT limited to HTTP APIs. Any way a module communicates is an interface. Each interface has a `type`, `direction`, and type-specific details.

```yaml
interfaces:
  # HTTP REST
  - type: rest
    direction: inbound
    endpoints:
      - path: /api/auth/login
        method: POST
        auth: none
        request: { email: string, password: string }
        response: { access_token: string, refresh_token: string }
      - path: /api/auth/refresh
        method: POST
        auth: refresh_token
        response: { access_token: string, refresh_token: string }

  # gRPC
  - type: grpc
    direction: inbound
    services:
      - name: AuthService
        methods: [Login, RefreshToken, ValidateToken]
        proto: auth.proto

  # Message queue (publishing)
  - type: pubsub
    direction: outbound
    topics:
      - name: user.login.success
        payload: { user_id: string, timestamp: datetime }
      - name: user.login.failed
        payload: { email: string, reason: string }

  # Message queue (consuming)
  - type: pubsub
    direction: inbound
    subscriptions:
      - topic: user.deleted
        handler: handleUserDeletion

  # WebSocket
  - type: websocket
    direction: bidirectional
    channels:
      - name: notifications
        events_in: [subscribe, unsubscribe]
        events_out: [notification, alert]

  # Scheduled jobs
  - type: scheduler
    direction: internal
    jobs:
      - name: cleanupExpiredTokens
        schedule: "0 */6 * * *"
        description: Remove expired refresh tokens every 6 hours

  # File I/O
  - type: file_io
    direction: inbound
    imports:
      - name: bulkUserImport
        format: CSV
        source: S3
        trigger: manual

  # Outbound API calls
  - type: http_client
    direction: outbound
    calls:
      - name: sendVerificationEmail
        target: email-service
        method: POST
        path: /api/emails/send
```

The framework does not prescribe what interface types exist — a project can have any combination. Common types include: `rest`, `graphql`, `grpc`, `websocket`, `sse`, `pubsub`, `scheduler`, `file_io`, `http_client`, `cli`, `soap`, `ftp`, `webhook`. New types can be added as needed.

**Direction values:** `inbound` (receives from outside), `outbound` (sends to outside), `bidirectional`, `internal` (self-triggered, like schedulers).

### L2: Logic

What the module does — its behaviors, business rules, and key operations. Not exact code, but enough for the orchestrator to understand what happens and how. Logic is captured in detailed step-by-step flows. Each flow includes a trigger, detailed steps (including error paths, edge cases, and integration points), and subsections for error handling and security where relevant.

```yaml
logic:
  description: |
    Handles user authentication via JWT. Supports login, token refresh,
    and token validation. Rate-limited on auth endpoints.
  flows:
    login:
      trigger: POST /api/auth/login
      steps:
        - Validate email format (return 400 if invalid)
        - Look up user by email from users table
        - If user not found → return 401 AUTH_FAILED (generic error, don't reveal whether email exists)
        - Check rate limit counter for this IP in Redis
        - If rate limit exceeded → return 429 RATE_LIMITED with retry-after header
        - Verify password against stored password_hash using bcrypt.compare()
        - If password mismatch → increment rate limit counter, emit user.login.failed event, return 401 AUTH_FAILED
        - Generate access token (JWT signed with RS256, payload: {user_id, email, iat, exp}, 15min TTL)
        - Generate refresh token (crypto.randomBytes(64), stored as SHA-256 hash in refresh_tokens table, 7 day TTL)
        - Revoke any existing refresh tokens for this user beyond the 5 most recent
        - Set httpOnly secure cookies for web clients (access_token + refresh_token)
        - Return tokens in response body for mobile/API clients
        - Emit user.login.success event with {user_id, timestamp}
      error_handling:
        - All auth errors return same generic 401 to prevent user enumeration
        - Rate limiting is per-IP, tracked in Redis with 60s TTL
    token_refresh:
      trigger: POST /api/auth/refresh
      steps:
        - Extract refresh token from cookie or request body
        - Hash the token with SHA-256, look up in refresh_tokens table
        - If not found or revoked → return 401 INVALID_TOKEN
        - If expired → delete token row, return 401 TOKEN_EXPIRED
        - Verify the associated user still exists and is active
        - Revoke the current refresh token (set revoked_at = now)
        - Generate new access token + new refresh token (same as login flow)
        - Return new token pair
      security:
        - Refresh token rotation prevents token theft replay attacks
        - If a revoked token is used, revoke ALL tokens for that user (potential theft detected)
```

### L3: Data

How the module stores or accesses state. Could be relational DB, NoSQL, cache, file system, or nothing (stateless). If the module has no persistence, this section says `stateless: true`.

```yaml
data:
  stores:
    - type: postgresql
      tables:
        - name: users
          columns:
            - { name: id, type: uuid, pk: true }
            - { name: email, type: varchar, unique: true }
            - { name: password_hash, type: varchar }
            - { name: created_at, type: timestamp }
            - { name: updated_at, type: timestamp }

        - name: refresh_tokens
          columns:
            - { name: id, type: uuid, pk: true }
            - { name: token_hash, type: varchar }
            - { name: user_id, type: uuid, fk: users.id }
            - { name: expires_at, type: timestamp }
            - { name: revoked_at, type: timestamp, nullable: true }

    - type: redis
      usage: Rate limiting counters
      keys:
        - pattern: "rate:login:{ip}"
          ttl: 60s
```

For stateless modules:
```yaml
data:
  stateless: true
```

### L4: Dependencies

What this module depends on (internal modules + external packages) and what depends on it. This is how the orchestrator understands blast radius — "if I change this module, what else is affected?"

```yaml
dependencies:
  internal:
    depends_on:
      - module: user-module
        usage: User lookup by email during login
      - module: notification-module
        usage: Emits login events via pubsub
    depended_by:
      - module: rbac-module
        usage: Role check after authentication
      - module: api-gateway
        usage: Auth middleware applied to all routes

  external:
    - package: bcrypt
      version: "^5.1"
      usage: Password hashing
    - package: jsonwebtoken
      version: "^9.0"
      usage: JWT token generation and validation

### Frontend Specs

The 4-layer model applies to frontend modules as well. Frontend specs capture user interactions, state management, and component interfaces.

```yaml
# .wonflowoo/workspace/specs/checkout-page.yml
name: checkout-page
description: Handles the final step of the purchase flow
source_paths:
  - src/pages/checkout/CheckoutPage.tsx
  - src/pages/checkout/components/PaymentStep.tsx
  - src/pages/checkout/components/ShippingStep.tsx
  - src/hooks/useCheckout.ts

interfaces:
  - type: route
    direction: inbound
    path: /checkout
  - type: props
    direction: inbound
    properties:
      - { name: cartId, type: string, required: true }
  - type: events
    direction: outbound
    events:
      - { name: onOrderComplete, payload: { orderId: string } }
  - type: api_consumer
    direction: outbound
    calls:
      - { name: createOrder, target: order-module, method: POST }

logic:
  flows:
    checkout_initialization:
      trigger: User navigates to /checkout
      steps:
        - Extract cartId from props
        - Fetch cart details from cart-store
        - If cart is empty → redirect to /cart
        - Initialize Stripe Elements with public key
        - Set loading state to false
    payment_submission:
      trigger: User clicks "Pay Now"
      steps:
        - Validate shipping address form (using react-hook-form)
        - If invalid → show validation errors, stop
        - Set processing state to true
        - Call Stripe API to confirm payment
        - If payment fails → show error message, set processing to false
        - Call createOrder API with payment confirmation
        - Clear cart-store
        - Navigate to /success
  state_management:
    - type: zustand
      store: cart-store
      usage: Reading cart items and total
    - type: local_state
      usage: Form data, loading/processing states

data:
  stateless: true

dependencies:
  internal:
    - module: cart-store
    - module: shared-components/Button
    - module: shared-components/AddressForm
  external:
    - package: react-hook-form
    - package: stripe-react
```

### Full Spec File Example

```yaml
# .wonflowoo/workspace/specs/auth.yml
name: auth
description: JWT authentication with refresh token rotation
owner: backend  # which team/category owns this
source_paths:  # actual source files this spec represents
  - src/middleware/auth.middleware.ts
  - src/services/auth.service.ts
  - src/routes/auth.routes.ts
  - src/repositories/refresh-token.repository.ts

interfaces:
  - type: rest
    direction: inbound
    file: src/routes/auth.routes.ts
    endpoints:
      - path: /api/auth/login
        method: POST
        auth: none
        request: { email: string, password: string }
        response: { access_token: string, refresh_token: string }
      - path: /api/auth/refresh
        method: POST
        auth: refresh_token
        response: { access_token: string, refresh_token: string }
  - type: pubsub
    direction: outbound
    file: src/services/auth.service.ts
    topics:
      - name: user.login.success
        payload: { user_id: string, timestamp: datetime }
  - type: scheduler
    direction: internal
    file: src/jobs/cleanup-tokens.ts
    jobs:
      - name: cleanupExpiredTokens
        schedule: "0 */6 * * *"

logic:
  description: |
    Handles user authentication via JWT. Supports login, token refresh,
    and token validation. Rate-limited on auth endpoints.
  services:
    - name: AuthService
      file: src/services/auth.service.ts
    - name: AuthMiddleware
      file: src/middleware/auth.middleware.ts
  flows:
    login:
      file: src/services/auth.service.ts  # where this flow is implemented
      trigger: POST /api/auth/login
      steps:
        - Validate email format (return 400 if invalid)
        - Look up user by email from users table
        - If user not found → return 401 AUTH_FAILED (generic error, don't reveal whether email exists)
        - Check rate limit counter for this IP in Redis
        - If rate limit exceeded → return 429 RATE_LIMITED with retry-after header
        - Verify password against stored password_hash using bcrypt.compare()
        - If password mismatch → increment rate limit counter, emit user.login.failed event, return 401 AUTH_FAILED
        - Generate access token (JWT signed with RS256, payload: {user_id, email, iat, exp}, 15min TTL)
        - Generate refresh token (crypto.randomBytes(64), stored as SHA-256 hash in refresh_tokens table, 7 day TTL)
        - Revoke any existing refresh tokens for this user beyond the 5 most recent
        - Set httpOnly secure cookies for web clients (access_token + refresh_token)
        - Return tokens in response body for mobile/API clients
        - Emit user.login.success event with {user_id, timestamp}
      error_handling:
        - All auth errors return same generic 401 to prevent user enumeration
        - Rate limiting is per-IP, tracked in Redis with 60s TTL
    token_refresh:
      file: src/services/auth.service.ts
      trigger: POST /api/auth/refresh
      steps:
        - Extract refresh token from cookie or request body
        - Hash the token with SHA-256, look up in refresh_tokens table
        - If not found or revoked → return 401 INVALID_TOKEN
        - If expired → delete token row, return 401 TOKEN_EXPIRED
        - Verify the associated user still exists and is active
        - Revoke the current refresh token (set revoked_at = now)
        - Generate new access token + new refresh token (same as login flow)
        - Return new token pair
      security:
        - Refresh token rotation prevents token theft replay attacks
        - If a revoked token is used, revoke ALL tokens for that user (potential theft detected)

data:
  stores:
    - type: postgresql
      tables:
        - name: users
          columns:
            - { name: id, type: uuid, pk: true }
            - { name: email, type: varchar, unique: true }
            - { name: password_hash, type: varchar }
            - { name: created_at, type: timestamp }
            - { name: updated_at, type: timestamp }
        - name: refresh_tokens
          columns:
            - { name: id, type: uuid, pk: true }
            - { name: token_hash, type: varchar }
            - { name: user_id, type: uuid, fk: users.id }
            - { name: expires_at, type: timestamp }
            - { name: revoked_at, type: timestamp, nullable: true }
    - type: redis
      usage: Rate limiting counters
      keys:
        - pattern: "rate:login:{ip}"
          ttl: 60s

dependencies:
  internal:
    depends_on:
      - module: user-module
        usage: User lookup by email
    depended_by:
      - module: rbac-module
        usage: Role check after auth
  external:
    - package: bcrypt
      usage: Password hashing
    - package: jsonwebtoken
      usage: JWT generation and validation
```

### Spec File Organization

One spec file per cohesive unit of functionality: `.wonflowoo/workspace/specs/{name}.yml`

What constitutes a "unit" depends on the project — it could be a service, a feature, a domain, a page, a package. However, specs are always **feature-grouped** (this is a framework constant decided during the bootstrap strategy design). The bootstrap pipeline's AI grouping step clusters files into feature groups, and this grouping becomes the spec organization. Projects may informally call their units "modules" or "services" — but the structure is always feature-based.

```
.wonflowoo/workspace/specs/
├── _system.yml              # System spec — holistic view (always loaded)
├── auth.yml                 # Individual specs — detailed, loaded on demand
├── user-management.yml
├── rbac.yml
├── notifications.yml
├── order-processing.yml
└── ...
```

Spec files are named by their unit (kebab-case), NOT numbered — they represent permanent entities, not time-ordered work items. Each file represents its unit's current state, updated in place as it evolves.

### Spec Size Management

If a spec file is too large, the unit it represents is probably too large (architectural signal). If splitting doesn't make sense, allow sub-spec files:

```
.wonflowoo/workspace/specs/
├── order-processing.yml
├── order-processing.returns.yml    # sub-spec for returns/refunds
├── order-processing.bulk.yml       # sub-spec for bulk processing
```

Soft guideline: ~300 lines. Not a hard limit.

### What Specs Do NOT Contain

- Exact code implementations, function signatures, variable names
- Exact SQL queries or line-by-line logic
- Test details or implementation minutiae
- Rationale or design decisions (that's in architecture docs)
- Aspirational features (that's in requirements + architecture docs)

### Spec Lifecycle

Specs are **generated from actual code** and kept in sync as the codebase evolves.

**Greenfield:**
```
Architecture → describes what we INTEND to build
  │
  ▼
Implementation → developer builds, then reports change manifest
  │
  ▼
Ongoing → after every code change, spec-updater updates the relevant spec
```

**Bootstrap:**
```
Fan-out investigators → analyze codebase areas
  │
  ▼
Synthesis agent → generates specs from all findings
  │
  ▼
Ongoing → same as above
```

**Adding features:**
```
Orchestrator reads specs → understands current state
  → Designs new feature (arch docs)
  → Developer implements + reports change manifest
  → spec-updater routes changes into the right feature specs
```

### Spec Generation

AI-assisted spec updates are a required capability. After a developer completes a task, a dedicated `spec-updater` agent (with tech-lead context) reads the developer's change manifest and affected source code, determines which specs to update, and writes the updates. This separation exists because specs are organized by feature (horizontal) while tasks are vertical slices — the developer doesn't know the spec structure.

The spec-updater reads changed code + existing specs and updates the required 4-layer feature specs plus `_system.yml` when cross-module topology changed.

### Design Decision: Specs Are Post-Implementation Only

Specs represent **what actually exists**, never what's planned:

- **No "intended vs actual" confusion** — specs are always ground truth
- **No stale aspirational specs** — if code doesn't exist, it's not in the spec
- **Clear responsibility** — architecture docs capture intent, specs capture reality
- **Dedicated spec-updater agent** — developers provide change manifests; a spec-updater with tech-lead context routes changes to the correct feature specs

### Spec Validation (Inspired by Choisor)

Specs must be validated to prevent drift. Inspired by Choisor's bidirectional validation pattern:

**Bidirectional coverage:**
- **Forward** (spec → code): Does everything in the spec actually exist in the codebase? Catches over-specification.
- **Backward** (code → spec): Does everything in the codebase exist in the spec? Catches under-specification (missed features/endpoints).

Choisor's data shows forward-only extraction missed 4.7% of endpoints. Bidirectional validation catches what one direction misses.

**Validation tiers** (from Choisor's schema validation pattern):
- **Structural**: Required fields present, YAML valid, layers complete
- **Content**: Names consistent, interface types valid, dependency references resolve to existing specs
- **Metric**: Endpoint counts match between spec and codebase, no orphaned dependencies

**When validation runs:**
- After implementation: developer reports change manifest; spec-updater performs spec updates
- Periodically: automated checks that specs still match the codebase
- On conflict: developer alignment loop catches discrepancies before they compound
- After bootstrap: human validates generated specs match reality

### Consistency Enforcement

Three layers of enforcement ensure spec quality:

1. **Schema validation**: Structural checks (required fields, valid types, layers present). Mechanical, can run in CI.
2. **Orchestrator review**: Validates spec quality as part of task acceptance criteria. Not just "did you update" but "does it reflect what you built at the required detail level."
3. **Conventions**: `conventions.yml` includes spec writing standards (logic detail level, must-capture items, min flow steps).

### Cross-Module Flows

Cross-module flows live in the **system spec** (`_system.yml`), not in individual specs. Each spec captures what its unit does internally. The system spec captures how they flow together — this is one of the key reasons the system spec exists.

The system spec's `cross_module_flows` section (see System Spec Structure above) documents every major business flow that spans multiple modules. This gives the orchestrator the ability to reason about cross-cutting changes without loading every involved module's full spec.

---

## Architecture Document Structure

Architecture docs use a combination of **structured YAML** (machine-parsable, agent-loadable) and **narrative Markdown** (human-readable, explains the WHY).

### YAML — Structured, Key-Value Data

For things that are inherently structured and benefit from machine parsing:

- **Tech stack** — language, framework, database, ORM, infra, deployment
- **Conventions** — naming patterns, folder structure, code patterns, testing patterns, spec organization
- **Dependencies** — external service integrations (Stripe, SendGrid, S3, etc.)

Note: detailed data model and API surface are NOT in architecture docs — they live in specs (L3: Data, L1: Interfaces) to avoid redundancy. Architecture docs capture HOW to design (conventions, patterns), not WHAT exists (that's the specs' job).

### Markdown — Narrative, Explanatory

For things that require context and reasoning:

- **System design rationale** — why these choices were made, what trade-offs were accepted
- **Integration approach** — how systems connect, data flow between services
- **Business context** — domain knowledge that informs technical decisions

### Diagrams — Mermaid Only (Project-Wide)

All diagrams and visual representations in **any Markdown file in the project** — not just architecture docs, but requirements, plans, system design, ADRs, READMEs, developer docs, anything — **must use Mermaid format**. No images, no external diagram tools, no ASCII art for anything that Mermaid can express.

Why Mermaid:
- **Text-based** — lives in markdown files, version-controlled, diffable
- **Agent-readable** — AI agents can read, generate, and modify diagrams
- **Renderable** — GitHub, GitLab, most markdown viewers render Mermaid natively
- **No external tools** — no Figma, Lucidchart, or draw.io dependencies

Use for: system architecture diagrams, data flow diagrams, sequence diagrams, entity-relationship diagrams, dependency graphs, state machines, workflow diagrams.

### ADRs — Separate, On-Demand Only

Architecture Decision Records live in their own `decisions/` directory and are **NOT auto-loaded into agent context**. They exist for traceability and are loaded only when a specific task requires understanding a past decision.

Why not auto-load:
- ADRs accumulate over a project's lifetime — loading all of them wastes context budget
- Most tasks don't need historical decision rationale — they need the current conventions (which are in YAML)
- When they ARE needed, the orchestrator or developer can load the specific ADR by reference

**When to load an ADR:**
- A developer's task touches a system area where a non-obvious decision was made
- A new decision might contradict or supersede a prior one
- The orchestrator needs to explain WHY something is the way it is to a developer

The orchestrator references specific ADRs in task briefs when relevant: "See `decisions/003-event-sourcing.md` for why we chose event sourcing over CRUD for this module."

### Architecture Doc Schemas (Examples)

These examples define the expected schema shape for architecture documents. Real projects fill in their own values.

**`tech-stack.yml`**

```yaml
language: TypeScript
runtime: Node.js 20
framework: Express.js
database:
  primary: PostgreSQL 15
  cache: Redis 7
  orm: Prisma 5
deployment:
  platform: AWS
  containerization: Docker
  orchestration: ECS Fargate
  ci_cd: GitHub Actions
monitoring:
  apm: Datadog
  logging: CloudWatch
  error_tracking: Sentry
```

**`conventions.yml`**

```yaml
naming:
  files: kebab-case
  classes: PascalCase
  functions: camelCase
  constants: UPPER_SNAKE_CASE
  database_tables: snake_case
  database_columns: snake_case
  api_endpoints: /api/{resource}/{action}

folder_structure:
  description: "Layered architecture: routes → middleware → controllers → services → repositories"
  src_layout:
    - routes/       # Express route definitions
    - middleware/    # Auth, validation, error handling
    - controllers/  # Request parsing, response formatting
    - services/     # Business logic
    - repositories/ # Data access
    - models/       # Prisma models
    - utils/        # Shared utilities
    - types/        # TypeScript type definitions

code_patterns:
  error_handling:
    pattern: "Custom AppError class with {error, code, message} response shape"
    http_errors: "Use AppError subclasses (NotFoundError, AuthError, ValidationError)"
  authentication:
    pattern: "JWT middleware applied globally, exclusion list for public routes"
  validation:
    pattern: "Zod schemas for request validation in middleware"
  logging:
    pattern: "Structured JSON logging via winston, correlation IDs on all requests"

testing:
  framework: vitest
  patterns:
    unit: "Co-located with source: src/services/__tests__/auth.test.ts"
    integration: "tests/integration/"
    e2e: "tests/e2e/"
  coverage_minimum: 80%

```

Note: `data-model.yml` and `api-surface.yml` are intentionally NOT included as architecture docs. Detailed data models (tables, columns, relationships) live in spec L3: Data. Detailed API surfaces (endpoints, methods, auth) live in spec L1: Interfaces. The system spec (`_system.yml`) provides the cross-cutting view via `data_ownership`, `data_relationships`, and interface summaries. Architecture docs capture conventions and rationale, not the detailed schema — that would be redundant with specs and prone to drift.

**`dependencies.yml`**

```yaml
internal:
  - from: auth
    to: user-management
    type: runtime
    description: User lookup during login

  - from: order-processing
    to: payment
    type: runtime
    description: Payment processing during checkout

  - from: order-processing
    to: notification
    type: async
    description: Order events via pubsub

  - from: api-gateway
    to: auth
    type: middleware
    description: Auth middleware on all routes

external:
  - name: Stripe API
    used_by: [payment]
    type: payment processing
    auth: API key

  - name: SendGrid API
    used_by: [notification]
    type: email delivery
    auth: API key

  - name: S3
    used_by: [file-storage]
    type: object storage
    auth: IAM role
```

**`system-design.md`** (Markdown, not YAML) should include:

- System Overview (what the system does, who uses it)
- Architecture Diagram (Mermaid)
- Component Relationships (how services/modules interact)
- Data Flow (how data moves through the system)
- Cross-Module Flows (from the system spec, but with WHY narrative — the system spec has WHAT)
- Security Architecture (auth strategy, data protection, API security)
- Infrastructure (deployment topology, scaling strategy)
- Design Rationale (why this architecture, what alternatives were considered)

### Directory Structure

The framework uses a **consistent directory structure** regardless of project size. A tiny project will have mostly empty directories or single-file contents, but the structure is the same. This means agents always know where to look — no conditional logic for "is this a small or large project?"

```
.wonflowoo/workspace/
├── architecture/                                        # Project-level (not per-requirement)
│   ├── tech-stack.yml                                   # Language, framework, DB, infra, deployment
│   ├── conventions.yml                                  # Naming, patterns, folder structure, code patterns
│   ├── dependencies.yml                                 # External service integrations (Stripe, SendGrid, S3)
│   ├── system-design.md                                 # Narrative: why, how it fits, data model design, API design
│   └── decisions/                                       # ADRs (loaded on demand, not auto-loaded)
│       ├── 001-auth-approach.md
│       └── 002-database-choice.md
├── specs/                                               # Generated from code (post-implementation)
│   ├── _system.yml                                      # System spec — holistic view (always loaded)
│   ├── auth.yml                                         # Module specs — detailed, loaded on demand
│   ├── user-management.yml
│   ├── order-processing.yml
│   └── notifications.yml
├── requirements/                                        # Discovery output
│   ├── 00001-inventory-system.md
│   └── 00002-rbac-feature.md
├── drafts/                                              # Orchestrator working memory (kept as historical record)
│   ├── 00001-inventory-system.md                        # Same {id}-{name}
│   ├── 00002-rbac-feature.md
│   └── bootstrap/                                       # Special: bootstrap investigator findings
│       ├── findings-auth.md
│       └── findings-api.md
├── plans/                                               # Planning phase output
│   ├── 00001-inventory-system.md                        # Same {id}-{name}
│   └── 00002-rbac-feature.md
├── workflow/                                            # Phase playbooks (lazy-loaded by orchestrator)
│   ├── discovery.md
│   ├── architecture.md
│   ├── planning.md
│   ├── delegation.md
│   ├── implementation.md
│   └── spec-interaction.md
├── agent-guides/                                        # Sub-agent instructions (loaded on demand)
│   ├── tech-leads.md                                    # Spec system context, what to load (tech-lead roles)
│   ├── developers.md                                    # Workflow, conventions, change manifest (developer roles)
│   └── spec-updater.md                                  # Routing logic for updating specs (spec-updater role)
└── tasks/                                               # All tasks — flat directory
    ├── 00002-inventory-system.setup-auth.yml            # Planned: {task-id}-{origin}.{task-name}.yml
    ├── 00002-inventory-system.setup-auth.plan.md        # Developer plan companion
    ├── 00003-inventory-system.user-mgmt.yml
    ├── 00003-inventory-system.user-mgmt.plan.md
    ├── 00004-inventory-system.add-roles-table.yml
    ├── 00004-inventory-system.add-roles-table.plan.md
    ├── 00005-bugfix.checkout-null.yml                   # Bugfix origin: bugfix
    ├── 00005-bugfix.checkout-null.plan.md
    ├── 00006-adhoc.update-readme.yml                    # Ad-hoc origin: adhoc
    └── 00006-adhoc.update-readme.plan.md

# Also at project root (framework level, not inside .wonflowoo/workspace/):
.claude/
├── agents/                                              # Agent definitions (Claude Code uses natively, OmO reference)
│   ├── architecture-consultant.md                       # Read-only architecture consultation
│   ├── plan-reviewer.md                                 # Plan quality review (executability, blockers)
│   ├── explorer.md                                      # Internal codebase search
│   ├── librarian.md                                     # External research (docs, OSS, GitHub)
│   ├── tech-lead.md                                     # General technical work (gap analysis, review)
│   ├── sr-dev.md                                        # Complex multi-file implementation
│   ├── jr-dev.md                                        # Straightforward established-pattern implementation
│   ├── quick-dev.md                                     # Trivial single-file/config work
│   └── frontend-dev.md                                  # Frontend implementation
└── skills/                                              # Skills (auto-discovered by both platforms)
    ├── bootstrap/SKILL.md                               # /bootstrap — 8-step pipeline
    ├── spec-generate/SKILL.md                           # /spec-generate — AI-assisted spec creation
    └── spec-validate/SKILL.md                           # /spec-validate — bidirectional validation
```

The root `AGENTS.md` and `CLAUDE.md` deliverables remain slim cores loaded every turn; current OmO `AGENTS.md` is ~8KB because it now includes Role Routing + sub-agent sections. Detailed phase procedures are still loaded from `.wonflowoo/framework/workflow/*.md` on demand.

Claude agent configs remain slim wrappers that point to shared `.wonflowoo/framework/agent-guides/` instructions, avoiding instruction duplication across platforms.

**Why consistent structure matters:**
- Agents don't need to discover the project's file layout — it's always the same
- Tooling can be built once and work everywhere
- A small project with `architecture/tech-stack.yml` containing 10 lines is fine — the file exists, it's just small
- Directories that aren't needed yet (e.g., `decisions/` on a new project) can be empty or absent — but when they appear, they're always in the same place

The framework mandates that **structured data is YAML** and **narrative reasoning is Markdown**. The directory structure is fixed; the content depth scales with the project.

### File Naming Convention

**All file and directory names use kebab-case.** No camelCase, no underscores, no spaces.

**Independent 5-digit sequences by artifact type**: requirements, drafts, plans, and tasks each maintain their own sequence (`00001`, `00002`, ...). IDs are stable within each type; cross-linking uses references (for example `plan_ref`).

| Artifact type | ID format | Example |
|---|---|---|
| Requirement (greenfield, feature, refactor, migration) | `{id}-{name}` | `00001-inventory-system` |
| Draft | `{id}-{name}` | `00001-inventory-system` |
| Plan | `{id}-{name}` | `00001-inventory-system` |
| Task | `{task-id}-{origin}.{task-name}` | `00002-inventory-system.setup-auth` |

**The ID flows through all artifacts:**

```
requirements/  00001-inventory-system.md        ← {id}-{name}.md
drafts/        00001-inventory-system.md        ← same {id}-{name}
plans/         00001-inventory-system.md        ← same {id}-{name}
tasks/         00002-inventory-system.setup-auth.yml      ← {task-id}-{origin}.{task-name}.yml
               00002-inventory-system.setup-auth.plan.md  ← same base name + .plan.md
```

**Task file naming:**

Task IDs use an independent 5-digit task sequence. The `{origin}` segment records provenance:
- plan-derived tasks: plan name (for example `inventory-system`)
- bug fixes: `bugfix`
- ad-hoc work: `adhoc`

Each task references its source plan via a `plan_ref` field (for planned work). The plan doc lists task IDs for tracking.

| Type | Pattern | Example |
|---|---|---|
| Planned task | `{task-id}-{origin}.{task-name}.yml` | `00002-inventory-system.setup-auth.yml` |
| Developer plan | `{task-id}-{origin}.{task-name}.plan.md` | `00002-inventory-system.setup-auth.plan.md` |
| Bug fix task | `{task-id}-bugfix.{task-name}.yml` | `00005-bugfix.checkout-null.yml` |
| Ad-hoc task | `{task-id}-adhoc.{task-name}.yml` | `00006-adhoc.update-readme.yml` |

**Architecture docs** — project-level, not numbered. Fixed filenames: `tech-stack.yml`, `conventions.yml`, `dependencies.yml`, `system-design.md`.

**ADRs** — sequential 3-digit numbering within `decisions/`: `001-auth-approach.md`, `002-database-choice.md`.

**Specs** — one file per unit, kebab-case: `auth.yml`, `user-management.yml`. NOT numbered — they represent permanent entities, updated in place. System spec is always `_system.yml` (underscore prefix = auto-derived, not manually maintained).

---

## Orchestrator Draft — Living Working Memory

The orchestrator maintains a **draft file** (`.wonflowoo/workspace/drafts/{id}-{name}.md`) as its working memory for each piece of work. The draft is not a deliverable — it's the orchestrator's personal notes, tracking where it is in the workflow, what's been decided, what's still open, and what it's learned.

The draft lives across the **entire orchestrator lifecycle** — from the moment work begins through Discovery, Architecture, Planning, and Delegation — until all developer plans are aligned and implementation is underway. Each phase produces its own confirmed artifact; the draft ties them together and tracks progress.

### Draft vs Confirmed Artifacts

The draft is orthogonal to the phase outputs. Each phase produces a confirmed, persistent document. The draft references them but is not the source of truth for any of them.

```
User Request
  │
  ▼
Draft created (.wonflowoo/workspace/drafts/{id}-{name}.md) — orchestrator's living memory
  │
  ├── DISCOVERY (WHAT are we building?)
  │   ├── Research, interview, back-and-forth with user
  │   ├── Draft tracks: findings, open questions, decisions, current phase status
  │   ├── Clearance passes
  │   └── → Requirements doc confirmed (.wonflowoo/workspace/requirements/{id}-{name}.md)
  │
  ├── ARCHITECTURE (HOW are we building it?)
  │   ├── Technical design: stack, data model, conventions, patterns
  │   ├── Draft tracks: arch decisions being explored, alignment status
  │   ├── User confirms approach
  │   └── → Architecture docs confirmed (.wonflowoo/workspace/architecture/*.yml + *.md)
  │
  ├── PLANNING (HOW do we orchestrate and hand off?)
  │   ├── Gap analysis, task breakdown, wave ordering, delegation targets
  │   ├── Draft tracks: task groupings, dependency analysis
  │   ├── User confirms plan
  │   └── → Plan doc confirmed (.wonflowoo/workspace/plans/{id}-{name}.md)
  │         └── → Task instruction files generated (.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.yml)
  │
  ├── DEVELOPER PLANNING (per developer)
  │   ├── Developer loads task file + arch docs + specs + code
  │   ├── Creates detailed implementation plan
  │   ├── Aligns with orchestrator
  │   └── Draft tracks: which developers assigned, alignment status, results
  │
  ▼
All developer plans aligned → Draft marked completed (status: done)
  │
  ▼
IMPLEMENTATION (developers execute, specs generated from code)
```

### What the Draft Contains

The draft is the orchestrator's scratchpad — not structured data, but working notes:

- **Workflow state**: Which phase am I in? What's confirmed, what's pending?
- **Research findings**: What did explore/librarian discover? Rejected alternatives and why.
- **Decision log**: Decisions made during the process, including ones that didn't make it into formal docs.
- **Open questions**: What's still unresolved? Who needs to answer?
- **References**: Pointers to confirmed artifacts created along the way (requirements doc, arch docs, plan doc, task files).
- **Case classification**: What kind of work this is, which clearance criteria apply.

### What the Draft is NOT

- **Not the requirements doc** — requirements get their own confirmed document in `.wonflowoo/workspace/requirements/`
- **Not the architecture docs** — architecture decisions go to `.wonflowoo/workspace/architecture/` (persistent, project-level)
- **Not the plan** — the plan is a separate structured document in `.wonflowoo/workspace/plans/`
- **Not ephemeral** — drafts are kept after completion as historical record (research findings, rejected alternatives, decision rationale are valuable for future reference)

### Draft Lifecycle

| Status | Meaning |
|---|---|
| **active** | Orchestrator is working through phases for this work item |
| **done** | All developer plans aligned, implementation underway. Draft preserved for historical reference. |

Drafts are never deleted. An active draft means the orchestrator has work in progress. A completed draft is a historical record of the decision-making process.

### Re-Entry via Document State

The draft solves the re-entry problem. When the orchestrator starts a new session, it checks:

| State | What it means | Action |
|---|---|---|
| Active draft exists | Work in progress | Read draft → resume from tracked phase/status |
| Active plan exists (no active draft) | Mid-implementation | Continue monitoring execution via task status |
| Neither | Idle | Wait for user input |

The draft tells the orchestrator exactly where it left off — which phase, what's confirmed, what's still open. No need to re-interview or re-research.

### Mixed Cases

When a user request spans multiple cases ("Add RBAC and refactor the auth module"), the orchestrator:

1. Recognizes multiple concerns in the request
2. Creates **separate drafts** for each: `.wonflowoo/workspace/drafts/00002-rbac-feature.md` and `.wonflowoo/workspace/drafts/00003-auth-refactor.md`
3. Each follows its own lifecycle independently
4. They may share dependency ordering (e.g., refactor auth first, then add RBAC on top of the cleaner structure)

Separate drafts ensure clean separation of concerns. Each work item has its own case classification, clearance criteria, and confirmed artifacts.

---

## Research Capabilities

The framework assumes the AI system has two categories of research tools. These aren't optional — they're required for the orchestrator to make informed decisions across every phase.

### Internal Search (Explore)

Search the **project's own codebase** — find patterns, understand structure, discover how things are currently implemented.

**Used by:**
- **Bootstrap** — investigators analyze codebase areas during fan-out phase
- **Developers** — read actual code to inform their implementation plans
- **Spec validation** — verify specs still match the codebase

**NOT used by the orchestrator on specced projects.** The orchestrator relies on specs + architecture docs for its understanding. If the orchestrator needs to search the codebase, the specs are incomplete — fix the specs, don't work around them.

**Examples:** "Find all auth middleware in this project." "How are API errors currently formatted?" "Which modules depend on the user service?"

### External Search (Librarian)

Search **outside the project** — official documentation, open-source implementations, best practices, community patterns.

**Used by:**
- **Orchestrator (Discovery, greenfield)** — research similar systems, tech landscape, proven patterns
- **Orchestrator (Architecture)** — find best practices for proposed tech stack choices, verify patterns against official docs
- **Developers (Implementation)** — API docs, library usage examples, framework conventions
- **Bootstrap (investigator)** — research unfamiliar tech in the stack

**Examples:** "What's the recommended way to handle refresh tokens in NextAuth?" "Find production examples of event-driven architecture with Kafka." "What does the Prisma docs say about cascading deletes?"

### Why This Matters

Without external search, the orchestrator proposes architecture based on training data that may be outdated — not current docs, not current best practices, not how the library actually works in its latest version.

Internal search is critical for bootstrap and developer work, but the orchestrator should NOT need it on projects with healthy specs. If the orchestrator is routinely searching the codebase, it's a signal that spec quality needs improvement.

---

# Part 5: Supporting Systems

## Category → Model Routing

The framework defines standard task categories for routing. Projects map these categories to AI models in project configuration.

| Category | Description |
|---|---|
| backend | Server-side logic, APIs, database, business rules |
| frontend | UI components, pages, state management, styling |
| visual-engineering | Design-heavy UI work, animations, complex layouts |
| infrastructure | CI/CD, deployment, monitoring, cloud config |
| data | Database migrations, data pipelines, ETL |
| testing | Test creation, test strategy, test infrastructure |
| documentation | Docs, READMEs, API docs, spec writing |
| planning | Developer implementation planning (pre-coding analysis) |

Category-to-model routing is **platform-native** — each AI platform (OmO, Claude Code) handles model selection through its own configuration mechanism. The framework does NOT store category routing in `.wonflowoo/workspace/config.yml` because:

1. Model names and capabilities differ between platforms
2. Platform-level configuration already handles this (OmO categories, Claude Code agent definitions)
3. Keeping routing in `.wonflowoo/workspace/config.yml` would create platform-specific config in a platform-agnostic file

The framework defines WHAT categories exist. The platform defines WHICH models handle them.

---

## Draft File Template

```markdown
# Draft: {id}-{name}
Status: active | done
Phase: discovery | architecture | planning | delegation
Case: greenfield | add-feature | bootstrap | bugfix | refactoring | migration
Created: {date}
Updated: {date}

---

## Documentation Layers

Three layers, each serving a different audience:

| Layer | What | Format | Who reads it |
|---|---|---|---|
| Universal Playbook (AGENTS.md) | Workflow rules, escalation, mandatory behaviors | Markdown | Every agent, every session |
| Architecture Docs | Tech stack, conventions, data model, system design, ADRs | YAML (structured) + MD (narrative) | Orchestrator + developers |
| Codebase Specs | 4-layer compressed representation of actual code (Interfaces, Logic, Data, Dependencies) | YAML (structured) | Primarily orchestrator |

Supporting artifacts:
- **Orchestrator Draft** — Markdown, living working memory across all phases (`.wonflowoo/workspace/drafts/`). Kept as historical record.
- **Requirements** (from Discovery) — Markdown, confirmed scope and features (`.wonflowoo/workspace/requirements/`)
- **Orchestrator Plans** (from Planning) — Markdown, task waves, briefs, ordering (`.wonflowoo/workspace/plans/`)
- **Task Instruction Files** (from Delegation) — YAML, self-contained technical user stories (`.wonflowoo/workspace/tasks/`)
- **Developer Plans** (from Developer Planning) — Markdown, persisted alongside task files (`.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.plan.md`)

---

## Execution Principles

These principles govern how work is executed across all phases. Each is detailed in the relevant phase section.

- **Feature-level task granularity** — tasks scoped at the feature level (not individual files, not entire modules). The right unit for parallel execution. See Planning Step 3.
- **Dependency-ordered execution** — foundation first, then core, then independent features (parallel), then supporting. Within a layer: parallelize. Across layers: sequential. See Planning Step 2 (wave structures per case).
- **Quality gates block, not advise** — every phase has clearance criteria that must pass before proceeding. Inspired by AIND's Phase Gates: 5% quality miss in early phases → 35% total rework downstream. See each phase's clearance checklist.
- **Mini-pilot before batch** — for large or migration work, validate approach on 2-3 representative items before scaling out. See Planning (Case 6 migration wave structure).

---

## Testing Strategy

Testing is embedded in the framework, not a separate concern:

- **Task acceptance criteria** include test expectations ("unit tests for all service methods", "integration test for the login flow")
- **Quality gates** require tests to pass ("all existing tests pass" is a clearance check)
- **Specs do NOT track test coverage** — that's a code-level concern, not an orchestrator-level concern
- **Test conventions** live in `conventions.yml` (test framework, file patterns, coverage minimums)

The framework says "tests must exist and pass." HOW to test is defined by the project's conventions.

---

## Wisdom Accumulation

After implementation, the orchestrator reviews developer output for learnings:

- Did the developer discover a pattern that should become a convention? → Update `conventions.yml`
- Did a non-obvious decision get made during implementation? → Create ADR in `decisions/`
- Did the spec validation reveal a gap in the spec format? → Update spec conventions
- Did the architecture not match reality? → Update architecture docs

The orchestrator reviews learnings as part of task completion validation. Developers report learnings in their completion report. The orchestrator decides what to promote to project-level docs.

This creates a feedback loop: Implementation → Learnings → Updated conventions/arch docs → Better future plans → Better implementation.

---

## Human Roles

Three human touchpoints in the framework:

| Role | When | What they do |
|---|---|---|
| **Stakeholder** | Discovery | Provides requirements, confirms scope, answers domain questions |
| **Technical Authority** | Architecture, Planning | Approves technical approach, reviews plans, resolves ambiguities |
| **Reviewer** | Implementation completion | Validates final output, approves for deployment |

In small teams, these may all be the same person. In large organizations, they may be different people (PM, Staff Engineer, QA Lead). The framework doesn't prescribe org structure — it prescribes the touchpoints.

The human is NOT involved in every step. AI leads, human validates at phase gates. This matches Choisor's "AI leads, human validates" principle.

---

## Tooling Requirements

The framework assumes minimal infrastructure:

**Required:**
- **Git** — version control for all `.wonflowoo/workspace/` artifacts. Specs, arch docs, task files, plans, drafts are all committed.
- **AI agent system** — with explore (internal search) + librarian (external search) capabilities. Must support parallel agent execution.
- **File system** — read/write access to `.wonflowoo/workspace/` directory.

**Optional (project-level):**
- CI/CD integration for spec validation
- YAML linter for spec/arch doc validation
- Mermaid renderer for diagram previews

The framework does not require specific IDE, CI/CD platform, hosting, or cloud provider.

---

## Framework Adoption

Two adoption paths:

**Path A — Greenfield (new project):**
1. Create `.wonflowoo/` directory with `framework/` + `workspace/`
2. Start at Discovery (Phase 1)
3. Architecture docs created during Architecture phase
4. Specs generated after first implementation
5. All subsequent work follows the standard lifecycle

**Path B — Existing Codebase:**
1. Run Bootstrap process (Case 3) — fan-out/fan-in analysis
2. Bootstrap generates: architecture docs + specs from existing code
3. Human reviews and corrects
4. `.wonflowoo/` directory is now populated
5. All subsequent work follows Case 2 (existing project with specs)

Day 1 is either `mkdir -p .wonflowoo/framework .wonflowoo/workspace` (greenfield) or "run bootstrap" (existing).

---

## Multi-Repo Specs

Each repository has its own `.wonflowoo/` directory. Cross-repo dependencies are captured as external references in the system spec:

```yaml
# In _system.yml
external_dependencies:
  - repo: payment-service
    specs: [payment, billing]
    interface: REST API
    contract: openapi/payment-api.yml

  - repo: shared-library
    specs: [auth-utils, validation]
    interface: npm package
    version: "^2.0"
```

Each repo is self-contained. No shared `.wonflowoo/` across repos. Cross-repo contracts are tracked but not managed by the framework — they're API contracts maintained by each repo's team.

---

## Versioning

All `.wonflowoo/workspace/` artifacts are version-controlled in Git alongside the code they describe. Git history IS the version history — no separate versioning scheme.

The system spec includes a format version:

```yaml
# _system.yml
framework_version: "1.0"  # spec format version
```

When the framework's spec format evolves (e.g., new required fields, changed structure), it's handled like any other migration:

1. Update `.wonflowoo/workspace/` artifacts to the new format
2. Commit the changes
3. The `framework_version` field indicates which format version the specs follow

---

# Part 6: Reference

## Phase Deliverables Summary

| Phase | Deliverable | Format | Location | Purpose |
|---|---|---|---|---|
| **All phases** | Orchestrator draft | Markdown | `.wonflowoo/workspace/drafts/` | Living working memory — tracks workflow state, research, decisions. Kept as historical record. |
| **Discovery** | Requirements document | Markdown | `.wonflowoo/workspace/requirements/` | Confirmed scope, features, constraints, acceptance criteria |
| **Architecture** | Tech stack, conventions, dependencies | YAML | `.wonflowoo/workspace/architecture/` | Structured, machine-parsable design decisions and conventions |
| **Architecture** | System design, ADRs | Markdown | `.wonflowoo/workspace/architecture/` | Narrative rationale, trade-offs, context |
| **Planning** | Orchestrator plan | Markdown | `.wonflowoo/workspace/plans/` | Task waves, ordering, high-level briefs, delegation targets |
| **Delegation** | Task instruction files | YAML | `.wonflowoo/workspace/tasks/` | Self-contained technical user stories — context, brief, references, guardrails, acceptance criteria |
| **Developer Planning** | Developer plan | Markdown | `.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.plan.md` | Detailed implementation approach, persisted alongside task file |
| **Implementation** | Code | Source files | project source | The actual deliverable |
| **Implementation** | Specs | YAML | `.wonflowoo/workspace/specs/{name}.yml` | Detailed 4-layer ground-truth per unit |
| **Implementation** | System spec | YAML | `.wonflowoo/workspace/specs/_system.yml` | Auto-derived holistic view — module registry, dependencies, data ownership, cross-module flows |

Each phase produces a confirmed artifact that feeds the next. The orchestrator draft ties them all together as working memory. Architecture docs persist across the project lifetime. Specs evolve with the code. Drafts are kept as historical record.

---

## Design Principles

- **Scales with project shape** — same framework whether it's 1 repo or 100, 1 person or 30+
- **Consistent structure** — same directory layout regardless of project size; content depth scales, structure doesn't
- **Specs are ground truth** — generated from actual code, never aspirational
- **Architecture docs capture intent** — why decisions were made, what conventions to follow
- **Two-level planning** — orchestrator plans WHAT/WHEN/WHO, developer plans HOW
- **Task files as contracts** — delegation through persistent, reviewable, reusable instruction files
- **Research before asking** — investigate internal codebase and external landscape before interviewing the user
- **Intent preservation** — WHY decisions were made survives across sessions and handoffs
- **Each phase produces confirmed artifacts** — Discovery → requirements, Architecture → arch docs, Planning → plan, Implementation → specs. Draft ties them together.
- **Draft as living memory** — orchestrator's working memory persists across all phases and sessions, never deleted
- **Living documentation** — specs and docs are updated after changes, validated to prevent staleness
- **Bidirectional alignment** — developers present their plans to the lead before implementing
- **Quality gates block, not advise** — progression requires passing defined criteria
- **Mini-pilot before scale** — validate approach on a small sample before batch execution
- **YAML for structure, Markdown for narrative, Mermaid for diagrams** — structured data is machine-parsable, reasoning is human-readable, diagrams are text-based and version-controlled
- **Ceremony scales with complexity** — same phases, different depth
- **Context budget awareness** — load only what's needed (ADRs on demand, specs by relevance, not everything always)

---

## Resolved Decisions

- **Specs are post-implementation only** — represent actual code, never aspirational. Architecture docs handle the "intended state" during planning.
- **4-layer spec model** — L1: Interfaces (generic I/O — REST, gRPC, pubsub, WebSocket, scheduler, file I/O, etc.), L2: Logic (services, behaviors, rules), L3: Data (storage — DB, cache, files, or stateless), L4: Dependencies (internal + external). Language-agnostic, application-type-agnostic.
- **Two-tier spec architecture** — system spec (`_system.yml`, always loaded, holistic view) + individual specs (`{name}.yml`, loaded on demand, full 4-layer detail). Prevents context window overflow for large systems. System spec is auto-derived from individual specs.
- **One spec file per unit** — `.wonflowoo/workspace/specs/{name}.yml`. Named by unit (kebab-case), NOT numbered. Updated in place as it evolves. What constitutes a "unit" (service, feature, domain, etc.) is defined per-project in conventions.yml.
- **Specs use `name:` not `module:`** — the spec doesn't assert what kind of organizational unit it represents. That's a project-level concern. The spec just identifies itself by name.
- **Generic interface types** — framework doesn't prescribe what I/O types exist. Each interface has `type` + `direction` + type-specific details. Covers any communication pattern.
- **Bidirectional spec validation** — forward (spec→code) + backward (code→spec) coverage. Inspired by Choisor, where forward-only missed 4.7%. Three validation tiers: structural, content, metric.
- **Two-level planning** — orchestrator plan (WHAT/WHEN/WHO) + developer plan (HOW, created in fresh session from arch docs + specs + code)
- **Architecture docs: YAML + Markdown** — structured data (tech stack, conventions, data model) in YAML; narrative reasoning (system design) in Markdown
- **ADRs: separate, not auto-loaded** — stored in `decisions/` directory, loaded on demand when a specific task requires understanding a past decision. Not bundled into context by default.
- **Task instruction files are self-contained technical user stories** — enough context, detail, and references that a developer can pick one up cold and work independently. Includes `context` (why, how it fits), `brief` (what + enough implementation detail), `must_do`/`must_not_do`, `acceptance_criteria`, and all doc references. Like a well-written Jira ticket.
- **Developer plans are persisted** — written as `.plan.md` companion files alongside task files. Useful for debugging, knowledge transfer, audit, and re-dispatch.
- **Ceremony scales with complexity** — trivial (skip) → simple (lightweight) → medium (standard) → large (full) → enterprise (full + specialists + review loops)
- **Discovery → Architecture → Planning → Delegation → Implementation** — five distinct phases with quality gates between each. Discovery only applies to Cases 1-2 (greenfield, add feature). Other cases have their own entry points.
- **Research before asking** — orchestrator investigates landscape before interviewing the user. For existing projects, loads specs + arch docs (NOT codebase). For greenfield, researches similar systems externally.
- **Orchestrator does not search codebase on existing projects** — specs should provide sufficient understanding. If they don't, the specs are incomplete — fix the specs, don't work around them with codebase search.
- **Research capabilities required** — framework specifies two tool categories: internal search (explore, for bootstrap/codebase analysis) and external search (librarian, for docs/OSS/web). Explore is used during bootstrap and by developers, NOT by the orchestrator on specced projects.
- **Mermaid for all diagrams** — any diagram in any Markdown file project-wide must use Mermaid format. No images, no external tools, no ASCII art for anything Mermaid can express. Text-based, diffable, agent-readable.
- **Gap classification** — critical (ask user) / minor (self-resolve) / ambiguous (apply default, disclose)
- **Parallel execution waves** — tasks grouped by dependency layer, maximizing throughput
- **Developer alignment loop is mandatory** — developer creates detailed implementation plan, presents to orchestrator before writing any code. Catches spec drift, ambiguous instructions, architecture conflicts. Bidirectional quality check.
- **Orchestrator owns task status** — only the orchestrator updates task file status. Developers report back, orchestrator validates against acceptance criteria before marking done.
- **Failure handling: re-dispatch or escalate** — developer-level failures → re-dispatch same task file. Plan-level failures → go back to Planning phase.
- **Consistent directory structure** — same `.wonflowoo/workspace/` structure regardless of project size. No small/large variants. Content depth scales, structure doesn't.
- **Files live in `.wonflowoo/`** — framework files in `.wonflowoo/framework/`, project artifacts in `.wonflowoo/workspace/`
- **Independent 5-digit sequences per type** — requirements, drafts, plans, tasks each start at `00001` and increment independently.
- **Task files are self-contained technical user stories** — `context` field includes relevant architecture detail inline (tech stack, conventions, data model excerpts). Developer can understand the task without loading every referenced doc separately.
- **Flat tasks directory** — no wave subdirectories. Wave is metadata in the task file. Execution order managed by plan doc + depends_on/blocks fields.
- **Discovery only for Cases 1-2** — Discovery captures WHAT we're building (requirements). Only greenfield and add-feature cases have new requirements. Bug fix, refactoring, migration skip Discovery. Bootstrap is a separate process.
- **Bootstrap uses fan-out / fan-in** — parallel investigator agents analyze specific codebase areas → findings files → synthesis agent (1M context) combines into specs + arch docs. Scales from small (one agent) to massive (dozens of investigators).
- **Discovery clearance checklist** — single checklist with core items (both cases) + case-specific additions (greenfield vs add-feature).
- **Orchestrator draft = living working memory** — draft (`.wonflowoo/workspace/drafts/`) is the orchestrator's personal notes across ALL phases. Not a deliverable. Tracks workflow state, research findings, decision log, references to confirmed artifacts. Marked done (not deleted) when developer plans are aligned — kept as historical record.
- **Each phase produces its own confirmed artifact** — Discovery → requirements doc (`.wonflowoo/workspace/requirements/`). Architecture → arch docs (`.wonflowoo/workspace/architecture/`). Planning → plan doc (`.wonflowoo/workspace/plans/`). Delegation → task files (`.wonflowoo/workspace/tasks/`). The draft references them but is not the source of truth.
- **Mixed cases = separate drafts** — when a request spans multiple cases (e.g., "add feature + refactor"), the orchestrator creates separate drafts, each following its own lifecycle independently.
- **Six defined cases** — greenfield, add features, bootstrap from existing codebase, bug fix, refactoring, migration. Each has a high-level flow and case-specific Discovery behavior.
- **Architecture doc schemas are defined** — `tech-stack.yml`, `conventions.yml`, and `dependencies.yml` field structures are explicitly specified in this document as schema examples. `data-model.yml` and `api-surface.yml` were removed — their content is redundant with specs (L3: Data, L1: Interfaces) and system spec (data_ownership, data_relationships). Architecture docs capture conventions and rationale, not detailed schemas.
- **Category routing is platform-native** — framework defines standard task categories; each AI platform (OmO, Claude Code) handles category-to-model routing through its own native configuration. Category routing is NOT stored in `.wonflowoo/workspace/config.yml` because model names and capabilities differ between platforms.
- **Draft template is lightweight and free-form** — draft files use a standard header + section template, but phase notes/research/decisions remain narrative rather than rigid schema.
- **Wisdom accumulation is orchestrator-owned** — post-implementation learnings are reviewed during completion validation and promoted to conventions/ADRs/architecture docs when broadly reusable.
- **Multi-repo model is repo-local** — each repository has its own `.wonflowoo/`; cross-repo interactions are tracked as external dependencies/contracts in `_system.yml`.
- **One orchestrator per repo for v1** — multi-orchestrator coordination is explicitly deferred as a future scaling concern.
- **Spec validation boundary is defined** — framework specifies when validation must happen (post-implementation, periodic checks, conflict/alignment points); projects choose implementation mechanics/tooling.
- **Testing is embedded, not separate** — tests are enforced through acceptance criteria and quality gates; test implementation details live in project conventions.
- **Human touchpoints are explicit** — stakeholder, technical authority, and reviewer are the three required validation roles (which may be the same person in small teams).
- **Main Tech Lead + Spawned Tech Leads model** — main tech lead is persistent, talks to human, captures everything into draft. Spawned tech leads load the same files (arch docs + specs + draft) for non-trivial work with fresh context. Same understanding, no conversation baggage. Context hygiene for AI agents.
- **Tooling baseline is minimal** — required: Git + AI agent system (explore/librarian + parallelism) + filesystem access; platform specifics are optional.
- **Adoption has two paths** — greenfield starts by creating `.wonflowoo/workspace/`; existing codebases start with bootstrap fan-out/fan-in.
- **Versioning uses Git + framework version field** — artifact history comes from Git commits; `_system.yml` carries `framework_version` for spec-format compatibility.
- **auto_proceed toggle** — `.wonflowoo/workspace/config.yml` has `auto_proceed: false` (default). When false, agent STOPS at every phase gate for human review. When true, logs summary to draft and proceeds automatically. For experienced users or automated pipelines.
- **Task naming includes origin** — task files use `{task-id}-{origin}.{task-name}` (for example `00002-inventory-system.setup-auth.yml`, `00005-bugfix.checkout-null.yml`, `00006-adhoc.update-readme.yml`). Tasks reference plans via `plan_ref` where applicable.
- **Requirements and plan docs have status fields** — requirements: `pending_approval → approved → amended`. Plan: `pending_approval → approved → in_progress → completed`. Status updated at phase gates when human confirms.
- **Sub-agents cannot spawn other sub-agents** — confirmed limitation on both OmO and Claude Code. All spawning goes through the main tech lead (flat hierarchy). Developer → tech lead review coordination happens via files (.plan.md), not nested spawning.
- **Specs are always feature-grouped** — framework constant decided during bootstrap strategy design. The bootstrap pipeline's AI grouping step clusters files into features. `spec_organization` removed from config.yml — not configurable.
- **Agent definitions in `.claude/agents/`** — Claude Code uses slim wrapper agent files (architecture-consultant, plan-reviewer, explorer, librarian, tech-lead, sr-dev, jr-dev, quick-dev, frontend-dev) that reference shared `.wonflowoo/framework/agent-guides/` instructions. OmO uses built-in specialists (`oracle`, `momus`, `librarian`, `explore`) plus `task(subagent_type="sisyphus")` for architect/gap-analyst/spec-updater tech-lead reasoning work.
- **dependencies.yml is external services only** — captures Shopify API, QuickBooks, SendGrid, S3 etc. NOT npm/pip packages. Skip the file entirely if no external service integrations.

---

## Open Questions

All design questions have been resolved for v1. Future considerations:

- Multi-orchestrator coordination (enterprise scaling concern, out of scope for v1)
- Framework plugin/extension system (custom categories, custom spec layers, custom validation rules)
- Spec format migration tooling (automated upgrade when `framework_version` changes)
- Metrics and observability (tracking spec coverage, plan accuracy, developer velocity over time)

---

*This document evolves. Sections will be added, rewritten, and reorganized as the framework takes shape.*
