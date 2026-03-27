# Spec Updater Guide

Load `.wonflowoo/framework/agent-guides/tech-leads.md` first for foundational context (spec system, what to load).

## What You Receive

1. **Developer's change manifest** — files created, files modified, endpoints added, data touched
2. **Task file** — the original task instruction (.yml)
3. **Source file paths** — the actual code the developer wrote/changed

## Process

### 1. Determine Affected Specs

Read the change manifest's file paths. For each file, check which existing spec's `source_paths` includes it (or is in the same module area). A single task may affect 1-3 specs.

- File matches existing spec's `source_paths` → UPDATE that spec
- File is in a new area not covered by any spec → CREATE new spec
- File adds cross-module interaction → UPDATE `_system.yml` flows

### 2. Update Each Affected Spec

For each affected spec, read the relevant source code and update:
- **L1 interfaces**: new endpoints, events, exports
- **L2 logic**: new flows, modified flows (trigger + steps + error paths)
- **L3 data**: new tables, columns, cache keys, schema changes
- **L4 dependencies**: new internal/external deps
- **source_paths**: add new files, keep existing ones

Preserve everything in the spec that wasn't affected. Only add/modify entries related to this task's changes.

### 3. Update `_system.yml`

If the changes affect the system level:
- New module added → add to `modules[]`
- New cross-module interaction → add to `cross_module_flows`
- New data ownership → update `data_ownership`
- New dependency between modules → update `dependency_graph`

If changes are purely within one module with no system-level impact, skip `_system.yml`.

## Rules

- Read the actual source code — don't guess from file names
- Preserve existing spec content — only ADD or MODIFY entries, never delete unless code was removed
- Every interface and flow entry must include `file:` pointing to the source file
- Every new source file must appear in some spec's `source_paths`
- Keep specs factual — document what the code DOES, not what it SHOULD do

## Output

Report back:
1. Which spec files were updated (list)
2. What was added/changed in each (1-2 lines per spec)
3. Whether `_system.yml` was updated and why
