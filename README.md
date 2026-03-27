# WonfloWoo (One Flow) — Summary

A universal AI-aided development workflow framework. One flow, any project shape.

---

## The Problem

AI coding agents today have no standard way to understand and operate within a project. Every project reinvents its own onboarding — or has none, leaving agents to guess. The result: agents lose context between sessions, make conflicting decisions, and can't scale beyond single-file changes.

## The Solution

WonfloWoo defines a **universal specification** so an AI agent can drop into *any* project and know how to navigate, contribute, and follow the right conventions. It works across:

- **Any scale**: solo projects to enterprise (100+ repos)
- **Any structure**: monorepo, multi-repo, single repo
- **Any maturity**: greenfield to legacy brownfield
- **Any platform**: OmO (OpenCode), Claude Code, adaptable to others

## How It Works

### The Spec System — AI's Mental Model of Your Code

Instead of reading every source file (impossible at scale), agents work from **specs** — structured YAML files that capture what the code does:

```
.wonflowoo/workspace/specs/
├── _system.yml          # System-level view (modules, dependencies, data flows)
├── auth.yml             # Feature spec: interfaces, logic, data, dependencies
├── order-processing.yml
└── user-management.yml
```

**Two tiers:**
- `_system.yml` — always loaded, gives the big picture (module map, cross-module flows)
- Feature specs — loaded on demand, give detailed 4-layer views (interfaces, logic, data, dependencies)

This is the **compression layer**: 1.7MB of source code becomes 233KB of specs. An agent loading specs gets equivalent understanding at 7:1 compression. Specs are updated after every implementation task, so they always reflect reality.

### Three Roles, One Orchestrator

| Role | What it does |
|---|---|
| **Main Tech Lead** | Persistent orchestrator. Talks to human. Delegates all work. Never writes code. |
| **Spawned Tech Lead** | Fresh agent for specific jobs: architecture design, gap analysis, plan review, spec updates. Has the macro view. |
| **Developer** | Fresh agent per task. Reads task file, writes plan, implements code, reports changes. |

The main tech lead coordinates everything through **files** (task files, plans, specs), not conversation. When the platform compacts conversation history, nothing is lost — all state lives on disk.

### Six Cases, One Flow

| Case | Entry Point | What Happens |
|---|---|---|
| **Greenfield** | No codebase | Discovery → Architecture → Planning → Delegation → Implementation |
| **Add Feature** | Existing project | Same phases, but loads existing specs and architecture |
| **Bootstrap** | Existing code, no specs | 8-step pipeline: scan → analyze → group → generate specs |
| **Bug Fix** | Something broken | Diagnose → Fix (skip Discovery + Planning) |
| **Refactoring** | Code quality | Assessment → Architecture → Plan → Execute |
| **Migration** | Tech A → Tech B | Extraction → Architecture → Plan → Execute |

Every case flows through the same phase system. Ceremony scales with complexity — a trivial fix skips everything; an enterprise feature gets full specialist review.

### Phase Gates — Human in the Loop

After every major phase, the agent **stops and presents a summary**. The human reviews, adjusts, and approves before the agent continues. This prevents runaway AI decisions.

```
Discovery → [STOP: "Here's what I understood. Correct?"]
    → Architecture → [STOP: "Here's the design. Approve?"]
        → Planning → [STOP: "Here's the task breakdown. Approve?"]
            → Delegation → Implementation → [DONE]
```

### Three-Step Protocol — No Coding Without a Plan

Every implementation task goes through exactly three dispatches:

1. **Developer writes a plan** (.plan.md) → STOPS
2. **Tech lead reviews the plan** for holistic alignment → APPROVES or REJECTS
3. **Developer implements** the approved plan → reports changes

This catches spec drift, architecture conflicts, and missing context **before** code is written.

### Spec-Updater — Keeping the Model Current

Developers don't update specs — they provide **change manifests** (what files changed, what endpoints were added, what data was touched). A dedicated **spec-updater** agent with the macro view then routes changes to the correct feature specs and updates `_system.yml`.

Why? Specs are organized by **feature** (horizontal). Tasks are **vertical slices** that cut across features. The developer doesn't know the spec structure. The spec-updater does.

### Bootstrap — Adopting on Existing Codebases

For existing projects with no specs, the bootstrap pipeline generates the entire spec system from source code:

1. **Scan** — identify files, tech stack, modules
2. **Fan-out** — parallel per-file analysis (one agent per batch)
3. **Compress** — extract compact metadata per file
4. **Group** — cluster files into features using naming, imports, data patterns
5. **Generate** — create feature specs from grouped analyses
6. **System spec** — build `_system.yml` incrementally
7. **Validate** — check completeness and consistency
8. **Human review** — confirm groupings match team mental model

The pipeline scales to 500+ file projects by writing intermediate results to disk (never accumulating raw data in the orchestrator's context).

## Directory Structure

```
project-root/
├── AGENTS.md / CLAUDE.md           # Platform manual (auto-loaded)
├── .claude/                        # Claude Code platform (agents, skills)
├── .opencode/                      # OmO platform (plugin config)
└── .wonflowoo/
    ├── framework/                  # Copied once during adoption
    │   ├── workflow/               #   Phase playbooks
    │   ├── agent-guides/           #   Sub-agent instructions
    │   └── schemas/                #   Reference YAML schemas
    └── workspace/                  # Generated during work
        ├── specs/                  #   Implementation reality (_system.yml + features)
        ├── architecture/           #   Design intent (tech stack, conventions, ADRs)
        ├── requirements/           #   Confirmed requirements
        ├── drafts/                 #   Orchestrator's persistent memory
        ├── plans/                  #   Task breakdowns
        └── tasks/                  #   Task files + developer plans
```

**Framework files** are copied once and rarely change. **Workspace files** are generated and updated continuously as work progresses.

## Why This Design

### Specs as Compression Layer
An orchestrator can't load a 500-file codebase into context. But it can load `_system.yml` (500 lines) and understand the entire system. Zoom into one feature? Load that spec (~200 lines) instead of reading 30 source files. 7:1 compression, always current.

### Files as Memory, Not Conversation
AI agents lose context when sessions end or compact. WonfloWoo puts all state in files — drafts, plans, task files, specs. The conversation is ephemeral; the files are permanent. Re-entry logic reads the draft and picks up where it left off.

### Separate Concerns by Role
The orchestrator never writes code. Developers never update specs. Tech leads never manage workflows. Each role has exactly the context it needs — no more, no less. This keeps sub-agent context lean (under 65K tokens observed in testing).

### Platform-Agnostic Core
Workflow docs, agent-guides, specs, and architecture docs are all platform-agnostic. Only `AGENTS.md` (OmO) and `CLAUDE.md` (Claude Code) contain platform-specific dispatch syntax. Adding a new platform means writing one new manual — everything else is reused.

---

*For the complete specification: see [CONCEPT.md](CONCEPT.md). For implementation details: see [TECHNICAL.md](TECHNICAL.md).*
