# Phase 3: Planning (Cases 1, 2, 5, 6)

## Goal

Break architecture into dependency-ordered, delegatable tasks.

## Inputs to Load

1. Active draft `.wonflowoo/workspace/drafts/{id}-{name}.md`
2. Requirements `.wonflowoo/workspace/requirements/{id}-{name}.md`
3. Architecture docs in `.wonflowoo/workspace/architecture/`
4. `.wonflowoo/workspace/specs/_system.yml` + relevant current specs

## Draft Management Rules (applies across phases)

- Create `.wonflowoo/workspace/drafts/{id}-{name}.md` for non-trivial work (template: `.wonflowoo/framework/schemas/draft.template.md`)
- Update after every meaningful exchange or decision
- Human tech preferences go in draft, not requirements
- Never delete drafts; mark `Status: done` when complete

## Steps

**Step 1 — Spawn tech lead for gap analysis.**
Spawn `gap-analyst` with:
- Load: requirements at `{path}` + architecture docs in `.wonflowoo/workspace/architecture/` + active draft at `{path}` + `.wonflowoo/workspace/specs/_system.yml` and relevant specs
- Goal: Identify missed questions, unvalidated assumptions, missing acceptance criteria, edge cases, and scope creep
- Output: Gap report classifying each item as critical (needs human answer), minor (self-resolve), or ambiguous (apply default)
- Stop condition: Stop after returning the gap report

If the specialist finds CRITICAL gaps → go back to human before planning.

**Step 2 — Task breakdown with dependency-ordered waves.**
Structure varies by case:
- Greenfield: foundation → core features (parallel) → dependent features → verification
- Add Feature: 1-3 waves
- Refactoring: incremental, each step leaves system working
- Migration: pilot (Wave 0) → batch → verification

**Step 3 — Write high-level task briefs only (no implementation-level details in plan).**
Each task in the plan includes high-level: description, category, acceptance criteria, dependencies, guardrails.

Do NOT write detailed implementation instructions in the plan doc.

Detailed task instruction files are generated **per-wave** during Delegation by spawned tech leads who load current architecture + specs at dispatch time.

**Step 4 — Write plan doc.**
Output: `.wonflowoo/workspace/plans/{id}-{name}.md` with:
- `Status: pending_approval | approved | in_progress | completed`
- `Task IDs: [00001, 00002, 00003, ...]` (populated during delegation)
- Gap analysis results
- Wave structure with high-level task briefs
- Per-task status tracking (pending/in_progress/completed/blocked)
- Acceptance criteria per task

The plan defines WHAT and ORDER. Detailed task files are produced later, wave-by-wave.

**Step 5 — Run clearance check.**

```
PLANNING CLEARANCE:
□ Gap analysis completed by specialist?
□ All tasks have clear deliverables and acceptance criteria?
□ Dependency ordering correct (no circular deps, no missing prerequisites)?
□ Each task scoped to feature-level (not too granular, not too coarse)?
□ Category assigned to every task (for model routing)?
□ Plan reviewed and confirmed by human?
□ Critical gaps resolved (or explicitly deferred with user approval)?
□ Plan doc written to .wonflowoo/workspace/plans/?
```

## Failure Handling

- Gap analyst finds unresolvable gaps → present to human with options, do not proceed until resolved
- Task decomposition doesn't cover all requirements → re-check requirements doc, add missing tasks
- Dependency ordering has circular deps → restructure waves, split tasks if needed
- 3 consecutive failures → STOP, document what's blocking, escalate to human

## Phase Gate

If `auto_proceed` is false (default): STOP. Present summary to human. Wait for explicit confirmation. DO NOT auto-advance.
If `auto_proceed` is true: Log the summary to draft, proceed automatically.
When human confirms the plan, update the plan doc status from `pending_approval` to `approved`.
