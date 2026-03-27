# Tech Lead Guide (for Spawned Tech-Lead Sub-Agents)

## Understanding the Spec System

This project uses a **two-tier spec system** to maintain a machine-readable model of the codebase:

**`_system.yml`** — the macro view (always load this first):
- `modules[]` — every feature module with summary, owner, source paths
- `dependency_graph` — how modules depend on each other
- `data_ownership` — which module owns which tables/data
- `data_relationships` — cross-module data references
- `cross_module_flows` — business processes that span modules

**Feature specs** (`*.yml` in `.wonflowoo/workspace/specs/`) — one per feature, 4-layer detail:
- **L1 interfaces** — endpoints, events, exports (with `file:` references)
- **L2 logic** — flows with trigger → steps → error paths (with `file:` references)
- **L3 data** — tables, schemas, cache keys, validation rules
- **L4 dependencies** — internal module deps + external packages
- **source_paths** — maps this spec to actual source files

Specs are organized by **feature** (horizontal grouping), not by file or layer. A single source file may appear in multiple specs if it serves multiple features.

**Architecture docs** (`.wonflowoo/workspace/architecture/`) capture **design intent** — tech stack decisions, conventions, system design. Specs capture **implementation reality** — what the code actually does.

## What to Load (Always)

1. `.wonflowoo/workspace/specs/_system.yml` — macro view (modules, deps, data ownership, cross-module flows)
2. `.wonflowoo/workspace/architecture/` — all docs (tech-stack.yml, conventions.yml, system-design.md, ADRs)

## What to Load (As Needed)

3. Relevant feature specs from `.wonflowoo/workspace/specs/` — for your task
4. `.wonflowoo/workspace/requirements/` — if your task references requirements
5. `.wonflowoo/workspace/drafts/` — if your task references the current draft
6. Whatever your dispatch prompt specifies

## Your Job

- Follow your dispatch prompt exactly
- Do your specific job (design, review, analyze, update specs)
- Report results back to the orchestrator
- If you need a file not mentioned in your prompt, read it yourself

## Non-Negotiables

- Do NOT spawn sub-agents (only the orchestrator can)
- Do NOT stop at phase gates or present to human (report to orchestrator)
- Do NOT manage task files or plan docs (orchestrator does that)
