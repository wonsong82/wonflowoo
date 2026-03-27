# Phase 4: Delegation + Developer Planning

## Goal

Dispatch planned tasks to developers and ensure alignment before any code is written.

This phase includes: per-wave task file generation, developer planning, review/alignment, and implementation dispatch.

## Core Constraints

- Only YOU (main tech lead) can spawn agents.
- Sub-agents cannot spawn sub-agents.
- Coordinate through files (`.wonflowoo/workspace/plans/`, `.wonflowoo/workspace/tasks/*.yml`, `.wonflowoo/workspace/tasks/*.plan.md`) — not agent-to-agent chat.
- Every task follows the three-step protocol: **Plan → Review → Implement**.
- These are separate dispatches. NEVER combine plan+implement.

## Dispatch Routing Reference

| Work type | Role to spawn | Why |
|---|---|---|
| Architecture consultation | `architecture-consultant` | Read-only architecture analysis, trade-offs, scaling |
| Gap analysis (pre-planning) | `gap-analyst` | Requirements/architecture gap detection |
| Plan quality review | `plan-reviewer` | Executability checks, contradictions, missing refs; approval-biased (80% clear = pass), max 3 blocking issues |
| Developer `.plan.md` review | `plan-reviewer` | Same checks for developer plan vs task file |
| External research | `librarian` | Docs/OSS best practices |
| Internal codebase search | `explorer` | Fast internal codebase search |
| Complex multi-file implementation | `sr-dev` | Autonomous implementation for non-trivial complexity |
| Simple established-pattern implementation | `jr-dev` | Lower-cost implementation for straightforward tasks |
| Quick trivial work | `quick-dev` | Trivial single-file/config tweaks |
| Frontend implementation | `frontend-dev` | UI/UX implementation |

Why spawn: context hygiene. Fresh spawned sessions spend context budget on work, not old conversation history.

What to pass in prompts: draft path, required docs/specs to load, exact deliverable, required report-back format.

---

## Two-Level Planning Model

- **Orchestrator plan (`.wonflowoo/workspace/plans/`)** = WHAT + ORDER (high-level task briefs).
- **Task instruction files (`.wonflowoo/workspace/tasks/*.yml`)** = self-contained technical user stories for execution.
- **Developer plan (`.wonflowoo/workspace/tasks/*.plan.md`)** = HOW for a specific codebase state.

The plan doc remains high-level. Detailed task files are generated per-wave with current specs loaded.

---

## Per-Wave Execution Pattern (Parallel by Default)

For each wave with N tasks, use this pattern:

1. **Task-file generation dispatch (PARALLEL):** Spawn **N tech leads simultaneously** to expand N high-level task briefs into N full `.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.yml` files.
2. **Developer planning dispatch (PARALLEL):** Spawn **N developers simultaneously** (one per task) to write `.plan.md` only.
3. **Plan review dispatch (PARALLEL):** Spawn **N reviewers simultaneously** (or review directly for simple items) to evaluate each `.plan.md`.
4. **Implementation dispatch (PARALLEL):** Spawn **N developers simultaneously** for implementation, reusing prior developer session/context when the platform supports continuation.

After each stage, WAIT for all N results before advancing to the next stage.

---

## Step 1 — Generate task instruction files (Per-Wave)

Each task gets a 5-digit sequential ID within the task sequence (starting from 00001, independent of requirement/plan IDs). The plan doc tracks all task IDs.

One file per task:
`.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.yml`

Where origin = plan name for plan-based tasks, `bugfix` for bug fixes, `adhoc` for ad-hoc tasks.

Task files are self-contained technical user stories:

```yaml
task: ...
wave: ...
status: pending
plan_ref: "00001-inventory-system"
category: backend | visual-engineering | ...
context: |
  WHY this task exists. Architecture detail inline — tech stack excerpt,
  conventions to follow, data model excerpts, error shapes. The developer
  should be able to work from this file alone.
brief: |
  WHAT to build. Specific enough to guide implementation.
architecture_refs: [...]
spec_refs: [...]
adr_refs: [...]
must_do: [...]
must_not_do: [...]
acceptance_criteria: [...]
depends_on: [...]
blocks: [...]
```

When generating files, spawned tech leads must load current architecture docs and current specs.

---

## Step 2 — Dispatch developer for PLANNING ONLY

For each task in the wave, dispatch one developer. They MUST NOT implement yet.

Spawn the developer role that matches task complexity/category (`sr-dev`, `jr-dev`, `quick-dev`, or `frontend-dev`) with:
- Load: `.wonflowoo/workspace/tasks/{task-file-name}.yml` + all referenced architecture docs/specs/ADRs + existing code to modify
- Goal: Write implementation plan only
- Output: `.wonflowoo/workspace/tasks/{task-file-name without .yml}.plan.md` including files to create/modify, approach, operation order, edge cases, and acceptance-criteria coverage mapping
- Stop condition: STOP after writing the plan and reporting it back. DO NOT implement yet.

---

## Step 3 — Review developer plans (MANDATORY)

Review each `.plan.md` before any coding starts.

Review can be done by you (simple tasks) or by spawned tech lead reviewers (recommended for medium+ or risky tasks).

Reviewer check is **holistic alignment**, not syntax-only:
- Load `.wonflowoo/workspace/specs/_system.yml`
- Load all current relevant specs
- Load referenced architecture docs + ADRs
- Compare task file ↔ developer plan ↔ current system reality
- Validate acceptance criteria coverage, conventions, dependencies, edge cases, and architecture fit

Reviewer output: APPROVE or REJECT with specific issues.

If REJECTED, send revision feedback to the same developer role and request plan revision only (no implementation).

---

## Step 4 — Dispatch implementation (ONLY after approval)

Once a task plan is approved, spawn the same developer role for implementation:
- Load: task file + approved `.plan.md` + referenced specs/architecture/ADRs
- Goal: Implement the approved plan
- Output: code changes + **change manifest** (files created, files modified, endpoints added, data touched, plan deltas)
- Required checks after implementation:
  1. Verify ALL acceptance criteria from the task file are met
  2. Write a structured change manifest in the completion report
  3. Report status back to orchestrator (do not edit orchestrator tracking files directly)
- Stop condition: Stop after reporting completion evidence and change manifest
- **Developers do NOT update specs.** Spec updates are handled by `spec-updater` (see Step 5).

When platform supports continuation, prefer reusing the planning session/context to reduce reload waste.

---

## Step 5 — Spec update + validate completion + advance wave

After each developer completes a task:

### 5a. Spawn `spec-updater`
- Load: _system.yml + existing specs + developer's change manifest + task file + affected source files
- Goal: Determine which specs this task affects, update them, update _system.yml if needed
- Output: list of specs updated, what changed in each

**Why spec-updater, not the developer?** Specs are organized by feature (horizontal). Tasks are vertical slices that can cut across multiple features. The developer knows what code they wrote; the spec-updater knows the spec structure and has the macro view to route changes to the right specs.

### 5b. Validate completion
- Check acceptance criteria met
- Check `.plan.md` exists
- Check specs were updated by spec-updater
- Update task file status: `pending` → `in_progress` → `completed`
- Update plan doc with task status
- Update draft Implementation section with task completion, deviations, issues, spec paths

Wave progression:
- Only when all tasks in current wave are completed does the next wave unblock.

Failure handling:
- Developer-level issue → re-dispatch task with improved constraints/context
- Plan-level issue → return to Planning, revise plan, regenerate affected task files
- 3 consecutive failures → STOP, document attempts, escalate with deep analysis + human decision
