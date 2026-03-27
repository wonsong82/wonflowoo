# Developer Guide (for Spawned Developer Sub-Agents)

## What to Load First

1. Your task file: `.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.yml`
2. Referenced architecture docs (`architecture_refs`)
3. Referenced specs (`spec_refs`) + `_system.yml`
4. Referenced ADRs (`adr_refs`, if present)
5. Existing code you will modify

## Mandatory Workflow

1. **Write plan first** to `.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.plan.md`
2. Plan must include: files to create/modify, approach, order, edge cases, acceptance-criteria mapping
3. **STOP after plan** and report back
4. Implement only after explicit approval dispatch
5. After implementation, write a **change manifest** in your completion report
6. Report completion with:
   - **Files created** (full paths)
   - **Files modified** (full paths)
   - **Endpoints/interfaces added or changed**
   - **Data touched** (tables, schemas, cache keys)
   - **Deviations from plan** (if any)

## Implementation Conventions

- Follow conventions in `.wonflowoo/workspace/architecture/conventions.yml`
- Follow guardrails in `must_do` / `must_not_do`
- Meet all `acceptance_criteria`
- Keep changes scoped to task brief

## Focus Areas by Domain

### Backend

When implementing backend work, verify:
- API request/response behavior and status semantics
- Domain/business rule correctness
- Persistence schema/query changes and migration safety
- Transaction boundaries and consistency behavior
- Idempotency/retry/error-path handling
- Logging/observability and failure diagnostics
- Authn/authz and security constraints
- Performance risks at hot paths

### Frontend

When implementing frontend work, verify:
- Component contract and props/state consistency
- Routing/navigation behavior
- Form validation and user error handling
- Loading/empty/error/success states
- Responsiveness and layout stability
- Accessibility semantics and keyboard/screen-reader behavior
- Animation/transition correctness and performance
- State management consistency and side-effect safety

## Non-Negotiables

- Do NOT combine plan + implementation in one dispatch
- Do NOT update specs yourself — the `spec-updater` agent handles this after you complete
- Do NOT edit task status fields directly; report to orchestrator
- DO include a detailed change manifest in your completion report — the spec-updater depends on it
