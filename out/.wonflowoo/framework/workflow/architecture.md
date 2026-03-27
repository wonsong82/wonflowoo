# Phase 2: Architecture (Cases 1, 2, 5, 6)

## Goal

Design HOW we're building it.

## Inputs to Load

1. Active draft `.wonflowoo/workspace/drafts/{id}-{name}.md`
2. Requirements `.wonflowoo/workspace/requirements/{id}-{name}.md`
3. `.wonflowoo/workspace/specs/_system.yml` + relevant current specs
4. Existing architecture docs (if extending/refactoring/migrating)

## Steps

**Step 1 — Research target technology.**
Fire librarian research for best practices, official docs, production patterns for the chosen (or proposed) tech stack. Do NOT design architecture from training data alone.

**Step 2 — Spawn tech lead for architecture design.**
For Medium+ complexity, ALWAYS spawn `architect` with:
- Load: active draft + requirements + `.wonflowoo/workspace/specs/_system.yml` + relevant current specs + existing architecture docs
- Goal: Design architecture for `{project}` (tech stack, system design, conventions, data model approach, API patterns), identify bottlenecks/security gaps/anti-patterns, and document trade-offs
- Output: architecture docs in `.wonflowoo/workspace/architecture/` + ADRs in `decisions/` for non-obvious decisions
- Stop condition: Stop after writing docs and returning summary of decisions/rationale

For Simple complexity, you may design architecture yourself.

**Step 3 — Write architecture docs:**
- `tech-stack.yml` — language, framework, DB, infra
- `conventions.yml` — naming, patterns, folder structure, error handling
- `system-design.md` — narrative: how it fits together, data model design, API design. Use Mermaid for diagrams.
- ADRs in `decisions/` for non-obvious decisions (e.g., "Why Prisma over raw SQL")

Also update `.wonflowoo/workspace/config.yml` with project metadata — ALL of these fields are REQUIRED:
- `project.name` — from requirements
- `project.description` — from requirements objective
- `spec_organization.unit_term` — the organizational unit from architecture (e.g., `module` for modular monolith, `service` for microservices, `package` for library)
- `spec_organization.boundary` — how units are separated (e.g., `service-layer` for layered arch, `api-boundary` for microservices)

If these fields are missing, spec generation downstream will not know how to organize specs. Do NOT skip them.

**Note on dependencies.yml:** This captures EXTERNAL SERVICE integrations (Shopify API, QuickBooks, SendGrid, S3) — NOT npm/pip packages. If there are no external service integrations, skip this file.

### Optional: Architecture Review (Medium+ complexity)

For Medium+ complexity, consider spawning `architecture-consultant` to review the architecture before presenting to human:
- Load: all architecture docs just written + requirements + _system.yml
- Goal: Identify scaling issues, security gaps, anti-patterns, missed trade-offs
- Output: Review report with findings and recommendations
- This is read-only consultation — the consultant does NOT modify architecture docs

If findings are critical, address them before running clearance.

**Step 4 — Run clearance check.**

```
ARCHITECTURE CLEARANCE:
□ System structure defined (how components connect)?
□ Data model designed (in system-design.md)?
□ API design established (patterns, auth, error format)?
□ Conventions decided (naming, folder structure, error handling)?
□ Non-obvious decisions documented as ADRs?
□ Specialist consulted (Medium+ complexity)?
□ Human aligned — no fundamental disagreements?
□ Architecture docs written to .wonflowoo/workspace/architecture/?
```

## Failure Handling

- Architect produces conflicting design → re-dispatch with specific conflict noted, ask for resolution
- Architecture-consultant review finds critical issues → address before phase gate, revise affected docs
- Librarian research contradicts proposed approach → present both options to human, let them decide
- 3 consecutive failures → STOP, document attempts and conflicts, escalate to human

## Phase Gate

If `auto_proceed` is false (default): STOP. Present summary to human. Wait for explicit confirmation. DO NOT auto-advance.
If `auto_proceed` is true: Log the summary to draft, proceed automatically.
