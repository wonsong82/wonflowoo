# Task Writer Guide

Load `.wonflowoo/framework/agent-guides/tech-leads.md` first for foundational context.

## What You Do

Expand a high-level task brief from the plan doc into a **self-contained task instruction file** (`.yml`). The developer who receives this file should be able to work from it alone — without reading the plan, requirements, or architecture docs themselves.

## What You Receive

1. **Plan doc** — with the task brief (name, wave, category, dependencies, high-level description)
2. **Task ID and origin** — for file naming

## What You Load

1. `.wonflowoo/workspace/specs/_system.yml` — module structure, dependencies, cross-module flows
2. `.wonflowoo/workspace/architecture/` — tech stack, conventions, system design, ADRs
3. `.wonflowoo/workspace/requirements/` — confirmed requirements for this plan
4. Relevant feature specs from `.wonflowoo/workspace/specs/` — for existing code context
5. Existing source code — if the task modifies existing files, read them

## What You Write

One file per task: `.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.yml`

The task file must be **self-contained** — inline the relevant architecture detail, conventions, data model excerpts, error shapes, and module context so the developer doesn't need to load those docs separately.

Required fields:
```yaml
task: (description)
wave: (number)
status: pending
plan_ref: "{plan-id}-{plan-name}"
category: (developer category — deep, quick, unspecified-low, visual-engineering)
context: |
  WHY this task exists. Architecture detail inline — tech stack excerpt,
  conventions to follow, data model excerpts, error shapes.
brief: |
  WHAT to build. Specific enough to guide implementation.
architecture_refs: [list of arch doc paths]
spec_refs: [list of spec paths — existing specs the developer should reference]
adr_refs: [list of ADR paths, if relevant]
must_do: [explicit requirements]
must_not_do: [explicit constraints]
acceptance_criteria: [verifiable items]
depends_on: [task IDs this depends on]
blocks: [task IDs this blocks]
```

## Rules

- The `context` field is the most important — it's what makes the task self-contained. Don't be brief here. Include actual code patterns, schema definitions, endpoint shapes from the architecture docs.
- Choose the right `category` for the developer — `deep` for complex multi-file work, `quick` for trivial changes, `visual-engineering` for frontend.
- `must_do` and `must_not_do` are guardrails — be specific about what the developer MUST and MUST NOT touch.
- `acceptance_criteria` must be verifiable — "endpoint returns 200 with correct shape" not "endpoint works."
